---
title: GitHub Mock-HTTP Fixture Format Specification
document_id: SWENG-EDUTECH-GITHUB-MOCK-HTTP-FIXTURE-SPEC
version: 0.1.0
status: accepted-constrained-for-fixture-implementation
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SDD
  requirements:
    - EDUOPS-FR-080
    - EDUOPS-FR-081
    - EDUOPS-FR-082
    - EDUOPS-FR-083
    - EDUOPS-FR-084
    - EDUOPS-NFR-034
    - EDUOPS-NFR-035
    - EDUOPS-NFR-036
  verification:
    - STD-087
    - STD-088
    - STD-089
    - STD-090
    - STD-091
---

# GitHub Mock-HTTP Fixture Format Specification

## 1. Purpose

This specification authorizes a constrained M7 follow-up slice for the `eduops_git` crate. The slice defines a fixture-local mock HTTP replay format, deterministic retry/backoff policy, clone/read metadata response envelope, rate-limit/error fixtures, and no-secret evidence for GitHub clone-only behavior.

The approved path is intentionally local and deterministic:

```text
mock fixture scenario
→ mock request sequence
→ deterministic retry/backoff classification
→ normalized clone-only evidence
→ no external network, no GitHub mutation, no credential lookup
```

## 2. Scope decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-M7-MOCK-HTTP-FIXTURE-SPEC` |
| Authorized scope | Fixture-local mock HTTP replay format and deterministic retry/backoff evidence |
| Adapter mode | `mock-http` only |
| Network boundary | No real network; fixtures represent response envelopes as data |
| Credential boundary | Credential reference identifiers and fingerprint hints only; no raw token lookup |
| External action | Not allowed |
| GitHub mutation | Not allowed |
| Live clone-readonly | Not authorized by this specification |
| Retry policy authority | Granted only for deterministic fixture replay classification, not for live connector behavior |

## 3. Non-claims

This specification does not approve or implement:

- live GitHub API calls;
- real `git clone`, `git fetch`, or remote network access;
- clone-readonly gate approval mechanics;
- raw credential lookup, token refresh, credential rotation, or credential storage changes;
- repository creation, push, branch/tag creation, pull request, issue, webhook, status, check-run, invitation, branch protection, or GitHub administration;
- production retry/backoff tuning for live systems;
- submission-state or provisioning-state promotion from clone evidence.

## 4. Fixture file model

A mock HTTP fixture is a local JSON-compatible record. It may be encoded as Rust fixtures or JSON files, but canonical evidence shall use sorted-key JSON.

### 4.1 `GitHubMockScenario`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `scenario_id` | string | yes | Stable fixture identifier. |
| `adapter_mode` | enum | yes | Must be `mock-http`. |
| `operation` | enum | yes | `validate_clone_configuration`, `plan_clone`, `clone_repository_read_only`, or `query_clone_evidence`. |
| `request_id` | string | yes | Stable request identifier. |
| `source_repo_url_hash` | hex string | yes | Hash only; no raw private repository URL in evidence. |
| `source_ref` | string | no | Branch/tag/SHA fixture ref. |
| `credential_ref_id` | string | no | Credential reference only; raw token forbidden. |
| `credential_fingerprint_hint` | string | no | Redacted fingerprint hint only. |
| `responses` | array[`GitHubMockResponse`] | yes | Ordered response envelopes. |
| `retry_policy` | `GitHubRetryPolicy` | yes | Deterministic bounded policy. |
| `expected_terminal_classification` | enum | yes | Expected final error/success class. |
| `external_call_made` | bool | yes | Must be `false`; replayed responses are fixture data. |
| `github_mutation_made` | bool | yes | Must be `false`. |
| `live_external_action` | bool | yes | Must be `false`. |

The scenario is invalid if any text field contains a raw credential-like value, if `adapter_mode` is not `mock-http`, or if any side-effect flag is `true`.

### 4.2 `GitHubMockResponse`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `step_index` | integer | yes | Zero-based response order. |
| `request_method` | enum | yes | `GET`, `HEAD`, or `LOCAL_FIXTURE`. No write methods are allowed. |
| `endpoint_class` | enum | yes | `repo_metadata`, `clone_ref`, `rate_limit`, `credential_probe`, or `local_fixture`. |
| `http_status` | integer | yes | Fixture status code. |
| `github_error_code` | enum/string | no | Normalized fixture error token. |
| `response_body_hash` | hex string | yes | SHA-256 over redacted response body fixture. |
| `rate_limit_remaining` | integer | no | Non-negative if present. |
| `retry_after_ms` | integer | no | Non-negative if present. |
| `source_commit_sha` | string | no | Fixture commit SHA when available. |
| `redacted_body_preview` | string | no | No credentials, no raw private URL, no PII. |

Allowed `request_method` values exclude `POST`, `PUT`, `PATCH`, and `DELETE`. If a write method appears, the scenario fails before replay with `GITHUB_NON_CLONE_OPERATION_BLOCKED`.

### 4.3 `GitHubRetryPolicy`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `policy_id` | string | yes | Example: `mock-http-bounded-v1`. |
| `max_attempts` | integer | yes | Range `1..=5`; recommended default `3`. |
| `base_delay_ms` | integer | yes | Deterministic base delay; no sleeping required in tests. |
| `multiplier_numerator` | integer | yes | Positive integer. |
| `multiplier_denominator` | integer | yes | Positive integer. |
| `max_delay_ms` | integer | yes | Upper bound. |
| `jitter` | enum | yes | Must be `none` in fixture tests. |
| `terminal_error_classes` | array | yes | Includes auth/scope/privacy/non-clone/live-blocked. |
| `retriable_error_classes` | array | yes | Includes rate-limited, outage, timeout. |

