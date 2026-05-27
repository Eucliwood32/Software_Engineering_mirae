---
title: Professor CSV Roster + Repository URL Intake Specification
document_id: SWENG-EDUTECH-PROFESSOR-CSV-INTAKE-SPEC
version: 0.2.0
status: accepted-for-fixture-implementation
date: 2026-05-16
owner: develop
quality_context: Ralph-controlled HOW-level specification checkpoint
traceability:
  upstream:
    - SWENG-EDUTECH-ROSTER-SCHEMA
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-ACCESS-CONTROL-AUTHORIZATION-MODEL
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
    - STD-M7-PROF-CSV-INTAKE-001
    - STD-M7-PROF-CSV-INTAKE-002
    - STD-M7-PROF-CSV-INTAKE-003
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
---

# Professor CSV Roster + Repository URL Intake Specification

## 1. Purpose

This specification defines the fixture-local HOW-level contract for the professor-mode CSV intake that the clone-readonly approval workflow consumes. It authorizes fixture-local validation, redaction, and evidence assembly for a roster CSV that carries a per-row `github_repository_url` field plus the existing controlled roster fields. It does **not** authorize a real `git clone`/`git fetch`/`git push`/`git ls-remote`, a real credential lookup, a remote configuration, a GitHub administration action, or any live external action; those remain user-managed per `EDUOPS-DEC-065`.

This specification extends the controlled roster fields from [Roster schema and identity policy](roster-schema-and-identity-policy.md) §2 with the GitHub repository URL field referenced by [Clone-readonly human approval workflow UX specification](clone-readonly-approval-workflow-ux-specification.md) §2.1 and [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md) §4.1, and reuses the redaction/non-mutation literals required by [GitHub adapter specification](github-adapter-specification.md) and the topology in [GitHub topology and token model](github-topology-and-token-model.md).

## 2. Authorized scope

| Area | Authorized for this slice | Not authorized |
|---|---|---|
| CSV format | UTF-8 encoded CSV with header row; minimal roster columns from [Roster schema and identity policy](roster-schema-and-identity-policy.md) §2 plus `github_repository_url`; deterministic NFC normalization | Excel/binary roster formats, multi-sheet workbooks, encrypted CSV |
| Repository URL field | Fixture-local parsing and validation of `github_repository_url`; redaction to `source_repo_url_hash` envelope before any evidence is emitted; `clone-only` operation tagging | Live HTTPS/SSH probe of the URL, real `git clone`, real `git ls-remote`, GitHub API call to verify repository existence or permissions |
| Credential reference | None; this layer does not resolve any credential | Token lookup, refresh, rotation, or persistence |
| Output | Deterministic `ProfessorCsvIntakeEvidence` envelope with sorted-key canonical JSON, in-crate SHA-256 manifest hash, accepted/rejected row counts, redacted per-row records, hardcoded `external_call_made=false`/`external_side_effect_made=false`/`github_mutation_made=false`/`live_external_action=false`/`clone_readonly_executed=false`/`no_raw_secret_observed=true`/`no_raw_repository_url_persisted=true` | Live-run evidence, submission/provisioning promotion |
| Privacy | Raw `student_internal_id`, raw `email`, and raw `github_repository_url` MUST NOT appear in evidence; redacted/hashed envelopes only | Persisting raw PII or raw repository URLs anywhere in evidence |

## 2.1 User-managed boundary

Per `EDUOPS-DEC-065`, the professor (or authorized course owner) is responsible for collecting roster rows and the corresponding GitHub repository URL outside EduOps automation. EduOps accepts the assembled CSV file as already-authorized input and immediately routes the raw `github_repository_url` field through redaction. EduOps does not configure remotes for the listed repositories, does not call the GitHub API, does not perform a real `git clone`/`git fetch`/`git push`, and does not store the raw URL anywhere on disk beyond the in-memory parse buffer.

## 3. CSV field contract

The professor CSV mode adds one field to the controlled roster schema:

| Field | Required | Type | Notes |
|---|---|---|---|
| All fields from [Roster schema and identity policy](roster-schema-and-identity-policy.md) §2 | as defined there | as defined there | Re-applied unchanged. |
| `github_repository_url` | Yes | string | Raw HTTPS or SSH form repository URL; rejected and redacted into `source_repo_url_hash` before emission. |

The header row MUST list every required field exactly once; column order is irrelevant. Unknown columns MUST be rejected with `PROF_CSV_UNKNOWN_COLUMN_REJECTED` and the offending column name MUST be redacted in evidence.

## 3.1 CSV grammar (RFC 4180 quoted-string)

The byte parser MUST accept RFC 4180 quoted-string CSV grammar in addition to the prior minimal comma-separated grammar (which remains a valid subset). The accepted grammar is:

- A record is a sequence of one or more fields separated by a comma (`,`).
- A field is either an unquoted field or a quoted field.
- An unquoted field is a sequence of zero or more characters that are not `,`, `"`, `\r`, or `\n`. NFC normalization is applied post-decode.
- A quoted field begins with `"`, ends with `"`, and may contain:
  - any character other than `"` (including `,`, `\r`, and `\n`);
  - the two-character escape sequence `""`, which represents a single literal `"` inside the quoted field.
