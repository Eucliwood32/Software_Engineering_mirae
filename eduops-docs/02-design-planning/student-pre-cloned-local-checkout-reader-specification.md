---
title: Student Pre-cloned Local-Checkout Reader Specification
document_id: SWENG-EDUTECH-STUDENT-LOCAL-CHECKOUT-READER-SPEC
version: 0.1.0
status: accepted-for-fixture-implementation
date: 2026-05-16
owner: develop
quality_context: Ralph-controlled HOW-level specification checkpoint
traceability:
  upstream:
    - SWENG-EDUTECH-ROSTER-SCHEMA
    - SWENG-EDUTECH-ACCESS-CONTROL-AUTHORIZATION-MODEL
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-MODULE-LAYOUT
    - SWENG-EDUTECH-INTERNAL-API
  requirements:
    - EDUOPS-FR-002
    - EDUOPS-FR-003
    - EDUOPS-FR-004
    - EDUOPS-FR-023
    - EDUOPS-FR-024
    - EDUOPS-NFR-004
    - EDUOPS-NFR-013
    - EDUOPS-NFR-035
  verification:
    - STD-M7-STUDENT-LOCAL-CHECKOUT-READER-001
    - STD-M7-STUDENT-LOCAL-CHECKOUT-READER-002
    - STD-M7-STUDENT-LOCAL-CHECKOUT-READER-003
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
---

# Student Pre-cloned Local-Checkout Reader Specification

## 1. Purpose

This specification defines the fixture-local HOW-level contract for the **student pre-cloned local-checkout reader** that the clone-readonly approval workflow's `cloneInputMode='student_local_checkout'` branch produces a downstream consumer for. It authorizes fixture-local filesystem-only reads inside a per-student workspace boundary, deterministic redaction, content safety scans, and evidence envelope assembly for a checkout that the student has already prepared outside EduOps automation. It does **not** authorize a real `git clone`/`git fetch`/`git push`/`git ls-remote`, a real credential lookup, a network call of any kind, a remote configuration, a GitHub administration action, or any live external action; those remain user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

This specification complements [Clone-readonly human approval workflow UX specification](clone-readonly-approval-workflow-ux-specification.md) (which authorizes the `cloneInputMode='student_local_checkout'` approval surface), [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md) (which defines the analogous read boundary contract for the live-clone path), [Access control and authorization model](access-control-authorization-model.md) (which establishes the per-student workspace isolation requirement), and the M4 local workspace provisioning evidence (which defines the per-student `<student-workspace>/` path structure produced by `M4-T4`).

## 2. Authorized scope

| Area | Authorized for this slice | Not authorized |
|---|---|---|
| Read source | Filesystem reads inside the per-student workspace boundary `<student-workspace>/local-checkouts/<repo-id>/` only; the workspace path label is supplied by the approval surface and is already a redacted/displayable label | Reads outside the per-student workspace; reads across student workspace boundaries; reads of EduOps configuration / credential / system files |
| Read protocol | Filesystem `read` syscalls on files under the authorized path; canonical path resolution that REJECTS any symlink whose target leaves the workspace boundary | Network requests of any kind; `git` invocations of any kind; credential resolution; environment-variable lookup beyond the controlled workspace path |
| Approval predecessor | Requires an approved dry-run plan id (produced by [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md) §4.4) with `cloneInputMode='student_local_checkout'`; the reader MUST reject any request whose predecessor mode is not `student_local_checkout` | Reading without a referenced approval predecessor; reading when the predecessor approval mode is `clone_readonly` or any other live mode |
| Content classification | Distinguish text vs. binary by a leading-byte heuristic; only text content is subject to UTF-8 decode; binary content is recorded as content kind without decode | Format-specific parsing of student source (e.g., executing student programs, compiling, evaluating) |
| Redaction | Redact workspace path label to FNV-1a 64 envelope `workspace_path_label_hash`; redact each file path to FNV-1a 64 `path_hash`; SHA-256 over canonical file bytes for `content_sha256` | Persisting raw filesystem paths or raw file contents in evidence beyond the bounded redacted records |
| Output | Deterministic `StudentLocalCheckoutReadEvidence` envelope with sorted-key canonical JSON, in-crate SHA-256 manifest hash, accepted/rejected file counts, redacted per-file records, hardcoded `external_call_made=false`/`external_side_effect_made=false`/`github_mutation_made=false`/`live_external_action=false`/`clone_readonly_executed=false`/`network_call_made=false`/`credential_resolved=false`/`local_checkout_read_executed=true`/`no_raw_secret_observed=true`/`no_raw_repository_url_persisted=true` | Live-run evidence; submission/provisioning promotion; evaluation-result authority |
| Privacy | Raw filesystem paths, raw file contents, raw `student_internal_id`, raw `email`, and raw `github_repository_url` MUST NOT appear in evidence; redacted/hashed envelopes only | Persisting any raw PII, raw paths, or raw secrets anywhere in evidence |

