---
title: GitHub Clone-Readonly Integration-Point Boundary Specification
document_id: SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
version: 0.1.0
status: accepted-constrained-for-fixture-implementation
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SDD
    - SWENG-EDUTECH-GITHUB-MOCK-HTTP-FIXTURE-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-CREDENTIAL-STORAGE
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
    - STD-086
    - STD-088
    - STD-089
    - STD-090
    - STD-091
---

# GitHub Clone-Readonly Integration-Point Boundary Specification

## 1. Purpose

This specification authorizes a constrained follow-up slice for the `eduops_git` crate that defines the **local fixture-only** HOW-level contract required before any live `clone-readonly` execution may be considered under a separate user-executed approval.

It closes the M7 SLICE-F evidence §7 follow-up item that calls for "a clone-readonly integration-point specification covering allowlist policy, approval workflow, credential-reference acquisition, scope-grant lifecycle, and audit linkage". It does so without authorizing a live GitHub call, real network round-trip, credential lookup, real clone/fetch, push, mutation, or production retry tuning.

The authorized boundary is:

```text
allowlist record
  -> clone-readonly gate approval envelope
    -> credential-reference status contract
      -> privacy-naming pre-check
        -> dry-run clone plan envelope
          -> fixture-only safety guards
            -> user-executed live-run runbook boundary
```

Each step is a deterministic in-process data transform. No step performs network I/O, real Git invocation, or raw credential resolution.

## 2. Scope decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-M7-CLONE-READONLY-INTEGRATION-POINT-SPEC` |
| Authorized scope | Fixture-local allowlist, gate approval envelope, credential-reference status contract, dry-run clone-plan envelope, and fail-closed safety guards |
| Adapter mode | `clone-readonly` mode mechanics defined for local planning and `mock-http`/`fake-local` test wiring only |
| Network boundary | No real network; approval envelope and dry-run plan are pure data records |
| Credential boundary | Credential reference identifiers, fingerprint hints, and presence/expiry status only; no raw token lookup |
| External action | Not allowed |
| GitHub mutation | Not allowed |
| Live clone-readonly execution | Not authorized by this specification |
| Live retry/backoff tuning | Not authorized; deterministic fixture replay only |
| Submission/provisioning promotion | Not granted |

The specification authorizes only local fixture-only mechanics. A live `clone-readonly` execution requires a separately user-executed approval recorded in a runbook (see §10) and is not in scope of this document.

## 2.1 User-managed GitHub boundary and input modes

`EDUOPS-DEC-065` narrows future live-operation responsibility. Live GitHub account setup, credential handling, remote configuration, repository creation/administration, and any externally consequential Git command remain outside EduOps automation and are handled by the user/operator.

EduOps supports two bounded clone input modes after that boundary:

1. **Professor/course-owner CSV mode.** A professor or authorized course owner supplies a controlled CSV containing roster identity fields and a GitHub repository URL field for each student/team repository. EduOps may parse this CSV, validate privacy/naming constraints, map rows to roster/workspace records, and clone the listed repositories only through the clone-only adapter path after the required approval/runbook gate. Persistent evidence must redact or hash repository URLs unless the runbook explicitly preserves a sanitized excerpt.
2. **Student local-checkout mode.** A student clones their own GitHub repository before launching EduOps. EduOps runs from the supplied local checkout path and treats the Git remote as pre-existing user-managed context. EduOps must not configure the student's remote, resolve credentials, or perform account-level GitHub actions for the student.

These modes replace any assumption that EduOps should own live GitHub credentials, remotes, repository setup, or student-account clone authority.

## 3. Non-claims

This specification does not approve or implement:

- EduOps-managed live GitHub API calls, credential lookup, remote setup, repository administration, or real `git clone`/`git fetch` against a remote outside a user-executed boundary;
- the human approval workflow itself (this document defines only the *shape* of the approval evidence that a future runbook produces);
- credential issuance, token refresh, credential rotation, or credential storage changes;
- raw token lookup, retrieval, decryption, or transmission of any kind;
- repository creation, push, branch/tag creation, pull request, issue, webhook, status, check-run, invitation, branch protection, or any GitHub administration;
- production retry/backoff tuning, rate-limit policy authority, or live retry jitter;
- submission/provisioning state promotion from clone-readonly evidence;
- instructor approval surface UX or evaluator integration;
- a cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope already shipped in `GitHubCloneEvidence`;
- DEMO-1 acceptance or working-demonstration approval.

A separate human-authored decision is required before any of the above may be authorized.

## 4. Integration-point model

