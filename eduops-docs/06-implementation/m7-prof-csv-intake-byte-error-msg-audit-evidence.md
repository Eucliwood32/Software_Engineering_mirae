---
title: M7 Professor CSV Byte Parser Error-Message Redaction Audit Gate Evidence
document_id: EDUOPS-M7-PROF-CSV-INTAKE-BYTE-ERROR-MSG-AUDIT-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-PROFESSOR-CSV-INTAKE-SPEC
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M7-PROF-CSV-INTAKE-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-BYTE-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-BYTE-RFC4180-EVIDENCE
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - eduops_domain::m7_professor_csv_intake_byte_error_msg_audit
    - eduops_domain::m7_professor_csv_intake_byte_rfc4180_contract
    - eduops_domain::m7_professor_csv_intake_byte_contract
    - eduops_domain::m7_professor_csv_intake_byte_safety_contract
    - eduops_domain::m7_professor_csv_intake_contract
    - eduops_domain::m7_professor_csv_intake_safety_contract
---

# M7 Professor CSV Byte Parser Error-Message Redaction Audit Gate Evidence

## 1. Gate result

`GATE-M7-PROFESSOR-CSV-INTAKE-BYTE-ERROR-MSG-AUDIT-FIXTURE-LOCAL` is accepted-constrained for the fixture-local error-message redaction audit added by `M7-PROF-CSV-INTAKE-BYTE-ERROR-MSG-AUDIT-T1` at `a5fe0d3`. The audit exercises every `PROF_CSV_*` rejection code reachable from `intake_professor_csv_from_bytes` and verifies that top-level `BlockDocumentError::message` values and row-level `ProfessorCsvIntakeRejection::message` values do not echo offending source bytes or fixture substrings.

This gate closes the follow-up recorded in [M7 professor CSV byte parser RFC 4180 grammar gate evidence](m7-prof-csv-intake-byte-rfc4180-evidence.md) §7 item 4. It preserves the same no-live-action boundary as the upstream CSV-intake gates.

