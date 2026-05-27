---
title: M7 Approval UX Predecessor Reference Integration Gate Evidence
document_id: EDUOPS-M7-APPROVAL-UX-INTAKE-LINK-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-PROFESSOR-CSV-INTAKE-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M7-APPROVAL-UX-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-EVIDENCE
    - EDUOPS-M7-PROF-CSV-INTAKE-BYTE-EVIDENCE
    - EDUOPS-M7-CLONE-READONLY-INTEGRATION-POINT-EVIDENCE
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - apps/desktop-ui::m7-approval-ux-intake-link-state
    - apps/desktop-ui::m7-approval-ux-intake-link-render
---

# M7 Approval UX Predecessor Reference Integration Gate Evidence

## 1. Gate result

`GATE-M7-APPROVAL-UX-INTAKE-LINK-FIXTURE-LOCAL` is accepted-constrained for the fixture-local extension of the approval workflow VM (M7-APPROVAL-UX-INTAKE-LINK-T1) and its rendered no-live-section predecessor references block (M7-APPROVAL-UX-INTAKE-LINK-T2). The extension adds two optional predecessor reference fields — `professorCsvIntakeEvidenceId` and `cloneReadonlyDryRunPlanId` — to the existing approval surface so the human approver can see at a glance which upstream intake evidence and clone-readonly dry-run plan led to this approval request, without changing any of the non-claims that already apply to [M7 clone-readonly approval workflow UX gate evidence](m7-approval-ux-evidence.md) or [M7 professor CSV roster + repository URL intake gate evidence](m7-prof-csv-intake-evidence.md) / [M7 professor CSV byte parser gate evidence](m7-prof-csv-intake-byte-evidence.md).

Live HTTPS/SSH probe, real `git clone`/`git fetch`/`git push`/`git ls-remote`, real credential resolution, repository administration, real CSV upload UI, notification delivery, identity-provider integration, submission/provisioning state promotion, and DEMO-1 acceptance remain explicitly out of scope and user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

```text
gate=GATE-M7-APPROVAL-UX-INTAKE-LINK-FIXTURE-LOCAL
status=accepted-constrained
scope=apps/desktop-ui::createApprovalWorkflowViewModel extended with optional professorCsvIntakeEvidenceId and cloneReadonlyDryRunPlanId fields; private validatePredecessorReferenceId helper that rejects raw repository URL form (https/http/git@ at boundary), raw email substring (X@Y.Z), raw GitHub PAT prefix (ghp_ / github_pat_ case-insensitive at boundary), and raw URL credential form (://...:...@); null/undefined/empty/whitespace-only inputs normalize to null; apps/desktop-ui::renderApprovalWorkflowScreen extended with a conditional <section aria-label="Predecessor evidence references" data-predecessor-references="true"> block nested inside the existing <section aria-label="No live action notice" role="status" data-no-live-action="true">; the block emits a <dl> with <dt data-kind="professor-csv-intake-evidence">/<dt data-kind="clone-readonly-dry-run-plan"> rows for each non-null field and is omitted when both fields are absent; render-side assertSafeDisplayValue also covers the two new fields so direct render() calls with mutated models still reject raw credential / URL / email values
constraint=live GitHub action, real network round-trip, real git clone/fetch/push/ls-remote execution, real credential resolution / token refresh / rotation / storage modification, repository administration (creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive), real CSV upload UI / drag-and-drop file picker / production deployment, notification delivery, external identity-provider integration, organization administration, submission/provisioning state promotion, DEMO-1 acceptance / working-demonstration approval, desktop screenshot capture, end-to-end interactive accessibility audit, Tauri shell wiring of renderApprovalWorkflowScreen into a live preview surface, dependency on the upstream intake evidence schema beyond the optional id string, and any cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live GitHub action, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real CSV upload UI deployment, Tauri shell wiring, notification delivery, submission/provisioning state promotion, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted M7 approval UX intake-link integration behavior:

- `apps/desktop-ui/src/approvalWorkflow.mjs` exposes `professorCsvIntakeEvidenceId: string | null` and `cloneReadonlyDryRunPlanId: string | null` on the `ApprovalWorkflowViewModel`. Both default to `null` when omitted from the input. Whitespace-only and empty-string inputs normalize to `null`.
- `validatePredecessorReferenceId(value, fieldName)` is a private helper that rejects raw repository URL form (`https?://` or `git@` at a non-letter boundary), raw email substring (`[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}`), raw GitHub PAT prefix (`ghp_` / `github_pat_` case-insensitive at a non-alphanumeric boundary), and raw URL credential form (`://[^/\s]*:[^/\s]*@`); each rejection throws an `Error` with a message that names the offending field.
- `renderApprovalWorkflowScreen` in `apps/desktop-ui/src/approvalWorkflowRender.mjs` extends the existing `assertSafeDisplayValue` invocations to cover both new fields and emits a `<section aria-label="Predecessor evidence references" data-predecessor-references="true">` block when at least one of the two fields is non-null. The block contains a `<dl>` with `<dt data-kind="professor-csv-intake-evidence">Professor CSV intake evidence id</dt><dd>{id}</dd>` and/or `<dt data-kind="clone-readonly-dry-run-plan">Clone-readonly dry-run plan id</dt><dd>{id}</dd>` rows for each non-null field. The block is nested inside the existing `<section aria-label="No live action notice" role="status" data-no-live-action="true">` so the predecessor references are part of the no-live-action announcement.
- When both fields are absent the rendered output is structurally identical to today's: a single no-live-action section, a single decision panel, the dry-run plan preview gated to `approved`, and the existing audit preview / read-only-action panel. All existing `m7-approval-ux-state` / `m7-approval-ux-render` / `m7-approval-ux-harden` tests remain green without modification.