A clone-readonly integration point is a local JSON-compatible record graph. It may be encoded as Rust types or JSON fixtures, but canonical evidence shall use sorted-key JSON.

### 4.1 `CloneReadonlyAllowlistEntry`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `allowlist_entry_id` | string | yes | Stable fixture identifier. |
| `source_repo_url_hash` | hex string | yes | FNV-1a 64 hash matching `GitHubCloneEvidence::source_repo_url_hash`; no raw URL stored. |
| `allowed_refs` | array[string] | yes | Branch/tag/SHA pattern tokens permitted for the entry. Empty array means "any ref". |
| `scope_owner` | string | yes | Course/section/assignment scope identifier; no raw student ID. |
| `scope_label` | string | yes | Pseudonymous controlled label (`[a-z0-9-_.]`); no raw PII. |
| `expires_at_utc` | string | yes | ISO 8601 UTC instant after which the entry must not be honored. |
| `requested_by_role` | enum | yes | `instructor`, `ta`, `course_admin`, or `platform_admin`. |
| `audit_event_id` | string | yes | Deterministic `audit_clone_readonly_allowlist_<allowlist_entry_id>`. |

The entry is invalid if `source_repo_url_hash` is not an FNV-1a 64 hex string, if `scope_label` contains a credential-shaped value or a denylist match, if `expires_at_utc` is not a valid ISO 8601 UTC instant, or if `requested_by_role` is unknown.

### 4.2 `CloneReadonlyGateApproval`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `approval_ref` | string | yes | Stable approval identifier supplied by the human-executed runbook. |
| `approver_role` | enum | yes | `course_admin` or `platform_admin`. (`instructor`/`ta` cannot approve.) |
| `approved_source_repo_url_hash` | hex string | yes | Must equal the allowlist entry's `source_repo_url_hash`. |
| `approved_operation` | enum | yes | Must be `clone`. (`push`/`create-repo`/`delete-repo` are not approvable.) |
| `approved_at_utc` | string | yes | ISO 8601 UTC instant. |
| `expires_at_utc` | string | yes | ISO 8601 UTC instant after which the approval must not be honored. |
| `idempotency_key` | string | yes | Stable key linking the approval to a planned clone request. |
| `audit_event_id` | string | yes | Deterministic `audit_clone_readonly_approval_<approval_ref>`. |

The approval is invalid if `approver_role` is not in the allowed set, if `approved_operation` is not `clone`, if `expires_at_utc <= approved_at_utc`, or if any field contains a credential-shaped value.

### 4.3 `CloneReadonlyCredentialStatus`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `credential_ref_id` | string | no | Reference only; raw token forbidden. Omit when the source allowlist entry is public. |
| `credential_fingerprint_hint` | string | no | Redacted hint only; never the raw token bytes. |
| `scope_class` | enum | yes | `none`, `clone_public`, or `clone_private`. |
| `status` | enum | yes | `present`, `missing`, `expired`, or `revoked`. |
| `status_observed_at_utc` | string | yes | ISO 8601 UTC instant when the status was last observed. |

The status is invalid if `credential_ref_id` is set when `scope_class=none`, if `status` is `missing`/`expired`/`revoked` while `scope_class=clone_private` (the planner shall reject the dry-run with `GITHUB_AUTH_REQUIRED`), or if any field contains a credential-shaped value.

This record carries presence/expiry status only. No raw credential resolution is performed at this layer; the actual credential resolution remains the responsibility of the user-executed live-run runbook (§10).

### 4.4 `CloneReadonlyDryRunPlanRequest`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `plan_request_id` | string | yes | Stable fixture identifier. |
| `requested_mode` | enum | yes | Must be `clone-readonly` for this layer to fire; other modes route to the existing fake-local/mock-http path. |
| `requested_operation` | enum | yes | Must be `clone`. |
| `requested_source_repo_url_hash` | hex string | yes | Must match an active allowlist entry's hash. |
| `requested_ref` | string | yes | Branch/tag/SHA token; must match one of the allowlist entry's `allowed_refs` (or any when the entry's list is empty). |
| `target_local_path_template` | string | yes | Local path template referencing course/assignment scope only; no raw student ID or roster number. |
| `idempotency_key` | string | yes | Must equal the approval's `idempotency_key`. |
| `actor_role` | enum | yes | `instructor`, `ta`, `course_admin`, `platform_admin`, or `evaluator`. |
| `privacy_naming_candidates` | array[string] | no | Repository alias/branch/team/ref candidates that must pass `evaluate_privacy_naming` before plan assembly. |

### 4.5 `CloneReadonlyDryRunPlan`

