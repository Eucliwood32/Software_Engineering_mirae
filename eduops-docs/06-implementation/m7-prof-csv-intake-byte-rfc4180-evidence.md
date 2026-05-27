---
title: M7 Professor CSV Byte Parser RFC 4180 Grammar Gate Evidence
document_id: EDUOPS-M7-PROF-CSV-INTAKE-BYTE-RFC4180-EVIDENCE
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
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - eduops_domain::m7_professor_csv_intake_byte_rfc4180_contract
    - eduops_domain::m7_professor_csv_intake_byte_contract
    - eduops_domain::m7_professor_csv_intake_byte_safety_contract
    - eduops_domain::m7_professor_csv_intake_contract
    - eduops_domain::m7_professor_csv_intake_safety_contract
---

# M7 Professor CSV Byte Parser RFC 4180 Grammar Gate Evidence

## 1. Gate result

`GATE-M7-PROFESSOR-CSV-INTAKE-BYTE-RFC4180-FIXTURE-LOCAL` is accepted-constrained for the fixture-local extension of the byte parser (M7-PROF-CSV-INTAKE-BYTE-RFC4180-SPEC-PREP at `5364d78`) and the RFC 4180 quoted-string grammar implementation (M7-PROF-CSV-INTAKE-BYTE-RFC4180-T1 at `7e15f34`). The extension formally adopts RFC 4180 quoted-string CSV grammar — double-quoted fields with embedded commas, embedded CRLF, and the `""` escape — and rejects unclosed quoted fields with `PROF_CSV_UNCLOSED_QUOTED_FIELD` and trailing garbage after a closing quote with `PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE`, without changing any of the non-claims that already apply to [M7 professor CSV roster + repository URL intake gate evidence](m7-prof-csv-intake-evidence.md) or [M7 professor CSV byte parser gate evidence](m7-prof-csv-intake-byte-evidence.md).

Live HTTPS/SSH probe, real `git clone`/`git fetch`/`git push`/`git ls-remote`, real credential resolution, repository administration, real CSV upload UI, full-Unicode NFC normalization (canonical reordering / compatibility decomposition / Latin combining marks), SSH PEM private-key blob detection (`-----BEGIN OPENSSH PRIVATE KEY-----` and related framings), password-form key-value detection (`password=`/`passwd=`/`secret=`/`token=`), SHA-256 source-URL audit hash upgrade, notification delivery, submission/provisioning state promotion, and DEMO-1 acceptance remain explicitly out of scope and user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