## 3. RED to GREEN evidence

### M7-APPROVAL-UX-INTAKE-LINK-T1 VM extension and defensive guard

```text
RED command:    node apps/desktop-ui/tests/m7-approval-ux-intake-link-state.test.mjs
RED result:     AssertionError: professorCsvIntakeEvidenceId must default to null when input field is absent (actual undefined, expected null)
GREEN command:  node apps/desktop-ui/tests/m7-approval-ux-intake-link-state.test.mjs
GREEN result:   m7_approval_ux_intake_link_state=ok (6 scenarios / 24 assertions pass)
Commit:         64b240b
```

### M7-APPROVAL-UX-INTAKE-LINK-T2 no-live-section render

```text
RED command:    node apps/desktop-ui/tests/m7-approval-ux-intake-link-render.test.mjs
RED result:     AssertionError: 0 !== 1 (missing data-predecessor-references="true" block)
GREEN command:  node apps/desktop-ui/tests/m7-approval-ux-intake-link-render.test.mjs
GREEN result:   m7_approval_ux_intake_link_render=ok (8 scenarios pass)
Commit:         54f6750
```

## 4. Repository-level validation

```text
node apps/desktop-ui/tests/m7-approval-ux-state.test.mjs            -> m7_approval_ux_state=ok
node apps/desktop-ui/tests/m7-approval-ux-render.test.mjs           -> m7_approval_ux_render=ok
node apps/desktop-ui/tests/m7-approval-ux-harden.test.mjs           -> m7_approval_ux_harden=ok combinations=36
node apps/desktop-ui/tests/m7-approval-ux-intake-link-state.test.mjs -> m7_approval_ux_intake_link_state=ok
node apps/desktop-ui/tests/m7-approval-ux-intake-link-render.test.mjs -> m7_approval_ux_intake_link_render=ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check) -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q  -> 6 passed
git diff --check                                                     -> clean
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Both predecessor reference fields default to null when absent from input | `m7-approval-ux-intake-link-state::1. Predecessor reference fields default to null when absent from input` | accepted |
| Redacted predecessor reference ids are carried through the VM unchanged | `m7-approval-ux-intake-link-state::2. Redacted predecessor reference ids are carried through the VM unchanged` | accepted |
| Empty-string inputs normalize to null | `m7-approval-ux-intake-link-state::3. Empty-string inputs normalize to null` | accepted |
| Whitespace-only inputs normalize to null | `m7-approval-ux-intake-link-state::6. Whitespace-only inputs normalize to null (treat as absent rather than reject as raw value)` | accepted |
| Raw HTTPS / HTTP / SSH URL form, raw email substring, GitHub PAT prefix (case-insensitive), fine-grained PAT prefix, and URL credential form are all rejected on each new field | `m7-approval-ux-intake-link-state::4. Defensive guards reject ... eight unsafe fixtures per field` | accepted |
| Existing `sourceRepoUrlHash` raw-URL rejection still throws when the new fields are clean | `m7-approval-ux-intake-link-state::5. Existing behavior remains intact ...` | accepted |
| When both new fields are absent the rendered output does NOT include a predecessor references block | `m7-approval-ux-intake-link-render::1. Absent → render output does NOT include a predecessor-references block` | accepted |
| When only one of the two fields is present, exactly one predecessor block emits with exactly one entry of the appropriate kind | `m7-approval-ux-intake-link-render::2. intakeId only ...`, `3. planId only ...` | accepted |
| When both fields are present, exactly one predecessor block emits with one entry of each kind | `m7-approval-ux-intake-link-render::4. Both → exactly one block containing exactly one entry each` | accepted |
| Predecessor references block is nested INSIDE the no-live-action section and before the request intake section | `m7-approval-ux-intake-link-render::5. Predecessor references block is nested INSIDE the no-live-action section` | accepted |
| Predecessor references section carries `aria-label="Predecessor evidence references"` | `m7-approval-ux-intake-link-render::6. Predecessor references section carries an aria-label` | accepted |
| Render-side `assertSafeDisplayValue` rejects raw repository URL form in `professorCsvIntakeEvidenceId` and raw PAT prefix in `cloneReadonlyDryRunPlanId` even when injected directly into the model | `m7-approval-ux-intake-link-render::7. The render output never echoes the new fields' raw repository URL form / email / PAT` | accepted |
| When both fields are absent, the no-live section still closes before the request intake section starts (structural invariant preserved) | `m7-approval-ux-intake-link-render::8. When both fields are absent ...` | accepted |
| Existing approval UX state / render / harden tests remain green after the extension | regression checks via `m7_approval_ux_state`, `m7_approval_ux_render`, `m7_approval_ux_harden` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live GitHub action, real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote`, or real credential resolution;
- repository administration, real CSV upload UI deployment, drag-and-drop file picker, or production approval workflow deployment;
- Tauri shell wiring of `renderApprovalWorkflowScreen` into a live preview surface (still deferred);
- notification delivery, external identity-provider integration, or organization administration;
- submission/provisioning state promotion from approval-surface state;
- DEMO-1 acceptance or live working-demonstration approval;
- end-to-end interactive accessibility audit, desktop screenshot capture, or screen-reader integration testing;
- a dependency on the upstream intake evidence schema beyond the optional id string (the approval surface treats the predecessor id as an opaque label);
- a cryptographic SHA-256 source-URL audit hash beyond the existing FNV-1a 64 envelope (deferred per `m7-clone-readonly-evidence.md` §7 item 3);
- legal / privacy / compliance authority beyond reapplication of existing controlled redaction rules;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. Wire `renderApprovalWorkflowScreen` into the Tauri/webview shell so a desktop preview surface is observable (carry-over from `m7-approval-ux-evidence.md` §7 item 1 and post-UX queue-refill);
2. Add a fixture-local interactive accessibility hardening pass that exercises keyboard navigation, focus order, and screen-reader text on the predecessor references block; out of scope for this constrained gate;
3. Extract a shared helper module for predecessor-reference defensive guards so the approval VM and the byte-stream scan in `eduops_domain::scan_csv_bytes_for_raw_secrets` can share a single denylist source (currently duplicated for layer-specific reasons);
4. Extend the predecessor references block with additional kinds (e.g., parent approval id, evaluator decision id) when an authorized control update enumerates them;
5. Author the user-managed runbook that prescribes how the professor/course-admin obtains the upstream intake_id and dry-run plan_id before approval, per `EDUOPS-DEC-065`; this is outside Ralph automation and remains user-managed.

## 8. Traceability

- [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md)
- [Professor CSV roster + repository URL intake specification](../02-design-planning/professor-csv-intake-specification.md)
- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [M7 clone-readonly approval workflow UX gate evidence](m7-approval-ux-evidence.md)
- [M7 professor CSV roster + repository URL intake gate evidence](m7-prof-csv-intake-evidence.md)
- [M7 professor CSV byte parser gate evidence](m7-prof-csv-intake-byte-evidence.md)
- [M7 clone-readonly integration-point gate evidence](m7-clone-readonly-evidence.md)
- [Software test description](../03-verification-validation/software-test-description.md) — a future addendum for `STD-M7-APPROVAL-UX-INTAKE-LINK-001..002`
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-002..004`, `EDUOPS-FR-023..024`, `EDUOPS-NFR-004/013/035`
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
