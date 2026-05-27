---
title: M7 Mock-HTTP Fixture Replay Gate Evidence
document_id: EDUOPS-M7-MOCKHTTP-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-GITHUB-MOCK-HTTP-FIXTURE-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SDD
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
  tests:
    - eduops_git::m7_mock_http_fixture_contract
    - eduops_git::m7_mock_http_retry_contract
    - eduops_git::m7_mock_http_safety_contract
---

# M7 Mock-HTTP Fixture Replay Gate Evidence

## 1. Gate result

M7-MOCKHTTP is accepted-constrained for fixture-local mock HTTP replay format, deterministic retry/backoff replay, clone-only response normalization, rate-limit/auth/scope/timeout fixture classification, and no-live/no-mutation/no-secret safety guards. Live GitHub readiness, real network behavior, clone-readonly approval mechanics, credential lookup, production retry tuning, and submission/provisioning state promotion remain explicitly out of scope.

```text
gate=GATE-M7-MOCKHTTP-FIXTURE-REPLAY
status=accepted-constrained
scope=GitHubMockScenario / GitHubMockResponse / GitHubRetryPolicy type contracts validating mock-http adapter mode, allowed GET/HEAD/LOCAL_FIXTURE methods, allowed repo_metadata/clone_ref/rate_limit/credential_probe/local_fixture endpoint classes, max_attempts in 1..=5, positive multiplier numerator/denominator, max_delay_ms >= base_delay_ms, jitter='none', and rejection of side-effect flags or raw credentials at construction; replay_mock_http(scenario) walking responses in order with deterministic per-retry delay computed via min(max_delay_ms, base_delay_ms * mult_num^n / mult_den^n) and the retry_after_ms<max_delay_ms override rule, attempt/retry counters, ordered response hashes, per-attempt audit ids, hardcoded non-mutation safety flags, sorted-key canonical evidence JSON excluding evidence_sha256/canonical_json keys, and an in-crate SHA-256 over the canonical evidence; enforce_clone_readonly_gate / enforce_privacy_naming_safety / scan_evidence_for_raw_secrets safety guards rejecting clone-readonly without external approval (GITHUB_LIVE_ACTION_BLOCKED), privacy-naming failures (GITHUB_PRIVACY_POLICY_VIOLATION), and raw credential strings in any evidence field (GITHUB_RAW_SECRET_REJECTED)
constraint=live GitHub readiness, real network round-trip, clone-readonly approval mechanism, credential lookup or rotation, production retry/rate-limit/backoff tuning for live systems, submission/provisioning state promotion, repository creation/push/branch/tag/issue/webhook/check-run mutation, instructor approval surface, host-process invocation, and any cryptographic source-URL audit hash beyond the existing FNV-1a 64 envelope are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
host_process_invocations=0
remote=none
```

M7-MOCKHTTP does not claim a live GitHub mock-http session, real network round-trip, real retry tuning, credential rotation, or submission-state promotion authority.

## 2. Implemented acceptance scope

Accepted M7-MOCKHTTP behavior:

