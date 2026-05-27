---
title: M7 Professor CSV Byte Parser Gate Evidence
document_id: EDUOPS-M7-PROF-CSV-INTAKE-BYTE-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-PROFESSOR-CSV-INTAKE-SPEC
    - SWENG-EDUTECH-ROSTER-SCHEMA
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M7-PROF-CSV-INTAKE-EVIDENCE
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - eduops_domain::m7_professor_csv_intake_byte_contract
    - eduops_domain::m7_professor_csv_intake_byte_safety_contract
---

# M7 Professor CSV Byte Parser Gate Evidence

## 1. Gate result

`GATE-M7-PROFESSOR-CSV-INTAKE-BYTE-FIXTURE-LOCAL` is accepted-constrained for the fixture-local CSV-byte parser (M7-PROF-CSV-INTAKE-BYTE-T1) and its pre-decode byte-stream raw-secret guard (M7-PROF-CSV-INTAKE-BYTE-T2) defined by [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md) §3-§6. The byte parser extends the already-accepted row-input pipeline ([M7 professor CSV intake gate evidence](m7-prof-csv-intake-evidence.md)) with UTF-8 decoding, header validation, Hangul NFC composition, comma-split row parsing, and a pre-decode byte-stream credential scan, without changing any of the non-claims that already apply to the upstream gate.

Live HTTPS/SSH probe of any GitHub repository URL, real `git clone`/`git fetch`/`git push`/`git ls-remote`, real credential resolution, repository administration, real CSV upload UI, notification delivery, identity-provider integration, submission/provisioning state promotion, and DEMO-1 acceptance remain explicitly out of scope and user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

