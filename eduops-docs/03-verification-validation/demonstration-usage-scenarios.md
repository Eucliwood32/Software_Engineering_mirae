---
title: Demonstration Usage Scenarios
document_id: EDUOPS-DEMONSTRATION-USAGE-SCENARIOS
version: 0.1.0
status: draft
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  related:
    - EDUOPS-IMPLEMENTATION-MILESTONES
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
    - SWENG-EDUTECH-WORKING-DEMO-EVIDENCE-PLAN
---

# Demonstration Usage Scenarios

## 1. Purpose

This document defines controlled usage scenarios for demonstrating EduOps. The scenarios are not marketing scripts. Each scenario states the actor, visible screen flow, backend/evidence expectations, acceptance criteria, and explicit non-claims.

The first executable scenario is `SCN-M1A-001`, aligned with `M1A — Desktop shell demonstration slice`. Later scenarios extend the demonstration toward `DEMO-1` without changing the no-live-action boundary.

## 2. Demonstration boundaries

All scenarios in this document use these controls unless a later approved gate states otherwise:

- Product target: Windows and Linux desktop application using Tauri 2. Windows uses WebView2; Linux uses the Tauri-supported system webview runtime recorded in evidence.
- Frontend: TypeScript UI under `apps/desktop-ui`.
- Backend: Rust Tauri command host and EduOps command/query envelope.
- Mode: fake/local fixture mode.
- External action: `live_external_action=false`.
- Evidence root: `build/evidence/<slice>/<run-id>/`.
- Disallowed: remote Git URL use, GitHub mutation, network request, runner invocation except a later local advisory fixture, exporter invocation except a later local export fixture, raw credential lookup, direct UI filesystem access, and direct UI Git access.

A scenario is accepted only when the user-visible flow and controlled evidence agree.

## 3. Scenario set overview

| Scenario | Level | Actor | Purpose | Gate |
|---|---|---|---|---|
| `SCN-M1A-001` | M1A / DEMO-SLICE-A | Reviewer as instructor/operator | Prove the desktop shell can launch, call backend health, create a local course fixture, and display evidence. | `GATE-UI-SHELL-DEMO-SLICE-A` |
| `SCN-DEMO1-001` | DEMO-1 | Instructor and student | Prove one local fixture assignment workflow from course setup through submission evidence. | Future `GATE-DEMO-1-LOCAL-FIXTURE` |
| `SCN-DEMO1-002` | DEMO-1 | Instructor/TA | Prove review, feedback, and evidence inspection over a completed local submission. | Future `GATE-DEMO-1-REVIEW-FEEDBACK` |
| `SCN-DEMO1-003` | DEMO-1 | Student and instructor | Prove local export preview and derived DOCX/HWPX artifact evidence without treating export as canonical source. | Future `GATE-DEMO-1-EXPORT` |

## 4. SCN-M1A-001 — UI shell local course evidence

### 4.1 Objective

Show the first credible executable UI screen: a Windows desktop shell that connects to the Rust backend through IPC, runs one fake/local SLICE-A course action, and displays evidence that no live external action occurred.

### 4.2 Actors

| Actor | Role in scenario |
|---|---|
| Reviewer | Observes the screen, verifies evidence links, and checks pass/fail criteria. |
| Instructor/operator fixture actor | The selected actor identity in `RequestEnvelope.actor`. |
| Application backend | Validates command/query envelope, executes fake/local course action, emits `ResultEnvelope`, audit event, and evidence. |

### 4.3 Preconditions

- M0 scaffold exists with `apps/desktop`, `apps/desktop-ui`, and `eduops_desktop` package name.
- M1 SLICE-A local skeleton passes or has the required GREEN evidence.
- `TC-UI-SHELL-001` expected RED result was recorded before implementation.
- Windows or Linux desktop evidence-capture environment is named.
- The fixture `fixtures/slice-a/empty-course` or equivalent controlled fixture exists.
- The run identifier is selected before execution.

