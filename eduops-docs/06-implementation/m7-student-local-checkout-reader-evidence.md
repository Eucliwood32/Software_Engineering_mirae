---
title: M7 Student Pre-cloned Local-Checkout Reader Gate Evidence
document_id: EDUOPS-M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-STUDENT-LOCAL-CHECKOUT-READER-SPEC
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-ROSTER-SCHEMA
    - SWENG-EDUTECH-ACCESS-CONTROL-AUTHORIZATION-MODEL
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M7-APPROVAL-UX-EVIDENCE
    - EDUOPS-M7-APPROVAL-UX-INTAKE-LINK-EVIDENCE
    - EDUOPS-M7-APPROVAL-UX-PREDECESSOR-A11Y-HARDEN-EVIDENCE
    - EDUOPS-M7-CLONE-READONLY-EVIDENCE
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - m7_student_local_checkout_reader_contract
    - m7_student_local_checkout_reader_safety_contract
---

# M7 Student Pre-cloned Local-Checkout Reader Gate Evidence

## 1. Gate result

`GATE-M7-STUDENT-LOCAL-CHECKOUT-READER-FIXTURE-LOCAL` is accepted-constrained for the fixture-local in-process student pre-cloned local-checkout reader added by `M7-STUDENT-LOCAL-CHECKOUT-READER-T1` at `2b9d4ea` and the fail-closed safety guards added by `M7-STUDENT-LOCAL-CHECKOUT-READER-T2` at `d42e75c`. The reader implements [Student pre-cloned local-checkout reader specification](../02-design-planning/student-pre-cloned-local-checkout-reader-specification.md) §3-§6 within the no-live-action / no-real-git / no-credential-resolution / no-network / no-repository-administration boundary established by `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

This gate closes the follow-up recorded in [M7 approval UX predecessor block accessibility hardening gate evidence](m7-approval-ux-predecessor-a11y-harden-evidence.md) §7 item 4 (student pre-cloned local-checkout reader specification and reader implementation).

```text
gate=GATE-M7-STUDENT-LOCAL-CHECKOUT-READER-FIXTURE-LOCAL
status=accepted-constrained
scope=crates/eduops_domain/src/lib.rs::read_student_local_checkout accepts a StudentLocalCheckoutReadRequest with approval_predecessor_mode="student_local_checkout" and approved_dry_run_plan_id matching pattern "audit_clone_readonly_plan_*", performs in-process std::fs::read of each expected file under <workspace_root_path>/<relative_repo_path>/<rel>, applies FNV-1a 64 redaction to the workspace path label and relative repo path, applies FNV-1a 64 redaction to each file path, computes per-file SHA-256, classifies content via leading-4096-byte null/UTF-8 heuristic into text-utf8 / binary-opaque, emits per-file audit_student_local_checkout_file_<read_id>_<index>_<12hex> audit ids plus a per-read audit_student_local_checkout_read_<read_id> audit id, builds sorted-key canonical JSON with hardcoded external_call_made=false / external_side_effect_made=false / github_mutation_made=false / live_external_action=false / clone_readonly_executed=false / network_call_made=false / credential_resolved=false / local_checkout_read_executed=true / no_raw_secret_observed=true / no_raw_repository_url_persisted=true literals, computes evidence_sha256 via in-crate SHA-256 over the canonical JSON, and emits a StudentLocalCheckoutReadEvidence; fail-closed safety guards include top-level rejection of empty/non-prefixed approved_dry_run_plan_id (STUDENT_LOCAL_CHECKOUT_APPROVAL_PLAN_MISSING), non-"student_local_checkout" approval_predecessor_mode (STUDENT_LOCAL_CHECKOUT_INPUT_MODE_MISMATCH), unknown requested_by_role outside the [student,instructor,ta,course_admin,platform_admin,evaluator] enum (STUDENT_LOCAL_CHECKOUT_NOT_AUTHORIZED), pre-construction raw-credential scan over every text-bearing request field including every expected_files entry (STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED for raw PAT prefix / URL credential form / raw HTTPS/HTTP/SSH URL / raw email substring / SSH PEM blob), and per-file content scan over read bytes before SHA-256 (STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED for raw PAT prefix / URL credential form / SSH PEM blob); per-file rejection records preserve STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE for lex-only .. segment / absolute path / root component / prefix component / NUL byte, STUDENT_LOCAL_CHECKOUT_EXPECTED_FILE_MISSING for fs::metadata or fs::read error, STUDENT_LOCAL_CHECKOUT_FILE_SIZE_EXCEEDED for metadata-based size cap, and STUDENT_LOCAL_CHECKOUT_INVALID_UTF8 for text-utf8-classified files whose full content fails std::str::from_utf8 decode; all rejection record redacted_reason fields contain only the rejection code, no offending bytes
constraint=live HTTPS/SSH probe, real git clone/fetch/push/ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration (creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive), real desktop file-picker UI / drag-and-drop file selection / Tauri shell wiring of a production student-checkout import surface, real authorization-predecessor lookup against a live identity provider, network call of any kind, submission/provisioning state promotion from local-checkout read evidence, evaluation-result authority, defensive READ_OUTSIDE_WORKSPACE canonical-path comparison duplicate (rule 5), symlink-target inspection (partial rule 4), strict rule-6 not-symlink/not-device/not-directory file-kind check beyond plain file existence, post-construction scan_local_checkout_evidence_for_raw_secrets evidence-text scan (every input that could carry a raw secret is already blocked pre-construction, and every output field is either FNV-1a 64 redacted, SHA-256 redacted, an enum literal, or a hardcoded boolean — the defensive belt-and-suspenders sweep remains deferred), full-Unicode NFC normalization beyond existing Hangul L+V+T composition (deferred per existing professor CSV non-claims), password-form key-value detection (password=/passwd=/secret=/token=) beyond the explicitly-enumerated SSH PEM blob headers, SHA-256 source-URL audit hash upgrade beyond the FNV-1a 64 envelope, legal/privacy/compliance authority beyond reapplication of existing controlled redaction rules, and DEMO-1 acceptance are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
credential_resolutions=0
remote=none
```

This evidence does not claim a live GitHub action, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, repository administration, real desktop file-picker UI, submission/provisioning state promotion from local-checkout read evidence, evaluation-result authority, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted student pre-cloned local-checkout reader behavior:

- `crates/eduops_domain/src/lib.rs` defines public types `STUDENT_LOCAL_CHECKOUT_READ_SCHEMA_VERSION = "eduops.student-local-checkout-read/0.1"`, `StudentLocalCheckoutReadRequest` (10 fields: `read_id`, `approved_dry_run_plan_id`, `approval_predecessor_mode`, `workspace_path_label`, `workspace_root_path`, `relative_repo_path`, `expected_files`, `safe_read_byte_cap`, `requested_by_role`, `requested_at_utc`), `StudentLocalCheckoutRedactedFileRecord` (5 fields: `path_hash`, `content_sha256`, `file_size_bytes`, `content_kind`, `audit_event_id`), `StudentLocalCheckoutRejectedFileRecord` (3 fields: `reason_code`, `redacted_path_hash`, `redacted_reason`), and `StudentLocalCheckoutReadEvidence` (24 fields including the redacted-and-aggregated record arrays, sorted-key `canonical_json` + in-crate `evidence_sha256`, per-read and per-file `audit_event_ids`, and the spec §5 hardcoded literal flags).
- `read_student_local_checkout(request)` enforces spec §4 rules 1, 2, 3-subset, 4 (lex-only), 6, 7 (metadata-based), 8 (full-file UTF-8 decode for text-classified), 9 (PAT + URL credential + SSH PEM), and 10 (role enum).
- Pre-construction raw-credential scan `scan_local_checkout_request_for_raw_secrets` walks every text-bearing request field including every `expected_files` entry and detects raw GitHub PAT prefix (`ghp_`/`github_pat_` case-insensitive substring), URL credential form (`://...:...@...` ASCII pattern), raw HTTPS/HTTP/SSH URL form (`https://`/`http://`/`ssh://`/`git@`), raw email substring (`<alphanum>@<host>.<TLD≥2 ASCII letters>`), or SSH PEM blob (`-----BEGIN OPENSSH/RSA/EC/PRIVATE KEY-----`).
- Per-file content scan `scan_local_checkout_content_for_raw_secrets` runs on the read byte buffer BEFORE SHA-256 and detects PAT prefix, URL credential form, or SSH PEM blob; on hit, the reader returns `Err(BlockDocumentError::new("STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED"))` so the offending bytes are never fed to SHA-256 nor recorded in the evidence.
- Path-safety pre-read check `local_checkout_expected_path_safety` operates lex-only via `std::path::Path::components()` and rejects any `Component::ParentDir`, `Component::RootDir`, `Component::Prefix`, or NUL byte; failures emit a per-file rejection record with `reason_code = "STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE"` and `redacted_reason = "STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE"` (code-only, no offending bytes).
- Per-file size cap uses `std::fs::metadata(&abs).len()` BEFORE the full read, per spec §4 rule 7 "the size check uses metadata"; over-cap files emit a `STUDENT_LOCAL_CHECKOUT_FILE_SIZE_EXCEEDED` rejection record without opening the file content.
- Text-classified files (`content_kind == "text-utf8"` per leading-4096-byte heuristic) are full-validated via `std::str::from_utf8(&bytes)` after the content scan; decode failure emits a `STUDENT_LOCAL_CHECKOUT_INVALID_UTF8` rejection record.
- Authorization (spec §4 rule 10) is enforced via a constant enum `STUDENT_LOCAL_CHECKOUT_AUTHORIZED_ROLES = ["student", "instructor", "ta", "course_admin", "platform_admin", "evaluator"]`. Per spec §7 non-claim, the approved dry-run plan id IS the authorization predecessor for non-`student` roles; a valid `audit_clone_readonly_plan_*` predecessor id with any enum role proceeds. Unknown roles abort with `STUDENT_LOCAL_CHECKOUT_NOT_AUTHORIZED`.
- The evidence's sorted-key canonical JSON serialises the spec §5 fields in lexicographic key order: `accepted_file_count`, `approved_dry_run_plan_id`, `audit_event_ids`, `clone_readonly_executed`, `credential_resolved`, `external_call_made`, `external_side_effect_made`, `github_mutation_made`, `live_external_action`, `local_checkout_read_executed`, `network_call_made`, `no_raw_repository_url_persisted`, `no_raw_secret_observed`, `read_id`, `redacted_file_records`, `rejected_file_count`, `rejected_file_records`, `relative_repo_path_hash`, `requested_at_utc`, `requested_by_role`, `schema_version`, `workspace_path_label_hash`. Per-record key order is `audit_event_id`, `content_kind`, `content_sha256`, `file_size_bytes`, `path_hash` for accepted and `reason_code`, `redacted_path_hash`, `redacted_reason` for rejected.