## 2.1 User-managed boundary

Per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`, the student is responsible for performing the actual `git clone` outside EduOps automation and supplying the resulting local checkout under their own workspace. EduOps accepts the prepared checkout as already-authorized input and immediately routes the workspace path label through redaction. EduOps does not configure remotes, does not call the GitHub API, does not perform a real `git clone`/`git fetch`/`git push`/`git ls-remote`, does not resolve credentials, does not invoke any process beyond the in-process filesystem read, and does not store the raw workspace path anywhere in evidence beyond the in-memory request buffer.

The professor / course-admin remains responsible for the upstream allowlist and approval per the clone-readonly integration-point spec; the reader only operates on a checkout whose predecessor approval id is already accepted.

## 3. Input contract: `StudentLocalCheckoutReadRequest`

| Field | Required | Type | Notes |
|---|---|---|---|
| `read_id` | Yes | string | Stable fixture id; no raw PII or credential-shaped value; pattern `read_student_local_checkout_<short-id>`. |
| `approved_dry_run_plan_id` | Yes | string | The redacted dry-run plan id produced by the upstream approval workflow; pattern `audit_clone_readonly_plan_<short-id>`. |
| `approval_predecessor_mode` | Yes | enum | MUST be `student_local_checkout`; any other value rejects with `STUDENT_LOCAL_CHECKOUT_INPUT_MODE_MISMATCH`. |
| `workspace_path_label` | Yes | string | Redacted/displayable label for the student workspace root (NOT a raw filesystem path); pattern `student-local-checkout-<short-id>`. |
| `workspace_root_path` | Yes | string (filesystem path) | Per-student workspace absolute path produced by `M4-T4`; only accessed in-memory and via canonical-path resolution; never persisted in evidence beyond the FNV-1a 64 `workspace_path_label_hash`. |
| `relative_repo_path` | Yes | string | Path under `workspace_root_path` to the cloned repo root (e.g., `local-checkouts/<repo-id>/`); MUST stay within the workspace boundary. |
| `expected_files` | Yes | array of relative file paths | List of expected assignment files (e.g., `["src/main.c", "README.md"]`); each path MUST stay within `relative_repo_path` and MUST NOT contain `..` segments. |
| `safe_read_byte_cap` | Yes | non-negative integer | Per-file safe-read size cap (e.g., `262144` for 256 KiB); files exceeding this cap reject with `STUDENT_LOCAL_CHECKOUT_FILE_SIZE_EXCEEDED`. |
| `requested_by_role` | Yes | enum | One of `student`, `instructor`, `ta`, `course_admin`, `platform_admin`, `evaluator`; only `student` may read their own checkout, and only `course_admin`/`platform_admin`/`evaluator`/`ta`/`instructor` (with explicit per-student authorization recorded in the approval evidence) may read on behalf of a student. |
| `requested_at_utc` | Yes | RFC 3339 UTC timestamp | Stable fixture timestamp; no clock skew compensation. |

Raw filesystem paths and raw file contents are explicitly not persisted in the evidence; they exist only in the in-memory request buffer and are redacted before envelope construction. The `workspace_root_path` and `relative_repo_path` are scrubbed from any error message produced by the reader.

## 4. Validation rules

For each `StudentLocalCheckoutReadRequest` and per expected file:

1. **Approval predecessor**: `approved_dry_run_plan_id` MUST be non-empty and MUST match the redacted-id form (`audit_clone_readonly_plan_<short-id>`); otherwise reject with `STUDENT_LOCAL_CHECKOUT_APPROVAL_PLAN_MISSING`.
2. **Approval mode**: `approval_predecessor_mode` MUST be `student_local_checkout`; otherwise reject with `STUDENT_LOCAL_CHECKOUT_INPUT_MODE_MISMATCH`.
3. **Workspace label redaction shape**: `workspace_path_label` MUST NOT contain raw HTTPS / HTTP / SSH URL form (`https://`, `http://`, `git@`), raw GitHub PAT prefix (`ghp_`/`github_pat_`), raw URL credential form (`://user:token@host`), or raw email substring (`X@Y.Z`); otherwise reject with `STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED`.
4. **Path safety (pre-read)**: every expected file path under `relative_repo_path` MUST resolve canonically inside the workspace boundary `<workspace_root_path>/<relative_repo_path>/`; any `..` segment, absolute path component, or symlink whose target leaves the workspace MUST be rejected with `STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE`. No file is opened until this check passes.
5. **Read boundary**: every actual filesystem `read` MUST occur inside the workspace boundary; any read attempt outside the boundary (defensively detected via canonical path comparison) MUST be rejected with `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` and the reader MUST abort emission.
6. **Expected file presence**: each expected file MUST exist as a regular file (not directory, not symlink, not device); otherwise reject with `STUDENT_LOCAL_CHECKOUT_EXPECTED_FILE_MISSING`.
7. **Safe-read size cap**: each file's size in bytes MUST NOT exceed `safe_read_byte_cap`; otherwise reject with `STUDENT_LOCAL_CHECKOUT_FILE_SIZE_EXCEEDED` and the reader MUST NOT attempt the full read (the size check uses metadata).
8. **Content classification**: files are classified as text (UTF-8 decodable) or binary by a leading-byte heuristic that scans the first 4096 bytes for null bytes or non-UTF-8 sequences. Text classification with invalid UTF-8 after metadata-based classification rejects with `STUDENT_LOCAL_CHECKOUT_INVALID_UTF8`.
9. **Per-file raw-secret scan (post-read)**: every file's content buffer MUST be scanned for raw GitHub PAT prefix (`ghp_`/`github_pat_` case-insensitive), URL credential form (`://user:token@host`), and SSH private-key blob prefix (`-----BEGIN OPENSSH PRIVATE KEY-----`) before SHA-256 computation; any hit MUST be rejected with `STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED` and the reader MUST abort emission to prevent the offending bytes from being hashed or recorded.
10. **Authorization**: when `requested_by_role` is not `student`, the request MUST carry an authorization predecessor recorded in the approval evidence (instructor/ta/course_admin/platform_admin/evaluator with per-student authorization); otherwise reject with `STUDENT_LOCAL_CHECKOUT_NOT_AUTHORIZED`.

