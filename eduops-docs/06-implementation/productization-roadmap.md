---
title: Productization Roadmap
document_id: SWENG-EDUTECH-ROADMAP
version: 0.5.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Productization Roadmap

## 1. Purpose

This roadmap converts the pre-development baseline into implementation increments while preserving ISO-oriented traceability and no-live-action-before-fixture-gates discipline.

## 2. Increment plan

| Increment | Goal | Key outputs | Gate |
|---|---|---|---|
| INC-0 | Documentation and fixture skeleton | SDD, IDD, STD, UI specs, RBAC, access-control model, rendering fixtures | Link/check/traceability pass |
| INC-1 | Local course/roster/provisioning MVP | Local DB/index, roster import, student lifecycle, fake Git backend | STD-001..STD-005 pass |
| INC-2 | Student workspace MVP | Assignment viewer, workspace editor, checkpoint, local sync states | STD-007..STD-010 pass |
| INC-3 | Submission/evidence MVP | Submission branch/tag/metadata, queued/confirmed state simulator | STD-011..STD-013 pass |
| INC-4 | Rendering MVP | Graph/table/image fixtures, HTML5/SVG path, snapshot/export evidence | STD-021..STD-023 pass |
| INC-5 | C/C++ evaluation MVP | Toolchain profile, compile/run/static-analysis harness, resource limits | STD-014..STD-016 pass |
| INC-6 | Review/feedback/export MVP | TA/instructor review, release, grade/audit export | STD-017..STD-024 pass |
| INC-7 | GitHub clone-only integration | GitHub clone adapter, source allowlist, token-reference checks, clone evidence | Local fixture gates plus approved clone-readonly connector review |

## 3. Implementation-readiness gate

Before coding beyond spikes, the project needs:

1. selected UI/rendering/runtime stack in [Technology stack decision record](../02-design-planning/technology-stack-decision-record.md);
2. selected Git library/adapter strategy in the same stack decision and later adapter contract;
3. process topology and IPC in [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md);
4. initial schema definitions in [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md);
5. command/query signatures in [Internal API contract](../02-design-planning/internal-api-contract.md);
6. source tree/dependency controls in [Module and package layout](../02-design-planning/module-and-package-layout.md);
7. local fixture repository topology and gates in [Fixture corpus and harness plan](../03-verification-validation/fixture-corpus-and-harness-plan.md);
8. state/time/conflict rules in [State machine implementation tables](../02-design-planning/state-machine-implementation-tables.md);
9. no-live-GitHub side effects until local harness passes.

## 4. First recommended sprint

Build a local-only EduOps vertical slice:

```text
Course fixture -> roster import -> student provision -> assignment view -> workspace edit
-> graph/table/image render -> checkpoint -> submit to local Git branch -> evidence receipt
```

This proves the product core before live GitHub or full evaluation automation.

## 7. Claude review gap-closure implementation gates

Before coding the classroom pilot, the roadmap shall add implementation spikes for editor stack/block schema, knowledge topology, HWPX export, evaluation runner sandbox, canonical state machines, roster schema, GitHub feasibility, performance budget, Korean text handling, accessibility, and repository retention. These gates precede any live classroom deployment or production KPI claim.

## 11. Codex/Claude implementation executability gate

The roadmap is revised by Codex/Claude/Hermes review findings. Implementation shall not proceed directly from SRS/SDD/STD into production code. The first phase is a controlled implementation-executability phase:

1. Produce and review P0 documents: `technology-stack-decision-record.md`, `process-topology-and-ipc-contract.md`, `module-and-package-layout.md`, `canonical-domain-idl.md`, `internal-api-contract.md`, `fixture-corpus-and-harness-plan.md`, and `state-machine-implementation-tables.md`.
2. Produce P1 adapter/harness documents before ending SLICE-A/B: Git adapter, local storage adapter, editor adapter bridge, evaluation runner I/O, GitHub clone adapter, fixture corpus, and build/packaging baseline.
3. Implement vertical slices in order: SLICE-A empty skeleton, SLICE-B editor canonical path, SLICE-C roster/identity, SLICE-D assignment sync/submission, SLICE-E C/C++ advisory runner, SLICE-F GitHub clone-readonly, SLICE-G export fixture.

Live GitHub, live classroom, and official evaluation side effects remain blocked until local fixture gates pass.

## 5. Working demonstration roadmap

Before product-readiness claims, EduOps should pass DEMO-1 using local fixtures only. DEMO-1 should be implemented as an evidence-producing harness after P0 implementation contracts are accepted. It should prove the vertical thread from course/roster fixture through editor storage, Git checkpoint/submission snapshot, advisory evaluation, review evidence, and derived export. DEMO-0 screen prototypes remain useful for discussion but are not sufficient evidence of working behavior.


## 12. Ralph-loop readiness boundary

Before a product-code Ralph loop begins, EduOps shall close the findings in [Ralph Loop Readiness Review](../00-research-analysis/ralph-loop-readiness-review.md). The next autonomous loop is limited to documentation/test-card closure: executable SLICE-A/GH-SLICE-0 test cards, fixture/harness schema, build/dev command baseline, and gap-register reconciliation.


## 13. First implementation-loop entry candidate

The first candidate product-code Ralph loop is limited to `TC-SLICE-A-001..003` and `TC-GH-000`. The expected result artifact is a fake/local evidence package under `build/evidence/` with `live_external_action=false`, no remote URL, fixture hashes, audit records, and local commit evidence.

## 14. Claude-reviewed implementation milestones

[Implementation Milestones](implementation-milestones.md) defines the current M0..M8 develop-repository milestone sequence plus M1A Desktop Shell Demonstration Slice. The first actual development milestone is M1 SLICE-A local skeleton, with M0 repository scaffold/toolchain bootstrap completed first or in the same controlled implementation branch if source scaffolding is not yet present. M1A follows M1 to prove the Tauri/WebView2 shell, TypeScript UI build, IPC bridge, local/fake mode display, and screenshot or screen-recording evidence before expanding into configuration, editor, roster, and export work. Later milestones close configuration/credential, editor canonical document path, roster/identity, assignment/submission, advisory runner, GitHub clone-only, and export/demo evidence slices.

The milestone structure is based on the Claude Code read-only advisory review recorded in [Claude Design Milestone Analysis](../00-research-analysis/claude-design-milestone-analysis.md), the Codex UI-readiness review recorded in [Codex Demo UI Readiness Analysis](../00-research-analysis/codex-demo-ui-readiness-analysis.md), and the Claude validation recorded in [Claude Demo UI Readiness Validation](../00-research-analysis/claude-demo-ui-readiness-validation.md). It preserves the local-only fixture gate and GitHub clone-only boundary.

## GitHub clone-only roadmap correction

`INC-7` shall be interpreted as GitHub clone-only integration. GitHub is a read-only repository source, not a provisioning or submission backend, unless a future controlled baseline explicitly changes this.