## 3. RED to GREEN evidence

### M7-STUDENT-LOCAL-CHECKOUT-READER-T1 reader contract

```text
RED command:    cargo test -p eduops_domain --test m7_student_local_checkout_reader_contract -- --nocapture
RED result:     error[E0432]: unresolved imports `eduops_domain::STUDENT_LOCAL_CHECKOUT_READ_SCHEMA_VERSION`, `eduops_domain::StudentLocalCheckoutReadRequest`, `eduops_domain::read_student_local_checkout`
GREEN command:  cargo test -p eduops_domain --test m7_student_local_checkout_reader_contract -- --nocapture
GREEN result:   test result: ok. 6 passed; 0 failed
Commit:         2b9d4ea
```

### M7-STUDENT-LOCAL-CHECKOUT-READER-T2 fail-closed safety contract

```text
RED command:    cargo test -p eduops_domain --test m7_student_local_checkout_reader_safety_contract -- --nocapture
RED result:     test result: FAILED. 3 passed; 14 failed (3 already-green cases predated the guards: file-size-exceeded post-read, instructor-ok happy-path, happy-path)
GREEN command:  cargo test -p eduops_domain --test m7_student_local_checkout_reader_safety_contract -- --nocapture
GREEN result:   test result: ok. 17 passed; 0 failed
Commit:         d42e75c
```