## 5. Evidence envelope: `StudentLocalCheckoutReadEvidence`

The reader emits a `StudentLocalCheckoutReadEvidence` value with the following shape (logical names; concrete field names follow the existing Rust/JS naming conventions in [Internal API contract](internal-api-contract.md)):

| Field | Type | Rule |
|---|---|---|
| `read_id` | string | Stable fixture id from the request. |
| `approved_dry_run_plan_id` | string | Redacted predecessor id from the request. |
| `workspace_path_label_hash` | string | FNV-1a 64 envelope `fnv1a64:<16hex>` over the canonical workspace path label. |
| `relative_repo_path_hash` | string | FNV-1a 64 envelope over the canonical relative repository path. |
| `accepted_file_count` | integer | Non-negative. |
| `rejected_file_count` | integer | Non-negative. |
| `redacted_file_records` | array of records | Each record carries `path_hash` (FNV-1a 64 over canonical relative file path), `content_sha256` (SHA-256 over canonical file bytes), `file_size_bytes` (non-negative integer), `content_kind` (`text-utf8`/`binary-opaque`), and `audit_event_id` (`audit_student_local_checkout_file_<read_id>_<index>_<path_hash_short>`). No raw filesystem paths or raw contents. |
| `rejected_file_records` | array of records | Each record carries a `reason_code` (one of the `STUDENT_LOCAL_CHECKOUT_*` codes), a `redacted_path_hash` (or empty when the rejection occurred before path resolution), and a `redacted_reason` (code-only string; no offending bytes). |
| `requested_by_role` | string | Echoed from the request for audit. |
| `requested_at_utc` | string | Echoed from the request for audit. |
| `canonical_json` | string | Sorted-key canonical JSON of all fields except `canonical_json` and `evidence_sha256`. |
| `evidence_sha256` | string | In-crate SHA-256 over `canonical_json`. |
| `audit_event_ids` | array | Includes `audit_student_local_checkout_read_<read_id>` plus per-file audit ids from the `redacted_file_records`. |
| `external_call_made` | bool | Hardcoded `false`. |
| `external_side_effect_made` | bool | Hardcoded `false`. |
| `github_mutation_made` | bool | Hardcoded `false`. |
| `live_external_action` | bool | Hardcoded `false`. |
| `clone_readonly_executed` | bool | Hardcoded `false`. |
| `network_call_made` | bool | Hardcoded `false`. |
| `credential_resolved` | bool | Hardcoded `false`. |
| `local_checkout_read_executed` | bool | Hardcoded `true` (this is the only true literal; it records the fact that the in-process filesystem read inside the workspace boundary did occur). |
| `no_raw_secret_observed` | bool | Hardcoded `true`. |
| `no_raw_repository_url_persisted` | bool | Hardcoded `true`. |