- A record terminator is one of `\r\n`, `\n`, or end-of-input. Records inside a quoted field do not terminate the record.
- The header row uses the same grammar; a header column name MAY be quoted and MAY contain embedded commas / CRLF / escaped quotes.
- The parser MUST reject an unclosed quoted field (a quoted field that reaches end-of-input without a matching closing quote that is not part of a `""` escape) with `PROF_CSV_UNCLOSED_QUOTED_FIELD`.
- The parser MUST treat a character that follows a closing quote but is neither a separator (`,`) nor a record terminator (`\r\n`/`\n`/end-of-input) as malformed and reject the record with `PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE`.

The pre-decode byte-stream raw-secret scan (`scan_csv_bytes_for_raw_secrets`) in §6 continues to fire BEFORE any grammar parsing, so a raw GitHub PAT prefix or URL credential form anywhere in the byte stream (including inside a quoted field) is rejected with `PROF_CSV_RAW_SECRET_REJECTED` before the quoted-string grammar is evaluated.

## 4. Row validation rules

For each non-header row:

1. UTF-8 decoding MUST succeed; otherwise reject with `PROF_CSV_INVALID_UTF8`.
2. NFC normalization MUST be applied to every text-bearing field.
3. Required fields MUST be non-empty after normalization; otherwise reject with `PROF_CSV_REQUIRED_FIELD_EMPTY`.
4. `github_repository_url` MUST match one of the accepted URL shapes (fixture set):
   - `https://github.com/<owner>/<repo>(\.git)?`;
   - `git@github.com:<owner>/<repo>(\.git)?`.
   Other shapes MUST be rejected with `PROF_CSV_URL_FORM_REJECTED`.
5. `github_repository_url` MUST NOT carry a URL credential form (`://user:token@host`); otherwise reject with `PROF_CSV_URL_CREDENTIAL_REJECTED`.
6. `github_repository_url` MUST be redacted to `source_repo_url_hash` using the FNV-1a 64 envelope already shipped by [GitHub adapter specification](github-adapter-specification.md). A future SHA-256 upgrade is tracked as a separate follow-up.
7. PII fields (`student_internal_id`, `email`) MUST be redacted before emission. The raw values MUST NOT appear anywhere in the output evidence.
8. Duplicate `student_internal_id` within the CSV MUST be rejected with `PROF_CSV_DUPLICATE_STUDENT_INTERNAL_ID`.
9. Duplicate `source_repo_url_hash` within the CSV MAY be accepted (a single repository may host multiple students by design), but the evidence MUST record the duplicate-hash count for audit.
10. An unclosed quoted field MUST be rejected with `PROF_CSV_UNCLOSED_QUOTED_FIELD` per §3.1; trailing characters after a closing quote that are neither separator nor record terminator MUST be rejected with `PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE`. Both rejections fire after the pre-decode byte-stream raw-secret scan and before any field-level redaction.

## 5. Evidence envelope

The intake emits a `ProfessorCsvIntakeEvidence` value with the following shape (logical names; concrete field names follow the existing Rust/JS naming conventions in [Internal API contract](internal-api-contract.md)):

| Field | Type | Rule |
|---|---|---|
| `intake_id` | string | Stable fixture id; no raw PII or credential-shaped value. |
| `source_csv_sha256` | string | SHA-256 over the canonical UTF-8 CSV bytes (after NFC normalization). |
| `accepted_row_count` | integer | Non-negative. |
| `rejected_row_count` | integer | Non-negative. |
| `duplicate_source_repo_url_hash_count` | integer | Non-negative. |
| `redacted_rows` | array of records | Each record carries redacted institutional id hash, redacted email hash (when present), `source_repo_url_hash`, `course_id`, `section_id`, `status`. No raw values. |
| `rejected_rows` | array of records | Each record carries a `reason_code` and a redacted reason text. |
| `canonical_json` | string | Sorted-key canonical JSON of all fields except `canonical_json` and `evidence_sha256`. |
| `evidence_sha256` | string | In-crate SHA-256 over `canonical_json`. |
| `audit_event_ids` | array | Includes `audit_prof_csv_intake_<intake_id>` plus per-row `audit_prof_csv_row_<intake_id>_<row_index>`. |
| `external_call_made` | bool | Hardcoded `false`. |
| `external_side_effect_made` | bool | Hardcoded `false`. |
| `github_mutation_made` | bool | Hardcoded `false`. |
| `live_external_action` | bool | Hardcoded `false`. |
| `clone_readonly_executed` | bool | Hardcoded `false`. |
| `no_raw_secret_observed` | bool | Hardcoded `true`. |
| `no_raw_repository_url_persisted` | bool | Hardcoded `true`. |

The intake MUST refuse to emit when any hardcoded flag is mutated, when any raw credential / URL credential form / raw repository URL appears in any field of the evidence, or when the redacted-rows array contains any raw PII.