## 4. Repository-level validation

```text
cargo test -p eduops_domain --test m7_student_local_checkout_reader_contract        -> ok. 6 passed
cargo test -p eduops_domain --test m7_student_local_checkout_reader_safety_contract -> ok. 17 passed
cargo test --workspace                                                              -> all targets pass
cargo fmt --all --check                                                             -> clean
git diff --check                                                                    -> clean
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)                -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q                 -> 6 passed in 0.06s
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| `StudentLocalCheckoutReadRequest` / `StudentLocalCheckoutRedactedFileRecord` / `StudentLocalCheckoutRejectedFileRecord` / `StudentLocalCheckoutReadEvidence` type contract published in `eduops_domain` | `crates/eduops_domain/src/lib.rs` `pub struct` definitions | accepted |
| Reader emits deterministic sorted-key canonical JSON + in-crate SHA-256 envelope with the spec §5 hardcoded literals | `m7_student_local_checkout_reader_contract::happy_path_reads_fixture_and_emits_deterministic_evidence` and `::canonical_json_keys_are_sorted_lexicographically` | accepted |
| Workspace path label and per-file paths are FNV-1a 64 redacted; raw filesystem paths never appear in canonical JSON | `m7_student_local_checkout_reader_contract::happy_path_reads_fixture_and_emits_deterministic_evidence` raw-path assertions | accepted |
| Per-file `content_sha256` is in-crate SHA-256 over file bytes; changes when content changes | `m7_student_local_checkout_reader_contract::evidence_sha256_changes_when_content_changes` | accepted |
| Per-file `content_kind` distinguishes `text-utf8` (default) from `binary-opaque` (leading null byte / invalid UTF-8 head) | `m7_student_local_checkout_reader_contract::binary_file_is_classified_as_binary_opaque` | accepted |
| Per-file audit ids follow `audit_student_local_checkout_file_<read_id>_<index>_<12hex>` template; per-read audit id follows `audit_student_local_checkout_read_<read_id>` template | `m7_student_local_checkout_reader_contract::audit_event_ids_include_per_file_and_per_read_entries` | accepted |
| Missing expected files produce a `STUDENT_LOCAL_CHECKOUT_EXPECTED_FILE_MISSING` rejection record with code-only `redacted_reason` (no offending path bytes) | `m7_student_local_checkout_reader_contract::missing_expected_file_records_a_rejection_without_offending_path` | accepted |
| Empty / wrong-prefix `approved_dry_run_plan_id` aborts with `STUDENT_LOCAL_CHECKOUT_APPROVAL_PLAN_MISSING` | `m7_student_local_checkout_reader_safety_contract::empty_approved_dry_run_plan_id_aborts_with_approval_plan_missing` and `::wrong_prefix_approved_dry_run_plan_id_aborts_with_approval_plan_missing` | accepted |
| Non-`student_local_checkout` `approval_predecessor_mode` aborts with `STUDENT_LOCAL_CHECKOUT_INPUT_MODE_MISMATCH` | `m7_student_local_checkout_reader_safety_contract::wrong_approval_predecessor_mode_aborts_with_input_mode_mismatch` | accepted |
| Pre-construction request scan rejects raw PAT prefix / URL credential form / raw HTTPS URL / raw email substring in any text-bearing request field with `STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED` and no offending bytes in the rejection message | `m7_student_local_checkout_reader_safety_contract::raw_pat_in_workspace_path_label_aborts_with_raw_secret_rejected` and `::raw_url_credential_in_relative_repo_path_aborts_with_raw_secret_rejected` and `::raw_email_in_workspace_path_label_aborts_with_raw_secret_rejected` and `::raw_https_url_in_workspace_path_label_aborts_with_raw_secret_rejected` | accepted |
| `..` segment in `expected_files` records a `STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE` rejection with no offending bytes echoed | `m7_student_local_checkout_reader_safety_contract::dotdot_segment_in_expected_file_records_path_escape` | accepted |
| Absolute path in `expected_files` records a `STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE` rejection | `m7_student_local_checkout_reader_safety_contract::absolute_path_in_expected_file_records_path_escape` | accepted |
| Metadata-based file-size cap rejects over-cap files with `STUDENT_LOCAL_CHECKOUT_FILE_SIZE_EXCEEDED` per-file record, BEFORE attempting the full read | `m7_student_local_checkout_reader_safety_contract::file_exceeding_safe_read_byte_cap_records_rejection_via_metadata` | accepted |
| Text-classified file (first-4096-byte ASCII heuristic) with invalid UTF-8 in the tail records `STUDENT_LOCAL_CHECKOUT_INVALID_UTF8` rejection | `m7_student_local_checkout_reader_safety_contract::text_classified_file_with_invalid_utf8_beyond_head_records_rejection` | accepted |
| Per-file content scan aborts emission on raw PAT prefix, SSH PEM blob, or URL credential form BEFORE SHA-256, with code-only rejection message | `m7_student_local_checkout_reader_safety_contract::raw_pat_in_file_content_aborts_with_raw_secret_rejected` and `::ssh_pem_blob_in_file_content_aborts_with_raw_secret_rejected` and `::url_credential_in_file_content_aborts_with_raw_secret_rejected` | accepted |
| Unknown `requested_by_role` aborts with `STUDENT_LOCAL_CHECKOUT_NOT_AUTHORIZED` | `m7_student_local_checkout_reader_safety_contract::unknown_requested_by_role_aborts_with_not_authorized` | accepted |
| Valid non-`student` enum role (`instructor`) with valid approval predecessor proceeds per spec §7 non-claim | `m7_student_local_checkout_reader_safety_contract::authorized_non_student_role_with_valid_approval_proceeds` | accepted |
| Happy path remains green with all safety guards active | `m7_student_local_checkout_reader_safety_contract::happy_path_with_safety_guards_in_place_remains_green` and the full `m7_student_local_checkout_reader_contract` bucket | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live HTTPS/SSH probe of any GitHub repository URL;
- real `git clone`, `git fetch`, `git push`, `git ls-remote`, or any other live Git command;
- real credential resolution, token refresh, credential rotation, or credential storage modification;
- repository creation, push, branch/tag, issue, webhook, check-run, invitation, branch protection, archive, or any GitHub administration action;
- a network call of any kind from the reader;
- a real desktop file-picker UI, drag-and-drop file selection, or Tauri shell wiring of a production student-checkout import surface;
- a real authorization-predecessor lookup against a live identity provider; the role check operates on the request `requested_by_role` enum plus the redacted approved dry-run plan id only and assumes the upstream approval evidence has already recorded any per-student authorization for non-`student` roles, per spec §7 non-claim;
- submission/provisioning state promotion from local-checkout read evidence;
- evaluation-result authority (the reader emits read-evidence only; evaluation is a separate downstream concern bounded by the M6 advisory runner gate);
- the defensive `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` rule 5 canonical-path comparison duplicate — every observable rejection path goes through the lex-only rule 4 `PATH_ESCAPE` check today; canonical-path-comparison defense (which catches symlink swap TOCTOU edge cases) remains deferred until symlink-target inspection is in scope;
- partial rule 4 symlink-target inspection that classifies a symlink whose target leaves the workspace as `PATH_ESCAPE` distinct from `EXPECTED_FILE_MISSING` — symlink handling beyond `fs::read` failure remains deferred and requires Unix-specific test scaffolding;
- strict rule 6 "not symlink / not device / not directory" file-kind check beyond plain file-existence — `fs::metadata` errors and `fs::read` errors both map to `STUDENT_LOCAL_CHECKOUT_EXPECTED_FILE_MISSING`;
- the post-construction `scan_local_checkout_evidence_for_raw_secrets` evidence-text scan — every input that could carry a raw secret is already blocked pre-construction, every output field is either FNV-1a 64 redacted, SHA-256 redacted, an enum literal, or a hardcoded boolean, so a leak path would require a future code change; the defensive belt-and-suspenders sweep remains spec-required and deferred;
- full-Unicode NFC normalization beyond the existing controlled Hangul L+V+T composition behavior;
- password-form key-value detection (`password=`/`passwd=`/`secret=`/`token=`) beyond the explicitly-enumerated SSH PEM blob headers (`-----BEGIN OPENSSH/RSA/EC/PRIVATE KEY-----`);
- SHA-256 source-URL audit hash upgrade beyond the existing FNV-1a 64 envelope (deferred per `m7-clone-readonly-evidence.md` §7 item 3);
- consolidation of the case-preserving `fnv1a64_envelope` helper with the case-normalizing `fnv1a64_source_repo_url_hash` helper (the two are intentionally separate because file paths are case-sensitive on Linux while URL hosts are case-insensitive);
- notification delivery, external identity-provider integration, organization administration, or submission/provisioning state promotion;
- DEMO-1 acceptance or live working-demonstration approval;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Author the defensive `scan_local_checkout_evidence_for_raw_secrets` post-construction evidence-text scan as a belt-and-suspenders sweep, walking every text-bearing field on the constructed `StudentLocalCheckoutReadEvidence` (including `canonical_json` and `evidence_sha256`) and rejecting any raw-secret/raw-path leak; the current implementation already blocks all observable leak paths pre-construction, so the new scan is regression protection only;
2. Add the defensive rule 5 `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` canonical-path comparison guard via `std::fs::canonicalize` on both the absolute file path and the workspace boundary; this catches symlink-swap TOCTOU edge cases between the lex-only pre-read scan and the actual `std::fs::read` (deferred — requires Unix-specific test scaffolding);
3. Extend rule 4 symlink-target inspection to distinguish symlinks whose target leaves the workspace (PATH_ESCAPE) from symlinks whose target is inside the workspace (EXPECTED_FILE_MISSING per rule 6); requires `std::os::unix::fs::symlink` test scaffolding on Linux;
4. Tighten rule 6 to a strict "not symlink / not device / not directory" file-kind check via `fs::symlink_metadata().file_type()` so symlinks, directories, FIFOs, sockets, and block/char devices all map distinctly from `EXPECTED_FILE_MISSING`; this requires an authorized control update enumerating the additional rejection codes or a documentation note that all non-regular-file kinds collapse to `EXPECTED_FILE_MISSING`;
5. Extract a shared FNV-1a 64 helper across `eduops_domain` and `eduops_git` (carry-over from `m7-clone-readonly-evidence.md` §7 item 3); deferred until a cross-crate dependency is wired up;
6. Extend per-file content scan with password-form key-value detection (`password=`/`passwd=`/`secret=`/`token=`) beyond the SSH PEM blob headers; requires an authorized control update enumerating the additional patterns;
7. Wire the reader's `StudentLocalCheckoutReadEvidence` into the approval workflow's predecessor reference list as a third predecessor kind (`student-local-checkout-read-evidence`) so the approval surface can display the redacted local-checkout read id alongside the existing `professorCsvIntakeEvidenceId` and `cloneReadonlyDryRunPlanId` fields; requires an authorized control update enumerating the additional predecessor reference kind;
8. Author the user-managed runbook that prescribes how the student performs the actual `git clone` outside EduOps automation and supplies the resulting local checkout under their own workspace, per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`; this is outside Ralph automation and remains user-managed.

## 8. Traceability

- [Student pre-cloned local-checkout reader specification](../02-design-planning/student-pre-cloned-local-checkout-reader-specification.md)
- [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md)
- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [Roster schema and identity policy](../02-design-planning/roster-schema-and-identity-policy.md)
- [Access control and authorization model](../02-design-planning/access-control-authorization-model.md)
- [M4 SLICE-C roster, identity, and workspace gate evidence](m4-slice-c-roster-identity-workspace-evidence.md)
- [M7 clone-readonly integration-point gate evidence](m7-clone-readonly-evidence.md)
- [M7 clone-readonly approval workflow UX gate evidence](m7-approval-ux-evidence.md)
- [M7 approval UX predecessor reference integration gate evidence](m7-approval-ux-intake-link-evidence.md)
- [M7 approval UX predecessor block accessibility hardening gate evidence](m7-approval-ux-predecessor-a11y-harden-evidence.md)
- [Software test description](../03-verification-validation/software-test-description.md) — a future addendum for `STD-M7-STUDENT-LOCAL-CHECKOUT-READER-001..003`
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