The reader MUST refuse to emit when any hardcoded `false` flag is mutated to `true` (or vice versa for `local_checkout_read_executed`/`no_raw_secret_observed`/`no_raw_repository_url_persisted`), when any raw credential / URL credential form / raw repository URL appears in any field of the evidence, when any raw filesystem path appears in any field of the evidence, or when the redacted-file-records array contains any raw content.

## 6. Fail-closed safety guards

- **Pre-construction request scan** (`scan_local_checkout_request_for_raw_secrets`): every text-bearing field on the request (`workspace_path_label`, `relative_repo_path`, every expected file path, `read_id`, `approved_dry_run_plan_id`, `requested_by_role`, `requested_at_utc`) is scanned for raw PAT prefix, URL credential form, raw HTTPS/HTTP/SSH URL form, raw email substring, and SSH private-key blob prefix BEFORE any filesystem read; any hit rejects with `STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED`.
- **Path-safety pre-read scan** (`evaluate_local_checkout_path_safety`): every expected file path is canonicalized against the workspace boundary; any `..` segment, absolute path, or symlink whose target leaves the boundary rejects with `STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE` BEFORE the file is opened.
- **Per-read boundary check**: every actual filesystem `read` is preceded by a canonical-path comparison against the workspace boundary; defensive duplicate of the pre-read scan that catches TOCTOU edge cases (e.g., a symlink swapped between the pre-read scan and the actual read).
- **Per-file content scan** (`scan_local_checkout_content_for_raw_secrets`): every read content buffer is scanned for raw PAT prefix, URL credential form, and SSH private-key blob prefix BEFORE the buffer is fed to SHA-256; any hit aborts emission. The scan operates on bytes, not UTF-8-decoded strings, so it works for both text and binary content.
- **Post-construction evidence scan** (`scan_local_checkout_evidence_for_raw_secrets`): every text-bearing field on the constructed evidence is scanned with the same patterns plus a raw-filesystem-path heuristic (`/`, `\\`, `:/` on Windows) that catches any path leakage; any hit aborts emission.
- **Privacy scan**: raw `workspace_root_path`, `relative_repo_path`, expected file paths, file contents, and any PII-shaped substring MUST be absent from the constructed evidence text; any leak aborts emission.

## 7. Non-claims

This specification does not claim:

- live HTTPS/SSH probe of any GitHub repository URL;
- real `git clone`, `git fetch`, `git push`, `git ls-remote`, or any other live Git command;
- real credential resolution, token refresh, credential rotation, or credential storage modification;
- repository creation, push, branch/tag, issue, webhook, check-run, invitation, branch protection, archive, or any GitHub administration action;
- a network call of any kind from the reader;
- a real desktop file-picker UI, drag-and-drop file selection, or Tauri shell wiring of a production student-checkout import surface;
- submission/provisioning state promotion from local-checkout read evidence;
- evaluation-result authority (the reader emits read-evidence only; evaluation is a separate downstream concern bounded by the M6 advisory runner gate);
- DEMO-1 acceptance or live working-demonstration approval;
- full-Unicode NFC normalization beyond the existing controlled Hangul L+V+T composition behavior (canonical reordering / compatibility decomposition / Latin combining marks remain identity until a controlled external `unicode-normalization` dependency is adopted);
- password-form key-value detection (`password=`/`passwd=`/`secret=`/`token=`) beyond the explicitly-enumerated SSH private-key blob prefix;
- SHA-256 source-URL audit hash upgrade beyond the existing FNV-1a 64 envelope (deferred per `m7-clone-readonly-evidence.md` §7 item 3);
- a real authorization-predecessor lookup against a live identity provider; the authorization check operates on the redacted approval predecessor id only and assumes the upstream approval evidence has already recorded any per-student authorization for non-`student` roles;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 8. First executable Ralph tasks

