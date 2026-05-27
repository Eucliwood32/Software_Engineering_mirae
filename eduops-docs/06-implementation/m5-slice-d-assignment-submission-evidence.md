---
title: M5 SLICE-D Assignment Publication, Submission, and Repository Conflict Gate Evidence
document_id: EDUOPS-M5-SLICE-D-ASSIGNMENT-SUBMISSION-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-STATE-TABLES
    - SWENG-EDUTECH-REPO-WORKFLOW
    - SWENG-EDUTECH-ACM
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M5-AUTH-SPEC-BLOCKER
  tests:
    - eduops_domain::m5_assignment_release_contract
    - eduops_domain::m5_submission_state_contract
    - eduops_storage::m5_repository_conflict_contract
---

# M5 SLICE-D Assignment Publication, Submission, and Repository Conflict Gate Evidence

## 1. Gate result

M5 is accepted-constrained for the fixture-local assignment release state machine, submission state machine, and repository conflict guard boundary, with explicit deferral of production scoped-authorization implementation per `EDUOPS-M5-AUTH-SPEC-BLOCKER`.

```text
gate=GATE-SLICE-D-ASSIGNMENT-SUBMISSION
status=accepted-constrained
scope=deterministic assignment version creation, release-state transitions, and update transitions; submission state machine with distinct Checkpointed/Queued/Pushed/Confirmed/Rejected/ManualReview states; repository conflict guard that rejects assignment-update writes outside assignment/** and never overwrites workspace/** or knowledge/** paths; structured RepositoryConflictEvidence
constraint=production scoped-authorization engine (AuthorizationDecisionRecord persistence, allow-with-confirmation/approval/queue mechanics, TA scope-grant lifecycle, offline promotion enforcement, instructor publication-update notification surface, TA review queue, feedback release authority, evaluator/sync-worker boundary, live GitHub push, server-backed submission receipt, observability ingestion) all out of scope per EDUOPS-M5-AUTH-SPEC-BLOCKER
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
remote=none
```

M5 does not claim production scoped-authorization engine, live GitHub push, server-backed submission receipt, instructor publication-update notification surface, scoped TA review queue, feedback release authority, evaluator/sync-worker authority boundary, late-policy enforcement, manual-review prior-state restriction, observability ingestion of authorization decisions or audit events beyond in-memory `audit_event_id` strings, or assignment-side conflict detection against released-version baseline hashes.

## 2. Implemented acceptance scope

Accepted M5 behavior:

- `eduops_domain` defines `ASSIGNMENT_SCHEMA_VERSION = "eduops.assignment/0.1"`, `AssignmentReleaseState { Scheduled, Released, UpdateAvailable, Closed, Archived }`, `AssignmentVersionInput`, `AssignmentVersionRef`, `AssignmentVersion` with deterministic canonical sorted JSON and SHA-256 content hash, `AssignmentVersion::derive` validation (required fields, release_at < due_at), `AssignmentReleaseError`, and `AssignmentReleaseRegistry` with `publish_version`/`publish_update`/`release`/`snapshot`. Publish rejects duplicate version labels; release requires `authoritative_now >= release_at` and rejects transitions from non-Scheduled state; publish_update marks previously Released versions for the same assignment as `UpdateAvailable`; snapshot is sorted by course/assignment/version label.
- `eduops_domain` defines `SUBMISSION_SCHEMA_VERSION = "eduops.submission/0.1"`, `SubmissionState`, `SubmissionRecord`, `SubmissionError`, and `SubmissionRegistry` with `checkpoint`/`queue`/`mark_pushed`/`confirm`/`mark_rejected`/`mark_manual_review`/`snapshot`. Queued, pushed, and confirmed are distinct states; confirm requires Pushed state and records `authoritative_received_at` distinct from `submitted_at`; queue requires Checkpointed; mark_rejected accepts Queued or Pushed; mark_manual_review records conflict review. Each transition emits a distinct `audit_event_id`.
- `eduops_storage` defines `AssignmentUpdateEntry`, `ApplyAssignmentUpdateRequest`, `RepositoryConflictEvidence` (affected_path, scope, base_sha256, local_sha256, incoming_sha256, actor, reason, decision, audit_event_id), `ApplyAssignmentUpdateEvidence`, and `LocalStorageAdapter::apply_assignment_update` that rejects non-local mode and live external action, rejects empty entries, validates `course_id`/`student_internal_id` against path-escape, classifies each entry by its first path component (assignment accepted; workspace/knowledge produce a `block` conflict with `EDUOPS_REPO_CONFLICT_SCOPE_VIOLATION`; any other or `..`/absolute path produces an `unknown` conflict with `EDUOPS_VALIDATION_PATH_SCOPE`), records the local SHA-256 of any existing target before deciding, and applies the update all-or-nothing: a single conflict blocks the entire request and no filesystem write occurs.

## 3. RED to GREEN evidence

### M5-T1/M5-T2 assignment release state machine

```text
RED command:    cargo test -p eduops_domain --test m5_assignment_release_contract -- --nocapture
RED result:     unresolved imports for AssignmentReleaseState/AssignmentVersion/AssignmentReleaseRegistry
GREEN command:  cargo test -p eduops_domain --test m5_assignment_release_contract -- --nocapture
GREEN result:   7 passed; 0 failed
Commit:         f48c7af
```

### M5-T3 submission state machine

```text
RED command:    cargo test -p eduops_domain --test m5_submission_state_contract -- --nocapture
RED result:     unresolved submission state type imports
GREEN command:  cargo test -p eduops_domain --test m5_submission_state_contract -- --nocapture
GREEN result:   7 passed; 0 failed
Commit:         2eb609b
```

