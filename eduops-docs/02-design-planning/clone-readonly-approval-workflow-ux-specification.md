---
title: Clone-Readonly Human Approval Workflow UX Specification
document_id: SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
version: 0.1.0
status: accepted-for-fixture-implementation
date: 2026-05-16
owner: develop
quality_context: Ralph-controlled HOW-level specification checkpoint
traceability:
  upstream:
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SDD
    - SWENG-EDUTECH-ACCESS-CONTROL-AUTHORIZATION-MODEL
  requirements:
    - EDUOPS-FR-023
    - EDUOPS-FR-024
    - EDUOPS-FR-025
    - EDUOPS-FR-026
    - EDUOPS-FR-050
    - EDUOPS-NFR-004
    - EDUOPS-NFR-010
    - EDUOPS-NFR-013
    - EDUOPS-NFR-035
  verification:
    - STD-050
    - STD-052
    - STD-079
    - STD-083
    - STD-086
    - STD-088
    - STD-089
    - STD-091
    - STD-M7-APPROVAL-UX-001
    - STD-M7-APPROVAL-UX-002
    - STD-M7-APPROVAL-UX-003
    - STD-M7-APPROVAL-UX-004
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
---

# Clone-Readonly Human Approval Workflow UX Specification

## 1. Purpose

This specification defines the fixture-local UX contract for human approval of a future `clone-readonly` GitHub operation. It authorizes UI/state-model implementation for approval review, denial, expiry, credential-reference status display, dry-run plan preview, and audit evidence capture without authorizing a live GitHub network call, credential lookup, `git clone`, `git fetch`, `git push`, repository mutation, or submission/provisioning state promotion.

It closes the UX-authority follow-up item recorded in [M7 clone-readonly integration-point gate evidence](../06-implementation/m7-clone-readonly-evidence.md) §7 item 2. The accepted upstream fixture-local decision pipeline remains [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md).

## 2. Authorized scope

| Area | Authorized for this slice | Not authorized |
|---|---|---|
| UX surface | Local desktop approval-review screen model, rendered fixture UI, accessibility labels, Korean/English text placeholders, status badges, and audit preview | Production deployment, role administration, notification delivery, external identity provider integration |
| Actor model | `course_admin` and `platform_admin` may approve; `instructor`, `ta`, `student`, and `evaluator` may view/request according to fixture role only | Granting new real-world authority beyond existing controlled roles |
| GitHub operation | Preview and approve a `clone`-only dry-run plan envelope | Live `git clone`, `git fetch`, `git push`, repo creation, branch/tag/issue/webhook/check-run mutation |
| Credential handling | Display credential-reference status (`present`, `missing`, `expired`, `revoked`) and fingerprint hint only | Raw token lookup, token rendering, credential refresh, credential rotation, credential storage modification |
| Evidence | Produce deterministic approval UX evidence with no raw PII/secret values and hardcoded non-live flags | Live-run evidence, DEMO-1 acceptance, submission/provisioning promotion |

## 2.1 Live GitHub authority assumption

The first live GitHub integration target assumes a professor-provisioned course repository. The professor or authorized course owner is treated as holding the repository access authority required to approve read-only clone/fetch access for EduOps. This assumption is recorded by `EDUOPS-DEC-064` and is consumed by this UX specification as the authority basis for `course_admin` and `platform_admin` approval surfaces.

The UX may therefore present an approval path for a professor-owned repository after fixture-local gates pass. The UI must still show that live execution is a separate human-operated step: approval does not itself run `git clone`, resolve a raw credential, create a repository, push, mutate branch protection, or promote submission/provisioning state.

`EDUOPS-DEC-065` further fixes the user-managed boundary for actual operation. In professor/course-owner mode, the UI may model CSV intake where each approved roster row carries a GitHub repository URL field supplied by the professor or authorized operator; EduOps validates and redacts the field, then uses the controlled clone-only path for those listed repositories. In student mode, the UI must model EduOps as running from a local repository checkout that the student has already cloned; EduOps must not configure the student's remote, resolve student credentials, or clone on the student's behalf in that mode.

## 3. UX state model

The approval UX is represented as a deterministic `ApprovalWorkflowViewModel` fixture record. The first product-code slice should implement this model before rendering behavior.

Required fields:

| Field | Type | Rule |
|---|---|---|
| `workflow_id` | string | Stable fixture id, no raw PII or credential-shaped value. |
| `actor_role` | enum | One of `student`, `instructor`, `ta`, `course_admin`, `platform_admin`, `evaluator`. |
| `approval_status` | enum | One of `not_requested`, `pending_review`, `approved`, `denied`, `expired`, `blocked`. |
| `source_repo_url_hash` | string | Hash/envelope value only; raw URL is not displayed. |
| `requested_ref` | string | Ref token already accepted by the integration-point allowlist policy. |
| `operation_class` | enum | Must be `clone-only`. |
| `credential_status` | enum | One of `present`, `missing`, `expired`, `revoked`, `not_required`. |
| `credential_fingerprint_hint` | string or null | Optional redacted hint only. |
| `privacy_decision_count` | integer | Number of privacy naming decisions already evaluated. |
| `blocking_reasons` | array | Redacted reason codes; no raw PII or raw secrets. |
| `available_actions` | array | Allowed UI actions for the actor/status combination. |
| `audit_preview_ids` | array | Deterministic audit event ids that would be emitted by fixture approval. |
| `external_call_made` | bool | Must be `false`. |
| `github_mutation_made` | bool | Must be `false`. |
| `clone_readonly_executed` | bool | Must be `false`. |
| `raw_secret_observed` | bool | Must be `false`. |

