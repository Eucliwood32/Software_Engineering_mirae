---
title: GitHub Integration Implementation Requirements Review
document_id: SWENG-EDUTECH-GITHUB-IMPL-REQ-REVIEW
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
review_type: implementation-readiness assessment
traceability:
  requirements: ['EDUOPS-FR-023', 'EDUOPS-FR-024', 'EDUOPS-FR-059', 'EDUOPS-FR-068', 'EDUOPS-FR-075']
  candidates: ['EDUOPS-CIR-006', 'EDUOPS-CFR-020', 'EDUOPS-CVR-009']
---

# GitHub Integration Implementation Requirements Review

## 1. Question

Can GitHub integration modules be implemented without adding requirements?

## 2. Conclusion

**No for implementation-level work.** The existing SRS is sufficient to state the product intent: GitHub-first repository backend, later self-hosted Git abstraction, token/privacy controls, offline/local fixture gates, and GitHub feasibility qualification. However, it is **not sufficient by itself** to implement GitHub integration modules safely because it does not define the adapter-level command contract, mode gates, retry/rate-limit semantics, credential-reference flow, mock/dry-run behavior, audit events, or TDD fixture commands.

A new product-level direction is not required. A controlled **GitHub adapter implementation specification** is required before source-code implementation of live or sandbox GitHub behavior.

## 3. Existing sufficient SRS/product baseline

| Area | Existing baseline |
|---|---|
| Product direction | `EDUOPS-FR-023`: provision and validate GitHub repositories, branches, permissions, and tokens. |
| Abstraction boundary | `EDUOPS-FR-024`: retain backend abstraction for later self-hosted Git. |
| Feasibility/KPI qualification | `EDUOPS-FR-059`: GitHub API feasibility, topology, token, rate-limit, and outage controls before production claims. |
| No-live-action gate | `EDUOPS-FR-068`, STD/V&V gates: fake/local adapters before live GitHub. |
| Credential boundary | `EDUOPS-FR-075`, credential-storage contract: configuration stores references only, raw credentials stay in OS-protected storage. |

## 4. Missing implementation-level requirements

| Gap | Why it blocks implementation | Control output |
|---|---|---|
| Adapter operations | Developers need exact operations for repository validation, provisioning, branch creation, submission refs, status/check runs, invitations, collaborator/team mapping, and deletion/archive dry-run. | [GitHub Adapter Specification](../02-design-planning/github-adapter-specification.md) |
| Adapter modes | Fake, local, dry-run, sandbox, and live modes must have explicit side-effect gates and evidence records. | GitHub adapter spec + STD/V&V gates |
| Credential-reference flow | The adapter must consume credential references and status only, never raw token strings from config/UI/logs. | GitHub adapter spec + credential-storage contract |
| Rate-limit/retry/outage semantics | GitHub APIs require deterministic backoff, retry ceilings, partial-failure handling, and queued operation semantics. | GitHub adapter spec + feasibility analysis |
| Authorization/audit | High-impact GitHub actions require actor, scope, reason, before/after, external request ID, and no-secret audit evidence. | Internal API, audit taxonomy, GitHub adapter spec |
| TDD fixtures | Current STD has grouped anchors; GitHub module needs exact fake/mock/dry-run test cards before implementation. | STD GitHub adapter section |

## 5. Implementation-start decision

- **Allowed now:** local/fake Git adapter and GitHub configuration validation fixtures that perform zero network calls.
- **Allowed after this spec and exact test cards:** GitHub mock/dry-run adapter implementation.
- **Not allowed yet:** live GitHub repository creation, collaborator invitation, branch protection mutation, token exchange, webhook registration, Actions/check-run writes, or sandbox-org side effects.

## 6. Required next action

Create and maintain `02-design-planning/github-adapter-specification.md`, update the gap register to promote `EDUOPS-CIR-006`, and add STD/V&V gates for fake/mock/dry-run/live GitHub modes.


## Clone-only supersession note

This review was later narrowed by [GitHub Clone-Only Baseline Review](github-clone-only-baseline-review.md). Any broader references to provisioning, branch policy, submission-ref mutation, archive/access-disable, sandbox mutation, or live GitHub management are superseded by the clone-only baseline.
