---
title: GitHub Adapter Software Design Description
document_id: SWENG-EDUTECH-GITHUB-ADAPTER-SDD
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  requirements: ['EDUOPS-FR-080', 'EDUOPS-FR-081', 'EDUOPS-FR-082', 'EDUOPS-FR-083', 'EDUOPS-FR-084', 'EDUOPS-NFR-034', 'EDUOPS-NFR-035', 'EDUOPS-NFR-036']
  parent: 'SWENG-EDUTECH-SDD'
  related: ['SWENG-EDUTECH-GITHUB-ADAPTER-SPEC', 'SWENG-EDUTECH-IDD', 'SWENG-EDUTECH-STD']
---

# GitHub Adapter Software Design Description

## 1. Purpose

Define the detailed software design for the EduOps GitHub adapter under the clarified **clone-only baseline**. The adapter treats GitHub as a read-only repository source. It does not create, push, invite, protect, webhook, check-run, archive, or administer GitHub resources.

## 2. Design scope and non-scope

| Category | Scope |
|---|---|
| In scope | Adapter mode controller, clone planner, fake-local implementation, mock-http clone implementation, credential-reference boundary, clone-source privacy validation, rate-limit/outage handling, clone evidence normalization, and audit binding. |
| Deferred | Real private-repository clone credential mechanism, approved clone-readonly connector, and self-hosted Git clone-source profile. |
| Explicitly excluded | UI-direct GitHub calls, raw token propagation, repository creation, push, collaborator invitation, branch protection mutation, webhook/check-run writes, GitHub org administration, and treating clone evidence as submission/provisioning confirmation. |

## 3. Component decomposition

```text
Application Core / Local Backend
  -> GitHub Clone Adapter Facade
      -> Mode Gate
      -> Clone Planner
      -> Clone Source Privacy Policy
      -> Credential Reference Resolver
      -> Fake-Local Clone Backend
      -> Mock-HTTP Clone Backend
      -> Clone-Readonly Backend Slot
      -> Retry and Rate-Limit Controller
      -> Clone Evidence Normalizer
      -> Audit Binder
  -> State Machine Service
  -> Credential Service
  -> Configuration Service
  -> Audit/Evidence Service
```

| Component | Responsibility | Must not own |
|---|---|---|
| GitHub Clone Adapter Facade | Provides stable clone-only interface used by application core use cases. | Product authorization, final workflow state promotion, raw credentials, GitHub mutation. |
| Mode Gate | Validates `fake-local`, `mock-http`, and `clone-readonly` eligibility. | User-facing policy exceptions not approved by core. |
| Clone Planner | Converts source repository inputs into a clone plan and side-effect class. | Repository provisioning, branch policy, push, or write planning. |
| Clone Source Privacy Policy | Validates repository URL aliases, evidence labels, and local path names. | Roster identity truth or pseudonym mapping ownership. |
| Credential Reference Resolver | Requests credential status/fingerprint hints from credential service. | Raw token storage or raw secret logging. |
| Fake-Local Clone Backend | Simulates clone results with zero network calls. | Network I/O. |
| Mock-HTTP Clone Backend | Talks only to local mock server fixtures for clone contract tests. | Live GitHub calls. |
| Clone-Readonly Backend Slot | Reserved implementation for approved read-only clone. | Mutation, push, collaborator, branch-protection, or webhook/check writes. |
| Retry and Rate-Limit Controller | Applies deterministic retry/backoff and terminal/retriable classification. | Infinite retry or workflow state promotion. |
| Clone Evidence Normalizer | Converts backend-specific responses into EduOps clone evidence records. | Final audit persistence without core validation. |
| Audit Binder | Prepares no-secret audit payloads and links request/result identifiers. | Writing unredacted token or credential material. |

## 4. Adapter mode state machine

```text
fake-local
  -> mock-http        # local mock-server clone tests only
  -> clone-readonly   # future approved GitHub clone/fetch only
```

| Transition | Required gate | Denial behavior |
|---|---|---|
| `fake-local -> mock-http` | Local mock server fixture profile and no external network assertion. | `GITHUB_LIVE_ACTION_BLOCKED` if target is not local mock endpoint. |
| `mock-http -> clone-readonly` | Read-only clone approval, target repository allowlist, credential reference valid when needed, and no-mutation assertion. | Gate-denial audit event; no external request. |
| any mode -> mutation | Not supported in current baseline. | `GITHUB_NON_CLONE_OPERATION_BLOCKED`; no external request. |

## 5. Core operation design

