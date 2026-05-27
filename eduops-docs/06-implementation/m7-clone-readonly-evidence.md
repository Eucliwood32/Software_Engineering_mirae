---
title: M7 Clone-Readonly Integration-Point Gate Evidence
document_id: EDUOPS-M7-CLONE-READONLY-INTEGRATION-POINT-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SDD
    - SWENG-EDUTECH-GITHUB-MOCK-HTTP-FIXTURE-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
  tests:
    - eduops_git::m7_clone_readonly_gate_contract
    - eduops_git::m7_clone_readonly_safety_contract
---

# M7 Clone-Readonly Integration-Point Gate Evidence

## 1. Gate result

`GATE-M7-CLONE-READONLY-INTEGRATION-POINT` is accepted-constrained for the fixture-local clone-readonly allowlist/approval/credential-status/dry-run-plan integration-point boundary plus fail-closed safety guards defined by [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md). Live `clone-readonly` execution remains separately approved by a human-executed runbook and is not authorized by this gate.

```text
gate=GATE-M7-CLONE-READONLY-INTEGRATION-POINT
status=accepted-constrained
scope=CloneReadonlyAllowlistEntry / CloneReadonlyGateApproval / CloneReadonlyCredentialStatus / CloneReadonlyDryRunPlanRequest / CloneReadonlyDryRunPlan record contracts plus enum families CloneReadonlyApproverRole (CourseAdmin / PlatformAdmin) / CloneReadonlyRequestedByRole / CloneReadonlyActorRole / CloneReadonlyScopeClass (None / ClonePublic / ClonePrivate) / CloneReadonlyCredentialStatusKind (Present / Missing / Expired / Revoked); decision pipeline evaluate_mode_gate (defensive non-CloneReadonly rejection plus gate-approval rejection) -> evaluate_clone_readonly_allowlist (FNV-1a 64 hash lookup with ISO 8601 UTC expiry and trailing-* glob prefix support) -> evaluate_clone_readonly_approval (approval_ref/idempotency/source-hash/operation/expiry checks; only course_admin or platform_admin approve) -> evaluate_clone_readonly_credential_status (clone_private requires Present; scope_class=none rejects credential_ref_id) -> evaluate_privacy_naming for each candidate -> assemble_clone_readonly_dry_run_plan producing CloneReadonlyDryRunPlan with hardcoded external_call_made=false / external_side_effect_made=false / github_mutation_made=false / live_external_action=false / clone_readonly_executed=false / no_raw_secret_observed=true literals plus deterministic sorted-key canonical_json excluding canonical_json/plan_sha256 fields and in-crate SHA-256 plan_sha256; pre-construction raw-credential sweep scan_inputs_for_raw_secrets over every text-bearing input record/request field (except privacy candidates routed through the privacy evaluator and the denylist itself); post-construction scan_clone_readonly_evidence_for_raw_secrets walking every text-bearing field on the constructed plan including canonical_json/plan_sha256/audit_event_ids/privacy_decisions
constraint=live GitHub action, real network round-trip, real git clone/fetch/push/ls-remote execution, credential lookup / token refresh / rotation / storage modification, human approval workflow UX authority, production retry/rate-limit/backoff tuning, repository creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive/administration, submission/provisioning state promotion authority, instructor approval surface UX, observability ingestion, DEMO-1 acceptance / working-demonstration approval, cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope, and any host-process invocation are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live GitHub clone, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real human approval workflow, real retry/backoff tuning, submission-state promotion, DEMO-1 acceptance, or any host-process invocation.

## 2. Implemented acceptance scope

Accepted M7 clone-readonly integration-point behavior:

- `eduops_git::github::clone_readonly` defines `CloneReadonlyError` with `From<GitHubCredentialLeakage>`, enum families `CloneReadonlyApproverRole { CourseAdmin, PlatformAdmin }`, `CloneReadonlyRequestedByRole { Instructor, Ta, CourseAdmin, PlatformAdmin }`, `CloneReadonlyActorRole { Instructor, Ta, CourseAdmin, PlatformAdmin, Evaluator }`, `CloneReadonlyScopeClass { None, ClonePublic, ClonePrivate }`, `CloneReadonlyCredentialStatusKind { Present, Missing, Expired, Revoked }`, plus record types `CloneReadonlyAllowlistEntry`, `CloneReadonlyGateApproval`, `CloneReadonlyCredentialStatus`, `PrivacyNamingCandidate`, `CloneReadonlyDryRunPlanRequest`, `PrivacyNamingDecisionRecord`, `CloneReadonlyDryRunPlan`, and `AssembleCloneReadonlyDryRunPlanInput`.
- `evaluate_clone_readonly_allowlist(request, allowlist, observed_at_utc)` finds the entry by FNV-1a 64 hash, enforces ISO 8601 UTC expiry, and validates the requested ref against the entry's `allowed_refs` (empty list = any ref allowed; trailing-`*` glob prefix supported). It returns `GITHUB_CLONE_READONLY_ALLOWLIST_DENIED` for unknown or expired entries and `GITHUB_CLONE_READONLY_REF_DENIED` for ref-pattern mismatches.
- `evaluate_clone_readonly_approval(request, allowlist_entry, approval, observed_at_utc)` validates `approval_ref` non-empty, `approved_operation == Clone` (else `GITHUB_NON_CLONE_OPERATION_BLOCKED`), `approved_source_repo_url_hash == requested == allowlist_entry`, `idempotency_key == request.idempotency_key`, `expires_at_utc > approved_at_utc`, and `observed_at_utc < expires_at_utc`. The `approver_role` enum only admits `CourseAdmin` and `PlatformAdmin`; `Instructor`/`TA` are not representable as approvers.
- `evaluate_clone_readonly_credential_status(credential_status)` rejects `credential_ref_id` set when `scope_class=none`, and rejects any non-`Present` status under `scope_class=ClonePrivate`, both with `GITHUB_AUTH_REQUIRED`.
- `assemble_clone_readonly_dry_run_plan(input)` composes the full pipeline: defensive non-`CloneReadonly` mode rejection (`GITHUB_LIVE_ACTION_BLOCKED`); pre-construction raw-credential sweep `scan_inputs_for_raw_secrets` over every text-bearing input field (request `plan_request_id`/`requested_source_repo_url_hash`/`requested_ref`/`target_local_path_template`/`idempotency_key`; allowlist entries' identifiers/hashes/refs/scope_owner/scope_label/expires_at_utc/audit_event_id; approval `approval_ref`/`approved_source_repo_url_hash`/`approved_at_utc`/`expires_at_utc`/`idempotency_key`/`audit_event_id`; credential `credential_ref_id`/`credential_fingerprint_hint`/`status_observed_at_utc`; top-level `observed_at_utc` and `expected_commit_sha`); `evaluate_mode_gate(CloneReadonly, Clone, gate_approved)` propagating any Blocked decision as `CloneReadonlyError`; `evaluate_clone_readonly_allowlist`; `evaluate_clone_readonly_approval`; `evaluate_clone_readonly_credential_status`; per-candidate `evaluate_privacy_naming` (Block propagates as `CloneReadonlyError` with the privacy code/reason); audit event id assembly (`audit_clone_readonly_plan_<plan_request_id>` plus mirrored allowlist/approval/mode-gate/privacy ids); deterministic sorted-key `canonical_plan_json` excluding `canonical_json`/`plan_sha256` by construction; in-crate SHA-256 `plan_sha256` over the canonical JSON. The plan envelope hardcodes `external_call_made=false`/`external_side_effect_made=false`/`github_mutation_made=false`/`live_external_action=false`/`clone_readonly_executed=false`/`no_raw_secret_observed=true` at the struct field and canonical JSON level.
- `scan_clone_readonly_evidence_for_raw_secrets(plan, denylist)` walks every text-bearing field on the constructed plan — `plan_request_id`/`operation_class`/`source_repo_url_hash`/`planned_ref`/`target_local_path_template`/`idempotency_key`/`approval_ref`/`allowlist_entry_id`/`mode_decision_audit_event_id`/`canonical_json`/`plan_sha256`, the optional `expected_commit_sha`/`credential_ref_id`/`credential_fingerprint_hint`, every `privacy_decisions[*]` (scope, sanitized_name, audit_event_id), and every `audit_event_ids[*]` — and rejects PAT-prefix/URL-credential-form/denylist-substring hits with `GITHUB_RAW_SECRET_REJECTED`.

## 3. RED to GREEN evidence

### M7-CLONE-READONLY-GATE-T1 type contract and decision pipeline

```text
RED command:    cargo test -p eduops_git --test m7_clone_readonly_gate_contract -- --nocapture
RED result:     unresolved AssembleCloneReadonlyDryRunPlanInput / CloneReadonlyActorRole / CloneReadonlyAllowlistEntry / CloneReadonlyApproverRole / CloneReadonlyCredentialStatus / CloneReadonlyCredentialStatusKind / CloneReadonlyDryRunPlan / CloneReadonlyDryRunPlanRequest / CloneReadonlyError / CloneReadonlyGateApproval / CloneReadonlyRequestedByRole / CloneReadonlyScopeClass / PrivacyNamingCandidate / assemble_clone_readonly_dry_run_plan / evaluate_clone_readonly_allowlist / evaluate_clone_readonly_approval / evaluate_clone_readonly_credential_status imports
GREEN command:  cargo test -p eduops_git --test m7_clone_readonly_gate_contract -- --nocapture
GREEN result:   26 passed; 0 failed
Commit:         2a722fd
```

### M7-CLONE-READONLY-GATE-T2 fail-closed safety guards

```text
RED command:    cargo test -p eduops_git --test m7_clone_readonly_safety_contract -- --nocapture
RED result:     10 raw-credential pre-construction cases failed (no pre-construction sweep yet); privacy-naming and evidence-scan cases already passed because the underlying helpers existed from T1
GREEN command:  cargo test -p eduops_git --test m7_clone_readonly_safety_contract -- --nocapture
GREEN result:   21 passed; 0 failed
Commit:         9a4ad43
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> 57/57 test target groups report ok, including M7-CLONE-READONLY-GATE-T1 26 passed; M7-CLONE-READONLY-GATE-T2 21 passed; M7-MOCKHTTP-T1 21 passed; M7-MOCKHTTP-T2 15 passed; M7-MOCKHTTP-T3 12 passed; M7-T1 6 passed; M7-T2 9 passed; M7-T3 7 passed; M8-T1 20 passed; M8-T2 13 passed; M8-T3 13 passed; M6-T1 10 passed; M6-T2 5 passed; M6-T3 9 passed; plus existing M1..M5 totals all green
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
docs link/JSON sweep                                                       -> bad_local_links=0; bad_json_parse=0
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Defensive non-`CloneReadonly` mode is rejected up front | `m7_clone_readonly_gate_contract::requested_mode_non_clone_readonly_is_defensively_rejected` (`GITHUB_LIVE_ACTION_BLOCKED`) | accepted |
| `clone_readonly_gate_approved=false` is rejected before allowlist/approval/credential evaluation | `m7_clone_readonly_gate_contract::gate_not_approved_is_rejected_with_live_action_blocked` | accepted |
| Non-clone operation is rejected before any plan emission | `m7_clone_readonly_gate_contract::requested_operation_non_clone_is_rejected_with_non_clone_operation_blocked`, `m7_clone_readonly_gate_contract::approval_with_non_clone_operation_is_rejected_with_non_clone_operation_blocked` | accepted |
| Unknown / expired allowlist entry and out-of-allowed-ref are rejected | `m7_clone_readonly_gate_contract::unknown_source_repo_url_hash_is_rejected_with_allowlist_denied`, `expired_allowlist_entry_is_rejected_with_allowlist_denied`, `requested_ref_outside_allowed_refs_is_rejected_with_ref_denied`, `empty_allowed_refs_treats_any_ref_as_allowed`, `glob_ref_pattern_with_trailing_star_matches_prefix` | accepted |
| Approval idempotency / source-hash / empty-ref / expiry mismatches are rejected | `m7_clone_readonly_gate_contract::approval_idempotency_key_mismatch_is_rejected_with_approval_denied`, `approval_source_hash_mismatch_is_rejected_with_approval_denied`, `approval_empty_ref_is_rejected_with_approval_denied`, `approval_observed_after_expiry_is_rejected_with_approval_denied` | accepted |
| Credential status mismatch under `clone_private` rejects with `GITHUB_AUTH_REQUIRED` and `credential_ref_id` set under `scope_class=none` rejects | `m7_clone_readonly_gate_contract::credential_missing_under_clone_private_is_rejected_with_auth_required`, `credential_revoked_under_clone_private_is_rejected_with_auth_required`, `credential_missing_under_clone_public_is_allowed`, `credential_ref_id_with_scope_class_none_is_rejected` | accepted |
| Privacy-naming candidates are routed through `evaluate_privacy_naming` and classified as `GITHUB_PRIVACY_POLICY_VIOLATION` | `m7_clone_readonly_safety_contract::privacy_candidate_pat_prefix_is_rejected_with_privacy_policy_violation`, `privacy_candidate_email_like_*`, `privacy_candidate_ssn_like_*`, `privacy_candidate_long_digit_run_*`, `privacy_candidate_denylist_match_*` | accepted |
| Pre-construction raw-credential sweep rejects PAT-prefix/URL-credential-form/denylist hits in every text-bearing input field | `m7_clone_readonly_safety_contract::raw_pat_in_plan_request_id_*`, `url_credential_form_in_target_local_path_template_*`, `raw_pat_in_idempotency_key_*`, `raw_pat_in_allowlist_scope_owner_*`, `raw_pat_in_allowlist_audit_event_id_*`, `raw_pat_in_approval_ref_*`, `raw_pat_in_approval_audit_event_id_*`, `raw_pat_in_credential_ref_id_*`, `raw_pat_in_credential_fingerprint_hint_*`, `raw_pat_in_expected_commit_sha_*` | accepted |
| Evidence scan walks every text-bearing plan field including canonical_json and privacy decisions | `m7_clone_readonly_safety_contract::scan_evidence_passes_clean_plan`, `scan_evidence_rejects_pat_prefix_in_audit_event_ids`, `scan_evidence_rejects_url_credential_form_in_target_local_path_template`, `scan_evidence_rejects_denylist_match_in_canonical_json`, `scan_evidence_rejects_pat_prefix_in_credential_ref_id`, `scan_evidence_walks_privacy_decision_records` | accepted |
| Plan envelope hardcodes non-mutation literals and produces deterministic canonical JSON and SHA-256 | `m7_clone_readonly_gate_contract::happy_path_assembles_dry_run_plan_with_hardcoded_non_mutation_literals`, `canonical_json_is_deterministic_across_repeated_calls`, `canonical_json_excludes_canonical_json_and_plan_sha256_fields`, `plan_sha256_changes_when_a_canonical_field_changes`, `audit_event_ids_are_deterministic_and_redacted` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live GitHub clone, real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, or real authentication handshake;
- the human approval workflow itself — only the *shape* of the approval evidence envelope and the fixture-only verification of its required fields;
- credential issuance, token refresh, credential rotation, raw token lookup/decryption/transmission, or any modification to credential storage;
- production retry/rate-limit/backoff policy authority or live retry jitter tuning;
- repository creation, push, branch/tag creation, pull request, issue, webhook, status, check-run, invitation, branch protection, archive, or any GitHub administration action;
- submission-state or provisioning-state promotion from clone-readonly evidence;
- instructor approval surface UX, evaluator integration, or observability ingestion;
- DEMO-1 acceptance, working-demonstration approval, or fidelity threshold authority;
- a cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope already shipped in `GitHubCloneEvidence`;
- live external action of any kind.

