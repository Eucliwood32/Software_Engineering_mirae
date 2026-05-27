---
title: M7 Approval UX Predecessor Block Accessibility Hardening Gate Evidence
document_id: EDUOPS-M7-APPROVAL-UX-PREDECESSOR-A11Y-HARDEN-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M7-APPROVAL-UX-EVIDENCE
    - EDUOPS-M7-APPROVAL-UX-INTAKE-LINK-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-BYTE-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-BYTE-RFC4180-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-BYTE-ERROR-MSG-AUDIT-EVIDENCE
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - m7-approval-ux-predecessor-a11y-harden
    - m7-approval-ux-state
    - m7-approval-ux-render
    - m7-approval-ux-harden
    - m7-approval-ux-intake-link-state
    - m7-approval-ux-intake-link-render
---

# M7 Approval UX Predecessor Block Accessibility Hardening Gate Evidence

## 1. Gate result

`GATE-M7-APPROVAL-UX-PREDECESSOR-A11Y-HARDEN-FIXTURE-LOCAL` is accepted-constrained for the fixture-local interactive accessibility hardening audit added by `M7-APPROVAL-UX-PREDECESSOR-A11Y-HARDEN-T1` at `ea5ede3`. The audit exercises the full 6 roles × 6 approval statuses × 4 predecessor combinations (`neither`/`intake-only`/`plan-only`/`both`) = 144-combination coverage matrix and verifies 9 structural HTML + accessibility invariants over the predecessor evidence references block emitted by `apps/desktop-ui/src/approvalWorkflowRender.mjs`.

This gate closes the follow-up recorded in [M7 approval UX predecessor reference integration gate evidence](m7-approval-ux-intake-link-evidence.md) §7 item 2. It preserves the same no-live-action / no-real-GitHub / no-real-credential / no-real-network boundary as the upstream approval UX gates.