| Task ID | Test command | RED condition | GREEN acceptance |
|---|---|---|---|
| `M7-STUDENT-LOCAL-CHECKOUT-READER-T1` | Add `crates/eduops_domain/tests/m7_student_local_checkout_reader_contract.rs` (or analogous crate location aligned with existing checkout/workspace types), then run `cargo test -p eduops_domain --test m7_student_local_checkout_reader_contract -- --nocapture` | No `StudentLocalCheckoutReadRequest`/`StudentLocalCheckoutReadEvidence` types or reader function exists. | Reader accepts a controlled fixture request with an approved dry-run plan id and `approval_predecessor_mode='student_local_checkout'`, reads a small controlled fixture file tree inside a temporary workspace boundary, redacts the workspace path label to `workspace_path_label_hash`, redacts each file path to `path_hash`, computes `content_sha256` per file, produces deterministic canonical JSON + in-crate SHA-256, and emits `StudentLocalCheckoutReadEvidence` with the hardcoded non-mutation literals. STD-M7-STUDENT-LOCAL-CHECKOUT-READER-001 covered. |
| `M7-STUDENT-LOCAL-CHECKOUT-READER-T2` | Add focused fail-closed safety contract tests (raw PAT in workspace label, URL credential form in request fields, path escape via `..` segment, path escape via symlink to outside workspace, read outside workspace boundary, expected file missing, file exceeds safe-read byte cap, invalid UTF-8 when text was expected, raw PAT in read content, SSH PEM blob in read content, approval predecessor missing, approval mode mismatch, not-authorized non-`student` role without approval-predecessor authorization), then run the focused safety test | Safety guards absent or incomplete. | Every safety guard rejects the listed unsafe fixture before evidence emission; `STUDENT_LOCAL_CHECKOUT_*` rejection codes match the spec §4 / §6 enumeration; no offending bytes leak into rejection messages. STD-M7-STUDENT-LOCAL-CHECKOUT-READER-002/003 covered. |
| `M7-STUDENT-LOCAL-CHECKOUT-READER-GATE` | Repository docs/control validation plus focused reader/safety tests | Evidence summary missing or overclaims live behavior. | Constrained evidence records fixture-local reader acceptance and explicit non-claims; no live HTTPS/SSH probe, real `git clone`/`fetch`/`push`/`ls-remote`, credential resolution, repository administration, real desktop file-picker UI, submission/provisioning promotion, or DEMO-1 acceptance. |

## 9. Traceability

- Upstream design: [Roster schema and identity policy](roster-schema-and-identity-policy.md); [Access control and authorization model](access-control-authorization-model.md); [Clone-readonly human approval workflow UX specification](clone-readonly-approval-workflow-ux-specification.md); [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md); [GitHub adapter specification](github-adapter-specification.md); [GitHub topology and token model](github-topology-and-token-model.md); [Module and package layout](module-and-package-layout.md); [Internal API contract](internal-api-contract.md).
- Upstream evidence: [M4 SLICE-C roster, identity, and workspace gate evidence](../06-implementation/m4-slice-c-roster-identity-workspace-evidence.md); [M7 clone-readonly integration-point gate evidence](../06-implementation/m7-clone-readonly-evidence.md); [M7 clone-readonly approval workflow UX gate evidence](../06-implementation/m7-approval-ux-evidence.md); [M7 approval UX predecessor reference integration gate evidence](../06-implementation/m7-approval-ux-intake-link-evidence.md); [M7 approval UX predecessor block accessibility hardening gate evidence](../06-implementation/m7-approval-ux-predecessor-a11y-harden-evidence.md).
- Verification anchors: [Software test description](../03-verification-validation/software-test-description.md) §M7 student pre-cloned local-checkout reader test addendum (to be authored alongside `M7-STUDENT-LOCAL-CHECKOUT-READER-T1`).
- Requirements: [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`.
- Decisions: `EDUOPS-DEC-064`; `EDUOPS-DEC-065`.