| Operation | Design owner | Preconditions | State/evidence output |
|---|---|---|---|
| `github.validateCloneConfiguration` | Clone Adapter Facade + Mode Gate | Config schema valid; repository URL/ref allowlist checked; credential reference optional in fake-local. | Clone capability set, validation issues, no-secret evidence. |
| `github.planClone` | Clone Planner + Privacy Policy | Course/assignment/source inputs validated; privacy aliases applied. | Clone plan with source URL hash, target local path, expected ref/SHA, warnings. |
| `github.cloneRepositoryReadOnly` | Mode Gate + Clone Backend Slot | Approved clone plan, idempotency key, no-mutation assertion. | Local clone path, source ref/SHA, manifest hash, `github_mutation_made=false`. |
| `github.queryCloneEvidence` | Clone Evidence Normalizer | Local clone path and expected ref/SHA exist. | Normalized clone evidence and rate-limit metadata when applicable. |

## 6. Data structures

### 6.1 Clone adapter request

```ts
interface GitHubCloneRequest<T> {
  request_id: string;
  correlation_id: string;
  actor: EduOpsActor;
  adapter_mode: 'fake-local' | 'mock-http' | 'clone-readonly';
  operation: 'github.validateCloneConfiguration' | 'github.planClone' | 'github.cloneRepositoryReadOnly' | 'github.queryCloneEvidence';
  idempotency_key: string;
  credential_ref_id?: string;
  gate_approval_ref?: string;
  source_repo_url_hash: string;
  source_ref?: string;
  expected_commit_sha?: string;
  target_local_path?: string;
  payload: T;
}
```

### 6.2 Clone adapter result

```ts
interface GitHubCloneResult<T> {
  adapter_mode: string;
  operation_class: 'clone-only';
  external_call_made: boolean;
  external_side_effect_made: false;
  github_mutation_made: false;
  credential_ref_id?: string;
  credential_fingerprint_hint?: string;
  request_id: string;
  provider_request_id?: string;
  source_repo_url_hash: string;
  source_ref?: string;
  source_commit_sha?: string;
  rate_limit_remaining?: number;
  retry_count: number;
  idempotency_key: string;
  audit_event_ids: string[];
  redaction_profile: string;
  no_raw_secret_observed: true;
  data?: T;
  error?: GitHubCloneAdapterError;
}
```

## 7. Clone evidence boundary

The application core owns assignment, workspace, submission, and provisioning state. The GitHub clone adapter reports clone-source evidence only.

| Current state | Clone adapter evidence | Core transition allowed |
|---|---|---|
| `ClonePlanned` | fake-local planned source and target only | remains local planned evidence |
| `ClonePlanned` | mock-http accepted clone response | test-only clone evidence, not production confirmation |
| `CloneAttempted` | approved clone-readonly source SHA/ref and local manifest | `CloneVerified` only after core validates scope, source allowlist, and audit record |
| Any | timeout/outage/rate-limit | no verification; state remains planned/attempted with retry metadata |

## 8. Clone source privacy design

GitHub-visible and evidence-visible clone source names shall use controlled repository aliases and URL hashes.

| Visible object | Required source | Forbidden |
|---|---|---|
| Source repository alias | course/assignment pseudonym and controlled version label | raw student ID, email, phone, grade, private roster field |
| Local target path | assignment instance ID or pseudonymous source key | student name, raw roster number, credential hint |
| Clone evidence label | stable EduOps clone operation label | private feedback text or raw credential hint |

A violation returns `GITHUB_PRIVACY_POLICY_VIOLATION` and no external request is made.

## 9. Retry, outage, and rate-limit design

| Condition | Behavior |
|---|---|
| Authentication missing/expired | Fail closed as `GITHUB_AUTH_REQUIRED`; do not request raw token from UI or worker. |
| Scope denied | Return `GITHUB_SCOPE_DENIED`; no mutation is possible. |
| Primary/secondary rate limit | Classify as `GITHUB_RATE_LIMITED`; record retry-after if available; preserve planned clone state. |
| Timeout/outage | Classify as `GITHUB_OUTAGE_OR_TIMEOUT`; no clone verification; persist retry metadata. |
| Privacy violation | Classify as terminal; no external call. |
| Non-clone operation requested | Classify as `GITHUB_NON_CLONE_OPERATION_BLOCKED`; no external call. |
| Gate denial | Classify as terminal for that command; write gate-denial audit event. |

Retry policy is deterministic and bounded. It is configured through controlled configuration keys and tested by mock-http fixtures. The constrained fixture format, retry schedule, classification rules, and non-claims are defined in [GitHub mock-HTTP fixture format specification](github-mock-http-fixture-specification.md).