The dry-run plan is the canonical output of the integration-point pipeline. It is a pure data record:

| Field | Rule |
|---|---|
| `plan_request_id` | Mirrors request. |
| `adapter_mode` | `clone-readonly`. |
| `operation_class` | `clone-only`. |
| `source_repo_url_hash` | Mirrors request and allowlist entry. |
| `planned_ref` | Mirrors request. |
| `expected_commit_sha` | Optional; fixture-supplied when known. |
| `target_local_path_template` | Mirrors request. |
| `idempotency_key` | Mirrors request and approval. |
| `actor_role` | Mirrors request. |
| `approval_ref` | Mirrors approval. |
| `approver_role` | Mirrors approval. |
| `allowlist_entry_id` | Mirrors allowlist entry. |
| `credential_ref_id` | Mirrors credential status (when present). |
| `credential_fingerprint_hint` | Mirrors credential status (when present). |
| `credential_scope_class` | Mirrors credential status. |
| `credential_status` | Mirrors credential status. |
| `privacy_decisions` | Ordered list of `evaluate_privacy_naming` decisions for the candidates. |
| `mode_decision` | The `evaluate_mode_gate` decision used at planning time. |
| `audit_event_ids` | Deterministic identifiers (`audit_clone_readonly_plan_<plan_request_id>`, plus mirrored allowlist/approval ids). |
| `external_call_made` | Must be hardcoded `false`. |
| `external_side_effect_made` | Must be hardcoded `false`. |
| `github_mutation_made` | Must be hardcoded `false`. |
| `live_external_action` | Must be hardcoded `false`. |
| `clone_readonly_executed` | Must be hardcoded `false`. |
| `no_raw_secret_observed` | Must be hardcoded `true` unless the pipeline rejects. |
| `canonical_json` | Sorted-key canonical JSON of the plan excluding `canonical_json`/`plan_sha256` fields. |
| `plan_sha256` | SHA-256 over `canonical_json`. |

The dry-run plan envelope is not submission confirmation, provisioning confirmation, clone verification, or live clone execution.

### 4.6 Decision pipeline

The integration point composes existing fixture functions in a deterministic order:

```text
evaluate_mode_gate(CloneReadonly, Clone, gate_approved)
  -> enforce_clone_readonly_gate(CloneReadonly, gate_approved)
    -> evaluate_clone_readonly_allowlist(request, allowlist)
      -> evaluate_clone_readonly_approval(request, allowlist, approval)
        -> evaluate_clone_readonly_credential_status(request, credential_status)
          -> evaluate_privacy_naming(each candidate)
            -> assemble_clone_readonly_dry_run_plan(...)
              -> scan_clone_readonly_evidence_for_raw_secrets(plan, denylist)
```

Each function is a pure deterministic transform. The pipeline halts at the first rejection. No step constructs a network connection, invokes Git, or resolves a raw credential.

## 5. Decision classifications

| Fixture condition | Classification | Pipeline halt | Required evidence |
|---|---|---:|---|
| `requested_mode != CloneReadonly` | `GITHUB_LIVE_ACTION_BLOCKED` (defensive) | yes | no plan produced; mode_decision recorded. |
| `gate_approved=false` | `GITHUB_LIVE_ACTION_BLOCKED` | yes | mode_decision Blocked; audit id. |
| `requested_operation != Clone` | `GITHUB_NON_CLONE_OPERATION_BLOCKED` | yes | mode_decision Blocked; audit id. |
| `requested_source_repo_url_hash` not in allowlist or expired | `GITHUB_CLONE_READONLY_ALLOWLIST_DENIED` | yes | no plan produced; allowlist decision recorded. |
| `requested_ref` not in allowlist's `allowed_refs` | `GITHUB_CLONE_READONLY_REF_DENIED` | yes | allowlist entry id and rejected ref token (redacted). |
| approval `idempotency_key != request.idempotency_key`, or `approval_ref` empty, or expired, or wrong approver role | `GITHUB_CLONE_READONLY_APPROVAL_DENIED` | yes | approval decision Blocked; no plan produced. |
| `credential_status` is `missing`/`expired`/`revoked` while `scope_class=clone_private` | `GITHUB_AUTH_REQUIRED` | yes | credential reference and status only; no raw token request. |
| `evaluate_privacy_naming` returns Block on any candidate | `GITHUB_PRIVACY_POLICY_VIOLATION` | yes | redacted block reason; no plan produced. |
| raw credential-shaped value detected in any record field | `GITHUB_RAW_SECRET_REJECTED` | yes | field name only; no plan produced. |
| all checks pass | `GITHUB_CLONE_READONLY_DRY_RUN_READY` | no | full dry-run plan with hardcoded non-mutation flags. |