### 4.4 Screen layout

```text
EduOps Desktop
├── Header
│   ├── product name
│   ├── mode: fake/local
│   ├── live_external_action=false
│   ├── backend health status
│   └── evidence run id
├── Left navigation
│   ├── Demo Home
│   ├── Local Course
│   ├── Evidence
│   └── Diagnostics
├── Main panel: Local Course
│   ├── selected fixture
│   ├── Create local course action
│   ├── ResultEnvelope summary
│   ├── course ID
│   ├── audit event IDs
│   └── fake Git checkpoint/status
└── Evidence panel
    ├── evidence path
    ├── run-summary.json selected fields
    ├── no-live-action assertion
    ├── command log link
    └── screenshot/screen-recording reference
```

### 4.5 User-visible flow

| Step | User action | Expected screen response | Evidence record |
|---|---|---|---|
| M1A-01 | Launch EduOps desktop app. | Shell opens and shows `fake/local` mode. | Startup command log, screenshot frame. |
| M1A-02 | Wait for automatic session/health query. | Header shows backend health as `healthy` or controlled fixture-ready state. | `ResultEnvelope` for health/session query. |
| M1A-03 | Select `Local Course` demo route. | Main panel shows selected empty-course fixture and action button. | Route/navigation observation. |
| M1A-04 | Click `Create local course`. | Button enters progress state, then shows success. | `RequestEnvelope` with `live_external_action=false`; audit event. |
| M1A-05 | Inspect result summary. | Screen displays course ID, audit event ID, evidence path, fake Git checkpoint/status. | `ResultEnvelope`, local storage record, fake Git evidence. |
| M1A-06 | Open `Evidence` panel. | Screen displays selected `run-summary.json` fields and no-live-action assertion. | `run-summary.json`, validation log. |
| M1A-07 | Trigger expected failure fixture. | Screen displays backend error code/message without hiding failure. | Failure `ResultEnvelope`, error code, screenshot. |
| M1A-08 | Reviewer checks diagnostics. | Diagnostics show no remote URL, no network request, no GitHub mutation, no runner/exporter, no raw credential lookup. | No-live-action observation. |

### 4.6 Backend and evidence expectations

The scenario shall create or link the following evidence package:

```text
build/evidence/ui-shell-slice-a/<run-id>/
├── demo-script.md
├── run-summary.json
├── screenshots/
├── screen-recording/
├── commands.log
├── validation.log
├── artifacts/
│   ├── request-envelope-health.json
│   ├── result-envelope-health.json
│   ├── request-envelope-create-course.json
│   ├── result-envelope-create-course.json
│   ├── audit-event-create-course.json
│   ├── local-course-record.json
│   └── expected-failure-result-envelope.json
└── git/
    ├── git-log.txt
    ├── refs.txt
    └── diff-stat.txt
```

`run-summary.json` shall include at least:

```json
{
  "scenario_id": "SCN-M1A-001",
  "gate": "GATE-UI-SHELL-DEMO-SLICE-A",
  "mode": "fake/local",
  "live_external_action": false,
  "ui_capture": {
    "screenshot": "screenshots/m1a-success.png",
    "failure_screenshot": "screenshots/m1a-failure.png"
  },
  "backend": {
    "health_query_status": "ok",
    "create_course_status": "ok"
  },
  "observations": {
    "remote_url_used": false,
    "network_request_observed": false,
    "github_mutation_observed": false,
    "runner_invoked": false,
    "exporter_invoked": false,
    "raw_credential_lookup_observed": false
  }
}
```

### 4.7 Acceptance criteria

`SCN-M1A-001` passes only when:

