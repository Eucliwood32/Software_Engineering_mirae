---
title: M7 Clone-Readonly Approval Workflow UX Gate Evidence
document_id: EDUOPS-M7-APPROVAL-UX-EVIDENCE
version: 0.2.0
status: accepted-constrained
date: 2026-05-16
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-CLONE-READONLY-APPROVAL-UX-SPEC
    - SWENG-EDUTECH-GITHUB-CLONE-READONLY-INTEGRATION-POINT-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SDD
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
  decisions:
    - EDUOPS-DEC-064
    - EDUOPS-DEC-065
  tests:
    - apps/desktop-ui/tests/m7-approval-ux-state.test.mjs
    - apps/desktop-ui/tests/m7-approval-ux-render.test.mjs
    - apps/desktop-ui/tests/m7-approval-ux-harden.test.mjs
---

# M7 Clone-Readonly Approval Workflow UX Gate Evidence

## 1. Gate result

`GATE-M7-APPROVAL-UX-FIXTURE-LOCAL` is accepted-constrained for the fixture-local approval workflow UX state model (M7-APPROVAL-UX-T1), the deterministic clone-readonly approval review screen render (M7-APPROVAL-UX-T2), and the role × status coverage matrix plus structural HTML invariant audit (M7-APPROVAL-UX-HARDEN-T1) defined by [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md). Real human approval workflow deployment, real credential resolution, live GitHub network access, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, repository administration, notification delivery, external identity-provider integration, submission/provisioning state promotion, and DEMO-1 acceptance are explicitly out of scope and remain user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