- `eduops_git::github::mock_http` defines `GitHubMockScenario`, `GitHubMockResponse`, `GitHubRetryPolicy`, `GitHubMockOperation { ValidateCloneConfiguration, PlanClone, CloneRepositoryReadOnly, QueryCloneEvidence }`, `GitHubMockRequestMethod { Get, Head, LocalFixture }`, `GitHubMockEndpointClass { RepoMetadata, CloneRef, RateLimit, CredentialProbe, LocalFixture }`, `GitHubMockTerminalClassification` covering all spec §5 classification codes, `GitHubRetryPolicyJitter { None }`, and `MockFixtureError { code, message }` plus `From<GitHubCredentialLeakage>` impl. Construction enforces: `adapter_mode == "mock-http"`; `responses.len() >= 1`; non-empty `scenario_id`/`request_id`/`source_repo_url_hash`; `max_attempts` in `1..=5`; positive multiplier numerator/denominator; `max_delay_ms >= base_delay_ms`; jitter token `"none"` only; raw credential scan over every text-bearing field rejecting PAT prefix (`ghp_`/`github_pat_`), URL credential form (`://...:...@`), or denylist substring; write methods (`POST`/`PUT`/`PATCH`/`DELETE`) and unknown HTTP methods rejected before any replay; `external_call_made`/`live_external_action` true rejected with `GITHUB_LIVE_ACTION_BLOCKED`; `github_mutation_made` true rejected with `GITHUB_NON_CLONE_OPERATION_BLOCKED`.
- `replay_mock_http(scenario)` walks the response array in order, classifies each via `github_error_code` (with http_status fallback to `GITHUB_MOCK_SUCCESS`/`GITHUB_AUTH_REQUIRED`/`GITHUB_SCOPE_DENIED`/`GITHUB_OUTAGE_OR_TIMEOUT` for 200-304/401/403/4xx-5xx respectively), enforces `responses.len() <= max_attempts`, computes per-retry delays via the spec §4.3 formula `min(max_delay_ms, base_delay_ms * mult_num^n / mult_den^n)` at attempt index n=1,2,..., applies `retry_after_ms` override only when lower than `max_delay_ms`, records `selected_backoff_schedule_ms` per retried response (length = `retry_count`), tracks last seen `rate_limit_remaining` and `source_commit_sha`, emits per-attempt `audit_github_mock_attempt_<scenario_id>_step_<n>` audit ids, terminates on the first response whose classification appears in `terminal_error_classes` (or treats the last retriable response as terminal when no further attempts remain), rejects classifications neither terminal nor retriable, and rejects `terminal_classification != expected_terminal_classification`. The constructed `GitHubMockReplayEvidence` carries hardcoded `external_call_made=false`/`external_side_effect_made=false`/`github_mutation_made=false`/`live_external_action=false`/`no_raw_secret_observed=true`, deterministic sorted-key canonical JSON (excluding `evidence_sha256` and `canonical_json` fields by construction), and `evidence_sha256` over the canonical JSON.
- `enforce_clone_readonly_gate(requested_mode, gate_approved)` rejects `CloneReadonly` mode without external approval with `GITHUB_LIVE_ACTION_BLOCKED`. `enforce_privacy_naming_safety(request)` delegates to the M7 `evaluate_privacy_naming` deterministic function and surfaces any `Block` decision as `MockFixtureError::new(code, reason)` (typically `GITHUB_PRIVACY_POLICY_VIOLATION` with redacted reason). `scan_evidence_for_raw_secrets(evidence, denylist)` walks every text-bearing evidence field (scenario_id, operation_class, request_id, source_repo_url_hash, canonical_json, evidence_sha256, source_ref, source_commit_sha, credential_ref_id, credential_fingerprint_hint, response_hashes, audit_event_ids) and rejects any leakage with `GITHUB_RAW_SECRET_REJECTED`.

## 3. RED to GREEN evidence

### M7-MOCKHTTP-T1 mock-http fixture type contract

```text
RED command:    cargo test -p eduops_git --test m7_mock_http_fixture_contract -- --nocapture
RED result:     unresolved GitHubMockScenario / GitHubMockResponse / GitHubRetryPolicy / GitHubMockOperation / GitHubMockRequestMethod / GitHubMockEndpointClass / GitHubMockTerminalClassification / GitHubRetryPolicyJitter / MockFixtureError imports
GREEN command:  cargo test -p eduops_git --test m7_mock_http_fixture_contract -- --nocapture
GREEN result:   21 passed; 0 failed
Commit:         74c1d2b
```

### M7-MOCKHTTP-T2 deterministic retry/backoff replay

```text
RED command:    cargo test -p eduops_git --test m7_mock_http_retry_contract -- --nocapture
RED result:     unresolved GitHubMockReplayEvidence / replay_mock_http imports
GREEN command:  cargo test -p eduops_git --test m7_mock_http_retry_contract -- --nocapture
GREEN result:   15 passed; 0 failed
Commit:         c8d60bf
```

### M7-MOCKHTTP-T3 fail-closed safety guards

