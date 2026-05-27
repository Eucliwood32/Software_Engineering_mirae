---
title: M7 Student Pre-cloned Local-Checkout Reader Post-Construction Evidence Scan Gate Evidence
document_id: EDUOPS-M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE-SCAN-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-STUDENT-LOCAL-CHECKOUT-READER-SPEC
    - EDUOPS-M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - m7_student_local_checkout_reader_evidence_scan_contract
    - m7_student_local_checkout_reader_contract
    - m7_student_local_checkout_reader_safety_contract
---

# M7 Student Pre-cloned Local-Checkout Reader Post-Construction Evidence Scan Gate Evidence

## 1. Gate result

`GATE-M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE-SCAN-FIXTURE-LOCAL` is accepted-constrained for the fixture-local belt-and-suspenders post-construction evidence-text scan added by `M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE-SCAN-T1` at `e5403ab`. The scan closes the deferred follow-up item recorded in [M7 student pre-cloned local-checkout reader gate evidence](m7-student-local-checkout-reader-evidence.md) §7 item 1 and implements the spec §6 `scan_local_checkout_evidence_for_raw_secrets` safety guard.

```text
gate=GATE-M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE-SCAN-FIXTURE-LOCAL
status=accepted-constrained
scope=crates/eduops_domain/src/lib.rs::scan_local_checkout_evidence_for_raw_secrets walks every text-bearing field on the constructed StudentLocalCheckoutReadEvidence (schema_version, read_id, approved_dry_run_plan_id, workspace_path_label_hash, relative_repo_path_hash, requested_by_role, requested_at_utc, canonical_json, evidence_sha256, every audit_event_ids[i], every accepted record's path_hash/content_sha256/content_kind/audit_event_id, every rejected record's reason_code/redacted_path_hash/redacted_reason) and rejects any byte-stream PAT prefix / URL credential form / SSH PEM blob hit with STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED; read_student_local_checkout is wired to construct the evidence into a let binding and invoke scan_local_checkout_evidence_for_raw_secrets(&evidence)? immediately before Ok(evidence) so any future implementation regression that leaks a raw secret into the evidence is caught
constraint=live HTTPS/SSH probe, real git clone/fetch/push/ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration, real desktop file-picker UI, real authorization-predecessor lookup against a live identity provider, network call of any kind, submission/provisioning state promotion, evaluation-result authority, defensive READ_OUTSIDE_WORKSPACE canonical-path comparison duplicate (rule 5), symlink-target inspection (partial rule 4), strict rule-6 not-symlink/not-device/not-directory file-kind check, password-form key-value detection beyond enumerated SSH PEM blob headers, SHA-256 source-URL audit hash upgrade beyond FNV-1a 64 envelope, shared FNV-1a 64 helper extraction across eduops_domain/eduops_git, additional predecessor reference kinds in the approval workflow VM, and DEMO-1 acceptance are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
credential_resolutions=0
remote=none
```

This evidence does not claim a live GitHub action, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, repository administration, real desktop file-picker UI, submission/provisioning state promotion, evaluation-result authority, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted post-construction evidence-text scan behavior:

- `crates/eduops_domain/src/lib.rs` defines `pub fn scan_local_checkout_evidence_for_raw_secrets(&StudentLocalCheckoutReadEvidence) -> Result<(), BlockDocumentError>`.
- The scan walks 9 top-level evidence fields (`schema_version`, `read_id`, `approved_dry_run_plan_id`, `workspace_path_label_hash`, `relative_repo_path_hash`, `requested_by_role`, `requested_at_utc`, `canonical_json`, `evidence_sha256`), every `audit_event_ids[i]`, every accepted record's 4 text-bearing fields (`path_hash`, `content_sha256`, `content_kind`, `audit_event_id`), and every rejected record's 3 text-bearing fields (`reason_code`, `redacted_path_hash`, `redacted_reason`). For each field, the scan reuses the existing byte-stream helpers `local_checkout_bytes_contain_pat_prefix`/`local_checkout_bytes_contain_url_credential_form`/`local_checkout_bytes_contain_ssh_pem_blob` on the field's `as_bytes()` view.
- On any hit, the scan returns `Err(BlockDocumentError::new("STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED"))`. The rejection message contains the code only; no offending bytes are echoed.
- `read_student_local_checkout` is wired to bind the constructed `StudentLocalCheckoutReadEvidence` to a `let` binding, invoke `scan_local_checkout_evidence_for_raw_secrets(&evidence)?` immediately before `Ok(evidence)`, so the post-construction sweep runs on every successful reader emission.
- Because every input field that could carry a raw secret is already blocked pre-construction (per T2 `scan_local_checkout_request_for_raw_secrets` and per-file `scan_local_checkout_content_for_raw_secrets`), and every output field is either FNV-1a 64 redacted, SHA-256 redacted, an enum literal, or a hardcoded boolean, the legitimate happy-path evidence passes the post-construction scan by construction. The scan is regression protection for any future implementation change that introduces a new field, drops a pre-construction guard, or otherwise leaks a raw secret into the evidence text.

## 3. RED to GREEN evidence

```text
RED command:    cargo test -p eduops_domain --test m7_student_local_checkout_reader_evidence_scan_contract -- --nocapture
RED result:     error[E0432]: unresolved import `eduops_domain::scan_local_checkout_evidence_for_raw_secrets`
GREEN command:  cargo test -p eduops_domain --test m7_student_local_checkout_reader_evidence_scan_contract -- --nocapture
GREEN result:   test result: ok. 12 passed; 0 failed
Commit:         e5403ab
```

## 4. Repository-level validation