1. The app launches in the named Windows or Linux desktop evidence-capture environment.
2. The UI renders the shell route and records keyboard focus on the first actionable control.
3. Startup calls backend health/session through IPC.
4. `Create local course` invokes only the backend command/query envelope path.
5. `RequestEnvelope.live_external_action=false` is preserved into backend handling and evidence output.
6. The UI displays local/fake mode, course ID, audit event ID, evidence path, and fake Git checkpoint/status.
7. The UI displays an expected failure `ResultEnvelope` with visible error code/message.
8. Screenshot or screen-recording evidence is linked from `run-summary.json`.
9. No direct UI filesystem, Git, network, runner, exporter, or credential side effects are observed.
10. `TC-UI-SHELL-001..003` pass or the equivalent controlled UI smoke commands are recorded.

### 4.8 Non-claims

Passing this scenario does not claim:

- full student assignment editing;
- instructor roster import;
- live GitHub integration;
- official C/C++ grading;
- DOCX/HWPX export fidelity;
- full accessibility or performance compliance;
- beta readiness.

## 5. SCN-DEMO1-001 — Local fixture assignment workflow

### 5.1 Objective

Show one local fixture workflow from instructor course setup to student submission evidence. This is the first complete DEMO-1 scenario after editor, roster, workspace, and submission slices exist.

### 5.2 Actors

| Actor | Role in scenario |
|---|---|
| Instructor | Creates/imports course, imports roster, publishes assignment instance. |
| Student | Opens assignment, edits workspace, validates, checkpoints, and submits locally. |
| Application backend | Applies authorization, state transitions, local storage, fake Git, and audit evidence. |
| Reviewer | Verifies screen outputs and evidence package. |

### 5.3 Scenario flow

| Step | Actor | User action | Expected screen response | Evidence record |
|---|---|---|---|---|
| D1-01 | Instructor | Open course dashboard. | Course fixture is visible with local/fake mode. | Course fixture record. |
| D1-02 | Instructor | Import privacy-safe roster fixture. | Roster status shows one valid student. | Roster import evidence and validation log. |
| D1-03 | Instructor | Publish one assignment instance. | Assignment appears as released to the section. | Assignment version, release audit, local fake Git evidence. |
| D1-04 | Student | Open student dashboard. | Active assignment appears with due/status indicators. | Student session query. |
| D1-05 | Student | Open assignment viewer. | Read-only instructions/rubric/assets render. | Renderer profile and assignment version. |
| D1-06 | Student | Edit workspace document. | Editor saves canonical JSON and Markdown projection. | `main.eduops.json`, `main.md`, `main.manifest.json`. |
| D1-07 | Student | Run validation. | Validation panel shows pass/warnings. | Validation result JSON. |
| D1-08 | Student | Create checkpoint. | Local history shows checkpoint. | Fake Git checkpoint evidence. |
| D1-09 | Student | Submit locally. | Submission state moves through local fake queued/confirmed states as defined for the fixture. | Submission snapshot and state transition evidence. |
| D1-10 | Reviewer | Open evidence view. | Run summary, artifacts, validation result, and warnings are visible. | `run-summary.json`, screenshots, logs. |

### 5.4 Acceptance criteria

`SCN-DEMO1-001` passes only when:

- instructor and student screens are role-separated;
- student cannot edit `assignment/**` content;
- student editable work is limited to authorized `workspace/**` and, where applicable, `knowledge/**` content;
- canonical editor JSON, Markdown projection, and manifest agree;
- fake Git checkpoint/submission evidence exists;
- submission state labels are not collapsed into an unsupported live confirmation claim;
- all evidence reports `live_external_action=false`.

## 6. SCN-DEMO1-002 — Review and feedback evidence

### 6.1 Objective

Show that an instructor or TA can review a local fixture submission, inspect evidence, draft feedback, and release controlled feedback without silently editing student work.

### 6.2 Scenario flow

