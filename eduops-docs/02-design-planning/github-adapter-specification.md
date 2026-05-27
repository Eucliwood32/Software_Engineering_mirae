---
title: GitHub Adapter Specification
document_id: SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  requirements: ['EDUOPS-FR-023', 'EDUOPS-FR-024', 'EDUOPS-FR-059', 'EDUOPS-FR-068', 'EDUOPS-FR-075', 'EDUOPS-FR-080', 'EDUOPS-FR-081', 'EDUOPS-FR-084']
  candidates: ['EDUOPS-CIR-006', 'EDUOPS-CFR-020', 'EDUOPS-CVR-009']
---

# GitHub Adapter Specification

## 1. Purpose

Define the implementation-level contract for GitHub as a **clone-only repository source**. This document does not authorize live GitHub mutation. It defines the controlled contract that fake, mock, and future approved clone-readonly adapters must satisfy.

## 2. Clone-only baseline

EduOps shall use GitHub only to clone or read/fetch approved repositories in the current baseline.

Allowed GitHub-side behavior after gate approval:

- validate clone configuration;
- plan clone targets;
- perform read-only clone/fetch of an approved repository URL or reference;
- query/record clone evidence such as source URL hash, commit SHA, ref, timestamp, and rate-limit metadata.

Forbidden GitHub-side behavior:

- repository or organization creation;
- branch/tag creation on GitHub;
- push or submission-ref mutation;
- collaborator/team invitation or permission mutation;
- branch protection mutation;
- webhook/check-run/status writes;
- issue, PR, release, archive, or access-disable actions;
- any GitHub administration operation.

Any non-clone operation fails as `GITHUB_NON_CLONE_OPERATION_BLOCKED` before an external request is made.

## 3. Adapter modes

| Mode | Network allowed | External side effect allowed | Use |
|---|---:|---:|---|
| `fake-local` | No | No | SLICE-A/B/C local implementation and TDD fixtures. |
| `mock-http` | Local mock server only | No | Contract tests for clone validation, auth failure, rate limit, retry, and timeout responses. |
| `clone-readonly` | Approved GitHub read/clone only | No GitHub mutation | Future approved clone evidence against a real GitHub source. |

All modes default to `fake-local`. `clone-readonly` requires configuration gate approval, credential-reference status check when the repository is private, actor authorization, target repository allowlist, and audit evidence. There is no sandbox/live mutation mode in the current baseline.

Implementation of `mock-http` fixtures is governed by [GitHub mock-HTTP fixture format specification](github-mock-http-fixture-specification.md). The fixture profile is local-only: replayed HTTP responses are data records, `external_call_made=false`, and no real GitHub network call is made.

## 4. Credential and configuration boundary

- The adapter shall accept `credential_ref_id`, provider, scope, and status only.
- The adapter shall not receive raw token strings from UI, configuration files, logs, exports, diagnostics, or test manifests.
- Raw credentials remain inside OS-protected credential storage as defined by [Credential Storage Contract](credential-storage-contract.md).
- GitHub clone configuration shall use controlled configuration keys and shall respect offline/network-call denial behavior from [Configuration Contract](configuration-contract.md).

## 5. Required clone-only adapter operations

| Operation | Input summary | Output summary | Side-effect class |
|---|---|---|---|
| `github.validateCloneConfiguration` | repository URL/ref, allowlist, credential ref, adapter mode | validation issues, resolved clone capability, no-secret evidence | read/none |
| `github.planClone` | course/assignment/source repository references | clone plan, predicted local paths, privacy warnings, required credential status | none |
| `github.cloneRepositoryReadOnly` | approved clone plan ID, target local path, expected ref/SHA, idempotency key | local clone path, source commit SHA, manifest hash, no-mutation evidence | external read only in `clone-readonly`; none in fake/mock |
| `github.queryCloneEvidence` | local clone path, expected ref/SHA, evidence filters | normalized clone evidence view with rate-limit metadata when applicable | read |

No operation may push, create, invite, protect, write a webhook/check-run/status, or mutate GitHub state.

## 6. Required output fields

Every operation returns a result envelope with:

- `adapter_mode`
- `operation_class='clone-only'`
- `external_call_made`
- `external_side_effect_made=false`
- `github_mutation_made=false`
- `credential_ref_id`
- `credential_fingerprint_hint`
- `request_id` or mock request ID
- `source_repo_url_hash`
- `source_ref`
- `source_commit_sha` where available
- `rate_limit_remaining` where applicable
- `retry_count`
- `idempotency_key`
- `audit_event_ids`
- `redaction_profile`
- `no_raw_secret_observed=true`

## 7. Error and retry semantics

| Error class | Example | Required behavior |
|---|---|---|
| `GITHUB_AUTH_REQUIRED` | private repository requires missing/expired credential ref | fail closed; do not prompt workers for raw tokens. |
| `GITHUB_SCOPE_DENIED` | credential lacks read/clone scope | return actionable issue; no external mutation. |
| `GITHUB_RATE_LIMITED` | core/search/secondary limit reached | backoff using deterministic policy and preserve planned clone state. |
| `GITHUB_OUTAGE_OR_TIMEOUT` | network/API unavailable | preserve local planned/queued clone evidence; do not mark clone verified. |
| `GITHUB_PRIVACY_POLICY_VIOLATION` | raw student ID in visible clone source alias/evidence | block before external call. |
| `GITHUB_NON_CLONE_OPERATION_BLOCKED` | push, create repo, invite collaborator, webhook/check write attempted | fail before external request and emit gate-denial audit event. |
| `GITHUB_LIVE_ACTION_BLOCKED` | clone-readonly attempted before gate | fail with gate-denial audit event. |

## 8. Audit requirements

Each protected GitHub clone operation shall record:

- actor, role, course/section/assignment scope;
- requested clone action and adapter mode;
- clone-readonly gate decision;
- credential reference and fingerprint hint only;
- source repository URL hash and redacted host/path class;
- local target path and manifest hash;
- source ref and commit SHA where available;
- explicit `github_mutation_made=false` evidence.

## 9. TDD and fixture gates

Implementation of a GitHub module shall start with failing tests for:

| Gate | Required fixture |
|---|---|
| `GH-FIX-001` | fake-local mode rejects all network calls and produces clone-only evidence. |
| `GH-FIX-002` | mock-http mode handles clone validation, auth failure, rate limit, retry, and timeout responses. |
| `GH-FIX-003` | privacy naming policy blocks raw student identifiers in visible repository aliases and clone evidence. |
| `GH-FIX-004` | raw credential fixture value does not appear in logs, Git files, exports, diagnostics, or result envelopes. |
| `GH-FIX-005` | planned/cloned/verified clone evidence remains distinct from submission or provisioning state. |
| `GH-FIX-006` | every non-clone GitHub operation is blocked even if credentials or network are configured. |

No source-code implementation task may cite this specification alone. It must cite a specific `GH-FIX-*` fixture, expected RED condition, expected GREEN evidence artifact, and no-live-action assertion.