The retry schedule is computed without wall-clock sleeps. Attempt `n` delay is:

```text
min(max_delay_ms, base_delay_ms * multiplier_numerator^(n-1) / multiplier_denominator^(n-1))
```

`retry_after_ms` from the fixture response may override the computed delay only when it is lower than `max_delay_ms`; the selected delay is recorded as evidence. This rule is deterministic and fixture-local only.

## 5. Error classification

| Fixture condition | Classification | Retry? | Required evidence |
|---|---|---:|---|
| `200`, `304` metadata or clone-ref response | `GITHUB_MOCK_SUCCESS` | no | source ref/SHA, response hash, retry count. |
| `401` missing/expired credential ref | `GITHUB_AUTH_REQUIRED` | no | credential ref only; no token prompt. |
| `403` scope denial | `GITHUB_SCOPE_DENIED` | no | no mutation, no credential contents. |
| `403` rate-limit headers or normalized rate-limit body | `GITHUB_RATE_LIMITED` | yes | rate-limit remaining, selected delay, retry count. |
| timeout/outage fixture | `GITHUB_OUTAGE_OR_TIMEOUT` | yes | no clone verified, state remains planned/attempted. |
| privacy-naming rejection | `GITHUB_PRIVACY_POLICY_VIOLATION` | no | redacted reason codes. |
| write method or non-clone operation | `GITHUB_NON_CLONE_OPERATION_BLOCKED` | no | fails before replay. |
| clone-readonly requested without gate | `GITHUB_LIVE_ACTION_BLOCKED` | no | no external request. |
| raw credential observed in fixture/evidence | `GITHUB_RAW_SECRET_REJECTED` | no | field name and redacted reason only. |

## 6. Evidence envelope

`GitHubMockReplayEvidence` shall include:

| Field | Rule |
|---|---|
| `scenario_id` | Mirrors scenario. |
| `adapter_mode` | `mock-http`. |
| `operation_class` | `clone-only`. |
| `request_id` | Mirrors scenario. |
| `source_repo_url_hash` | Hash only. |
| `source_ref` / `source_commit_sha` | Fixture values when available. |
| `attempt_count` | Number of consumed fixture responses. |
| `retry_count` | `attempt_count - 1` for retried responses. |
| `selected_backoff_schedule_ms` | Deterministic selected delays. |
| `terminal_classification` | Final classification. |
| `rate_limit_remaining` | Final response metadata when present. |
| `credential_ref_id` | Reference only. |
| `credential_fingerprint_hint` | Redacted hint only. |
| `response_hashes` | Ordered response body hashes. |
| `audit_event_ids` | Deterministic fixture audit identifiers. |
| `external_call_made` | Must be `false`. |
| `external_side_effect_made` | Must be `false`. |
| `github_mutation_made` | Must be `false`. |
| `live_external_action` | Must be `false`. |
| `no_raw_secret_observed` | Must be `true` unless replay is rejected. |
| `evidence_sha256` | SHA-256 over canonical evidence excluding this field. |

The evidence envelope is not submission confirmation, provisioning confirmation, or live clone verification.

## 7. Fixture acceptance rules

The constrained M7 mock-http tests shall verify:

1. a successful metadata/clone-ref fixture produces deterministic clone-only evidence with no external call and no mutation;
2. rate-limit and outage fixtures produce bounded deterministic retry schedules without sleeps;
3. auth-required and scope-denied fixtures fail closed and do not prompt for or expose raw credentials;
4. write methods and non-clone operations are blocked before replay;
5. clone-readonly mode remains blocked without a separate approval boundary;
6. privacy-naming failures block before replay;
7. raw credential-shaped strings in scenario fields, response previews, diagnostics, or evidence are rejected;
8. canonical evidence serialization is deterministic across repeated construction.

## 8. Ralph task queue seed

After this specification is accepted, Ralph may create the following executable rows:

| Task | Purpose | First RED command |
|---|---|---|
| `M7-MOCKHTTP-PREP` | Re-evaluate M7 under this constrained mock-http fixture specification and create RED/GREEN rows. | docs/control validation |
| `M7-MOCKHTTP-T1` | Define mock scenario/response/retry-policy/evidence type contracts and validation. | `cargo test -p eduops_git --test m7_mock_http_fixture_contract -- --nocapture` |
| `M7-MOCKHTTP-T2` | Implement deterministic retry/backoff replay and terminal/retriable classification. | `cargo test -p eduops_git --test m7_mock_http_retry_contract -- --nocapture` |
| `M7-MOCKHTTP-T3` | Add no-live/no-mutation/no-secret safety guards and clone-readonly gate denial. | `cargo test -p eduops_git --test m7_mock_http_safety_contract -- --nocapture` |
| `M7-MOCKHTTP-GATE` | Record constrained mock-http evidence and non-claims. | focused GitHub mock-http tests plus repository validation |

## 9. Gate evidence non-claims

An accepted constrained M7 mock-http gate may claim only:

```text
fixture-local mock HTTP replay format
deterministic retry/backoff evidence
clone-only response normalization
rate-limit/auth/scope/timeout fixture classification
no-live/no-mutation/no-secret safety guards
```

It shall not claim live GitHub readiness, clone-readonly approval, credential lookup, real network behavior, production retry tuning, or submission/provisioning state promotion.