```text
gate=GATE-M7-APPROVAL-UX-FIXTURE-LOCAL
status=accepted-constrained
scope=ApprovalWorkflowViewModel fixture-local state model (createApprovalWorkflowViewModel / getApprovalActions / summarizeCloneInputMode) covering role/status/action matrix for student/instructor/ta/course_admin/platform_admin/evaluator and approval_status pending_review/approved/denied/blocked/expired; redacted display fields (source_repo_url_hash 16-hex envelope only, credential_fingerprint_hint redacted, no raw URL/email/SSN/long-digit identifiers); hardcoded externalCallMade=false / githubMutationMade=false / cloneReadonlyExecuted=false / rawSecretObserved=false / rawRepositoryUrlDisplayed=false / remoteConfigurationAllowed=false / credentialLookupAllowed=false / studentCloneDelegatedToEduOps=false flags; runtimeBoundary=user-managed-github; clone-input modes professor_csv (csvRepositoryUrlField default github_repository_url, localCheckoutPathRequired=false) and student_local_checkout (localCheckoutPathRequired=true, localCheckoutPathLabel supplied); renderApprovalWorkflowScreen producing deterministic HTML for six screen states (no-live-action notice with Korean banner plus English user-managed GitHub boundary text and role=status, request intake summary, review panel with non-color-only status badge, decision panel enabling approve/deny/request-more-info only for course_admin/platform_admin under pending_review and disabling otherwise with data-state status-not-pending or not-authorized-or-blocked, dry-run plan preview visible only when approved with hardcoded false literals, audit preview list, optional read-only-action panel) plus pre-render guards rejecting non-false no-live flags, non-user-managed-github boundary, non-clone-only operation class, GitHub PAT prefix (ghp_/github_pat_), URL credential form (://user:token@), raw repository URL (^https?://), email-like, or long-digit run in any text-bearing display field
constraint=real human approval workflow deployment, role administration, real credential resolution / token refresh / rotation / storage modification, raw token rendering, live GitHub API readiness, real network round-trip, real git clone/fetch/push/ls-remote execution, repository administration (creation/push/branch/tag/issue/webhook/check-run/invitation/branch-protection/archive), notification delivery, external identity-provider integration, submission/provisioning state promotion, DEMO-1 acceptance / working-demonstration approval, fidelity / privacy / legal policy authority, desktop screenshot capture, and end-to-end interactive accessibility audit are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

This evidence does not claim a live GitHub clone, a real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, real credential resolution, real human approval workflow deployment, real notification delivery, submission/provisioning state promotion, or DEMO-1 acceptance.

## 2. Implemented acceptance scope

Accepted M7 approval workflow UX behavior:

- `apps/desktop-ui/src/approvalWorkflow.mjs` defines `createApprovalWorkflowViewModel(input)` returning a deterministic `ApprovalWorkflowViewModel` with workflow id, actor role, approval status, clone-input mode, source repository hash (validated as 16-hex envelope only via `validateHashEnvelope`), requested ref, hardcoded `operationClass='clone-only'`, credential reference status, optional redacted credential fingerprint hint, privacy decision count, blocking reasons list, derived `availableActions` array, deterministic `auditPreviewIds=[audit_clone_readonly_approval_<workflow_id>]`, `runtimeBoundary='user-managed-github'`, Korean `사용자 관리 GitHub` no-live banner, and hardcoded `externalCallMade=false`/`githubMutationMade=false`/`cloneReadonlyExecuted=false`/`rawSecretObserved=false`/`rawRepositoryUrlDisplayed=false`/`remoteConfigurationAllowed=false`/`credentialLookupAllowed=false`/`studentCloneDelegatedToEduOps=false`.
- `getApprovalActions(actorRole, approvalStatus)` returns the role/status/action matrix from [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md) §4: `course_admin`/`platform_admin` may approve/deny/request-more-info under `pending_review`, view-approval/copy-evidence-id under `approved`, and view-reason under `denied`/`blocked`/`expired`; `instructor` may view-pending-status under `pending_review`, view-approved-dry-run-plan-summary under `approved`, and view-reason under `denied`/`blocked`/`expired`; `ta`/`evaluator` may view-pending-status (TA only) / view-approved-summary / view-reason as applicable; `student` has no approval actions.
- `summarizeCloneInputMode(model)` produces a deterministic string describing the active clone input mode: `professor_csv` references the CSV repository URL field name and notes URLs are redacted or hashed in evidence; `student_local_checkout` notes the student has already cloned the repository and EduOps runs in the supplied local checkout path label.
- `cloneInputFields(input)` derives mode-specific fields: `professor_csv` sets `csvRosterFieldCount`, defaults `csvRepositoryUrlField='github_repository_url'`, `localCheckoutPathRequired=false`, and `inputModeLabel='Professor CSV roster and repository URL intake'`; `student_local_checkout` zeroes CSV fields, sets `localCheckoutPathRequired=true`, defaults `localCheckoutPathLabel='student-local-checkout'`, and `inputModeLabel='Student supplied pre-cloned local checkout'`; unknown modes throw.
- `apps/desktop-ui/src/approvalWorkflowRender.mjs` exposes `renderApprovalWorkflowScreen(model)` returning a deterministic HTML string composed of an `<article>` wrapper with `data-no-live-action="true"`/`data-runtime-boundary="user-managed-github"`/`data-approval-status=<status>`/`data-workflow-id=<workflow_id>` plus six sections: (1) no-live-action notice with `role="status"`, the Korean `사용자 관리 GitHub` banner, and the English user-managed GitHub boundary text describing that EduOps does not configure remotes, resolve credentials, run `git clone`/`git fetch`/`git push`, or perform repository administration on the user's behalf; (2) request intake summary with workflow id, actor role, operation class, redacted source repository hash, requested ref, clone-input-mode label, and privacy-decision count; (3) review panel with status badge using `aria-hidden="true"` symbol glyph plus textual label (non-color-only indicator), credential reference status, redacted credential fingerprint hint, and blocking reasons list; (4) decision panel containing approve/deny/request-more-info buttons with `aria-label` plus `data-state` and `aria-disabled`/`disabled` reflecting whether the actor's `availableActions` admit the action under the current status; (5) dry-run plan preview gated to `data-visible="true"` only when status is `approved` and displaying hardcoded `external_call_made`/`github_mutation_made`/`clone_readonly_executed`/`raw_secret_observed=false` literals; (6) audit preview list of deterministic `audit_clone_readonly_approval_<workflow_id>` ids; plus a conditional read-only-action panel for view-pending-status / view-approval / copy-evidence-id / view-approved-dry-run-plan-summary / view-approved-summary / view-reason actions.
- Render-time safety guards reject any model that mutates any of `externalCallMade`/`githubMutationMade`/`cloneReadonlyExecuted`/`rawSecretObserved`/`rawRepositoryUrlDisplayed`/`remoteConfigurationAllowed`/`credentialLookupAllowed`/`studentCloneDelegatedToEduOps` to non-false, sets `runtimeBoundary` to anything other than `user-managed-github`, sets `operationClass` to anything other than `clone-only`, or carries a GitHub PAT prefix (`ghp_`/`github_pat_`), URL credential form (`://user:token@`), raw repository URL (`^https?://`), email-like pattern (`[\w.+-]+@[\w.-]+\.[\w.-]+`), or long-digit run (`\d{6,}`) in any text-bearing display field (workflow id, actor role, requested ref, credential fingerprint hint, CSV repository URL field name, local checkout path label, blocking reasons, audit preview ids). All HTML output is escaped via a local `escapeHtml` helper.