## 6. Fail-closed safety guards

- Pre-parse scan: raw bytes of every cell are scanned for GitHub PAT prefix (`ghp_`/`github_pat_`) and URL credential form before NFC normalization; any hit is rejected with `PROF_CSV_RAW_SECRET_REJECTED`.
- Post-construction scan: every text-bearing field on the constructed evidence is scanned with the same patterns; any hit aborts emission.
- Privacy scan: raw `student_internal_id`/`email`/`github_repository_url` MUST be absent from the constructed evidence text; any leak aborts emission.

## 7. Non-claims

This specification does not claim:

- live HTTPS/SSH probe of any GitHub repository URL;
- real `git clone`, `git fetch`, `git push`, `git ls-remote`, or any other live Git command;
- real credential resolution, token refresh, credential rotation, or credential storage modification;
- repository creation, push, branch/tag, issue, webhook, check-run, invitation, branch protection, archive, or any GitHub administration action;
- a real CSV upload UI, drag-and-drop file picker, or production deployment;
- submission/provisioning state promotion from CSV intake;
- DEMO-1 acceptance or live working-demonstration approval;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- full-Unicode NFC normalization (canonical reordering / compatibility decomposition / Latin combining marks); only Hangul L+V+T → precomposed-syllable composition is in scope today, with other Unicode normalization remaining the identity until a controlled external `unicode-normalization` dependency is adopted;
- SSH private-key blob detection (PEM-framed `-----BEGIN ... PRIVATE KEY-----` patterns) or password-form key-value detection (`password=`, `passwd=`, `secret=`, `token=`) in `scan_csv_bytes_for_raw_secrets`; these are deferred until an authorized control update enumerates the additional patterns;
- a real CSV upload UI, drag-and-drop file picker, or Tauri shell wiring of a production CSV import surface.

## 8. First executable Ralph tasks

| Task ID | Test command | RED condition | GREEN acceptance |
|---|---|---|---|
| `M7-PROF-CSV-INTAKE-T1` | Add the fixture-local CSV parser test, run `cargo test -p eduops_domain --test m7_professor_csv_intake_contract -- --nocapture` (or the analogous Rust/JS test that integrates with the existing roster types) | No `ProfessorCsvIntakeEvidence` parser exists. | Parser accepts a controlled fixture CSV, rejects each negative fixture with the specified `PROF_CSV_*` code, redacts PII and raw repository URLs, and produces deterministic canonical JSON + SHA-256. |
| `M7-PROF-CSV-INTAKE-T2` | Add fail-closed safety contract tests (raw PAT, URL credential, raw URL persistence, mutated flags) and run the focused test | Safety guards absent. | Every safety guard rejects the listed unsafe fixture before evidence emission. |
| `M7-PROF-CSV-INTAKE-GATE` | Repository docs/control validation plus focused parser/safety tests | Evidence summary missing or overclaims live behavior. | Constrained evidence records fixture-local intake acceptance and explicit non-claims. |
| `M7-PROF-CSV-INTAKE-BYTE-RFC4180-T1` | Add `crates/eduops_domain/tests/m7_professor_csv_intake_byte_rfc4180_contract.rs` and run `cargo test -p eduops_domain --test m7_professor_csv_intake_byte_rfc4180_contract -- --nocapture` | The byte parser today supports only minimal comma-separated grammar with CRLF tolerance; quoted-string fixtures with embedded commas / CRLF / escaped `""` are not yet parsed correctly, and unclosed quoted fields are not yet rejected with `PROF_CSV_UNCLOSED_QUOTED_FIELD`. | The byte parser accepts §3.1 RFC 4180 quoted-string grammar (quoted header column, quoted value with embedded comma, quoted value with embedded CRLF, escaped `""` inside quotes); rejects unclosed quoted fields with `PROF_CSV_UNCLOSED_QUOTED_FIELD` and quoted-field trailing garbage with `PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE`; existing byte-parser tests (`m7_professor_csv_intake_byte_contract`/`m7_professor_csv_intake_byte_safety_contract`/`m7_professor_csv_intake_contract`/`m7_professor_csv_intake_safety_contract`) remain green. |

## 9. Traceability

- Upstream design: [Roster schema and identity policy](roster-schema-and-identity-policy.md); [Clone-readonly human approval workflow UX specification](clone-readonly-approval-workflow-ux-specification.md); [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md); [GitHub adapter specification](github-adapter-specification.md); [GitHub topology and token model](github-topology-and-token-model.md).
- Upstream evidence: [M7 clone-readonly integration-point gate evidence](../06-implementation/m7-clone-readonly-evidence.md); [M7 clone-readonly approval workflow UX gate evidence](../06-implementation/m7-approval-ux-evidence.md).
- Verification anchors: [Software test description](../03-verification-validation/software-test-description.md) §M7 professor CSV intake test addendum (to be authored alongside `M7-PROF-CSV-INTAKE-T1`).
- Decisions: `EDUOPS-DEC-064`; `EDUOPS-DEC-065`.
