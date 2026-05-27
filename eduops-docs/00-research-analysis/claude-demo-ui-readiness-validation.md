---
title: Claude Demo UI Readiness Validation
document_id: EDUOPS-CLAUDE-DEMO-UI-READINESS-VALIDATION
version: 0.1.0
status: advisory-review
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
source_tool: Claude Code
source_session_id: be354112-eaf0-42cc-ad2c-4bf81a377676
validated_review: codex-demo-ui-readiness-analysis.md
---

# Claude Demo UI Readiness Validation

## 1. Review scope

Claude Code performed a read-only validation review of the Codex-derived UI-readiness conclusion and the documentation changes that introduced the M1A desktop shell demonstration gate.

The review inspected the Codex analysis, UI shell test cards, implementation milestones, module layout, productization roadmap, working demonstration plan, technology stack decision, and process topology/IPC contract.

Claude Code was instructed not to edit, create, delete, or commit files. Hermes records this document as advisory validation evidence and applies the non-blocking findings as controlled documentation corrections.

## 2. Verdict

Claude returned:

```text
PASS_WITH_FINDINGS
```

The Codex verdict is correct. The previous M0..M8 structure was insufficient to guarantee a demonstrable UI because it could complete SLICE-A backend and evidence work without launching the desktop shell, building the TypeScript UI, proving IPC, or capturing UI evidence.

Claude also concluded that adding `M1A — Desktop shell demonstration slice` after M1 and before M2 adequately closes the immediate UI-readiness gap for the first slice.

## 3. Validation findings

1. M0 and M1 previously did not force an executable Tauri/WebView2 app, TypeScript build, IPC smoke call, or captured UI evidence.
2. M1A is correctly positioned after M1 backend/evidence behavior and before configuration, credential, editor, roster, and export expansion.
3. `TC-UI-SHELL-001..003` and `GATE-UI-SHELL-DEMO-SLICE-A` are sufficient first controls because they cover launch plus IPC health, user-visible SLICE-A action, evidence view, and controlled failure display.
4. The M1A gate has no material contradiction with no-live-action policy, GitHub clone-only boundary, Windows/Tauri/WebView2 target, or adapter isolation.
5. Remaining findings are non-blocking but should be closed before the first product-code implementation loop.

## 4. Non-blocking findings and disposition

| Finding | Disposition |
|---|---|
| Evidence path conventions were split across `build/evidence/slice-a/local-skeleton/`, `build/evidence/ui-shell/slice-a/`, and `build/demo-runs/<run-id>/`. | Closed in follow-up documentation: use `build/evidence/<slice>/<run-id>/` as the common evidence root; DEMO-1 uses `build/evidence/demo-1/<run-id>/`. |
| Test command used `eduops_desktop` without pinning that package name in the module layout. | Closed: the Tauri shell package name is pinned as `eduops_desktop` in the module/package layout. |
| Codex analysis described M0 UI scaffold absence but did not explicitly note the corrective disposition. | Closed: the Codex analysis records that M0 and M1A now close the immediate finding. |
| Accessibility/performance smoke was mentioned but not scoped. | Closed at M1A level: minimal keyboard-focus and startup/render timing smoke are required; full accessibility/performance validation is deferred to later role/editor milestones. |
| M1A allowed a documented Windows prerequisite blocker without naming evidence-capture responsibility. | Closed: the UI shell gate requires named Windows evidence capture environment and reviewer/owner before completion. |
| `live_external_action=false` was checked in evidence but not called out as a runtime contract assertion. | Closed: runtime assertion is required in the UI shell gate/test-card expectations. |

## 5. Final recommendation

The M1A gate can stand as the next controlled milestone correction. It closes the demonstrable-UI gap identified by Codex while preserving local-only fixture mode, GitHub clone-only behavior, and the Windows/Tauri/WebView2/Rust/TypeScript target.

The non-blocking findings have been closed as controlled documentation corrections before the first product-code Ralph loop begins. The M1A gate remains accepted as the next controlled milestone correction.
