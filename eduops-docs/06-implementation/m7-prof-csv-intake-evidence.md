---
title: M7 Professor CSV Roster + Repository URL Intake Gate Evidence
document_id: EDUOPS-M7-PROF-CSV-INTAKE-EVIDENCE
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
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - eduops_domain::m7_professor_csv_intake_contract
    - eduops_domain::m7_professor_csv_intake_safety_contract
---

# M7 Professor CSV Roster + Repository URL Intake Gate Evidence

## 1. Gate result

`GATE-M7-PROFESSOR-CSV-INTAKE-FIXTURE-LOCAL` is accepted-constrained for the fixture-local professor CSV intake parser (M7-PROF-CSV-INTAKE-T1) and its fail-closed safety guards (M7-PROF-CSV-INTAKE-T2) defined by [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md). Live HTTPS/SSH probe of any GitHub repository URL, real `git clone`/`git fetch`/`git push`/`git ls-remote`, real credential resolution, repository administration, real CSV upload UI, notification delivery, identity-provider integration, submission/provisioning state promotion, and DEMO-1 acceptance are explicitly out of scope and remain user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

```text
gate=GATE-M7-PROFESSOR-CSV-INTAKE-FIXTURE-LOCAL
status=accepted-constrained
scope=eduops_domain::ProfessorCsvIntakeRow / ProfessorCsvIntakeRequest / ProfessorCsvIntakeRedactedRow / ProfessorCsvIntakeRejection / ProfessorCsvIntakeEvidence types; intake_professor_csv pipeline that for each row scans every text-bearing cell except github_repository_url for raw GitHub PAT prefix (ghp_ / github_pat_) and URL credential form (://user:token@host) and rejects with PROF_CSV_RAW_SECRET_REJECTED; required-field non-empty / course_id match / accepted URL shape (https://github.com/<owner>/<repo>(.git)? and git@github.com:<owner>/<repo>(.git)?) / URL credential form / duplicate student_internal_id validations with PROF_CSV_* codes per spec §4; FNV-1a 64 source-URL hash envelope fnv1a64:<16hex> over normalized-lowercase URL bytes; SHA-256 redaction of student_internal_id, optional email, and NFC-normalized student_display_name; deterministic per-row audit ids audit_prof_csv_row_<intake_id>_<idx>_<sha> plus the intake-level audit_prof_csv_intake_<intake_id>; sorted-key canonical JSON containing only redacted fields and hardcoded external_call_made / external_side_effect_made / github_mutation_made / live_external_action / clone_readonly_executed = false plus no_raw_secret_observed / no_raw_repository_url_persisted = true; in-crate SHA-256 evidence hash over the canonical JSON; ProfessorCsvSecretLeakage enum and scan_professor_csv_evidence_for_raw_secrets post-construction scan walking every text-bearing field on the constructed evidence including audit ids, redacted-row canonical JSON / source-URL hash / student-internal-id SHA-256, and rejected-row code / message / student-internal-id SHA-256 with PAT-prefix / URL-credential-form / denylist-substring rejection
constraint=live HTTPS/SSH probe of repository URL, real git clone / git fetch / git push / git ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration (creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive), real CSV upload UI / drag-and-drop file picker / production deployment, notification delivery, external identity-provider integration, organization administration, submission/provisioning state promotion, DEMO-1 acceptance / working-demonstration approval, fidelity / privacy / legal policy authority beyond reapplication of existing controlled redaction rules, full CSV-byte parser with PROF_CSV_INVALID_UTF8 and PROF_CSV_UNKNOWN_COLUMN_REJECTED codes, host-process invocation, and any cryptographic source-URL audit hash beyond the existing FNV-1a 64 envelope are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live HTTPS/SSH probe, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real CSV upload UI deployment, notification delivery, submission/provisioning state promotion, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted M7 professor CSV intake behavior:

- `eduops_domain` defines `ProfessorCsvIntakeRow`, `ProfessorCsvIntakeRequest`, `ProfessorCsvIntakeRedactedRow`, `ProfessorCsvIntakeRejection`, and `ProfessorCsvIntakeEvidence` types plus the `PROFESSOR_CSV_INTAKE_SCHEMA_VERSION="eduops.professor-csv-intake/0.1"` constant.
- `intake_professor_csv(request)` runs the row pipeline:
  1. `scan_row_for_raw_secrets(row)` rejects raw PAT prefix or URL credential form in any text-bearing cell except `github_repository_url` with `PROF_CSV_RAW_SECRET_REJECTED`;
  2. required-field-non-empty check rejects with `PROF_CSV_REQUIRED_FIELD_EMPTY`;
  3. course_id match rejects with `PROF_CSV_COURSE_ID_MISMATCH`;
  4. accepted URL shape check (HTTPS `github.com/<owner>/<repo>(.git)?` or SSH `git@github.com:<owner>/<repo>(.git)?`) rejects unsupported shapes with `PROF_CSV_URL_FORM_REJECTED`;
  5. URL credential form check on the authority portion of HTTPS URLs rejects with `PROF_CSV_URL_CREDENTIAL_REJECTED`;
  6. duplicate `student_internal_id` rejects with `PROF_CSV_DUPLICATE_STUDENT_INTERNAL_ID`;
  7. `fnv1a64_source_repo_url_hash` produces the `fnv1a64:<16hex>` envelope over normalized-lowercase URL bytes;
  8. duplicate `source_repo_url_hash` is accepted and counted via `duplicate_source_repo_url_hash_count`;
  9. per-row canonical JSON contains only `course_id`, `email_sha256` (or null), `privacy_flags` (sorted), `section_id`, `source_repo_url_hash`, `status`, `student_display_name_sha256` (SHA-256 over NFC-normalized name), and `student_internal_id_sha256`;
  10. accepted/rejected rows are sorted by `student_internal_id_sha256` for deterministic ordering;
  11. envelope canonical JSON includes `accepted_count`, `audit_event_ids[]`, `course_id`, `duplicate_source_repo_url_hash_count`, hardcoded `external_call_made`/`external_side_effect_made`/`github_mutation_made`/`live_external_action`/`clone_readonly_executed=false`, `intake_id`, `no_raw_repository_url_persisted`/`no_raw_secret_observed=true`, redacted rows, rejected rows, `schema_version`, and `source_csv_sha256`;
  12. `evidence_sha256` is the in-crate SHA-256 over the canonical JSON.
- `scan_professor_csv_evidence_for_raw_secrets(evidence, denylist)` walks every text-bearing field on the constructed evidence and returns `ProfessorCsvSecretLeakage::PatPrefix`/`UrlCredentialForm`/`DenylistEntry` on hit.

## 3. RED to GREEN evidence

### M7-PROF-CSV-INTAKE-T1 parser contract and evidence envelope

```text
RED command:    cargo test -p eduops_domain --test m7_professor_csv_intake_contract
RED result:     unresolved imports for ProfessorCsvIntakeRow / ProfessorCsvIntakeRequest / intake_professor_csv; could not compile eduops_domain
GREEN command:  cargo test -p eduops_domain --test m7_professor_csv_intake_contract
GREEN result:   10 passed; 0 failed
Commit:         24f7ec4
```

### M7-PROF-CSV-INTAKE-T2 fail-closed safety guards

```text
RED command:    cargo test -p eduops_domain --test m7_professor_csv_intake_safety_contract
RED result:     unresolved import for scan_professor_csv_evidence_for_raw_secrets; could not compile eduops_domain
GREEN command:  cargo test -p eduops_domain --test m7_professor_csv_intake_safety_contract
GREEN result:   9 passed; 0 failed
Commit:         8aaf146
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
cargo test --workspace                                                     -> all test target groups report ok (existing M0..M8 + M7-MOCKHTTP + M7-CLONE-READONLY + the new M7-PROF-CSV-INTAKE-T1 10 passed + M7-PROF-CSV-INTAKE-T2 9 passed)
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Happy path accepts well-formed rows and produces deterministic canonical JSON + SHA-256 | `m7_professor_csv_intake_contract::happy_path_accepts_well_formed_rows_and_produces_deterministic_evidence` | accepted |
| Evidence does not contain raw PII or raw repository URL | `m7_professor_csv_intake_contract::evidence_does_not_contain_raw_pii_or_raw_repository_url` | accepted |
| Hardcoded no-live flags are false and `no_raw_repository_url_persisted=true` | `m7_professor_csv_intake_contract::hardcoded_no_live_flags_are_false_and_no_raw_repository_url_persisted_is_true` | accepted |
| Missing required field rejected with `PROF_CSV_REQUIRED_FIELD_EMPTY` | `m7_professor_csv_intake_contract::missing_required_field_is_rejected_with_required_field_empty_code` | accepted |
| Unsupported URL form rejected with `PROF_CSV_URL_FORM_REJECTED` | `m7_professor_csv_intake_contract::unsupported_url_form_is_rejected_with_url_form_rejected_code` | accepted |
| URL credential form in `github_repository_url` rejected with `PROF_CSV_URL_CREDENTIAL_REJECTED` | `m7_professor_csv_intake_contract::url_credential_form_is_rejected_with_url_credential_rejected_code` | accepted |
| Duplicate `student_internal_id` rejected | `m7_professor_csv_intake_contract::duplicate_student_internal_id_is_rejected` | accepted |
| Duplicate `source_repo_url_hash` accepted but counted | `m7_professor_csv_intake_contract::duplicate_source_repo_url_hash_is_counted_but_accepted` | accepted |
| `course_id` mismatch rejected | `m7_professor_csv_intake_contract::course_id_mismatch_is_rejected` | accepted |
| `evidence_sha256` is 64 hex chars and changes when input changes | `m7_professor_csv_intake_contract::evidence_sha256_is_64_hex_chars_and_changes_when_input_changes` | accepted |
| Raw PAT prefix or URL credential form in any non-URL text cell rejected with `PROF_CSV_RAW_SECRET_REJECTED` before downstream validation | `m7_professor_csv_intake_safety_contract::raw_pat_in_student_internal_id_*`, `raw_pat_in_student_display_name_*`, `raw_pat_prefix_github_pat_*`, `url_credential_form_anywhere_else_*` | accepted |
| Single unsafe row does not taint adjacent safe rows | `m7_professor_csv_intake_safety_contract::raw_pat_in_a_single_row_does_not_taint_other_rows` | accepted |
| Clean evidence passes post-construction scan and injected unsafe values are rejected | `m7_professor_csv_intake_safety_contract::clean_evidence_passes_post_construction_raw_secret_scan`, `post_construction_scan_rejects_pat_prefix_injected_into_canonical_json`, `post_construction_scan_rejects_url_credential_injected_into_audit_ids`, `post_construction_scan_rejects_denylist_match` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live HTTPS/SSH probe of any GitHub repository URL;
- a real `git clone`, `git fetch`, `git push`, `git ls-remote`, or any other live Git command;
- real credential resolution, token refresh, credential rotation, or credential storage modification;
- repository creation, push, branch/tag, issue, webhook, check-run, invitation, branch protection, archive, or any GitHub administration action;
- a real CSV upload UI, drag-and-drop file picker, or production deployment;
- submission/provisioning state promotion from CSV intake;
- DEMO-1 acceptance or live working-demonstration approval;
- a full CSV-byte parser with `PROF_CSV_INVALID_UTF8` UTF-8 decoding error or `PROF_CSV_UNKNOWN_COLUMN_REJECTED` unknown-column-rejection code (deferred to a later iteration alongside CSV-byte intake);
- a cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope (deferred per `m7-clone-readonly-evidence.md` §7 item 3);
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. add a CSV-byte parser that produces `ProfessorCsvIntakeRow` values, handles `PROF_CSV_INVALID_UTF8`, `PROF_CSV_UNKNOWN_COLUMN_REJECTED`, and the spec §3 header contract before delegating to the existing row-input pipeline;
2. extract a shared FNV-1a 64 helper so `eduops_domain::fnv1a64_source_repo_url_hash` and `eduops_git::github::clone_evidence::source_repo_url_hash` share a single implementation, and prepare for the SHA-256 envelope upgrade tracked under `m7-clone-readonly-evidence.md` §7 item 3;
3. extend the row pipeline to apply NFC normalization to all text-bearing fields (currently only `student_display_name` is normalized before hashing);
4. integrate the professor CSV intake evidence into the upstream clone-readonly approval workflow UX so the approval surface can reference both the intake evidence id and the dry-run plan id as predecessors;
5. record an authorized human runbook for the user-managed CSV preparation step (assembling roster rows and GitHub repository URLs outside EduOps automation) per `EDUOPS-DEC-065`; this is outside Ralph automation and remains user-managed.

## 8. Traceability

- [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md)
- [Roster schema and identity policy](../02-design-planning/roster-schema-and-identity-policy.md)
- [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md)
- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [Software test description](../03-verification-validation/software-test-description.md) — STD-M7-PROF-CSV-INTAKE-001..003 (to be cross-linked in the test description addendum)
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [M7 clone-readonly integration-point gate evidence](m7-clone-readonly-evidence.md)
- [M7 clone-readonly approval workflow UX gate evidence](m7-approval-ux-evidence.md)
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