```text
gate=GATE-M7-PROFESSOR-CSV-INTAKE-BYTE-RFC4180-FIXTURE-LOCAL
status=accepted-constrained
scope=crates/eduops_domain::parse_rfc4180_records private state-machine helper (BetweenFields/Unquoted/Quoted/QuotedAfterQuote) that walks UTF-8 codepoints and handles double-quoted fields, embedded commas / CRLF, the "" escape, unclosed quoted field → PROF_CSV_UNCLOSED_QUOTED_FIELD, trailing garbage after closing quote → PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE, suppresses spurious trailing empty records via a record_has_content flag, and treats the existing line-based parsing as a strict subset; intake_professor_csv_from_bytes refactored to delegate to parse_rfc4180_records for both header and data rows while preserving header column matching (REQUIRED_COLUMNS/OPTIONAL_COLUMNS), PROF_CSV_DUPLICATE_HEADER_COLUMN / PROF_CSV_UNKNOWN_COLUMN_REJECTED / PROF_CSV_REQUIRED_COLUMN_MISSING / PROF_CSV_HEADER_MISSING checks, NFC normalization on every text-bearing field, delegation to intake_professor_csv row-input pipeline, and pre-decode scan_csv_bytes_for_raw_secrets which continues to fire BEFORE grammar parsing so PROF_CSV_RAW_SECRET_REJECTED takes precedence over grammar-level codes for credential-shaped bytes
constraint=live HTTPS/SSH probe, real git clone/fetch/push/ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration (creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive), real CSV upload UI / drag-and-drop file picker / production deployment, full-Unicode NFC normalization beyond Hangul L+V+T composition (canonical reordering / compatibility decomposition / Latin combining marks remain identity), SSH PEM private-key blob detection (-----BEGIN OPENSSH PRIVATE KEY----- and related framings) — requires authorized control update enumerating the additional patterns, password-form key-value detection (password=/passwd=/secret=/token=) — same authorization requirement, SHA-256 source-URL audit hash upgrade (FNV-1a 64 remains in place), notification delivery, external identity-provider integration, organization administration, submission/provisioning state promotion, DEMO-1 acceptance / working-demonstration approval, and legacy single-`\r`-terminated record support are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live GitHub action, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real CSV upload UI deployment, full-Unicode NFC normalization, SSH PEM blob / password-form detection, notification delivery, submission/provisioning state promotion, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted M7 professor CSV byte parser RFC 4180 grammar behavior:

- `crates/eduops_domain/src/lib.rs` defines a private `Rfc4180State` enum (`BetweenFields`/`Unquoted`/`Quoted`/`QuotedAfterQuote`) and a private `parse_rfc4180_records(text: &str) -> Result<Vec<Vec<String>>, BlockDocumentError>` helper that walks the UTF-8 codepoint stream via `chars().peekable()`.
- The state machine handles every production listed in `professor-csv-intake-specification.md` §3.1: an unquoted field contains any non-`,`/`"`/`\r`/`\n` characters; a quoted field begins with `"`, ends with `"`, and accepts any other character including embedded `,`/`\r`/`\n`; the two-character `""` sequence inside a quoted field represents a single literal `"`; record terminators are `\r\n`, `\n`, or end-of-input.
- Unclosed quoted fields at EOF emit `PROF_CSV_UNCLOSED_QUOTED_FIELD`. Trailing characters after a closing quote that are neither separator (`,`) nor record terminator emit `PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE`.
- A `record_has_content` flag suppresses spurious trailing empty records from terminator-at-EOF inputs (`"a,b\n"` parses to one record `["a","b"]`, not two).
- `intake_professor_csv_from_bytes` was refactored to delegate to `parse_rfc4180_records` for both header and data rows. The pre-decode `scan_csv_bytes_for_raw_secrets` call remains the FIRST check inside the function, so raw PAT prefix / URL credential form bytes inside a quoted field still reject with `PROF_CSV_RAW_SECRET_REJECTED` before the grammar parser observes them.
- All existing rejection codes (`PROF_CSV_INVALID_UTF8`, `PROF_CSV_HEADER_MISSING`, `PROF_CSV_DUPLICATE_HEADER_COLUMN`, `PROF_CSV_UNKNOWN_COLUMN_REJECTED`, `PROF_CSV_REQUIRED_COLUMN_MISSING`, `PROF_CSV_RAW_SECRET_REJECTED`, plus the row-input pipeline's `PROF_CSV_REQUIRED_FIELD_EMPTY`, `PROF_CSV_URL_FORM_REJECTED`, `PROF_CSV_URL_CREDENTIAL_REJECTED`, `PROF_CSV_DUPLICATE_STUDENT_INTERNAL_ID`) continue to fire on the same fixtures they did before the RFC 4180 extension.
- NFC normalization (Hangul L+V+T composition only) continues to apply to every text-bearing field after the grammar parser produces it.
- The empty-quoted-record case `""` parses to a single-field record `[""]` and is then filtered as an empty record by the existing `if record.len() == 1 && record[0].is_empty() { continue; }` filter in the consumer — matching the prior parser's "skip empty lines" semantics.

## 3. RED to GREEN evidence

### M7-PROF-CSV-INTAKE-BYTE-RFC4180-SPEC-PREP spec extension

```text
RED command:    n/a — docs/control checkpoint
RED result:     `professor-csv-intake-specification.md` v0.1.0 §3-§4 enumerated only the minimal comma-separated grammar with CRLF tolerance; quoted-string grammar productions and the two new rejection codes were absent
GREEN command:  npm run m0:check
GREEN result:   cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
Commit:         5364d78
```

### M7-PROF-CSV-INTAKE-BYTE-RFC4180-T1 grammar implementation

```text
RED command:    cargo test -p eduops_domain --test m7_professor_csv_intake_byte_rfc4180_contract -- --nocapture
RED result:     6 of 8 focused tests failed (quoted_header_column_with_value_equals_unquoted_form, quoted_value_with_embedded_comma_in_display_name, quoted_value_with_embedded_crlf_in_display_name, escaped_double_quote_inside_quoted_value, unclosed_quoted_field_is_rejected, quoted_field_trailing_garbage_is_rejected) — the prior minimal grammar treats `"` as a literal field character and would either misalign field counts (reject as PROF_CSV_REQUIRED_FIELD_EMPTY) or compare wrong display-name SHA-256 values; the unquoted-regression and raw-PAT-inside-quoted tests already passed (regression baseline and pre-decode scan firing order respectively)
GREEN command:  cargo test -p eduops_domain --test m7_professor_csv_intake_byte_rfc4180_contract -- --nocapture
GREEN result:   8 passed; 0 failed (quoted_header_column_with_value_equals_unquoted_form, quoted_value_with_embedded_comma_in_display_name, quoted_value_with_embedded_crlf_in_display_name, escaped_double_quote_inside_quoted_value, unclosed_quoted_field_is_rejected, quoted_field_trailing_garbage_is_rejected, unquoted_rows_still_parse_after_rfc4180_extension, raw_pat_inside_quoted_value_still_fires_pre_decode_byte_scan)
Commit:         7e15f34
```

## 4. Repository-level validation

```text
cargo test -p eduops_domain --test m7_professor_csv_intake_byte_rfc4180_contract   -> 8 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_byte_contract           -> 13 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_byte_safety_contract    -> 12 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_contract                -> 10 passed
cargo test -p eduops_domain --test m7_professor_csv_intake_safety_contract         -> 9 passed
cargo test --workspace                                                              -> all buckets green
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)               -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q                -> 6 passed
cargo fmt --all --check                                                             -> clean
git diff --check                                                                    -> clean
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Quoted header column name produces structurally-equivalent parse to the unquoted form | `m7_professor_csv_intake_byte_rfc4180_contract::quoted_header_column_with_value_equals_unquoted_form` | accepted |
| Quoted value with embedded comma in display name parses as a single field | `m7_professor_csv_intake_byte_rfc4180_contract::quoted_value_with_embedded_comma_in_display_name` | accepted |
| Quoted value with embedded CRLF in display name parses as a single field with the literal CRLF preserved | `m7_professor_csv_intake_byte_rfc4180_contract::quoted_value_with_embedded_crlf_in_display_name` | accepted |
| Escaped `""` inside a quoted field decodes to a single literal `"` | `m7_professor_csv_intake_byte_rfc4180_contract::escaped_double_quote_inside_quoted_value` | accepted |
| Unclosed quoted field at EOF rejects with `PROF_CSV_UNCLOSED_QUOTED_FIELD` | `m7_professor_csv_intake_byte_rfc4180_contract::unclosed_quoted_field_is_rejected` | accepted |
| Trailing characters after a closing quote that are neither separator nor terminator reject with `PROF_CSV_QUOTED_FIELD_TRAILING_GARBAGE` | `m7_professor_csv_intake_byte_rfc4180_contract::quoted_field_trailing_garbage_is_rejected` | accepted |
| Unquoted regression input continues to parse identically to the prior minimal grammar | `m7_professor_csv_intake_byte_rfc4180_contract::unquoted_rows_still_parse_after_rfc4180_extension` | accepted |
| Raw PAT prefix inside a quoted field still rejects pre-decode with `PROF_CSV_RAW_SECRET_REJECTED` (byte-stream scan fires BEFORE grammar parsing) | `m7_professor_csv_intake_byte_rfc4180_contract::raw_pat_inside_quoted_value_still_fires_pre_decode_byte_scan` | accepted |
| Existing byte parser tests remain green (header validation, UTF-8 decoding, NFC normalization, row-input delegation) | regression via `m7_professor_csv_intake_byte_contract` and `m7_professor_csv_intake_byte_safety_contract` | accepted |
| Existing row-input parser tests remain green | regression via `m7_professor_csv_intake_contract` and `m7_professor_csv_intake_safety_contract` | accepted |
| Spec v0.2.0 §3.1 grammar productions formally adopted | `professor-csv-intake-specification.md` §3.1 | accepted |
| §4 rule 10 enumerates the two new rejection codes and the firing order (after pre-decode raw-secret scan) | `professor-csv-intake-specification.md` §4 rule 10 | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live GitHub action, real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote`, or real credential resolution;
- repository administration, real CSV upload UI deployment, drag-and-drop file picker, Tauri shell wiring of a production CSV import surface, or production deployment;
- full-Unicode NFC normalization (canonical reordering / compatibility decomposition / Latin combining marks); only Hangul L+V+T → precomposed-syllable composition is in scope today;
- SSH PEM private-key blob detection or password-form key-value detection in `scan_csv_bytes_for_raw_secrets`; both remain deferred until an authorized control update enumerates the additional patterns;
- support for the legacy single-`\r`-terminated record form (Macintosh classic); `\r` alone inside a record continues to be treated as part of a field character per §3.1;
- SHA-256 source-URL audit hash upgrade beyond the existing FNV-1a 64 envelope;
- notification delivery, external identity-provider integration, organization administration, or submission/provisioning state promotion;
- DEMO-1 acceptance or live working-demonstration approval;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Extend `normalize_nfc` to cover full-Unicode NFC normalization (canonical reordering and compatibility decomposition) — likely requires adopting the `unicode-normalization` crate as a controlled dependency (carried over from `m7-prof-csv-intake-byte-evidence.md` §7 item 1);
2. Extend `scan_csv_bytes_for_raw_secrets` to detect SSH PEM private-key blob prefixes and password-form key-value patterns when an authorized control update enumerates them (carried over from `m7-prof-csv-intake-byte-evidence.md` §7 item 4);
3. Extract a shared FNV-1a 64 helper across `eduops_domain` and `eduops_git` and prepare for the SHA-256 envelope upgrade tracked under `m7-clone-readonly-evidence.md` §7 item 3 (carried over from `m7-prof-csv-intake-byte-evidence.md` §7 item 3);
4. Add a fixture-local error-message redaction audit for the two new rejection codes to confirm that the rejection text does not echo the offending bytes;
5. Author the user-managed runbook for the CSV preparation step per `EDUOPS-DEC-065` (carried over from `m7-prof-csv-intake-evidence.md` §7 item 5); this is outside Ralph automation and remains user-managed.

## 8. Traceability

- [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md) — v0.2.0 §3.1 RFC 4180 grammar; §4 rule 10; §7 non-claims; §8 RFC4180-T1 row
- [M7 professor CSV roster + repository URL intake gate evidence](m7-prof-csv-intake-evidence.md)
- [M7 professor CSV byte parser gate evidence](m7-prof-csv-intake-byte-evidence.md)
- [M7 approval UX predecessor reference integration gate evidence](m7-approval-ux-intake-link-evidence.md)
- [Software test description](../03-verification-validation/software-test-description.md) — a future addendum for `STD-M7-PROF-CSV-INTAKE-BYTE-RFC4180-001..002`
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