```text
RED command:    cargo test -p eduops_git --test m7_mock_http_safety_contract -- --nocapture
RED result:     unresolved enforce_clone_readonly_gate / enforce_privacy_naming_safety / scan_evidence_for_raw_secrets imports
GREEN command:  cargo test -p eduops_git --test m7_mock_http_safety_contract -- --nocapture
GREEN result:   12 passed; 0 failed
Commit:         17bf805
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> M7-MOCKHTTP-T1 21 passed; M7-MOCKHTTP-T2 15 passed; M7-MOCKHTTP-T3 12 passed; plus existing M0..M8 totals all green
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Successful metadata/clone-ref fixture produces deterministic clone-only evidence with no external call and no mutation | `m7_mock_http_retry_contract::replay_success_on_first_attempt_records_no_retries_or_delays`, `m7_mock_http_retry_contract::replay_evidence_is_deterministic_across_repeated_calls` | accepted |
| Rate-limit and outage fixtures produce bounded deterministic retry schedules without sleeps | `m7_mock_http_retry_contract::replay_rate_limited_then_success_records_bounded_deterministic_delay`, `replay_caps_delay_at_max_delay_ms`, `replay_records_outage_terminal_when_retries_exhausted` | accepted |
| `retry_after_ms` overrides the computed delay only when lower than `max_delay_ms` | `m7_mock_http_retry_contract::replay_uses_retry_after_ms_when_lower_than_max_delay`, `replay_ignores_retry_after_ms_when_not_lower_than_max_delay` | accepted |
| Auth-required and scope-denied fixtures fail closed and do not prompt for or expose raw credentials | `m7_mock_http_retry_contract::replay_terminates_on_auth_required`, `replay_terminates_on_scope_denied`; `m7_mock_http_safety_contract::scan_evidence_for_raw_secrets_*` | accepted |
| Write methods and non-clone operations are blocked before replay | `m7_mock_http_fixture_contract::response_rejects_write_method`, `scenario_rejects_unknown_operation_token`, `m7_mock_http_safety_contract::replay_already_rejects_write_method_at_construction` | accepted |
| Clone-readonly mode remains blocked without a separate approval boundary | `m7_mock_http_safety_contract::enforce_clone_readonly_gate_blocks_when_clone_readonly_requested_without_approval`, `enforce_clone_readonly_gate_allows_clone_readonly_when_approved` | accepted |
| Privacy-naming failures block before replay | `m7_mock_http_safety_contract::enforce_privacy_naming_safety_blocks_pii_candidate`, `enforce_privacy_naming_safety_blocks_email_like_candidate`, `enforce_privacy_naming_safety_accepts_pseudonymous_candidate` | accepted |
| Raw credential-shaped strings in scenario fields, response previews, diagnostics, or evidence are rejected | `m7_mock_http_fixture_contract::scenario_rejects_raw_credential_in_text_fields`, `response_rejects_raw_credential_in_redacted_preview`; `m7_mock_http_safety_contract::scan_evidence_for_raw_secrets_rejects_pat_prefix_in_canonical_json`, `scan_evidence_for_raw_secrets_rejects_denylist_match_in_audit_id`, `scan_evidence_for_raw_secrets_rejects_url_credential_in_response_hash` | accepted |
| Canonical evidence serialization is deterministic across repeated construction | `m7_mock_http_retry_contract::replay_evidence_is_deterministic_across_repeated_calls`, `replay_evidence_sha256_excludes_self_field` | accepted |
| Hardcoded non-mutation safety flags appear in both struct and canonical JSON | `m7_mock_http_retry_contract::replay_success_on_first_attempt_records_no_retries_or_delays` (asserts `external_call_made=false`/`external_side_effect_made=false`/`github_mutation_made=false`/`live_external_action=false`/`no_raw_secret_observed=true`) | accepted |

## 6. Non-claims

This evidence summary does not claim:

- live GitHub readiness, real network round-trip, real authentication handshake, or real GitHub API call;
- a clone-readonly approval mechanism — `enforce_clone_readonly_gate` is a refusal helper, not an approval helper, and the `clone_readonly_gate_approved` boolean is a *test input*, not a Ralph-authored approval;
- production retry/rate-limit/backoff tuning — the spec §4.3 formula and bounded `1..=5` `max_attempts` cap are fixture-only and do not authorize live retry behavior;
- credential lookup, raw token retrieval, credential rotation, or any credential persistence beyond `credential_ref_id` and `credential_fingerprint_hint` references in scenario records;
- repository creation, push, branch/tag/ref creation, pull request, issue, webhook, status, check-run, invitation, branch protection, GitHub administration, or any GitHub state mutation;
- submission-state or provisioning-state promotion from mock replay evidence;
- a cryptographic source-URL audit hash beyond the existing FNV-1a 64 envelope (M7 SLICE-F evidence);
- instructor approval surface, evaluator integration, or live observability ingestion;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain prerequisites for broader GitHub-related milestones:

1. an authorized human owner must accept a clone-readonly integration-point specification (allowlist policy, approval workflow, credential-reference acquisition, scope-grant lifecycle, audit linkage) before any executable real-network row is queued under Ralph;
2. integrate `replay_mock_http` and the safety guards with a clone planner so that clone plans are constructed only after a passing privacy-naming decision and a passing `enforce_clone_readonly_gate` decision;
3. extend the response-classification fallback table once the live network connector is authorized so that real HTTP status codes map to the same `GitHubMockTerminalClassification` enum values consistently;
4. extend `GitHubRetryPolicyJitter` beyond `None` only when an authorized human owner accepts a live retry tuning decision;
5. proceed to M8 export real-writer scope only after the human-authored extended exporter implementation specification (writer profile registry decisions, fidelity threshold authority, host-tool execution authority, privacy/legal policy authority, DEMO-1 acceptance authority) is authored and accepted (per `EDUOPS-M8-EXPORT-SPEC-BLOCKER` §5).

## 8. Traceability

- [GitHub mock-http fixture format specification](../02-design-planning/github-mock-http-fixture-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub adapter software design description](../02-design-planning/github-adapter-software-design-description.md)
- [Software test description](../03-verification-validation/software-test-description.md) — STD-087, STD-090, STD-091
- [Implementation milestones](implementation-milestones.md)
- [M7 SLICE-F GitHub clone-only adapter gate evidence](m7-slice-f-github-clone-only-evidence.md)
- [M8 SLICE-G constrained export fixture gate evidence](m8-slice-g-export-fixture-evidence.md)
