---
title: M5 Scoped Submission and Review Authorization Specification Gap Closure
document_id: EDUOPS-M5-AUTH-SPEC-BLOCKER
version: 0.1.0
status: blocker-recorded
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - SWENG-EDUTECH-ACM
    - SWENG-EDUTECH-STATE-TABLES
    - SWENG-EDUTECH-REPO-WORKFLOW
  gaps_recorded:
    - Authorization implementation specification (M5 row in implementation-milestones §6)
---

# M5 Scoped Submission and Review Authorization Specification Gap Closure

## 1. Purpose

This document records the controlled gap-closure decision for the scoped submission and review authorization implementation specification before the M5 SLICE-D assignment publication/sync/submission state-machine gate is claimed. The "Authorization implementation specification" entry in the milestone-gated gap table of [Implementation milestones §6](implementation-milestones.md) is listed as `Required before M5` with the rationale that submission/review workflows require executable authorization behavior, not only UI hiding.

[Access control and authorization model](../02-design-planning/access-control-authorization-model.md) defines the authorization baseline (AC-001 through AC-014, decision record fields, high-impact actions, traceability) at a rules level. It does not yet contain:

- a concrete per-action authorization handler enumeration for M5 submission/review use cases (`assignment.publish`, `assignment.publish_update`, `assignment.release`, `submission.queue`, `submission.confirm`, `submission.reject`, `submission.manual_review`, `submission.reopen`, `feedback.release`);
- a controlled decision-record persistence schema and JSON manifest format for `AuthorizationDecisionRecord` and the linked `AuditEvent`;
- an `allow-with-confirmation` / `allow-with-approval` / `queue` flow specification for high-impact actions (publish, release, override, reopen) including approver identity, before/after state, and audit linkage;
- a TA delegated-scope grant specification (`TaScopeGrant`) with course/section/assignment scope, action allowlist, expiry, and revocation behavior consistent with AC-005;
- an offline-mode promotion rule specification consistent with AC-009 for queued-but-not-confirmed submissions when the local clock or adapter is offline;
- an observability and diagnostics specification for decision and audit ingestion, redaction, retention, and review workflow.

Authoring or commissioning an authorization implementation specification crosses a design/decision boundary that requires human review of policy authority, deferred legal/academic constraints, TA delegation policy, and approval workflow ownership. The Ralph loop must not author or accept that specification directly under its non-delegable safety boundary.

## 2. Decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-M5-AUTH-SPEC-DEFERRED` |
| Decision date | 2026-05-15 |
| Status | blocker-recorded; M5 gate scope constrained |
| Authority required | human design owner with policy/authorization decision authority |
| Ralph delegation | not authorized to author the specification |

The scoped submission/review authorization implementation specification is deferred to a separate controlled document/decision pass. The M5 SLICE-D assignment publication/sync/submission gate proceeds with explicitly constrained scope so it does not overclaim production authorization.

## 3. M5 gate scope constraint

M5 acceptance under this gap-closure decision is limited to:

- deterministic assignment version creation, release-state transitions, and update transitions inside `eduops_domain` (`M5-T1`/`M5-T2`);
- submission state machine with distinct `Checkpointed`/`Queued`/`Pushed`/`Confirmed`/`Rejected`/`ManualReview` states and audit-event ids inside `eduops_domain` (`M5-T3`);
- repository conflict guard that rejects assignment-update writes outside `assignment/**` and never overwrites `workspace/**` or `knowledge/**` paths, with structured `RepositoryConflictEvidence` and audit ids inside `eduops_storage` (`M5-T4`);
- the M4-T5 default-deny `decide_access` decision evidence already in `eduops_storage` as the baseline access-control surface;
- documentation/control evidence summary for the SLICE-D scope above with explicit non-claims for the deferred work below.

M5 acceptance under this gap-closure decision does not claim:

- a production scoped-authorization engine (RBAC + policy attributes per AC-001 through AC-014) for submission/review actions;
- `AuthorizationDecisionRecord` persistence, JSON manifest, ingestion, retention, or redaction;
- `allow-with-confirmation` / `allow-with-approval` / `queue` mechanics for high-impact actions per AC-010;
- TA delegated-scope grant lifecycle, expiry, and revocation per AC-005;
- offline promotion rule enforcement per AC-009 beyond fixture-local state transitions;
- instructor publication-update notification surface, scoped TA review queue, or feedback release authority;
- evaluator/sync-worker authority boundary per AC-008;
- live GitHub push, server-backed submission receipt, or remote audit ingestion;
- observability/diagnostics ingestion of authorization decisions or audit events beyond in-memory `audit_event_id` strings.