## 3. RED to GREEN evidence

### M7-APPROVAL-UX-T1 approval workflow state model

```text
RED command:    node apps/desktop-ui/tests/m7-approval-ux-state.test.mjs
RED result:     ERR_MODULE_NOT_FOUND for missing apps/desktop-ui/src/approvalWorkflow.mjs
GREEN command:  node apps/desktop-ui/tests/m7-approval-ux-state.test.mjs
GREEN result:   m7_approval_ux_state=ok
Commit:         5f69556
```

### M7-APPROVAL-UX-T2 clone-readonly approval review screen render

```text
RED command:    node apps/desktop-ui/tests/m7-approval-ux-render.test.mjs
RED result:     ERR_MODULE_NOT_FOUND for missing apps/desktop-ui/src/approvalWorkflowRender.mjs
GREEN command:  node apps/desktop-ui/tests/m7-approval-ux-render.test.mjs
GREEN result:   m7_approval_ux_render=ok
Commit:         276919e
```

### M7-APPROVAL-UX-HARDEN-T1 role × status coverage matrix and structural HTML audit

```text
RED command:    node apps/desktop-ui/tests/m7-approval-ux-harden.test.mjs
RED result:     the initial test fixture generator produced a hash with a 10-digit run; the existing render's defensive long-digit-run guard correctly rejected the unsafe fixture before any structural assertion ran
GREEN command:  node apps/desktop-ui/tests/m7-approval-ux-harden.test.mjs
GREEN result:   m7_approval_ux_harden=ok combinations=36
Commit:         eac68d6
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> cargo check --workspace finished; desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok path=fixtures/slice-a
cargo test --workspace                                                     -> all test target groups report ok (no new Rust tests in this slice; existing M0..M8 + M7-MOCKHTTP + M7-CLONE-READONLY totals all green)
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
node apps/desktop-ui/tests/m7-approval-ux-state.test.mjs                   -> m7_approval_ux_state=ok
node apps/desktop-ui/tests/m7-approval-ux-render.test.mjs                  -> m7_approval_ux_render=ok
node apps/desktop-ui/tests/m7-approval-ux-harden.test.mjs                  -> m7_approval_ux_harden=ok combinations=36
git diff --check                                                           -> clean
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| `ApprovalWorkflowViewModel` validates `sourceRepoUrlHash` as a 16-hex redacted envelope and rejects raw repository URL form | `m7-approval-ux-state.test.mjs` — assertion that raw `https://github.com/example/raw-url.git` input throws `sourceRepoUrlHash must be a redacted hash envelope` | accepted |
| Role/status/action matrix matches UX specification §4 | `m7-approval-ux-state.test.mjs` — `course_admin/pending_review → [approve, deny, request-more-info]`; `ta/pending_review → [view-pending-status]`; `student/pending_review → []`; `course_admin/blocked → [view-reason]` | accepted |
| Hardcoded non-live and user-managed boundary flags remain false | `m7-approval-ux-state.test.mjs` — assertions on `externalCallMade`/`githubMutationMade`/`cloneReadonlyExecuted`/`rawSecretObserved`/`rawRepositoryUrlDisplayed`/`remoteConfigurationAllowed`/`credentialLookupAllowed`/`studentCloneDelegatedToEduOps` all false | accepted |
| Professor CSV clone-input mode exposes deterministic field names without rendering raw URLs | `m7-approval-ux-state.test.mjs` — `csvRepositoryUrlField='github_repository_url'`; `localCheckoutPathRequired=false`; `summarizeCloneInputMode` returns CSV-mode summary | accepted |
| Student pre-cloned local-checkout mode requires `localCheckoutPathLabel` and does not delegate clone to EduOps | `m7-approval-ux-state.test.mjs` — `localCheckoutPathRequired=true`; `localCheckoutPathLabel='student-local-checkout'`; `studentCloneDelegatedToEduOps=false`; `summarizeCloneInputMode` returns local-checkout summary | accepted |
| Korean `사용자 관리 GitHub` no-live banner is rendered as a status-region notice | `m7-approval-ux-render.test.mjs` — regex `<section [^>]*aria-label="No live action notice"`, `role="status"`, `사용자 관리 GitHub`, `User-managed GitHub boundary`, `data-runtime-boundary="user-managed-github"`, `data-no-live-action="true"` | accepted |
| Request intake summary displays redacted source hash without raw URL | `m7-approval-ux-render.test.mjs` — regex `Source repository hash \(redacted\)`, `a1b2c3d4e5f60718`; `doesNotMatch /https?:\/\//` | accepted |
| Review panel uses non-color-only status badge with `aria-hidden="true"` symbol plus textual label | `m7-approval-ux-render.test.mjs` — regex `data-status="pending_review"`, `aria-hidden="true">…`, `Pending review` label | accepted |
| Decision panel enables approve/deny/request-more-info only for `course_admin`/`platform_admin` under `pending_review` and disables otherwise | `m7-approval-ux-render.test.mjs` — pending+course_admin sees `id="action-approve"[^>]*aria-disabled="false"`; pending+ta sees `data-state="not-authorized-or-blocked"` and `aria-disabled="true"`; approved+course_admin sees `data-state="status-not-pending"` and `aria-disabled="true"`; blocked+course_admin forces approve disabled | accepted |
| Dry-run plan preview is hidden until approval and then displays hardcoded false literals | `m7-approval-ux-render.test.mjs` — pending sees `data-visible="false"`; approved sees `data-visible="true"` plus `external_call_made[\s\S]*?false`, `github_mutation_made[\s\S]*?false`, `clone_readonly_executed[\s\S]*?false` | accepted |
| Audit preview list contains deterministic `audit_clone_readonly_approval_<workflow_id>` id | `m7-approval-ux-render.test.mjs` — regex `audit_clone_readonly_approval_wf_m7_professor_csv_001` | accepted |
| Read-only action panel surfaces view-pending / view-approval / copy-evidence-id / view-reason for non-decision contexts | `m7-approval-ux-render.test.mjs` — TA pending sees `data-action="view-pending-status"`; approved+course_admin sees `data-action="view-approval"` and `data-action="copy-evidence-id"`; denied+instructor sees `data-action="view-reason"` | accepted |
| Render output is deterministic across repeated invocation on the same model | `m7-approval-ux-render.test.mjs` — `renderApprovalWorkflowScreen(approvedAdmin) === renderApprovalWorkflowScreen(approvedAdmin)` | accepted |
| Render refuses to display raw PAT, URL credential form, or raw repository URL in any field | `m7-approval-ux-render.test.mjs` — `credentialFingerprintHint='ghp_…'` throws `raw credential`; `requestedRef='https://github.com/example/leak.git'` throws `raw repository URL` | accepted |
| Render refuses to emit when no-live flags or runtime boundary or operation class are mutated | `m7-approval-ux-render.test.mjs` — `externalCallMade=true`, `runtimeBoundary='live-github'`, and `operationClass='push'` each throw | accepted |
| Full 6 actor roles × 6 approval statuses (36 combinations) plus student pre-cloned local-checkout fixture render deterministically with consistent structural HTML invariants | `m7-approval-ux-harden.test.mjs` — assertion `combinations=36`; per-fixture invariants: single `<article>` with `data-no-live-action="true"`/`data-runtime-boundary="user-managed-github"`/`data-approval-status=<status>`/`data-workflow-id=<id>`; single no-live-action section with `role="status"` and Korean banner + English boundary text; single decision panel with `role="group"`; approve/deny/request-more-info buttons each appearing exactly once with `aria-label`/`data-action`/`aria-disabled`/`data-state`; dry-run plan visible only when approved; deterministic audit id `audit_clone_readonly_approval_<workflow_id>`; every `<button>` carries `aria-label`/`data-action`; no GitHub PAT prefix, URL credential form, raw repository URL, email-like, or 6+ digit run in per-fixture output or aggregated corpus | accepted |
| Decision-triad enabled/disabled state matches role and status policy across all 36 combinations | `m7-approval-ux-harden.test.mjs` — when `status='pending_review'` and the role admits the action, `aria-disabled="false"`/`data-state="enabled"`; when `status='pending_review'` but the role does not admit, `aria-disabled="true"`/`data-state="not-authorized-or-blocked"`; otherwise `aria-disabled="true"`/`data-state="status-not-pending"` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live GitHub clone, real network round-trip, real `git clone`/`git fetch`/`git push`/`git ls-remote` execution, or real authentication handshake;
- production deployment of the approval workflow surface, role administration, or instructor approval surface UX wiring beyond the fixture-local state model and deterministic HTML render;
- real credential resolution, raw token rendering, credential issuance / refresh / rotation, or credential storage modification;
- external identity-provider integration, notification delivery, email/SMS dispatch, or organization administration;
- repository creation, push, branch/tag creation, pull request, issue, webhook, status, check-run, invitation, branch protection, archive, or any GitHub administration action;
- submission-state or provisioning-state promotion from approval evidence;
- desktop screenshot capture, Tauri/webview interactive shell wiring, keyboard-navigation interactive testing, font/style profile selection, or end-to-end interactive accessibility audit (e.g., axe-core/screen-reader live testing);
- localization framework adoption beyond the current literal Korean/English strings used in the no-live banner and boundary notice;
- DEMO-1 acceptance, working-demonstration approval, fidelity / privacy / legal policy authority, or live evidence closure;
- live external action of any kind.