```text
gate=GATE-M7-PROFESSOR-CSV-INTAKE-BYTE-ERROR-MSG-AUDIT-FIXTURE-LOCAL
status=accepted-constrained
scope=crates/eduops_domain/tests/m7_professor_csv_intake_byte_error_msg_audit.rs verifies message-redaction invariants for all PROF_CSV rejection codes reachable through intake_professor_csv_from_bytes: PROF_CSV_RAW_SECRET_REJECTED (PAT prefix and URL credential form), PROF_CSV_INVALID_UTF8, PROF_CSV_HEADER_MISSING, PROF_CSV_DUPLICATE_HEADER_COLUMN, PROF_CSV_UNKNOWN_COLUMN_REJECTED, PROF_CSV_REQUIRED_COLUMN_MISSING, PROF_CSV_UNCLOSED_QUOTED_FIELD, PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE, PROF_CSV_REQUIRED_FIELD_EMPTY, PROF_CSV_URL_FORM_REJECTED, and PROF_CSV_DUPLICATE_STUDENT_INTERNAL_ID; top-level errors are checked through BlockDocumentError::message and row-level errors through ProfessorCsvIntakeRejection::message; PROF_CSV_URL_CREDENTIAL_REJECTED remains intentionally unreachable through the byte parser because the pre-decode byte scan rejects URL credential form earlier as PROF_CSV_RAW_SECRET_REJECTED
constraint=live HTTPS/SSH probe, real git clone/fetch/push/ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration, real CSV upload UI / drag-and-drop file picker / production deployment, notification delivery, external identity-provider integration, organization administration, submission/provisioning state promotion, DEMO-1 acceptance / working-demonstration approval, full-Unicode NFC normalization, SSH PEM blob detection, password-form key-value detection, SHA-256 source-URL audit hash upgrade, and production error-localization UX are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live GitHub action, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real CSV upload UI deployment, notification delivery, submission/provisioning state promotion, production error-copy localization, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted error-message redaction audit behavior:

- `crates/eduops_domain/tests/m7_professor_csv_intake_byte_error_msg_audit.rs` contains 12 focused tests that call `intake_professor_csv_from_bytes` with controlled fixtures designed to trigger each reachable `PROF_CSV_*` rejection path.
- Top-level error checks cover `PROF_CSV_RAW_SECRET_REJECTED` for a raw PAT prefix and URL credential form, `PROF_CSV_INVALID_UTF8`, `PROF_CSV_HEADER_MISSING`, `PROF_CSV_DUPLICATE_HEADER_COLUMN`, `PROF_CSV_UNKNOWN_COLUMN_REJECTED`, `PROF_CSV_REQUIRED_COLUMN_MISSING`, `PROF_CSV_UNCLOSED_QUOTED_FIELD`, and `PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE`.
- Row-level rejection checks cover `PROF_CSV_REQUIRED_FIELD_EMPTY`, `PROF_CSV_URL_FORM_REJECTED`, and `PROF_CSV_DUPLICATE_STUDENT_INTERNAL_ID` through the `evidence.rejected_rows[*].message` path after successful byte parsing and row-input delegation.
- The audit asserts that messages do not contain fixture substrings such as `ghp_`, `://user:topsecret@`, `bogus_secret_column_value`, `이름 unterminated_secret_value`, `extra_garbage_after_close`, `stu_secret_id`, `ftp://invalid-form.example`, or `duplicate_secret_stu_id`.
- `PROF_CSV_URL_CREDENTIAL_REJECTED` is intentionally excluded from this byte-parser audit because URL credential form in raw CSV bytes is caught first by `scan_csv_bytes_for_raw_secrets` and rejected as `PROF_CSV_RAW_SECRET_REJECTED`; the row-input URL credential code remains covered by the upstream row-input intake gate.
- The audit is regression protection for future descriptive-message changes. The current implementation already satisfies the invariant structurally because `BlockDocumentError::new(code)` sets `message = code.to_string()` and row-level rejection messages are code strings.

## 3. RED to GREEN evidence

### M7-PROF-CSV-INTAKE-BYTE-ERROR-MSG-AUDIT-T1 audit test

```text
RED command:    cargo test -p eduops_domain --test m7_professor_csv_intake_byte_error_msg_audit -- --nocapture
RED result:     initial audit file run had 9 passed and 3 failed; the failures were fixture mistakes where the intended per-row REQUIRED_FIELD_EMPTY / URL_FORM_REJECTED / DUPLICATE_STUDENT_INTERNAL_ID cases used course_id=c and were pre-empted by PROF_CSV_COURSE_ID_MISMATCH
GREEN command:  cargo test -p eduops_domain --test m7_professor_csv_intake_byte_error_msg_audit -- --nocapture
GREEN result:   12 passed; 0 failed after correcting the per-row fixtures to use COURSE_ID="course_eduops_prof_csv_byte_err_msg_2026"
Commit:         a5fe0d3
```

## 4. Repository-level validation

