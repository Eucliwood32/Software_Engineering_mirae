---
title: Ralph Milestone Execution Alignment
document_id: EDUOPS-RALPH-MILESTONE-EXECUTION-ALIGNMENT
version: 0.1.0
status: active-control
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  anchors:
    - EDUOPS-IMPLEMENTATION-MILESTONES
    - EDUOPS-M0-SOURCE-SCAFFOLD-EVIDENCE
---

# Ralph Milestone Execution Alignment

## 1. Purpose

This document records how the EduOps implementation milestones are aligned for Ralph/Hermes execution. It supplements [Implementation Milestones](implementation-milestones.md) and the repository-root [`ralph.md`](../../ralph.md) control plan.

The goal is to prevent Ralph from treating the milestone list as a broad autonomous mandate. Ralph must instead execute small, resumable, test-first increments with local commits and reflection checkpoints.

## 2. Current baseline

```text
baseline_commit: be8c73c feat: add eduops M0 source scaffold
current_completed_milestone: M0
next_milestone: M1 — SLICE-A local skeleton
remote: none
live_external_action: disabled
```

M0 has produced the Rust/npm/fixture source scaffold and validation commands. M1 can now begin, but only with an explicit Prepare step that re-reads the SLICE-A test cards and confirms the first RED test.

## 3. Ralph-aligned milestone order

```text
M0-COMPLETE
  -> M1-PREP
  -> M1-T1 RED envelope/local-course contract
  -> M1-T2 GREEN domain/API envelope primitives
  -> M1-T3 local filesystem storage adapter
  -> M1-T4 fake-local Git adapter and clone-only gate hardening
  -> M1-T5 SLICE-A fixture runner and evidence package
  -> M1-GATE GATE-SLICE-A-LOCAL-SKELETON
  -> M1A-PREP
  -> M1A UI shell tasks
  -> M2 configuration/credential-reference services
  -> M3 canonical document path
  -> M4 roster/identity/workspace provisioning
  -> M5 assignment/submission state machine
  -> M6 advisory C/C++ runner
  -> M8 export fixture and DEMO-1 evidence package
```

M7 runs after M2 as a branch of clone-only adapter work:

```text
M2 credential-reference behavior accepted
  -> M7 GitHub clone-only adapter
```

M7 does not authorize live GitHub behavior. Clone-only live mode still requires a later explicit gate and user approval. Push, repository creation, archive, webhook, and admin behavior remain out of scope.

## 4. First executable queue

| ID | Description | Required before coding | Completion evidence |
|---|---|---|---|
| M1-PREP | Confirm first M1 test shape from controlled docs and current source | Read `ralph.md`, implementation milestones, internal API, domain IDL, SLICE-A test cards, storage/git specs | Updated `ralph.md` Prepare result or committed task-plan note |
| M1-T1 | Add failing contract test for local course command envelope/result | M1-PREP complete | RED output committed or recorded in task evidence |
| M1-T2 | Implement minimal envelope/course primitives | M1-T1 RED observed | Focused test GREEN; no live action |
| M1-T3 | Add local storage adapter for empty course fixture | M1-T2 GREEN | Storage test GREEN; fixture-only paths |
| M1-T4 | Add fake-local Git checkpoint/status evidence | M1-T3 GREEN | fake Git tests; clone-only denial tests |
| M1-T5 | Emit `run-summary.json` under `build/evidence/slice-a/<run-id>/` | M1-T4 GREEN | CLI test GREEN; evidence has `live_external_action=false` |
| M1-GATE | Run and record `GATE-SLICE-A-LOCAL-SKELETON` | M1-T5 GREEN | milestone gate summary and clean repo |

## 5. Ralph execution guardrails

Ralph must keep each task independently commit-ready. If a task needs changes across more than one implementation boundary plus tests, it must be split unless the extra boundary is a simple type import needed for the test to compile.

Each implementation task must run:

```text
cargo fmt --all --check
npm run m0:check
cargo test --workspace
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q
git diff --check
```

Documentation updates additionally require Markdown local link and JSON parse validation.

## 6. Stop conditions

Ralph stops before coding if:

1. controlled docs conflict about task order or acceptance criteria;
2. working tree is dirty with unrelated changes;
3. the next task requires live external behavior, credential lookup, push, destructive Git, or non-fixture data mutation;
4. the next task would cross from M1 to M1A before `GATE-SLICE-A-LOCAL-SKELETON` passes;
5. success likelihood after Reflection is below 75%.

## 7. Decision

The milestone structure is aligned for Ralph execution. The next safe action is `M1-PREP`, not direct broad implementation of all M1 behavior.