| Step | Actor | User action | Expected screen response | Evidence record |
|---|---|---|---|---|
| R1-01 | Instructor/TA | Open progress monitor. | Student submission state and validation/evaluation status are visible. | Progress query evidence. |
| R1-02 | Instructor/TA | Open submission review. | Snapshot, rendered document, Git evidence, and validation result are visible. | Submission snapshot and render evidence. |
| R1-03 | Instructor/TA | Add feedback notes. | Draft feedback is stored separately from student workspace. | Feedback draft audit. |
| R1-04 | Instructor | Release feedback. | Student-visible feedback state changes to released. | Feedback release audit and authorization decision. |
| R1-05 | Student | Open feedback view. | Released feedback and bounded logs are visible. | Student feedback query evidence. |

### 6.3 Acceptance criteria

- Review UI does not silently edit student `workspace/**` or `knowledge/**` content.
- Feedback release requires visible context and authorization evidence.
- Student-visible feedback excludes instructor-only diagnostics unless explicitly allowed.
- Evidence package records authorization decision, release audit, and student-visible result boundary.

## 7. SCN-DEMO1-003 — Export preview and derived artifact evidence

### 7.1 Objective

Show that EduOps can produce local DOCX/HWPX-derived export artifacts from canonical content while preserving the rule that export files are derived evidence, not source of truth.

### 7.2 Scenario flow

| Step | Actor | User action | Expected screen response | Evidence record |
|---|---|---|---|---|
| E1-01 | Student | Open report/export preview. | Canonical assignment/workspace content is previewed. | Canonical source references. |
| E1-02 | Student | Request local export preview. | Export job enters progress state. | Export request envelope with `live_external_action=false`. |
| E1-03 | Backend | Produce derived export fixture. | UI shows artifact path, warnings, and manifest hash. | `export.docx`, `export.hwpx`, `export.manifest.json`. |
| E1-04 | Instructor | Inspect export evidence. | Export warnings/loss categories are visible. | Export validation log and warning report. |

### 7.3 Acceptance criteria

- Export is derived from canonical editor JSON and deterministic Markdown projection.
- Export manifest records tool profile, warning/loss categories, hashes, and source references.
- UI does not imply that DOCX/HWPX is the canonical source.
- No live external converter or network service is invoked unless later approved by a separate gate.

## 8. Demo presenter checklist

Before a reviewer sees a demo, the presenter shall confirm:

- [ ] scenario ID and run ID are selected;
- [ ] Windows or Linux desktop evidence-capture environment is named;
- [ ] fixture data is privacy-safe;
- [ ] mode indicator shows fake/local;
- [ ] `live_external_action=false` appears in UI and evidence;
- [ ] screenshot or screen-recording capture path is ready;
- [ ] expected success and expected failure paths are available;
- [ ] validation command and evidence schema are ready;
- [ ] non-claims are stated before the demo.

## 9. Traceability to existing controls

| Scenario | Related controls |
|---|---|
| `SCN-M1A-001` | [UI Shell Demonstration Test Cards](ui-shell-demo-test-cards.md), [Implementation Milestones](../06-implementation/implementation-milestones.md), [Process Topology and IPC Contract](../02-design-planning/process-topology-and-ipc-contract.md) |
| `SCN-DEMO1-001` | [Working Demonstration and Evidence Plan](working-demonstration-evidence-plan.md), [Student UI Workflow Specification](../02-design-planning/student-ui-workflow-spec.md), [Instructor UI Workflow Specification](../02-design-planning/instructor-ui-workflow-spec.md) |
| `SCN-DEMO1-002` | [Role-Separated UI and Feature Model](../02-design-planning/role-separated-ui-feature-model.md), [Access Control and Authorization Model](../02-design-planning/access-control-authorization-model.md) |
| `SCN-DEMO1-003` | [Student Knowledge System and Export Profile](../02-design-planning/student-knowledge-export-profile.md), [HWP and HWPX Export Strategy](../02-design-planning/hwp-export-strategy.md), [Export Fidelity Acceptance Criteria](../02-design-planning/export-fidelity-acceptance.md) |