`GITHUB_CLONE_READONLY_DRY_RUN_READY` does not authorize live execution. It indicates that an externally executed live-run runbook may proceed under separate human approval.

## 6. Evidence envelope rules

- The dry-run plan is the only canonical evidence produced at this layer.
- All non-mutation flags are hardcoded literals at the type and canonical JSON level, not computed values.
- `clone_readonly_executed=false` is hardcoded; this layer never represents a real execution.
- `canonical_json` excludes the `canonical_json` and `plan_sha256` keys by construction.
- `plan_sha256` is computed over `canonical_json`.
- Audit event ids are deterministic, fixture-only, and contain no raw credential or PII content.
- A future live-run runbook that consumes this evidence must produce a separate live-run evidence envelope with its own non-claims and audit trail; that envelope is not in scope of this specification.

## 7. Fixture acceptance rules

The constrained M7 clone-readonly integration-point tests shall verify:

1. `requested_mode != CloneReadonly` is rejected defensively with `GITHUB_LIVE_ACTION_BLOCKED` (mis-routed callers cannot bypass the gate by passing a non-clone-readonly mode);
2. `gate_approved=false` is rejected with `GITHUB_LIVE_ACTION_BLOCKED` and no plan is produced;
3. `requested_operation != Clone` is rejected with `GITHUB_NON_CLONE_OPERATION_BLOCKED`;
4. an unknown or expired `source_repo_url_hash` is rejected with `GITHUB_CLONE_READONLY_ALLOWLIST_DENIED`;
5. a `requested_ref` outside the allowlist entry's `allowed_refs` is rejected with `GITHUB_CLONE_READONLY_REF_DENIED`;
6. a mismatched `idempotency_key`, empty `approval_ref`, expired approval, or non-approving role is rejected with `GITHUB_CLONE_READONLY_APPROVAL_DENIED`;
7. a `missing`/`expired`/`revoked` credential status with `scope_class=clone_private` is rejected with `GITHUB_AUTH_REQUIRED` and no raw token is requested or constructed;
8. a privacy-naming candidate that resembles a raw student id, email, SSN-like, PAT-shaped, or denylist match is rejected with `GITHUB_PRIVACY_POLICY_VIOLATION` before plan assembly;
9. a raw credential-shaped string in any allowlist/approval/credential-status/request/plan field is rejected with `GITHUB_RAW_SECRET_REJECTED`;
10. an accepted plan has `external_call_made=false`, `external_side_effect_made=false`, `github_mutation_made=false`, `live_external_action=false`, `clone_readonly_executed=false`, and `no_raw_secret_observed=true` as hardcoded literals;
11. canonical evidence serialization is deterministic across repeated assembly with identical inputs;
12. `plan_sha256` is computed over `canonical_json` and excludes the `canonical_json`/`plan_sha256` fields from the JSON.

## 8. Ralph task queue seed

After this specification is accepted, Ralph may execute the following queue rows.

| Task | Purpose | First RED command |
|---|---|---|
| `M7-CLONE-READONLY-SPEC-PREP` | Author this specification, link RTM/STD/README/INDEX/milestones, refine queue rows. | docs/control validation |
| `M7-CLONE-READONLY-GATE-T1` | Define allowlist/approval/credential-status/plan-request/dry-run-plan type contracts and the decision pipeline functions (`evaluate_clone_readonly_allowlist`, `evaluate_clone_readonly_approval`, `evaluate_clone_readonly_credential_status`, `assemble_clone_readonly_dry_run_plan`). | `cargo test -p eduops_git --test m7_clone_readonly_gate_contract -- --nocapture` |
| `M7-CLONE-READONLY-GATE-T2` | Add fail-closed safety guards: defensive non-`CloneReadonly` rejection, no-push/no-mutation invariants, privacy-naming pre-check, `scan_clone_readonly_evidence_for_raw_secrets` over every text-bearing record/plan field. | `cargo test -p eduops_git --test m7_clone_readonly_safety_contract -- --nocapture` |
| `M7-CLONE-READONLY-SPEC-GATE` | Record constrained evidence summary for the integration-point specification and fixture-only guards. | focused M7 clone-readonly tests plus repository validation |

## 9. Gate evidence non-claims

An accepted constrained M7 clone-readonly integration-point gate may claim only:

```text
fixture-local allowlist record contract
fixture-local clone-readonly gate approval envelope
fixture-local credential-reference status contract
fixture-local privacy-naming pre-check wiring
fixture-local dry-run clone plan envelope with hardcoded non-mutation flags
fixture-local fail-closed safety guards over the dry-run plan
```