## 4. Required follow-up before claiming production submission/review authorization

The following work shall be completed by an authorized human owner before any milestone or gate claims production submission/review authorization:

1. author `docs/02-design-planning/authorization-implementation-specification.md` covering:
   - per-action authorization handler enumeration for M5 use cases (`assignment.publish`, `assignment.publish_update`, `assignment.release`, `submission.queue`, `submission.confirm`, `submission.reject`, `submission.manual_review`, `submission.reopen`, `feedback.release`) with subject/resource/action/context inputs and `Decision` outputs aligned with AC-001 through AC-014;
   - a controlled `AuthorizationDecisionRecord` JSON manifest schema covering the §7 fields of the [access-control authorization model](../02-design-planning/access-control-authorization-model.md), with persistence path, sort/canonicalization, redaction policy, and retention;
   - an `allow-with-confirmation` / `allow-with-approval` / `queue` flow specification for AC-010 high-impact actions with approver identity, before/after state capture, and audit linkage;
   - a `TaScopeGrant` lifecycle specification with course/section/assignment scope, action allowlist, expiry, and revocation behavior consistent with AC-005;
   - an offline-mode promotion rule specification consistent with AC-009 covering queue/promotion transitions across offline-online boundaries and authoritative-time drift;
   - an `AuditEvent` persistence specification consistent with AC-013 covering grade, identity, token-reference, override, and export operations;
   - test requirements aligned with the [access-control authorization model §8](../02-design-planning/access-control-authorization-model.md) test catalogue;
2. author an explicit acceptance/decision record updating the milestone-gated gap table entry from open to closed;
3. update the affected RTM and STD rows to reference the new specification as the authorization-implementation acceptance source.

Only after these steps may a later Ralph or implementation pass create executable scoped-authorization tasks (`M5-AUTH-T*` or follow-up `M5-T*`) or claim production submission/review authorization in an updated M5 evidence summary.

## 5. Why this is a recorded blocker rather than a closed gap

The Ralph safety boundary prohibits live external action, destructive change, and any work that requires authority Ralph does not hold. Authoring the scoped submission/review authorization implementation specification is a design decision pass that requires:

- policy authority owned by the academic/operations function for confirmation/approval rules and TA delegation policy;
- design owner sign-off through the [decision log](../05-decisions/decision-log.md);
- coordination with the [access control and authorization model](../02-design-planning/access-control-authorization-model.md), the [state machine implementation tables](../02-design-planning/state-machine-implementation-tables.md), and the [repository permission and assignment workflow](../02-design-planning/repository-permission-workflow.md);
- alignment with retention and redaction policy that crosses ISO 9001 traceability and privacy/legal review.

Recording the gap as a controlled blocker preserves traceability without overclaiming acceptance or inventing implementation work outside Ralph's safety boundary.

## 6. Traceability

| Reference | Source |
|---|---|
| Milestone-gated gap table row | [Implementation milestones §6](implementation-milestones.md) — "Authorization implementation specification" row |
| Authorization rules baseline | [Access control and authorization model](../02-design-planning/access-control-authorization-model.md) |
| Submission/release state machine | [State machine implementation tables](../02-design-planning/state-machine-implementation-tables.md) §3–§5 |
| Repository permission workflow | [Repository permission and assignment workflow](../02-design-planning/repository-permission-workflow.md) §1, §5, §7 |
| Prior gap-closure precedent | [M3 editor adapter bridge specification gap closure](m3-bridge-spec-blocker.md) |
| Source candidate requirements | EDUOPS-FR-025, EDUOPS-FR-029, EDUOPS-FR-034, EDUOPS-NFR-010, EDUOPS-NFR-013, EDUOPS-DEC-022 |

## 7. Non-claims

This document does not author the authorization implementation specification, accept any scoped-authorization decision schema, approve any confirmation/approval workflow, close the authorization implementation gap, or expand M5 acceptance beyond the constrained SLICE-D scope listed in §3. It records the deferral and constrains the M5 gate scope so the fixture-local assignment publication, submission state-machine, and repository conflict guard work can be accepted on its own merits.
