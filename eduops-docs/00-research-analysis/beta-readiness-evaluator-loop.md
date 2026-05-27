---
title: Beta Readiness Evaluator Loop Record
document_id: SWENG-EDUTECH-BETA-READINESS-EVAL-LOOP
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Beta Readiness Evaluator Loop Record

## 1. Purpose

This record documents the evaluator loop requested for deciding whether HISYS EduOps may start development toward a beta-tester-usable Windows desktop product. Claude acted as evaluator and improvement planner. Codex acted as evaluator and implementation agent for the controlled-document improvement plan. Hermes verified and committed the results locally.

## 2. Baseline under evaluation

- Windows desktop-first and local-first product boundary.
- Git-backed Notion-style assignments.
- No LMS and no live Google Classroom integration.
- GitHub-first repository backend later, after fake/local gates.
- Fake/local fixture gates before live external actions.
- Development begins with SLICE-A local skeleton, not production external integration.

## 3. Loop rule

The loop stops when both evaluators approve development start or when ten improvement loops have been exceeded. A loop consists of:

1. Claude read-only readiness evaluation.
2. Codex read-only readiness evaluation.
3. If either evaluator returns `IMPROVE`, Claude's improvement plan is used.
4. Codex applies the improvement plan to controlled documents.
5. Hermes validates, commits, and triggers the next evaluator round.

## 4. Loop results

| Loop | Claude decision | Codex decision | Action | Result |
|---|---|---|---|---|
| 1 | `IMPROVE` | `IMPROVE` | Claude required P0 implementation contracts; Codex added the P0 contract package. | Continued to Loop 2. |
| 2 | `APPROVE` | `APPROVE` | Both evaluators agreed that development can begin toward beta-tester-usable product through fake/local vertical slices. | Stop condition met before ten loops. |

## 5. Improvement package committed after Loop 1

The improvement package was committed as `0c02119 docs: add eduops p0 beta readiness contracts`.

New controlled P0 documents:

- [Technology stack decision record](../02-design-planning/technology-stack-decision-record.md)
- [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md)
- [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md)
- [Module and package layout](../02-design-planning/module-and-package-layout.md)
- [Internal API contract](../02-design-planning/internal-api-contract.md)
- [State machine implementation tables](../02-design-planning/state-machine-implementation-tables.md)
- [Fixture corpus and harness plan](../03-verification-validation/fixture-corpus-and-harness-plan.md)

The package also updated README, INDEX, gap register, V&V, STD, risk, decision log, and roadmap traceability.

## 6. Final evaluator conclusions

### Claude final decision

`CLAUDE_DECISION: APPROVE`

Claude concluded that the P0 implementation-executability backlog declared by the project itself is closed. SLICE-A can begin. P1 adapter specifications and DEMO-1 harness work remain necessary but are implementation slices rather than pre-coding blockers.

### Codex final decision

`CODEX_DECISION: APPROVE`

Codex concluded that the controlled documents are sufficient to start development toward beta-tester-usable product through fake/local vertical slices. Remaining gaps are slice-specific P1/P2 work rather than blockers to starting SLICE-A/local skeleton development.

## 7. Approved development boundary

Development may begin under these constraints:

1. Start with SLICE-A local skeleton using fake/local adapters.
2. Use TDD and fixture-first validation for behavior changes.
3. Do not perform live GitHub, LMS, classroom, or external grading actions.
4. Keep `live_external_action=false` for DEMO-1/2 and early fixture runs.
5. Treat P1 adapter documents as required before the affected slice is completed.
6. Treat beta-tester-facing claims as blocked until DEMO-1 evidence package and subsequent pilot gates pass.

## 8. Remaining non-blocking implementation-slice work

The following remain required for later slices:

- Git adapter specification.
- Local storage adapter specification.
- Editor adapter bridge specification.
- Evaluation runner I/O contract.
- GitHub dry-run adapter specification.
- Exporter implementation specification.
- Build/packaging/release engineering baseline.
- DEMO-1 fixture corpus and runnable harness.
- Accessibility and performance harnesses before UI hardening/beta claims.

## 9. Traceability

- Related decisions: `EDUOPS-DEC-047`, `EDUOPS-DEC-048`, `EDUOPS-DEC-049`, `EDUOPS-DEC-050`.
- Related tests: `STD-071` through `STD-077`.
- Related risks: `EDUOPS-R-045` through `EDUOPS-R-051`.
- Stop condition: both evaluators approved at Loop 2; ten-loop limit was not reached.
