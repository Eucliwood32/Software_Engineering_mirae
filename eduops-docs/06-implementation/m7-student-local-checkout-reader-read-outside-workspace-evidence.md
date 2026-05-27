---
title: M7 Student Pre-cloned Local-Checkout Reader READ_OUTSIDE_WORKSPACE Guard Gate Evidence
document_id: EDUOPS-M7-STUDENT-LOCAL-CHECKOUT-READER-READ-OUTSIDE-WORKSPACE-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-STUDENT-LOCAL-CHECKOUT-READER-SPEC
    - EDUOPS-M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE
    - EDUOPS-M7-STUDENT-LOCAL-CHECKOUT-READER-EVIDENCE-SCAN-EVIDENCE
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - m7_student_local_checkout_reader_read_outside_workspace_contract
    - m7_student_local_checkout_reader_evidence_scan_contract
    - m7_student_local_checkout_reader_safety_contract
    - m7_student_local_checkout_reader_contract
---

# M7 Student Pre-cloned Local-Checkout Reader READ_OUTSIDE_WORKSPACE Guard Gate Evidence

## 1. Gate result

`GATE-M7-STUDENT-LOCAL-CHECKOUT-READER-READ-OUTSIDE-WORKSPACE-FIXTURE-LOCAL` is accepted-constrained for the fixture-local defensive rule 5 canonical-path comparison guard added by `M7-STUDENT-LOCAL-CHECKOUT-READER-READ-OUTSIDE-WORKSPACE-T1` at `85b1709`. The guard closes the deferred follow-up item recorded in [M7 student pre-cloned local-checkout reader gate evidence](m7-student-local-checkout-reader-evidence.md) §7 item 2 and [M7 student pre-cloned local-checkout reader post-construction evidence scan gate evidence](m7-student-local-checkout-reader-evidence-scan-evidence.md) §7 item 1, and implements the spec §4 rule 5 / §6 per-read boundary check.