## 7. Follow-up

The following follow-up items remain candidates for safe Ralph or user-managed work after this gate:

1. wire `renderApprovalWorkflowScreen` output into the existing Tauri/webview shell so the fixture states are observable from a local desktop window without altering the no-live boundary;
2. add fixture-local interactive accessibility hardening (keyboard focus order assertion, screen-reader label test) that does not require a live desktop capture;
3. extend the professor CSV intake to a fixture-local CSV parser + repository-URL validator specification/test that scrubs raw URLs into redacted hashes before they reach the approval UX or any subsequent evidence;
4. extend the student pre-cloned local-checkout mode with a fixture-local local-repository status reader specification/test that asserts EduOps never invokes `git clone`/`git fetch`/`git push` and never reads credentials on the student's behalf;
5. record an authorized human approval workflow live-run runbook covering production deployment, identity-provider wiring, notification delivery, and live approval signing before any live clone-readonly invocation may consume this UX; this is outside Ralph automation and remains user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

## 8. Traceability

- [Clone-readonly human approval workflow UX specification](../02-design-planning/clone-readonly-approval-workflow-ux-specification.md)
- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub adapter software design description](../02-design-planning/github-adapter-software-design-description.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [Software test description](../03-verification-validation/software-test-description.md) — STD-M7-APPROVAL-UX-001..004 plus STD-086/088/089/091 cross-references
- [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) — `EDUOPS-FR-023..026`, `EDUOPS-FR-050`, `EDUOPS-NFR-004/010/013/035`
- [M7 clone-readonly integration-point gate evidence](m7-clone-readonly-evidence.md)
- [M7 mock-http fixture replay gate evidence](m7-mockhttp-evidence.md)
- [M7 SLICE-F GitHub clone-only adapter gate evidence](m7-slice-f-github-clone-only-evidence.md)
- [Implementation milestones](implementation-milestones.md)
- [Decision log](../05-decisions/decision-log.md) — `EDUOPS-DEC-064` and `EDUOPS-DEC-065`