## 10. Security and audit design

1. Raw credentials do not enter adapter request/result payloads.
2. Credential fingerprints are hints only and are redacted according to diagnostics policy.
3. Result envelopes record whether external call occurred and always record `github_mutation_made=false`.
4. Clone-readonly carries idempotency key, source allowlist reference, actor/scope/reason, and gate approval reference.
5. Audit events distinguish validation, planning, clone-denied, clone-attempted, clone-verified, and non-clone-operation-denied facts.
6. Diagnostic packages include redacted request/result summaries and no raw token material.

## 11. Module placement

| Future module path | Responsibility |
|---|---|
| `crates/eduops_git/src/github/mod.rs` | Clone adapter facade and shared traits. |
| `crates/eduops_git/src/github/mode_gate.rs` | Adapter mode and gate validation. |
| `crates/eduops_git/src/github/clone_planner.rs` | Clone plan generation. |
| `crates/eduops_git/src/github/privacy_naming.rs` | Clone source alias/evidence privacy policy. |
| `crates/eduops_git/src/github/fake_local.rs` | Zero-network fake clone implementation. |
| `crates/eduops_git/src/github/mock_http.rs` | Local mock clone implementation. |
| `crates/eduops_git/src/github/retry.rs` | Retry/rate-limit controller. |
| `crates/eduops_git/src/github/evidence.rs` | Clone response normalization and evidence binding. |
| `tests/contract/github_adapter/` | `GH-FIX-*` clone contract fixtures. |
| `fixtures/github/` | Privacy-safe fake/mock clone input and expected-output records. |

## 12. Implementation slices

| Slice | Allowed implementation | Required gate |
|---|---|---|
| GH-SLICE-0 | Schema/types and fake-local clone no-network tests. | `GH-FIX-001`, `STD-086` |
| GH-SLICE-1 | Mock-http clone success/error/rate-limit/timeout tests. | `GH-FIX-002`, `STD-087` |
| GH-SLICE-2 | Clone source privacy and credential non-leak tests. | `GH-FIX-003`, `GH-FIX-004`, `STD-088`, `STD-089` |
| GH-SLICE-3 | Clone-state evidence and non-clone-operation denial tests. | `GH-FIX-005`, `GH-FIX-006`, `STD-090`, `STD-091` |
| GH-SLICE-4 | Approved clone-readonly evidence profile. | Separate approval required |

## 13. SRS-to-design traceability

| SRS ID | Design decision | Detailed sections | Test anchors |
|---|---|---|---|
| EDUOPS-FR-080 | Mode-gated clone-source adapter boundary with fake-local default. | §3, §4, §11, §12 | STD-086, STD-091, STD-SRS-FR-080 |
| EDUOPS-FR-081 | Required operations are clone-only: validate, plan, clone/fetch read-only, and query evidence. | §5, §6, §11 | STD-087, STD-SRS-FR-081 |
| EDUOPS-FR-082 | Credential reference only; no raw tokens in adapter-visible artifacts. | §4, §6, §10 | STD-089, STD-SRS-FR-082 |
| EDUOPS-FR-083 | Adapter provides clone evidence; application core owns workflow state transitions. | §7 | STD-090, STD-SRS-FR-083 |
| EDUOPS-FR-084 | Non-clone GitHub operations are blocked in the current baseline. | §2, §4, §5, §10, §12 | STD-091, STD-SRS-FR-084 |
| EDUOPS-NFR-034 | Fake-local/mock-http clone fixtures precede clone-readonly behavior. | §4, §12 | STD-086, STD-087, STD-SRS-NFR-034 |
| EDUOPS-NFR-035 | Clone source privacy policy blocks visible PII before external call planning. | §8 | STD-088, STD-SRS-NFR-035 |
| EDUOPS-NFR-036 | Error taxonomy and retry policy are deterministic and bounded for clone-only operations. | §9 | STD-087, STD-SRS-NFR-036 |

## 14. Open design items

| Item | Status | Resolution path |
|---|---|---|
| Private repository clone auth mechanism | Open | Compare GitHub App installation token, OAuth device flow, PAT fallback, and SSH deploy key for clone-readonly only. |
| Mock server implementation | Open | Select lightweight local fixture server during GH-SLICE-1 planning. |
| Rate-limit backoff constants | Open | Define in configuration profile before GH-SLICE-1 GREEN evidence. |
| Clone source allowlist ownership | Open | Requires explicit approval record before GH-SLICE-4. |