## 4. Role and action matrix

| Actor role | Pending review actions | Approved-state actions | Denied/blocked actions |
|---|---|---|---|
| `course_admin` | approve, deny, request-more-info | view approval, copy evidence id | view reason, reopen fixture request |
| `platform_admin` | approve, deny, request-more-info | view approval, copy evidence id | view reason, reopen fixture request |
| `instructor` | view pending status, cancel own fixture request | view approved dry-run plan summary | view reason, create corrected fixture request |
| `ta` | view pending status only | view approved summary when course policy allows | view reason |
| `student` | no approval action | no approval action | no approval action |
| `evaluator` | no approval action | view evidence summary only | view reason |

Approval requires an explicit human-click action in the fixture UI model by `course_admin` or `platform_admin`. Default-on approval is forbidden. Hidden UI controls are not a security boundary; backend authorization and existing `CloneReadonlyGateApproval` validation remain required.

## 5. Screen flow

1. **Request intake summary** displays actor role, operation class, source hash, requested ref, credential-reference status, privacy-decision count, and no-live-action banner.
2. **Review panel** displays allowlist match status, approval expiry, idempotency key hash/label, and all blocking reason codes.
3. **Decision panel** exposes approve/deny/request-more-info only when the actor role is `course_admin` or `platform_admin` and the status is `pending_review`.
4. **Dry-run plan preview** displays the fixture plan evidence id after approval. It must display `external_call_made=false`, `github_mutation_made=false`, and `clone_readonly_executed=false`.
5. **Audit preview** displays deterministic audit ids and the evidence envelope path that a fixture test will assert.

## 6. Acceptance and safety rules

- The UI must not display raw repository URLs, raw tokens, raw roster ids, email addresses, SSNs, or long digit identifiers.
- The UI must display a visible no-live-action indicator whenever clone-readonly approval is shown.
- A denied, expired, blocked, or missing-credential state must disable the approve action.
- `instructor` and `ta` roles may request or view according to fixture policy but cannot approve.
- Approval evidence must carry the predecessor dry-run plan id or hash and the gate approval envelope fields needed by [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md) §4.2.
- Fixture approval UX evidence must be accepted only when `external_call_made=false`, `github_mutation_made=false`, `clone_readonly_executed=false`, and `raw_secret_observed=false`.
- Accessibility acceptance includes keyboard focus order, role/action labels, non-color-only status indicators, and screen-reader labels for approve/deny/request-more-info controls.

## 7. First executable Ralph tasks

| Task ID | Test command | RED condition | GREEN acceptance |
|---|---|---|---|
| `M7-APPROVAL-UX-T1` | Create `apps/desktop-ui/tests/m7-approval-ux-state.test.mjs`, then run `node apps/desktop-ui/tests/m7-approval-ux-state.test.mjs`. | No `ApprovalWorkflowViewModel` fixture model or action matrix exists. | Role/status/action matrix, no-live flags, redacted display fields, professor CSV clone-input mode, and student pre-cloned local-checkout mode validate in a deterministic fixture test. |
| `M7-APPROVAL-UX-T2` | Create or update a focused render/typecheck fixture under `apps/desktop-ui/tests/`, then run the focused Node test plus `npm run m0:ui-typecheck && npm run m0:ui-build`. | Approval screen cannot render pending/approved/denied/blocked fixture states. | Local desktop UI renders the screen states, no-live banner, user-managed GitHub boundary notice, disabled/enabled actions, and accessibility labels without calling GitHub. |
| `M7-APPROVAL-UX-GATE` | repository docs/control validation plus focused UX tests | Evidence summary missing or overclaims live behavior. | Constrained evidence records fixture-local UX acceptance and explicit non-claims. |

## 8. Non-claims

This specification does not claim:

- live GitHub API readiness;
- real `git clone`, `git fetch`, `git push`, or `git ls-remote` execution;
- credential lookup, token refresh, credential rotation, or credential storage mutation;
- automatic production human approval workflow deployment without a separate user-executed live-run gate;
- EduOps-managed live GitHub credentials, remote setup, repository administration, or cloning on behalf of a student who has not supplied a local checkout;
- notification delivery, external identity provider integration, or organization administration;
- submission/provisioning state promotion from clone-readonly evidence;
- DEMO-1 acceptance or live working-demonstration closure.

## 9. Traceability

- Upstream design: [GitHub clone-readonly integration-point boundary specification](github-clone-readonly-integration-point-specification.md).
- Upstream evidence: [M7 clone-readonly integration-point gate evidence](../06-implementation/m7-clone-readonly-evidence.md).
- Role and authorization anchors: [Role permission matrix](role-permission-matrix.md) and [Access control and authorization model](access-control-authorization-model.md).
- Verification anchors: [Software test description](../03-verification-validation/software-test-description.md) §M7 clone-readonly approval workflow UX test addendum.