```text
gate=GATE-M7-APPROVAL-UX-PREDECESSOR-A11Y-HARDEN-FIXTURE-LOCAL
status=accepted-constrained
scope=apps/desktop-ui/tests/m7-approval-ux-predecessor-a11y-harden.test.mjs verifies 9 structural HTML + accessibility invariants across 6 roles (student/instructor/ta/course_admin/platform_admin/evaluator) × 6 approval statuses (not_requested/pending_review/approved/denied/blocked/expired) × 4 predecessor combinations (neither/intake-only/plan-only/both) = 144 rendered outputs of renderApprovalWorkflowScreen plus an aggregated forbidden-pattern check across the entire corpus; invariants: (1) data-predecessor-references=true block appears exactly once when at least one of professorCsvIntakeEvidenceId/cloneReadonlyDryRunPlanId is populated and is exactly absent when both are null/empty/whitespace-only; (2) the block <section> carries aria-label="Predecessor evidence references" and data-predecessor-references="true"; (3) the block contains exactly one <h2>Predecessor evidence references</h2> heading and exactly one <dl> wrapping the dt/dd pairs; (4) <dt>/<dd> pair count matches the number of populated predecessor fields; (5) data-kind attribute values present only for populated fields with the populated id appearing inside the section; (6) deterministic intake-before-plan ordering when both fields are populated; (7) the block is nested INSIDE the no-live-action section and appears BEFORE the request-intake summary so it inherits the no-live accessibility context; (8) no forbidden raw HTTPS/HTTP/SSH URL form, raw email substring (X@Y.Z), GitHub PAT prefix (ghp_/github_pat_ case-insensitive), URL credential form (://user:token@host), git@ SSH-URL form, or 6+ consecutive digit run appears in the rendered output; (9) render output is byte-identical across repeated calls with the same model
constraint=live HTTPS/SSH probe, real git clone/fetch/push/ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration (creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive), real CSV upload UI / drag-and-drop file picker / production deployment, Tauri shell wiring of renderApprovalWorkflowScreen into a live desktop preview surface, end-to-end interactive accessibility audit with a real screen-reader, keyboard navigation simulation, desktop screenshot capture, production approval workflow deployment, identity-provider integration, notification delivery, submission/provisioning state promotion, shared JS denylist helper extraction across approvalWorkflow.mjs and approvalWorkflowRender.mjs (intentionally divergent for layered defense per m7-approval-ux-intake-link-evidence.md §7 item 3), additional predecessor reference kinds, full-Unicode NFC normalization, SSH PEM blob / password-form detection, SHA-256 source-URL audit hash upgrade, and DEMO-1 acceptance are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live GitHub action, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real human approval workflow deployment, Tauri shell wiring of `renderApprovalWorkflowScreen`, end-to-end interactive accessibility audit, desktop screenshot capture, notification delivery, submission/provisioning state promotion, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted predecessor block accessibility hardening behavior:

- `apps/desktop-ui/tests/m7-approval-ux-predecessor-a11y-harden.test.mjs` builds a `createApprovalWorkflowViewModel` input for every (role, status, predecessor combination) tuple, calls `renderApprovalWorkflowScreen(model)` on each, and asserts the 9 numbered invariants per output plus an aggregated corpus forbidden-pattern check.
- Workflow id template `wf_m7_pred_a11y_${role}_${status}_${combo.kind}_${4-digit-pad}`, source-repo URL hash `a1b2c3d4e5f6a7b8` (alternating letter/digit hash with at most 1 consecutive digit), intake id template `audit_prof_csv_intake_${role}_${status}_${4-digit-pad}`, and plan id template `audit_clone_readonly_plan_${role}_${status}_${4-digit-pad}` are chosen so that no rendered output contains any of the forbidden patterns by construction.
- `credentialStatus` is chosen per status (`revoked` for `blocked`, `missing` for `denied`, otherwise `present`), `credentialFingerprintHint` is `gh_fgp_abcd` for all non-student roles and null for student, `blockingReasons` are set only for `blocked` and `denied` statuses, and `cloneInputMode` is `professor_csv` throughout (the student `student_local_checkout` branch is exercised by the existing `m7-approval-ux-harden.test.mjs`).
- Invariant (1) gates the predecessor block presence on at least one populated predecessor id. Invariant (2) anchors the documented `aria-label="Predecessor evidence references"` and `data-predecessor-references="true"` attributes on the `<section>`. Invariant (3) anchors exactly one `<h2>Predecessor evidence references</h2>` heading and exactly one `<dl>` wrapping the dt/dd pairs. Invariant (4) anchors the dt/dd pair count to the number of populated fields. Invariant (5) anchors the `data-kind` attribute values to the populated fields and asserts the populated id appears inside the block. Invariant (6) anchors the deterministic intake-before-plan ordering when both fields are populated (the render module's `predecessorReferences.push(...)` order produces this by construction). Invariant (7) anchors the structural nesting INSIDE the no-live-action section and BEFORE the request-intake summary so the predecessor block inherits the no-live accessibility context (`role="status"` on the parent section). Invariant (8) is the FORBIDDEN_PATTERNS regression check (raw HTTPS/HTTP URL, raw SSH `git@` URL, raw email, GitHub PAT prefix, URL credential form, 6+ consecutive digits). Invariant (9) is the byte-identical determinism check.
- The audit is regression protection. The current render structure in `apps/desktop-ui/src/approvalWorkflowRender.mjs` lines 221-255 already satisfies every audited invariant by construction; the audit will catch any future render-layer change that drops the aria attributes, wraps the dt/dd pairs in something other than a single `<dl>`, reorders intake/plan, misplaces the block outside the no-live-action section, leaks a forbidden pattern through the layered `escapeHtml` + `assertSafeDisplayValue` + `validatePredecessorReferenceId` defense, or becomes non-deterministic.

## 3. RED to GREEN evidence

### M7-APPROVAL-UX-PREDECESSOR-A11Y-HARDEN-T1 audit test

```text
RED command:    node apps/desktop-ui/tests/m7-approval-ux-predecessor-a11y-harden.test.mjs
RED result:     no RED iteration was required; the current render structure already satisfies every audited invariant by construction across all 144 combinations
GREEN command:  node apps/desktop-ui/tests/m7-approval-ux-predecessor-a11y-harden.test.mjs
GREEN result:   m7_approval_ux_predecessor_a11y_harden=ok combinations=144
Commit:         ea5ede3
```

## 4. Repository-level validation

```text
node apps/desktop-ui/tests/m7-approval-ux-predecessor-a11y-harden.test.mjs -> m7_approval_ux_predecessor_a11y_harden=ok combinations=144
node apps/desktop-ui/tests/m7-approval-ux-state.test.mjs                   -> m7_approval_ux_state=ok
node apps/desktop-ui/tests/m7-approval-ux-render.test.mjs                  -> m7_approval_ux_render=ok
node apps/desktop-ui/tests/m7-approval-ux-harden.test.mjs                  -> m7_approval_ux_harden=ok combinations=36
node apps/desktop-ui/tests/m7-approval-ux-intake-link-state.test.mjs       -> m7_approval_ux_intake_link_state=ok
node apps/desktop-ui/tests/m7-approval-ux-intake-link-render.test.mjs      -> m7_approval_ux_intake_link_render=ok
cargo fmt --all --check                                                     -> clean
git diff --check                                                            -> clean
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)        -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Predecessor block presence is gated on at least one populated id; absent when both ids are null | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (1) block presence and absence assertions` | accepted |
| `<section>` carries `aria-label="Predecessor evidence references"` and `data-predecessor-references="true"` | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (2) section attribute assertion` | accepted |
| Exactly one `<dl>` and one `<h2>Predecessor evidence references</h2>` heading inside the section | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (3) dl/heading count assertions` | accepted |
| dt/dd pair count matches the number of populated predecessor fields | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (4) dt/dd pair count assertions` | accepted |
| `data-kind="professor-csv-intake-evidence"` and `data-kind="clone-readonly-dry-run-plan"` present only for populated fields, with the populated id appearing inside the section | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (5) data-kind presence assertions` | accepted |
| Intake-before-plan ordering is deterministic when both fields are populated | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (6) ordering assertion` | accepted |
| Block is nested INSIDE the no-live-action section and starts BEFORE the request-intake summary | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (7) structural nesting assertions` | accepted |
| No forbidden raw HTTPS/HTTP/SSH URL, raw email, GitHub PAT prefix, URL credential form, `git@` SSH URL, or 6+ consecutive digit run appears in any rendered output across all 144 combinations | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (8) per-output and aggregated FORBIDDEN_PATTERNS assertions` | accepted |
| Render output is byte-identical across repeated calls with the same model | `m7-approval-ux-predecessor-a11y-harden.test.mjs::invariant (9) determinism assertion` | accepted |
| Coverage matrix is exactly 6 roles × 6 statuses × 4 predecessor combinations = 144 | `m7-approval-ux-predecessor-a11y-harden.test.mjs::auditedCombinations equality assertions` | accepted |
| Existing approval UX state / render / harden / intake-link state / intake-link render buckets remain green | regression validation commands in §4 | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live GitHub action, real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote`, or real credential resolution;
- real human approval workflow deployment, real credential rotation, or production approval workflow UX rollout;
- Tauri shell wiring of `renderApprovalWorkflowScreen` into a live desktop preview surface — the test runs purely against the in-process render function;
- end-to-end interactive accessibility audit with a real screen-reader, keyboard navigation simulation, or assistive-technology compatibility verification;
- desktop screenshot capture, visual regression testing, or production deployment;
- consolidation of the intentionally divergent JS denylist regex strictness between `approvalWorkflow.mjs` and `approvalWorkflowRender.mjs` — both layers continue to operate with their documented layered-defense regex strictness per `m7-approval-ux-intake-link-evidence.md` §7 item 3;
- additional predecessor reference kinds beyond `professor-csv-intake-evidence` and `clone-readonly-dry-run-plan`;
- full-Unicode NFC normalization, SSH PEM blob detection, or password-form detection;
- a cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope;
- notification delivery, external identity-provider integration, organization administration, or submission/provisioning state promotion;
- DEMO-1 acceptance or live working-demonstration approval;
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Wire `renderApprovalWorkflowScreen` into the Tauri/webview shell so a desktop preview surface is observable (carry-over from `m7-approval-ux-evidence.md` §7 item 1, `m7-approval-ux-intake-link-evidence.md` §7 item 1; requires user-installed desktop runtime and webview integration, deferred);
2. Author an authorized control update redefining the layered-defense rationale and extracting a shared JS denylist helper module so the approval VM (`approvalWorkflow.mjs`) and the render-side guard (`approvalWorkflowRender.mjs`) can share a single denylist source while preserving layered defense (carry-over from `m7-approval-ux-intake-link-evidence.md` §7 item 3; deferred);
3. Extend the predecessor references block with additional kinds (e.g., parent approval id, evaluator decision id) after an authorized control update enumerates them (carry-over from `m7-approval-ux-intake-link-evidence.md` §7 item 4; deferred);
4. Author the student pre-cloned local-checkout reader specification covering the `cloneInputMode='student_local_checkout'` branch, fixture-local file-system read boundary, and predecessor references for student-supplied checkouts;
5. Author the user-managed runbook that prescribes how the professor/course-admin obtains the upstream intake_id and dry-run plan_id before approval, per `EDUOPS-DEC-065`; this is outside Ralph automation and remains user-managed.

## 8. Traceability

- [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md)
- [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md)
- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [M7 clone-readonly approval workflow UX gate evidence](m7-approval-ux-evidence.md)
- [M7 approval UX predecessor reference integration gate evidence](m7-approval-ux-intake-link-evidence.md)
- [M7 professor CSV roster + repository URL intake gate evidence](m7-prof-csv-intake-evidence.md)
- [M7 professor CSV byte parser gate evidence](m7-prof-csv-intake-byte-evidence.md)
- [M7 professor CSV byte parser RFC 4180 grammar gate evidence](m7-prof-csv-intake-byte-rfc4180-evidence.md)
- [M7 professor CSV byte parser error-message redaction audit gate evidence](m7-prof-csv-intake-byte-error-msg-audit-evidence.md)
- [M7 clone-readonly integration-point gate evidence](m7-clone-readonly-evidence.md)
- [Software test description](../03-verification-validation/software-test-description.md) — a future addendum for `STD-M7-APPROVAL-UX-PREDECESSOR-A11Y-HARDEN-001`
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