## 7. Follow-up

The following follow-up items are required before broader clone-readonly behavior may claim acceptance:

1. an authorized human owner must author and accept a **clone-readonly live-run runbook** that records the user-executed steps (allowlist promotion, approval signing, credential reference resolution, `git clone` invocation, and live-run evidence capture) before any real network round-trip is performed; as of `EDUOPS-DEC-064`, the live-run authority assumption is a professor-provisioned repository for which the professor/authorized course owner holds all required access authority; the runbook is still required and is not part of this gate;
2. an authorized human owner accepted a **clone-readonly human approval workflow UX specification** for instructor/course-admin/platform-admin surfaces in [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md); fixture-local UX implementation remains required before the integration point is consumed by the desktop UI;
3. upgrade `source_repo_url_hash` from FNV-1a 64 to SHA-256 once a cryptographic audit hash is required by an accepted controlled-evidence policy;
4. extend the ref pattern matcher beyond literal equality and trailing-`*` prefix once a richer matching policy is authored;
5. integrate the clone-readonly dry-run plan envelope into a future clone planner so that a planned clone-readonly invocation always carries the dry-run plan evidence as a predecessor.

## 8. Traceability

- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub adapter software design description](../02-design-planning/github-adapter-software-design-description.md)
- [GitHub mock-HTTP fixture format specification](../02-design-planning/github-mock-http-fixture-specification.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [Software test description](../03-verification-validation/software-test-description.md) — STD-086 through STD-091
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-080..084` and `EDUOPS-NFR-034..036`
- [M7 SLICE-F GitHub clone-only adapter gate evidence](m7-slice-f-github-clone-only-evidence.md)
- [M7 mock-http fixture replay gate evidence](m7-mockhttp-evidence.md)
- [Implementation milestones](implementation-milestones.md)
- [Queue-end planning analysis](queue-end-planning-analysis.md)