It shall not claim:

- live GitHub readiness, real network round-trip, or real authentication handshake;
- real `git clone`/`git fetch`/`git push`/`git ls-remote` execution;
- credential lookup, token refresh, credential rotation, or credential storage modification;
- production retry/rate-limit/backoff policy authority;
- repository creation, push, branch/tag creation, pull request, issue, webhook, status, check-run, invitation, branch protection, archive, or GitHub administration authority;
- submission-state or provisioning-state promotion authority;
- instructor approval surface UX, evaluator integration, or observability ingestion;
- DEMO-1 acceptance or working-demonstration approval;
- a cryptographic SHA-256 source-URL audit hash beyond the FNV-1a 64 envelope.

## 10. User-executed live-run boundary

A live `clone-readonly` execution is **not** authorized by this specification. The dry-run plan envelope is the only canonical artifact produced under Ralph.

To proceed to a real network clone in a future increment, the following human-executed boundary must be crossed separately:

1. an authorized owner reviews the dry-run plan and produces a signed `CloneReadonlyGateApproval` (the approval evidence shape is defined in §4.2 but its production is human-authored);
2. an authorized owner accepts the allowlist entry under §4.1 and records the approval in a separate runbook;
3. an authorized owner verifies that the credential reference and scope class are appropriate for the planned source repository;
4. in professor/course-owner mode, the user supplies an approved CSV containing roster rows and GitHub repository URLs, then executes or authorizes the clone-only runbook for the listed repositories; in student local-checkout mode, the student has already cloned their repository and supplies the local checkout path;
5. the user records any live-run or local-checkout evidence in a new controlled evidence document; the live-run/local-checkout evidence document is not part of this specification.

Until step (4) is performed by a human/operator under a separate approval, no real GitHub network call is allowed. Ralph never executes step (4), never resolves credentials, and never configures remotes.

## 11. Traceability

| Anchor | Linkage |
|---|---|
| [GitHub adapter specification](github-adapter-specification.md) | §2 clone-only baseline, §3 adapter modes, §7 error and retry semantics, §8 audit requirements. |
| [GitHub adapter software design description](github-adapter-software-design-description.md) | §4 `mock-http -> clone-readonly` transition gate, §5 `github.cloneRepositoryReadOnly` design, §7 clone evidence boundary, §10 security and audit design. |
| [GitHub mock-HTTP fixture format specification](github-mock-http-fixture-specification.md) | §3 non-claims, §5 `GITHUB_LIVE_ACTION_BLOCKED` classification, §7 acceptance rule #5 (clone-readonly remains blocked without separate approval). |
| [GitHub topology and token model](github-topology-and-token-model.md) | §3 naming privacy, §4 token model. |
| [Credential storage contract](credential-storage-contract.md) | OS-protected credential reference shape; raw token forbidden in any adapter-visible artifact. |
| [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) §8 / new clone-readonly addendum | `EDUOPS-FR-080..084`, `EDUOPS-NFR-034..036`. |
| [Software test description](../03-verification-validation/software-test-description.md) §18 / new clone-readonly addendum | `STD-086`, `STD-088`, `STD-089`, `STD-090`, `STD-091`. |
| [M7 SLICE-F evidence](../06-implementation/m7-slice-f-github-clone-only-evidence.md) §7 follow-up #1 | Closes the integration-point specification follow-up for fixture-only mechanics. |
| [Implementation milestones](../06-implementation/implementation-milestones.md) §M7 | Adds this specification to the controlled inputs for M7. |
| [Queue-end planning analysis](../06-implementation/queue-end-planning-analysis.md) §5 | This specification is the safest candidate selected by the queue-end refill checkpoint. |

## 12. Open follow-up items (not in scope)

| Item | Path to closure |
|---|---|
| Human approval workflow UX and authority chain | Separate instructor-UI/admin workflow specification authored under user authority. |
| Professor CSV clone intake and student local-checkout runbook | Separate user-executed runbook/specification covering roster+repository-URL CSV validation, local checkout path validation, redaction/hash evidence, and clone-only/local execution boundaries. |
| Cryptographic SHA-256 source-URL audit hash | Separate audit-hash policy decision after a controlled-evidence policy promotes it. |
| Real network retry/backoff tuning for `clone-readonly` | Separate live-mode retry-policy authority decision. |
| Cross-process audit linkage from clone-readonly evidence to submission state | Separate state-machine authority decision under M5/M7 follow-up. |
