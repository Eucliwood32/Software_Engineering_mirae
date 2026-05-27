---
title: Claude Design Milestone Analysis
document_id: EDUOPS-CLAUDE-MILESTONE-ANALYSIS
version: 0.1.0
status: advisory-review
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
source_tool: Claude Code
source_session_id: 4adcd0c0-52dc-4dc3-ae11-c59ef16d1f89
---

# Claude Design Milestone Analysis

## 1. Review scope

Claude Code performed a read-only advisory review of the EduOps develop repository documentation under `docs/`. The review prioritized requirements, traceability, software design, interface design, executable test cards, fixture gates, implementation-readiness documents, roadmap, risk register, and decision log.

Claude Code was instructed not to edit, write, move, delete, or commit files. The run reached a max-turn boundary during inspection and was resumed with a final-report-only prompt using the same session. Hermes records this report as advisory evidence and uses the resulting milestone structure in [Implementation Milestones](../06-implementation/implementation-milestones.md).

## 2. Current design baseline assessed as sufficient for first implementation milestone

Claude identified the following baseline as sufficient for implementation of the first local skeleton slice:

- Product boundary: Windows-only desktop, Tauri 2 + WebView2 shell, Rust core, TypeScript UI, GitHub clone-only, no LMS, and no live actions before fixture gates.
- Architecture contracts:
  - [Technology stack decision record](../02-design-planning/technology-stack-decision-record.md)
  - [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md)
  - [Module and package layout](../02-design-planning/module-and-package-layout.md)
  - [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md)
  - [Internal API contract](../02-design-planning/internal-api-contract.md)
  - [State machine implementation tables](../02-design-planning/state-machine-implementation-tables.md)
  - [Configuration contract](../02-design-planning/configuration-contract.md)
  - [Credential storage contract](../02-design-planning/credential-storage-contract.md)
  - [Git adapter specification](../02-design-planning/git-adapter-specification.md)
  - [Local storage adapter specification](../02-design-planning/local-storage-adapter-specification.md)
- Test and evidence baseline:
  - [SLICE-A and GH-SLICE-0 executable test cards](../03-verification-validation/slice-a-executable-test-cards.md)
  - [Fixture corpus and harness plan](../03-verification-validation/fixture-corpus-and-harness-plan.md)
  - `run-summary.json` schema and checked-in fixture corpus
- Traceability baseline: [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) covers the SRS FR/NFR set, with implementation-level exactness to be promoted milestone by milestone.

## 3. Non-negotiable constraints identified by Claude

1. No live external action until local fixture gates pass. Evidence must carry `live_external_action=false` until an explicit later live gate is approved.
2. GitHub is clone-only in the current baseline. Repository creation, push, branch protection, webhooks, archive, and administration operations remain blocked.
3. Adapter layers own external side effects. UI and domain layers must not directly call storage, Git, runner, export, or external services.
4. TDD evidence is mandatory. Implemented behavior must link requirement ID, design anchor, STD/test card, recorded RED result, GREEN evidence, and regression/refactor validation.
5. Submission-state promotion is core-owned. Adapter evidence does not directly advance queued, pushed, or confirmed states.
6. Editor JSON is the source of truth; Markdown is a deterministic derived projection with manifest evidence.
7. Configuration is deterministic and hashable; secrets are never stored as raw values.
8. The first implementation loop is bounded to `TC-SLICE-A-001..003` and `TC-GH-000` plus the file list in module/package layout.
9. Official C/C++ grading is outside beta scope; only advisory local runner behavior is permitted before a later gate.
10. Windows-only desktop packaging remains the active target.

## 4. Claude recommendation

Claude recommended starting actual development with the local SLICE-A skeleton, with repository/toolchain bootstrap included as prerequisite scaffolding if not already present.

The reason is that SLICE-A is the smallest implementation cut that proves the runtime contract, adapter boundary, fake-local Git/local filesystem evidence, and no-live-action invariant before editor, roster, runner, export, or GitHub complexity is added.

## 5. Gaps not blocking SLICE-A

Claude found no blocking gap for SLICE-A. The following items should be closed before their corresponding later milestone:

- Editor adapter bridge specification before editor implementation.
- Evaluation runner I/O contract before advisory C/C++ runner implementation.
- Credential adapter implementation choice during configuration/credential milestone before GitHub clone-only work.
- Exporter implementation specification and export fidelity thresholds before DOCX/HWPX export implementation.
- Authorization implementation, rendering pipeline, and observability/diagnostics specifications before submission/review-heavy milestones.
- RTM row status should move from grouped planning coverage to exact implementation evidence as each milestone produces executable tests and evidence.