```text
gate=GATE-M7-PROFESSOR-CSV-INTAKE-BYTE-FIXTURE-LOCAL
status=accepted-constrained
scope=eduops_domain::intake_professor_csv_from_bytes(intake_id, course_id, source_csv_bytes) byte→row parser that runs scan_csv_bytes_for_raw_secrets BEFORE std::str::from_utf8 (PROF_CSV_RAW_SECRET_REJECTED takes precedence over PROF_CSV_INVALID_UTF8), decodes UTF-8 (reject systemic with PROF_CSV_INVALID_UTF8), reads the first non-empty header line (reject empty input with PROF_CSV_HEADER_MISSING), validates header columns against the controlled set [course_id, section_id, student_internal_id, student_display_name, github_repository_url] plus optional email (reject unknown columns with PROF_CSV_UNKNOWN_COLUMN_REJECTED, duplicates with PROF_CSV_DUPLICATE_HEADER_COLUMN, missing required columns with PROF_CSV_REQUIRED_COLUMN_MISSING), parses each non-empty data row by comma split with CRLF tolerance, maps fields when count matches header (otherwise leaves all fields empty so the row-input pipeline classifies them as PROF_CSV_REQUIRED_FIELD_EMPTY), NFC-normalizes every text-bearing field (course_id, section_id, student_internal_id, student_display_name, email, github_repository_url) via Hangul L+V+T → precomposed-syllable composition (S = 0xAC00 + Lindex*588 + Vindex*28 + Tindex), and delegates to the existing intake_professor_csv row-input pipeline; scan_csv_bytes_for_raw_secrets walks raw bytes without UTF-8 decoding and returns ProfessorCsvSecretLeakage::PatPrefix on case-insensitive ASCII match for ghp_ or github_pat_, or ProfessorCsvSecretLeakage::UrlCredentialForm on encountering :// followed by : then @ before a /, space, tab, CR, or LF boundary; the existing per-row scan_row_for_raw_secrets and post-construction scan_professor_csv_evidence_for_raw_secrets continue to provide defense-in-depth at the row/evidence layers
constraint=live HTTPS/SSH probe of repository URL, real git clone / git fetch / git push / git ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration (creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive), real CSV upload UI / drag-and-drop file picker / production deployment, notification delivery, external identity-provider integration, organization administration, submission/provisioning state promotion, DEMO-1 acceptance / working-demonstration approval, fidelity / privacy / legal policy authority beyond reapplication of existing controlled redaction rules, RFC 4180 quoted-string CSV grammar with embedded newlines / escaped quotes, full-Unicode NFC normalization (canonical reordering, compatibility decomposition, Latin combining marks), host-process invocation, cryptographic detection of fully synthetic high-entropy tokens or SSH key prefixes, and any cryptographic source-URL audit hash beyond the existing FNV-1a 64 envelope are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live HTTPS/SSH probe, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real CSV upload UI deployment, notification delivery, submission/provisioning state promotion, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted M7 professor CSV byte parser behavior:

- `eduops_domain::intake_professor_csv_from_bytes(intake_id, course_id, source_csv_bytes) -> Result<ProfessorCsvIntakeEvidence, BlockDocumentError>` provides a UTF-8 byte-stream entry point that delegates to the existing `intake_professor_csv` row-input pipeline after parsing and normalization.
- `eduops_domain::scan_csv_bytes_for_raw_secrets(bytes) -> Option<ProfessorCsvSecretLeakage>` provides a pre-decode byte-stream scan returning `PatPrefix { field: "source_csv_bytes" }` or `UrlCredentialForm { field: "source_csv_bytes" }` on a hit.
- The byte parser pipeline executes in this order:
  1. `scan_csv_bytes_for_raw_secrets(source_csv_bytes)` runs FIRST; any hit returns `Err(BlockDocumentError::new("PROF_CSV_RAW_SECRET_REJECTED"))` before UTF-8 decode is attempted.
  2. `std::str::from_utf8(source_csv_bytes)` decodes the bytes; failure returns `PROF_CSV_INVALID_UTF8`.
  3. The first non-empty line is read as the header; empty input returns `PROF_CSV_HEADER_MISSING`.
  4. Header columns are split by `,` and validated: duplicates return `PROF_CSV_DUPLICATE_HEADER_COLUMN`; columns outside the controlled set return `PROF_CSV_UNKNOWN_COLUMN_REJECTED`; missing required columns return `PROF_CSV_REQUIRED_COLUMN_MISSING`.
  5. Each non-empty data row is split by `,` with trailing `'\r'` stripped (CRLF tolerance). Field count must match the header column count; otherwise all fields stay empty so the existing pipeline classifies the row as `PROF_CSV_REQUIRED_FIELD_EMPTY`.
  6. Every text-bearing field (`course_id`, `section_id`, `student_internal_id`, `student_display_name`, `email`, `github_repository_url`) is NFC-normalized via Hangul L+V+T → precomposed-syllable composition before constructing a `ProfessorCsvIntakeRow`.
  7. The constructed `ProfessorCsvIntakeRequest` is delegated to `intake_professor_csv`, which applies the existing per-row `scan_row_for_raw_secrets`, validates URL form and credential form, computes FNV-1a 64 source-URL hashes and SHA-256 redactions, and produces the deterministic `ProfessorCsvIntakeEvidence` envelope (sorted-key canonical JSON + in-crate SHA-256, hardcoded `external_call_made`/`external_side_effect_made`/`github_mutation_made`/`live_external_action`/`clone_readonly_executed=false` plus `no_raw_secret_observed`/`no_raw_repository_url_persisted=true`).
- The existing `normalize_nfc` private helper is upgraded from an identity placeholder to a Hangul Syllable Composition implementation: walks the codepoint sequence, on encountering a Choseong jamo `L ∈ U+1100..U+1112` followed by a Jungseong jamo `V ∈ U+1161..U+1175`, optionally followed by a Jongseong jamo `T ∈ U+11A8..U+11C2`, emits the precomposed syllable `S = 0xAC00 + (Lindex * 588) + (Vindex * 28) + Tindex` (`Tindex = T - 0x11A7` or `0` for "no T"); other codepoints pass through unchanged. Full-Unicode NFC (canonical reordering, compatibility decomposition, Latin combining marks) is intentionally out of scope and remains a follow-up.

## 3. RED to GREEN evidence

### M7-PROF-CSV-INTAKE-BYTE-T1 byte→row parser and Hangul NFC composition

```text
RED command:    cargo test -p eduops_domain --test m7_professor_csv_intake_byte_contract -- --nocapture
RED result:     unresolved import for intake_professor_csv_from_bytes; could not compile eduops_domain
GREEN command:  cargo test -p eduops_domain --test m7_professor_csv_intake_byte_contract -- --nocapture
GREEN result:   13 passed; 0 failed
Commit:         3a8dd7f
```

### M7-PROF-CSV-INTAKE-BYTE-T2 pre-decode byte-stream raw-secret guard

```text
RED command:    cargo test -p eduops_domain --test m7_professor_csv_intake_byte_safety_contract -- --nocapture
RED result:     unresolved import for scan_csv_bytes_for_raw_secrets; could not compile eduops_domain
GREEN command:  cargo test -p eduops_domain --test m7_professor_csv_intake_byte_safety_contract -- --nocapture
GREEN result:   12 passed; 0 failed
Commit:         229c857
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
cargo test --workspace                                                     -> all test target groups report ok (the new m7_professor_csv_intake_byte_contract 13 passed + m7_professor_csv_intake_byte_safety_contract 12 passed; existing m7_professor_csv_intake_contract 10 passed + m7_professor_csv_intake_safety_contract 9 passed remain green; all M0..M8 + M7-MOCKHTTP-* + M7-CLONE-READONLY-* + M7-APPROVAL-UX-* + M7-APPROVAL-UX-HARDEN-* totals remain green)
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Happy-path UTF-8 CSV decodes and produces canonical evidence identical to equivalent row-input pipeline | `m7_professor_csv_intake_byte_contract::happy_path_decodes_utf8_csv_and_matches_row_input_pipeline` | accepted |
| Invalid UTF-8 bytes are rejected with `PROF_CSV_INVALID_UTF8` and invalid bytes are not echoed in the error message | `m7_professor_csv_intake_byte_contract::invalid_utf8_input_is_rejected_with_invalid_utf8_code` | accepted |
| Empty input is rejected with `PROF_CSV_HEADER_MISSING` | `m7_professor_csv_intake_byte_contract::missing_header_row_is_rejected_with_header_missing_code` | accepted |
| Unknown header column is rejected with `PROF_CSV_UNKNOWN_COLUMN_REJECTED` and row data does not leak into the error message | `m7_professor_csv_intake_byte_contract::unknown_header_column_is_rejected_with_unknown_column_code` | accepted |
| Missing required header column is rejected with `PROF_CSV_REQUIRED_COLUMN_MISSING` | `m7_professor_csv_intake_byte_contract::missing_required_header_column_is_rejected_with_required_column_missing_code` | accepted |
| Duplicate header column is rejected with `PROF_CSV_DUPLICATE_HEADER_COLUMN` | `m7_professor_csv_intake_byte_contract::duplicate_header_column_is_rejected_with_duplicate_column_code` | accepted |
| NFC normalization makes NFD and NFC display-name inputs produce the same row-level canonical JSON | `m7_professor_csv_intake_byte_contract::nfc_normalization_is_applied_so_nfd_and_nfc_inputs_produce_identical_row_canonical_json` | accepted |
| Per-row validation is still delegated to the existing row-input pipeline (URL form, etc.) | `m7_professor_csv_intake_byte_contract::per_row_validation_is_still_delegated_to_existing_pipeline` | accepted |
| Field-count mismatches (under or over) are rejected as `PROF_CSV_REQUIRED_FIELD_EMPTY` and raw extras do not leak into the canonical evidence | `m7_professor_csv_intake_byte_contract::data_row_with_fewer_fields_than_header_is_rejected_as_required_field_empty`, `data_row_with_more_fields_than_header_is_rejected_as_required_field_empty` | accepted |
| Evidence does not contain raw PII or raw repository URL when parsed from bytes | `m7_professor_csv_intake_byte_contract::evidence_does_not_contain_raw_pii_or_raw_repository_url_when_parsed_from_bytes` | accepted |
| Byte parser is deterministic across repeated runs | `m7_professor_csv_intake_byte_contract::byte_parser_call_is_deterministic_across_repeated_runs` | accepted |
| Hardcoded no-live flags are false and `no_raw_repository_url_persisted=true` for byte-parsed evidence | `m7_professor_csv_intake_byte_contract::hardcoded_no_live_flags_are_false_and_no_raw_repository_url_persisted_is_true_for_byte_parse` | accepted |
| Clean CSV bytes pass the pre-decode byte-stream scan and produce the expected evidence | `m7_professor_csv_intake_byte_safety_contract::clean_csv_bytes_pass_pre_decode_byte_stream_scan` | accepted |
| Plain HTTPS / SSH GitHub URLs and plain email addresses are NOT flagged as URL credential form | `m7_professor_csv_intake_byte_safety_contract::plain_https_github_url_is_not_flagged_as_url_credential_form`, `plain_ssh_github_url_is_not_flagged_as_url_credential_form`, `email_field_is_not_flagged_as_url_credential_form`, `scan_csv_bytes_for_raw_secrets_does_not_flag_plain_uris_without_credentials` | accepted |
| Raw PAT prefix (`ghp_` / `github_pat_`) anywhere in the CSV bytes is rejected with `PROF_CSV_RAW_SECRET_REJECTED` before parse | `m7_professor_csv_intake_byte_safety_contract::raw_pat_prefix_in_csv_bytes_is_rejected_before_parse`, `raw_github_pat_prefix_in_csv_bytes_is_rejected_before_parse`, `mixed_case_pat_prefix_is_still_detected`, `scan_csv_bytes_for_raw_secrets_directly_detects_pat_prefix_anywhere` | accepted |
| URL credential form anywhere in the CSV bytes is rejected with `PROF_CSV_RAW_SECRET_REJECTED` before parse | `m7_professor_csv_intake_byte_safety_contract::url_credential_form_in_csv_bytes_is_rejected_before_parse`, `scan_csv_bytes_for_raw_secrets_directly_detects_url_credential_form_anywhere` | accepted |
| The byte-stream scan runs BEFORE UTF-8 decode so PAT prefix in invalid-UTF-8 input is still rejected with `PROF_CSV_RAW_SECRET_REJECTED` (not `PROF_CSV_INVALID_UTF8`) | `m7_professor_csv_intake_byte_safety_contract::byte_stream_scan_runs_before_utf8_decode_for_invalid_utf8_input` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live HTTPS/SSH probe of any GitHub repository URL;
- a real `git clone`, `git fetch`, `git push`, `git ls-remote`, or any other live Git command;
- real credential resolution, token refresh, credential rotation, or credential storage modification;
- repository creation, push, branch/tag, issue, webhook, check-run, invitation, branch protection, archive, or any GitHub administration action;
- a real CSV upload UI, drag-and-drop file picker, or production deployment;
- submission/provisioning state promotion from CSV intake;
- DEMO-1 acceptance or live working-demonstration approval;
- RFC 4180 quoted-string CSV grammar with embedded newlines or escaped quotes (only minimal comma-separated grammar with CRLF tolerance is in scope);
- full-Unicode NFC normalization (canonical reordering, compatibility decomposition, Latin combining marks); the implementation composes Hangul jamo only and is documented as a partial NFC that is sufficient for the fixture-local Korean rosters used by the existing tests;
- cryptographic detection of fully synthetic high-entropy tokens, SSH key blob detection (`-----BEGIN OPENSSH PRIVATE KEY-----`, etc.), or password-form detection;
- a cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope (deferred per `m7-clone-readonly-evidence.md` §7 item 3);
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Extend `normalize_nfc` to cover full-Unicode NFC normalization (canonical reordering and compatibility decomposition) so non-Hangul decomposed input is normalized too; this likely requires adding a controlled, vetted dependency (e.g. `unicode-normalization`) or porting a minimal subset of the canonical decomposition tables;
2. Extend the byte parser to RFC 4180 quoted-string CSV grammar with embedded newlines and escaped quotes; today the parser supports only minimal comma-separated grammar with CRLF tolerance;
3. Extract a shared FNV-1a 64 helper across `eduops_domain` and `eduops_git` and prepare for the SHA-256 envelope upgrade tracked under `m7-clone-readonly-evidence.md` §7 item 3 (carried over from `m7-prof-csv-intake-evidence.md` §7 item 2);
4. Extend the byte-stream scan to include SSH private-key blob prefixes (`-----BEGIN OPENSSH PRIVATE KEY-----`, etc.) and password-like patterns when an authorized control update enumerates the additional patterns;
5. Integrate the byte parser into the clone-readonly approval workflow UX render so the approval surface can reference both the intake evidence id and the dry-run plan id as predecessors (carried over from `m7-prof-csv-intake-evidence.md` §7 item 4);
6. Record an authorized human runbook for the user-managed CSV preparation step per `EDUOPS-DEC-065` (carried over from `m7-prof-csv-intake-evidence.md` §7 item 5); this is outside Ralph automation and remains user-managed.

## 8. Traceability

- [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md)
- [M7 professor CSV roster + repository URL intake gate evidence](m7-prof-csv-intake-evidence.md)
- [Roster schema and identity policy](../02-design-planning/roster-schema-and-identity-policy.md)
- [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md)
- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [Software test description](../03-verification-validation/software-test-description.md) — STD-M7-PROF-CSV-INTAKE-001..003 plus a future addendum for `STD-M7-PROF-CSV-INTAKE-BYTE-001..002`
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [M7 clone-readonly integration-point gate evidence](m7-clone-readonly-evidence.md)
- [M7 clone-readonly approval workflow UX gate evidence](m7-approval-ux-evidence.md)
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
