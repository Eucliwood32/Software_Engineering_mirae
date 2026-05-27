---
title: Queue-End Planning Analysis
document_id: EDUOPS-QUEUE-END-PLANNING-ANALYSIS
version: 0.1.0
status: accepted-control-checkpoint
date: 2026-05-15
owner: develop
quality_context: Ralph control checkpoint
---

# Queue-End Planning Analysis

## 1. Finding

After `M7-MOCKHTTP-GATE` completed, Ralph stopped because the active task queue had no row marked `next` or prerequisite-satisfied `pending`. The existing auto-expansion rule only covered the finite milestone backlog and listed gap-closure checkpoints. It did not require a new backlog-discovery planning checkpoint after all listed milestone rows were complete.

The stop was therefore mechanically consistent with the prior `ralph.md`, but it did not satisfy the intended continuous planning behavior: when the queue is empty, Ralph should create a safe planning row before stopping, unless even planning would require a non-delegable action.

## 2. Root cause

| Control element | Behavior observed | Gap |
|---|---|---|
| Section 8 Active Task Queue | All M0..M8 and M7-MOCKHTTP rows were `done`. | No queue-end planning row existed. |
| Section 9.1 Downstream Expansion Plan | Covered M3→M8 and known gap closures. | Did not define post-backlog discovery after M8/M7-MOCKHTTP. |
| Section 10.2 condition #8 | Allowed stop when no pending safe task remained and auto-expansion could not produce a `PREP`. | Did not force a candidate-generation checkpoint before deciding no safe task exists. |
| Reflection Log | Listed three human-authority candidates. | Did not convert the safest candidate into a controlled documentation/specification row after the user authorized continuing. |

## 3. Corrective rule

When the active queue becomes empty after all listed milestones and follow-up constrained gates are complete, Ralph shall execute a `QUEUE-REFILL-PREP` checkpoint before stopping. That checkpoint shall:

1. read the latest evidence summaries and blockers;
2. list candidate next task families;
3. classify each candidate as safe documentation/control, safe fixture-local implementation, or non-delegable/live-authority;
4. select the safest candidate that can be expressed as a controlled local specification or fixture task;
5. add a new `PREP` row, executable task rows, and a gate row to Section 8 when the selected candidate stays within the safety boundary;
6. stop only if no candidate can be converted into a local controlled specification or fixture task.

## 4. Candidate analysis after M7-MOCKHTTP

| Candidate | Classification | Decision |
|---|---|---|
| M7 clone-readonly integration-point boundary specification | Safe documentation/control if it defines approval gates, allowlists, credential references, audit envelopes, and user-executed live-run boundaries without performing network calls. | Selected next. |
| Extended real-writer M8 exporter specification | Non-delegable product/runtime authority because it requires writer profile, converter license, host process, fidelity, privacy/legal, and DEMO-1 acceptance decisions. | Defer. |
| Live retry tuning / jitter policy | Non-delegable live operations authority because it tunes production behavior. | Defer. |

## 5. Selected next step

Create `docs/02-design-planning/github-clone-readonly-integration-point-specification.md` and seed a constrained queue for local specification and fixture-only gate mechanics.

The selected step does not authorize a live GitHub call. It authorizes only:

- allowlist policy shape;
- approval evidence envelope;
- credential-reference status contract;
- dry-run clone plan gating;
- user-executed live clone runbook boundary;
- no-push/no-mutation/no-secret guards;
- local fixture tests for gate approval/refusal behavior.