### M5-T4 repository conflict contract

```text
RED command:    cargo test -p eduops_storage --test m5_repository_conflict_contract -- --nocapture
RED result:     unresolved ApplyAssignmentUpdateRequest/AssignmentUpdateEntry imports and missing apply_assignment_update method
GREEN command:  cargo test -p eduops_storage --test m5_repository_conflict_contract -- --nocapture
GREEN result:   9 passed; 0 failed
Commit:         85ff379
```

### M5-AUTH-SPEC scoped authorization spec blocker

```text
Decision:       EDUOPS-DEC-M5-AUTH-SPEC-DEFERRED
Document:       docs/06-implementation/m5-auth-spec-blocker.md
Status:         blocker-recorded; M5 gate scope constrained
Commit:         dee97ec
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> passed=88 failed=0 ignored=0
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
docs link/JSON sweep                                                       -> markdown_files=103; json_files=9; bad_local_links=0; bad_json_parse=0
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Assignment update does not overwrite `workspace/**` or `knowledge/**` | `m5_repository_conflict_contract::apply_assignment_update_blocks_workspace_scope_entries`, `apply_assignment_update_blocks_knowledge_scope_entries`, `apply_assignment_update_blocks_entry_with_path_escape` | accepted |
| Queued, pushed, and confirmed states are separately represented in evidence | `m5_submission_state_contract` (distinct states across `checkpoint`/`queue`/`mark_pushed`/`confirm` transitions; confirm requires Pushed and records `authoritative_received_at` separate from `submitted_at`) | accepted |
| Submission snapshot links workspace SHA, assignment version, commit SHA, and timestamp | `m5_submission_state_contract` (SubmissionRecord captures `checkpoint_sha`, `submitted_at`, `pushed_ref`, `pushed_commit_sha`, `authoritative_received_at`, and assignment version reference) | accepted |
| Adapter evidence cannot advance state without core validation | `m5_submission_state_contract::confirm_requires_pushed_state`, `m5_submission_state_contract::queue_requires_checkpointed_state`, `m5_repository_conflict_contract::apply_assignment_update_rejects_live_external_action`, `m5_repository_conflict_contract::apply_assignment_update_rejects_non_local_adapter_mode`, `m5_repository_conflict_contract::apply_assignment_update_rejects_invalid_course_id` | accepted |
| Assignment publication and release transitions are deterministic and immutable | `m5_assignment_release_contract` (deterministic publish, early-release guard, update marks prior, missing-version rejection, time-window validation, missing-required-field validation, sorted snapshot) | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a production scoped-authorization engine for submission/review actions (deferred per [EDUOPS-M5-AUTH-SPEC-BLOCKER](m5-auth-spec-blocker.md));
- `AuthorizationDecisionRecord` persistence, JSON manifest, ingestion, retention, or redaction;
- `allow-with-confirmation` / `allow-with-approval` / `queue` mechanics for high-impact actions per AC-010;
- TA delegated-scope grant lifecycle, expiry, and revocation per AC-005;
- offline promotion rule enforcement per AC-009 beyond fixture-local state transitions;
- instructor publication-update notification surface, scoped TA review queue, or feedback release authority;
- evaluator/sync-worker authority boundary per AC-008;
- live GitHub push, server-backed submission receipt, or remote audit ingestion;
- observability/diagnostics ingestion of authorization decisions or audit events beyond in-memory `audit_event_id` strings;
- assignment-side conflict detection against the released-version baseline hash;
- late-policy enforcement, manual-review prior-state restriction, evaluation result attach, or instructor reopen workflow surface;
- DEMO-1 export evidence (deferred to M8).

## 7. Follow-up

The following follow-up items are required before broader submission-related milestones may claim acceptance:

1. close the scoped submission/review authorization implementation specification gap per the [M5 scoped submission and review authorization specification gap closure](m5-auth-spec-blocker.md) follow-up checklist;
2. thread the released-assignment-version baseline hash into `ApplyAssignmentUpdateRequest` so that `RepositoryConflictEvidence.base_sha256` is populated and assignment-side §5 conflict detection becomes executable;
3. add the `Closed`/`Archived` transition tests for `AssignmentReleaseRegistry` and the `Evaluated`/`Reopened` transitions for `SubmissionRegistry` when their state-machine entries become executable;
4. proceed to M6 advisory C/C++ runner only after the evaluation runner I/O contract is authored and accepted;
5. proceed to M7 GitHub clone-only adapter only at the selected safe integration point, preserving clone-only/fake/mock/dry-run boundaries and no live GitHub action;
6. proceed to M8 export fixture and DEMO-1 evidence only after the exporter implementation specification is authored and accepted.

## 8. Traceability

- [State machine implementation tables](../02-design-planning/state-machine-implementation-tables.md)
- [Repository permission and assignment workflow](../02-design-planning/repository-permission-workflow.md)
- [Access control and authorization model](../02-design-planning/access-control-authorization-model.md)
- [M5 scoped submission and review authorization specification gap closure](m5-auth-spec-blocker.md)
- [Implementation milestones](implementation-milestones.md)
- [M4 SLICE-C roster, identity, and workspace gate evidence](m4-slice-c-roster-identity-workspace-evidence.md)
- [M3 SLICE-B canonical document gate evidence](m3-slice-b-canonical-document-evidence.md)
- [M2 configuration and credential reference evidence](m2-configuration-credential-evidence.md)