```text
gate=GATE-M7-STUDENT-LOCAL-CHECKOUT-READER-READ-OUTSIDE-WORKSPACE-FIXTURE-LOCAL
status=accepted-constrained
scope=crates/eduops_domain/src/lib.rs::read_student_local_checkout now canonicalizes each absolute file path via std::fs::canonicalize after std::fs::read succeeds, lazily canonicalizes the workspace boundary <workspace_root_path>/<relative_repo_path> on the first successful read, and aborts emission with Err(BlockDocumentError::new("STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE")) whenever the canonical absolute path does not Path::starts_with the canonical boundary; canonicalize failures on the already-read absolute path or on the workspace boundary also abort with the same code for defense-in-depth against canonicalize-time TOCTOU
constraint=live HTTPS/SSH probe, real git clone/fetch/push/ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration, real desktop file-picker UI, real authorization-predecessor lookup against a live identity provider, network call of any kind, submission/provisioning state promotion, evaluation-result authority, symlink-target inspection that classifies escaping symlinks as PATH_ESCAPE distinct from this code (partial rule 4 carry-over), strict rule 6 not-symlink/not-device/not-directory file-kind check beyond plain file existence, password-form key-value detection beyond enumerated SSH PEM blob headers, full-Unicode NFC normalization, SHA-256 source-URL audit hash upgrade beyond the existing FNV-1a 64 envelope, shared FNV-1a 64 helper extraction across eduops_domain/eduops_git, additional predecessor reference kinds in the approval workflow VM, the user-managed clone runbook, and DEMO-1 acceptance are explicitly out of scope
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

Accepted defensive `READ_OUTSIDE_WORKSPACE` canonical-path comparison guard behavior:

- `crates/eduops_domain/src/lib.rs::read_student_local_checkout` declares a lazily-initialized `canonical_repo_root: Option<std::path::PathBuf>` outside the per-file loop and populates it on the first successful `std::fs::read` via `std::fs::canonicalize(&repo_root)`. The lazy population preserves the prior behavior where an entirely-missing `repo_root` collapses every file to `STUDENT_LOCAL_CHECKOUT_EXPECTED_FILE_MISSING` rejection records (the new canonicalize never runs in that case).
- After each successful per-file `std::fs::read(&abs_path)`, the reader canonicalizes `abs_path` via `std::fs::canonicalize(&abs_path)`. Any `Err` from the canonicalize call aborts emission with `Err(BlockDocumentError::new("STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE"))` as a defense-in-depth measure against canonicalize-time TOCTOU (the file was just read successfully, so the only plausible canonicalize error path is a concurrent unlink or permission flip).
- The reader then asserts `canon_abs.starts_with(canonical_repo_root.as_ref().unwrap())`. On `false` it aborts emission with the same `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` code.
- The lexical rule 4 `local_checkout_expected_path_safety` pre-read check remains the first line of defense against `..`/absolute/root/prefix/NUL path components; the new guard catches the TOCTOU class where the lexical check passes but the actual on-disk file resolves outside the canonical workspace boundary (the prototypical symlink-escape scenario).
- The rejection text contains the rejection code only; no offending path bytes, content bytes, or canonicalize-target bytes are echoed into the `BlockDocumentError::message`.

## 3. RED to GREEN evidence

```text
RED command:    cargo test -p eduops_domain --test m7_student_local_checkout_reader_read_outside_workspace_contract -- --nocapture
RED result:     2 of 4 tests fail (symlink_target_outside_workspace_aborts_with_read_outside_workspace and symlink_pointing_into_sibling_outside_repo_root_aborts_with_read_outside_workspace) — the symlink-followed std::fs::read succeeded without any canonical boundary check and the reader returned Ok(StudentLocalCheckoutReadEvidence { accepted_file_count: 1, ... })
GREEN command:  cargo test -p eduops_domain --test m7_student_local_checkout_reader_read_outside_workspace_contract -- --nocapture
GREEN result:   test result: ok. 4 passed; 0 failed
Commit:         85b1709
```

## 4. Repository-level validation

```text
cargo test -p eduops_domain --test m7_student_local_checkout_reader_read_outside_workspace_contract -> ok. 4 passed
cargo test -p eduops_domain --test m7_student_local_checkout_reader_evidence_scan_contract         -> ok. 12 passed
cargo test -p eduops_domain --test m7_student_local_checkout_reader_safety_contract                -> ok. 17 passed
cargo test -p eduops_domain --test m7_student_local_checkout_reader_contract                       -> ok. 6 passed
cargo test --workspace                                                                             -> all targets pass
cargo fmt --all --check                                                                            -> clean
git diff --check                                                                                   -> clean
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)                               -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Symlink target outside the workspace root aborts with `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` and the rejection text does not echo any offending path or content bytes | `m7_student_local_checkout_reader_read_outside_workspace_contract::symlink_target_outside_workspace_aborts_with_read_outside_workspace` | accepted |
| Symlink target inside the workspace root but outside the canonical `repo_root` boundary aborts with `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` | `m7_student_local_checkout_reader_read_outside_workspace_contract::symlink_pointing_into_sibling_outside_repo_root_aborts_with_read_outside_workspace` | accepted |
| Symlink target inside the canonical `repo_root` boundary succeeds and the resulting evidence has `accepted_file_count=1`, `rejected_file_count=0` | `m7_student_local_checkout_reader_read_outside_workspace_contract::symlink_target_inside_repo_root_is_accepted` | accepted |
| Legitimate plain-file read remains accepted (no symlink) | `m7_student_local_checkout_reader_read_outside_workspace_contract::legitimate_plain_file_read_remains_accepted` | accepted |
| Existing T1 contract bucket remains green (`m7_student_local_checkout_reader_contract` 6/6) | regression validation commands in §4 | accepted |
| Existing T2 safety bucket remains green (`m7_student_local_checkout_reader_safety_contract` 17/17) | regression validation commands in §4 | accepted |
| Existing EVIDENCE-SCAN-T1 bucket remains green (`m7_student_local_checkout_reader_evidence_scan_contract` 12/12) | regression validation commands in §4 | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live HTTPS/SSH probe of any GitHub repository URL;
- real `git clone`, `git fetch`, `git push`, `git ls-remote`, or any other live Git command;
- real credential resolution, token refresh, credential rotation, or credential storage modification;
- repository creation, push, branch/tag, issue, webhook, check-run, invitation, branch protection, archive, or any GitHub administration action;
- a network call of any kind from the reader or the new guard;
- a real desktop file-picker UI, drag-and-drop file selection, or Tauri shell wiring of a production student-checkout import surface;
- a real authorization-predecessor lookup against a live identity provider;
- submission/provisioning state promotion from local-checkout read evidence;
- evaluation-result authority;
- partial rule 4 symlink-target inspection that classifies an escaping symlink as `STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE` distinct from `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` (the new guard catches escaping symlinks under the rule-5 code; the distinct rule-4 classification remains deferred per spec authority);
- strict rule 6 "not symlink / not device / not directory" file-kind check beyond plain file-existence (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 4);
- password-form key-value detection (`password=`/`passwd=`/`secret=`/`token=`) beyond the explicitly-enumerated SSH PEM blob headers (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 6);
- shared FNV-1a 64 helper extraction across `eduops_domain` and `eduops_git` (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 5);
- approval workflow predecessor reference integration of the new `student-local-checkout-read-evidence` kind (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 7);
- the user-managed clone runbook (still deferred per `m7-student-local-checkout-reader-evidence.md` §7 item 8 and `EDUOPS-DEC-064`/`EDUOPS-DEC-065`);
- full-Unicode NFC normalization;
- SHA-256 source-URL audit hash upgrade beyond the existing FNV-1a 64 envelope;
- detection of TOCTOU paths other than symlinks-resolving-outside-boundary (e.g., bind mounts, hard links to outside-boundary inodes, namespace pivots) — the guard catches every case where `std::fs::canonicalize` resolves the post-read absolute path to a path that does not `Path::starts_with` the canonical workspace boundary, but does not enumerate or guarantee detection of every conceivable TOCTOU variant;
- platform coverage beyond `#[cfg(unix)]` for the symlink-escape test fixture (the guard itself is platform-independent and runs on every platform; only the test fixture that uses `std::os::unix::fs::symlink` is Unix-gated);
- DEMO-1 acceptance or live working-demonstration approval;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Add a distinct rule 4 partial symlink-target classification so a symlink whose target resolves outside the workspace boundary records `STUDENT_LOCAL_CHECKOUT_PATH_ESCAPE` instead of (or in addition to) `STUDENT_LOCAL_CHECKOUT_READ_OUTSIDE_WORKSPACE` (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 3 — the spec authority for this classification refinement remains open);
2. Tighten rule 6 to a strict not-symlink/not-device/not-directory file-kind check (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 4);
3. Extract a shared FNV-1a 64 helper across `eduops_domain` and `eduops_git` (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 5);
4. Extend per-file content scan with password-form key-value detection (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 6);
5. Wire the reader's `StudentLocalCheckoutReadEvidence` id into the approval workflow's predecessor reference list as a third predecessor kind (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 7);
6. Author the user-managed runbook for student-managed `git clone` (carry-over from `m7-student-local-checkout-reader-evidence.md` §7 item 8; user-managed per `EDUOPS-DEC-064`/`EDUOPS-DEC-065`).

## 8. Traceability

- [Student pre-cloned local-checkout reader specification](../02-design-planning/student-pre-cloned-local-checkout-reader-specification.md) §4 rule 5 and §6 per-read boundary check (this gate implements the deferred defensive canonical-path comparison guard)
- [M7 student pre-cloned local-checkout reader gate evidence](m7-student-local-checkout-reader-evidence.md) §7 item 2 (closes this deferred follow-up)
- [M7 student pre-cloned local-checkout reader post-construction evidence scan gate evidence](m7-student-local-checkout-reader-evidence-scan-evidence.md) §7 item 1 (closes this deferred follow-up)
- [Software test description](../03-verification-validation/software-test-description.md) — a future addendum for `STD-M7-STUDENT-LOCAL-CHECKOUT-READER-002/003`
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
