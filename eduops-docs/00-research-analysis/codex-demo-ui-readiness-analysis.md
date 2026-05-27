---
title: Codex Demo UI Readiness Analysis
document_id: EDUOPS-CODEX-DEMO-UI-READINESS-ANALYSIS
version: 0.1.0
status: advisory-review
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
source_tool: Codex CLI
source_session_id: 019e24d2-cc16-7f41-b005-e2e373418d23
---

# Codex Demo UI Readiness Analysis

## 1. Review scope

Codex CLI performed a read-only advisory review of whether the current M0..M8 implementation milestones are sufficient to produce a demonstrable user interface for EduOps.

The review inspected the implementation milestone document and related design and verification controls, including:

- [Implementation Milestones](../06-implementation/implementation-milestones.md)
- [Module and Package Layout](../02-design-planning/module-and-package-layout.md)
- [Process Topology and IPC Contract](../02-design-planning/process-topology-and-ipc-contract.md)
- [Technology Stack Decision Record](../02-design-planning/technology-stack-decision-record.md)
- [Working Demonstration and Evidence Plan](../03-verification-validation/working-demonstration-evidence-plan.md)

An initial Codex read-only sandbox run could not inspect files because the local Linux sandbox failed before shell execution. The review was rerun with the Codex documented sandbox bypass under an explicit read-only prompt. No tracked files were modified by Codex.

## 2. Verdict

The current M0..M8 milestone structure is **insufficient** to guarantee a demonstrable UI.

The milestones are sufficient to drive local backend and evidence implementation, but they do not require an executable Tauri application, TypeScript UI shell, WebView2 prerequisite check, UI-to-Rust IPC smoke test, screenshot or screen-recording evidence, UI accessibility/performance smoke checks, or a user-visible local-fixture flow.

## 3. Findings

1. M0 requires Cargo workspace, Rust toolchain, crate stubs, fixture corpus, and baseline build/test commands. It does not require `apps/desktop`, `apps/desktop-ui`, frontend buildability, or Tauri shell launch.
2. M1 proves the SLICE-A storage, fake-local Git, evidence, and no-live-action path. It does not require a UI artifact.
3. The planned source tree includes `apps/desktop` and `apps/desktop-ui`, but the current SLICE-A allowed file enumeration excludes those paths.
4. The demonstration plan states that a credible demonstration requires user-visible flow, backend/application evidence, and repository/evidence artifacts. A screen alone is not enough, and backend evidence alone is not enough for a desktop product demonstration.
5. M8 assembles DEMO-1 evidence, but deferring UI execution until that point creates late discovery risk for Tauri/WebView2 packaging, frontend build, IPC shape, and demo capture.

## 4. Required milestone change

Codex recommends adding an early `M1A — Desktop shell demonstration slice` after M1 and before M2.

M0 should also include UI scaffold outputs:

- `apps/desktop` Tauri 2 shell scaffold;
- `apps/desktop-ui` TypeScript UI scaffold;
- pinned Node/package-manager record;
- WebView2 runtime prerequisite check documented for Windows;
- baseline frontend typecheck/build and Tauri launch/build smoke commands where applicable.

## 5. Minimal demo UI slice

The earliest credible demo UI is `M1A`, after M1 backend/evidence behavior exists.

The minimal screen flow is:

1. Launch the Windows Tauri/WebView2 desktop app.
2. Show local/fake mode and `live_external_action=false`.
3. Load the SLICE-A empty-course fixture.
4. Execute a user action such as `Create local course`.
5. Receive a backend `ResultEnvelope` and display course ID, audit event ID, evidence path, and fake Git checkpoint/status.
6. Display selected `run-summary.json` fields in an evidence view without exposing direct Git or filesystem control.
7. Validate that no remote URL, network call, GitHub mutation, runner, exporter, or live credential lookup occurred.

This is a credible DEMO-SLICE-A UI. It is not the full DEMO-1 scenario, which still requires later editor, roster, submission, evaluation, review, and export slices.

## 6. Acceptance criteria for M1A

M1A should pass only when:

- `apps/desktop` launches on Windows with Tauri 2 and WebView2.
- `apps/desktop-ui` typecheck and production build pass.
- UI startup calls backend session or health query through IPC.
- UI action executes only the fake/local SLICE-A command path.
- `RequestEnvelope.live_external_action=false` is present in request and evidence records.
- UI has no direct filesystem, Git, network, runner, exporter, or credential side effects.
- UI displays success and failure states from `ResultEnvelope`, including a user-visible error code.
- screenshot or screen-recording evidence is saved under the demo evidence package.
- `run-summary.json` links UI capture, command log, audit file, local Git status, and manifest hash.
- fixture validation passes after the UI flow.

The M0 and M1A corrections in [Implementation Milestones](../06-implementation/implementation-milestones.md), [Module and Package Layout](../02-design-planning/module-and-package-layout.md), and [UI Shell Demonstration Test Cards](../03-verification-validation/ui-shell-demo-test-cards.md) address the immediate M0/M1 UI-readiness finding by adding desktop/UI scaffold, frontend build, Tauri/WebView2 launch, IPC, captured UI evidence, and runtime no-live-action controls before M2 expansion.

## 7. Disposition

The implementation milestones should be revised before starting product-code implementation so that the first visible desktop shell risk is closed immediately after SLICE-A backend evidence, not at the final demo packaging milestone.