```text
cargo test -p eduops_domain --test m7_professor_csv_intake_byte_error_msg_audit      -> 12 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_byte_rfc4180_contract     -> 8 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_byte_contract             -> 13 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_byte_safety_contract      -> 12 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_contract                  -> 10 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_safety_contract           -> 9 passed
cargo fmt --all --check                                                               -> clean
git diff --check                                                                      -> clean
npm run m0:check                                                                       -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Raw PAT prefix bytes reject without echoing PAT substrings | `m7_professor_csv_intake_byte_error_msg_audit::raw_pat_prefix_rejection_message_does_not_echo_bytes` | accepted |
| URL credential form bytes reject without echoing userinfo substrings | `m7_professor_csv_intake_byte_error_msg_audit::raw_url_credential_form_rejection_message_does_not_echo_bytes` | accepted |
| Invalid UTF-8 rejects with an ASCII code-only message | `m7_professor_csv_intake_byte_error_msg_audit::invalid_utf8_rejection_message_does_not_echo_bytes` | accepted |
| Missing header rejects with a code-only message | `m7_professor_csv_intake_byte_error_msg_audit::header_missing_rejection_message_does_not_echo_bytes` | accepted |
| Duplicate header column rejects without echoing the duplicated column name | `m7_professor_csv_intake_byte_error_msg_audit::duplicate_header_column_rejection_message_does_not_echo_bytes` | accepted |
| Unknown column rejects without echoing the unknown header name | `m7_professor_csv_intake_byte_error_msg_audit::unknown_column_rejection_message_does_not_echo_bytes` | accepted |
| Required column missing rejects with a code-only message | `m7_professor_csv_intake_byte_error_msg_audit::required_column_missing_rejection_message_does_not_echo_bytes` | accepted |
| Unclosed quoted field rejects without echoing offending quoted-field bytes | `m7_professor_csv_intake_byte_error_msg_audit::unclosed_quoted_field_rejection_message_does_not_echo_bytes` | accepted |
| Trailing garbage after a quoted field rejects without echoing the garbage substring | `m7_professor_csv_intake_byte_error_msg_audit::quoted_field_trailing_garbage_rejection_message_does_not_echo_bytes` | accepted |
| Row-level required-field rejection does not echo the row's student identifier substring | `m7_professor_csv_intake_byte_error_msg_audit::per_row_required_field_empty_message_does_not_echo_bytes` | accepted |
| Row-level URL-form rejection does not echo unsupported URL substrings | `m7_professor_csv_intake_byte_error_msg_audit::per_row_url_form_rejected_message_does_not_echo_bytes` | accepted |
| Row-level duplicate-student-id rejection does not echo the duplicate identifier substring | `m7_professor_csv_intake_byte_error_msg_audit::per_row_duplicate_student_internal_id_message_does_not_echo_bytes` | accepted |
| Existing RFC 4180, byte-parser, byte-safety, row-input, and row-safety buckets remain green | regression validation commands in §4 | accepted |

## 6. Non-claims

This evidence summary does not claim:

- live GitHub action, real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote`, or real credential resolution;
- repository administration, real CSV upload UI deployment, drag-and-drop file picker, Tauri shell wiring of a production CSV import surface, or production deployment;
- full-Unicode NFC normalization beyond the existing controlled Hangul composition behavior;
- SSH PEM private-key blob detection or password-form key-value detection in `scan_csv_bytes_for_raw_secrets`;
- SHA-256 source-URL audit hash upgrade beyond the existing FNV-1a 64 envelope;
- production copy/localization for descriptive error messages; the current accepted invariant is non-echoing code-only message content;
- notification delivery, external identity-provider integration, organization administration, submission/provisioning state promotion, or DEMO-1 acceptance;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Extend `normalize_nfc` to cover full-Unicode NFC normalization with a controlled dependency/adoption plan;
2. Extend byte-stream raw-secret scanning to SSH PEM private-key blob prefixes and password-form key-value patterns after an authorized control update enumerates the additional patterns;
3. Extract a shared FNV-1a 64 helper across `eduops_domain` and `eduops_git` as a preparation step for the SHA-256 source-URL audit hash upgrade;
4. Author the user-managed runbook for CSV preparation and live clone-readonly operation per `EDUOPS-DEC-065`;
5. Consider production-facing, localized error-copy design only after preserving the no-echo invariant in tests.

## 8. Traceability

- [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md)
- [M7 professor CSV roster + repository URL intake gate evidence](m7-prof-csv-intake-evidence.md)
- [M7 professor CSV byte parser gate evidence](m7-prof-csv-intake-byte-evidence.md)
- [M7 professor CSV byte parser RFC 4180 grammar gate evidence](m7-prof-csv-intake-byte-rfc4180-evidence.md)
- [M7 approval UX predecessor reference integration gate evidence](m7-approval-ux-intake-link-evidence.md)
- [Software test description](../03-verification-validation/software-test-description.md)
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
