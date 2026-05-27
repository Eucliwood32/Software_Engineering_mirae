---
title: UI Shell Demonstration Test Cards
document_id: EDUOPS-UI-SHELL-DEMO-TEST-CARDS
version: 0.1.0
status: draft
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
source_review: ../00-research-analysis/codex-demo-ui-readiness-analysis.md
---

# UI Shell Demonstration Test Cards

## 1. Purpose

This document defines the first UI-specific executable test cards for the EduOps desktop shell. The cards close the Codex finding that the existing M0/M1 milestones can produce backend evidence without proving a demonstrable Tauri/WebView2 UI.

The scope is local-only. The UI shall use fake/local adapters and shall not perform live external action.

## 2. Shared controls

All UI shell test cards use these controls:

- Product target: Windows and Linux desktop. Windows uses WebView2; Linux uses the platform webview runtime selected by Tauri 2, recorded in the evidence package.
- Shell: Tauri 2 with WebView2.
- Frontend: TypeScript UI under `apps/desktop-ui`.
- Backend: Rust Tauri command host and EduOps command/query envelope.
- Mode: fake/local fixture mode.
- External action flag: `live_external_action=false`.
- Disallowed during these cards: remote Git URL use, GitHub mutation, network request, runner invocation, exporter invocation, raw credential lookup, direct UI filesystem access, and direct UI Git access.

Each UI shell demonstration run should produce or link evidence under the shared evidence convention:

```text
build/evidence/<slice>/<run-id>/
```

For M1A the slice path is:

```text
build/evidence/ui-shell-slice-a/<run-id>/
```

The run shall record a named desktop evidence-capture environment and reviewer/owner before the gate is marked complete. A Windows run shall record WebView2 details. A Linux run shall record distribution, display/session type, and webview runtime details. Either Windows or Linux may close `GATE-UI-SHELL-DEMO-SLICE-A` when all test cards and evidence fields pass.

## 3. TC-UI-SHELL-001 — Desktop shell launch and health query

**Requirement intent.** Prove that the selected desktop stack can launch a real app shell and query backend health through the controlled IPC boundary.

**Preconditions.**

- M0 UI scaffold exists.
- Tauri/WebView2 prerequisite behavior is documented.
- Frontend dependencies are installed or restored by the controlled build command.

**Expected RED.** Before implementation, the Tauri shell cannot launch or the UI cannot query backend health through IPC.

**Test command.**

```text
cargo test -p eduops_desktop --test ui_shell_launch_health
```

or the equivalent controlled UI smoke command recorded in the evidence package.

**GREEN acceptance.**

- Tauri app launches in test or smoke mode.
- UI renders the shell route.
- UI calls the backend session or health query through IPC.
- Backend response is returned as `ResultEnvelope`.
- The rendered UI shows local/fake mode and `live_external_action=false`.
- Runtime contract assertion confirms the UI path preserves `RequestEnvelope.live_external_action=false` into the backend command and evidence record.
- No direct UI filesystem, Git, network, runner, exporter, or credential access is observed.
- Minimal UI smoke records keyboard focus on the first actionable control and a startup/render timing observation; full accessibility and performance validation remain scoped to later role/editor milestones.

**Evidence.**

- command log;
- UI screenshot or captured frame;
- backend health response;
- no-live-action assertion;
- `run-summary.json` reference.

## 4. TC-UI-SHELL-002 — SLICE-A local course action from UI

**Requirement intent.** Prove that a user-visible UI action can invoke the SLICE-A fake/local course path and display controlled evidence.

**Preconditions.**

- M1 SLICE-A local skeleton passes.
- `TC-UI-SHELL-001` passes.
- Empty-course fixture exists.

**Expected RED.** Before implementation, the UI cannot execute the local course action through IPC or cannot display returned evidence.

**Test command.**

```text
cargo test -p eduops_desktop --test ui_slice_a_local_course
```

or the equivalent controlled UI smoke command recorded in the evidence package.

**GREEN acceptance.**

- User action such as `Create local course` invokes the backend command path through `RequestEnvelope`.
- Request evidence records `dry_run` and `live_external_action=false` according to the controlled command contract.
- Backend creates or loads the local fixture course through the storage adapter and fake-local Git adapter.
- UI displays course ID, audit event ID, local evidence path, and fake Git checkpoint/status.
- UI does not expose direct Git or filesystem controls.
- No remote URL, network call, GitHub mutation, runner, exporter, or credential lookup occurs.

**Evidence.**

- UI screenshot or screen recording;
- command/result envelope record;
- audit event record;
- local fake Git evidence;
- `run-summary.json` validation result.

## 5. TC-UI-SHELL-003 — UI evidence view and failure display

**Requirement intent.** Prove that the demo UI can show evidence and controlled failure states without hiding backend errors.

**Preconditions.**

- `TC-UI-SHELL-001` and `TC-UI-SHELL-002` pass.
- At least one success fixture and one expected failure fixture are available.

**Expected RED.** Before implementation, the UI cannot render evidence summary or cannot display backend error code from `ResultEnvelope`.

**Test command.**

```text
cargo test -p eduops_desktop --test ui_evidence_and_failure_display
```

or the equivalent controlled UI smoke command recorded in the evidence package.

**GREEN acceptance.**

- UI displays selected `run-summary.json` fields: mode, `live_external_action`, fixture ID, command ID, evidence path, validation status, and warnings.
- UI displays backend error code and message for the expected failure fixture.
- UI keeps raw logs and internal paths bounded to the evidence view policy.
- Screenshot or screen-recording evidence is linked from `run-summary.json`.
- Fixture validation passes after the UI flow.

**Evidence.**

- success screenshot;
- failure screenshot;
- `run-summary.json` with UI capture references;
- validation command output.

## 6. Gate name

The UI shell demonstration gate is:

```text
GATE-UI-SHELL-DEMO-SLICE-A
```

The gate passes only when `TC-UI-SHELL-001..003` pass, the evidence package records `live_external_action=false`, the runtime contract assertion preserves that value from UI request through backend evidence, and the desktop evidence-capture record names the capture environment, platform runtime details, and reviewer/owner.

## 7. Deferred controls

M1A includes only minimal keyboard-focus and startup/render timing smoke. Full role-separated accessibility validation, editor IME behavior, large-document performance, screen-reader coverage, and packaging installer validation remain deferred to the relevant later milestones and shall not be claimed from M1A evidence.