```text
cargo test -p eduops_domain --test m7_student_local_checkout_reader_evidence_scan_contract -> ok. 12 passed
cargo test -p eduops_domain --test m7_student_local_checkout_reader_contract              -> ok. 6 passed
cargo test -p eduops_domain --test m7_student_local_checkout_reader_safety_contract       -> ok. 17 passed
cargo test --workspace                                                                    -> all targets pass
cargo fmt --all --check                                                                   -> clean
git diff --check                                                                          -> clean
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)                      -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q                       -> 6 passed in 0.06s
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| `scan_local_checkout_evidence_for_raw_secrets` is exposed as `pub fn` in `eduops_domain` | `crates/eduops_domain/src/lib.rs` `pub fn` definition | accepted |
| Legitimate happy-path evidence passes the post-construction scan | `m7_student_local_checkout_reader_evidence_scan_contract::happy_path_evidence_passes_post_construction_scan` and `::cleaned_redacted_record_path_hash_passes` and `::happy_path_with_two_records_still_passes` | accepted |
| Reader integration: `read_student_local_checkout` invokes the scan and still returns Ok for a legitimate clean fixture | `m7_student_local_checkout_reader_evidence_scan_contract::reader_invokes_post_construction_scan_so_clean_read_returns_ok` | accepted |
| Planted PAT prefix in `read_id` rejects with `STUDENT_LOCAL_CHECKOUT_RAW_SECRET_REJECTED` and no offending bytes in message | `m7_student_local_checkout_reader_evidence_scan_contract::planted_pat_in_read_id_field_rejects` | accepted |
| Planted URL credential form in `canonical_json` rejects | `m7_student_local_checkout_reader_evidence_scan_contract::planted_url_credential_in_canonical_json_rejects` | accepted |
| Planted SSH PEM blob in `audit_event_ids` rejects | `m7_student_local_checkout_reader_evidence_scan_contract::planted_ssh_pem_blob_in_audit_event_id_rejects` | accepted |
| Planted PAT prefix in a redacted record's `audit_event_id` rejects | `m7_student_local_checkout_reader_evidence_scan_contract::planted_pat_in_redacted_file_record_field_rejects` | accepted |
| Planted PAT prefix in a rejected record's `reason_code` rejects | `m7_student_local_checkout_reader_evidence_scan_contract::planted_pat_in_rejected_file_record_field_rejects` | accepted |
| Planted PAT prefix in `requested_by_role` rejects | `m7_student_local_checkout_reader_evidence_scan_contract::planted_pat_in_requested_by_role_rejects` | accepted |
| Planted URL credential form in `workspace_path_label_hash` rejects | `m7_student_local_checkout_reader_evidence_scan_contract::planted_url_credential_in_workspace_path_label_hash_rejects` | accepted |
| Planted PAT prefix in `schema_version` rejects | `m7_student_local_checkout_reader_evidence_scan_contract::planted_schema_version_with_pat_rejects` | accepted |
| Existing T1 contract bucket remains green (`m7_student_local_checkout_reader_contract` 6/6) and T2 safety bucket remains green (`m7_student_local_checkout_reader_safety_contract` 17/17) | regression validation commands in §4 | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live HTTPS/SSH probe of any GitHub repository URL;
- real `git clone`, `git fetch`, `git push`, `git ls-remote`, or any other live Git command;
- real credential resolution, token refresh, credential rotation, or credential storage modification;
- repository creation, push, branch/tag, issue, webhook, check-run, invitation, branch protection, archive, or any GitHub administration action;
- a network call of any kind from the reader or the scan;
- a real desktop file-picker UI, drag-and-drop file selection, or Tauri shell wiring of a production student-checkout import surface;
- a real authorization-predecessor lookup against a live identity provider;
- submission/provisioning state promotion from local-checkout read evidence;
- evaluation-result authority;
- the defensive `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` rule 5 canonical-path comparison duplicate (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 2);
- partial rule 4 symlink-target inspection that classifies a symlink whose target leaves the workspace as `PATH_ESCAPE` distinct from `EXPECTED_FILE_MISSING` (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 3);
- strict rule 6 "not symlink / not device / not directory" file-kind check beyond plain file-existence (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 4);
- password-form key-value detection (`password=`/`passwd=`/`secret=`/`token=`) beyond the explicitly-enumerated SSH PEM blob headers (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 6);
- shared FNV-1a 64 helper extraction across `eduops_domain` and `eduops_git` (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 5);
- approval workflow predecessor reference integration of the new `student-local-checkout-read-evidence` kind (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 7);
- the user-managed clone runbook (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 8 and `EDUOPS-DEC-064`/`EDUOPS-DEC-065`);
- full-Unicode NFC normalization;
- SHA-256 source-URL audit hash upgrade beyond the existing FNV-1a 64 envelope;
- detection of raw-secret patterns that do not match the three enumerated families (PAT prefix, URL credential form, SSH PEM blob);
- coverage of non-text-bearing evidence fields (the hardcoded boolean flags and integer counts cannot carry text and are not scanned);
- DEMO-1 acceptance or live working-demonstration approval;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Add the defensive rule 5 `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` canonical-path comparison guard via `std::fs::canonicalize` on both the absolute file path and the workspace boundary (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 2);
2. Extend rule 4 symlink-target inspection (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 3);
3. Tighten rule 6 to a strict not-symlink/not-device/not-directory file-kind check (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 4);
4. Extract a shared FNV-1a 64 helper across `eduops_domain` and `eduops_git` (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 5);
5. Extend per-file content scan with password-form key-value detection (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 6);
6. Wire the reader's `StudentLocalCheckoutReadEvidence` id into the approval workflow's predecessor reference list as a third predecessor kind (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 7);
7. Author the user-managed runbook for student-managed `git clone` (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 8; user-managed per `EDUOPS-DEC-064`/`EDUOPS-DEC-065`).

## 8. Traceability

- [Student pre-cloned local-checkout reader specification](../02-design-planning/student-pre-cloned-local-checkout-reader-specification.md) §6 fail-closed safety guards (this gate implements the deferred post-construction evidence scan)
- [M7 student pre-cloned local-checkout reader gate evidence](m7-student-local-checkout-reader-evidence.md) §7 item 1 (closes this deferred follow-up)
- [Software test description](../03-verification-validation/software-test-description.md) — a future addendum for `STD-M7-STUDENT-LOCAL-CHECKOUT-READER-002/003`
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
