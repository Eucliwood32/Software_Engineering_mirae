---
title: Claude SRS-Derived Design and STD Review
document_id: SWENG-EDUTECH-CLAUDE-SRS-DESIGN-STD-REVIEW
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
review_type: read-only advisory
reviewer: Claude Code
source_commit: 4408fa0
---

# Claude SRS-Derived Design and STD Review

## 1. Review scope

This review evaluates the SRS-derived downstream baseline created in commit `4408fa0 docs: expand eduops srs design test baseline`:

- [SRS](../01-requirements/requirements-record.md)
- [Requirements Traceability Matrix](../01-requirements/requirements-traceability-matrix.md)
- [Software Design Description](../02-design-planning/software-design-description.md)
- [Interface Design Description](../02-design-planning/interface-design-description.md)
- [Software Test Description](../03-verification-validation/software-test-description.md)
- [Verification and Validation Plan](../03-verification-validation/verification-validation-plan.md)
- [Design and Development Plan](../02-design-planning/design-and-development-plan.md)
- [Risk Register](../04-risk-management/risk-register.md)
- [Decision Log](../05-decisions/decision-log.md)

Claude was run in read-only print mode with no tools (`--allowedTools ""`) against a supplied document corpus. It did not edit files, run commands, or access external services.

## 2. Verdict

**PASS_WITH_FINDINGS.**

The package is internally coherent and does not contradict the accepted baseline: Windows desktop-first, GitHub-first with fake/local fixture gates before live actions, no LMS, advisory C/C++ runner until an approved official sandbox profile exists, and raw credentials excluded from configuration.

However, the SRS-derived SDD/IDD/STD/RTM expansion is not yet sufficient for broad production coding under TDD. It establishes a useful traceability surface, but many rows remain grouped test-design anchors rather than executable per-requirement test cards with RED--GREEN evidence.

## 3. Critical blockers identified by Claude

| ID | Finding | Disposition |
|---|---|---|
| CLAUDE-SRS-DESIGN-001 | SDD/IDD mapped NFR rows to `STD-086..STD-099`, but STD only defined `STD-001..STD-085`. | Fixed in this follow-up: NFR rows are treated as grouped cross-cutting coverage and no longer reference non-existent STD ranges. |
| CLAUDE-SRS-DESIGN-002 | `STD-SRS-*` rows are test-design anchors, not executable per-requirement test commands; generic expected RED text cannot drive TDD. | Accepted. RTM wording is corrected to `Grouped` readiness. Executable SLICE-A test cards remain required before production code. |
| CLAUDE-SRS-DESIGN-003 | SDD §14 and IDD §9 are grouped mappings repeated per requirement, not fully distinct per-requirement design/interface contracts. | Accepted. The rows remain useful for traceability indexing, but broad coding is blocked until slice-specific executable test cards and finer design anchors are created. |
| CLAUDE-SRS-DESIGN-004 | RTM v0.2.0 effectively self-declared non-readiness in every row while using wording that implied exact coverage. | Fixed in this follow-up: RTM rows now explicitly say grouped SRS-derived anchors and require executable test cards before production code. |

## 4. Major findings

1. Wildcard interface references such as `IF-CONFIG-*` and `IF-KNOWLEDGE-*` are not sufficient as implementation anchors for a single task.
2. The downstream expansion increased row-level traceability but did not yet convert acceptance seeds into fixture commands.
3. P0/P1 implementation contracts must still be verified together with the RTM before SLICE-A coding.
4. STD §18 defines TDD evidence fields but has no populated evidence record yet.
5. NFR rows require more specific design/test anchors for packaging, sandboxing, resource limits, UI responsiveness, authorization, privacy, and audit evidence.

## 5. Baseline contradiction check

Claude found no direct contradictions with the accepted product baseline:

- Windows desktop-first remains consistent.
- GitHub-first is consistently gated by fake/local fixtures before live action.
- No-LMS remains consistent; classroom tools are benchmark/reference systems only.
- C/C++ execution remains advisory until a separate official sandbox/runner approval profile exists.
- Credential handling preserves references only; raw credentials are excluded from configuration and logs.

## 6. Required next controlled-document actions

1. Convert a narrow SLICE-A subset into executable test cards with fixture path, command, expected RED output, expected GREEN evidence path, and no-live-action flag.
2. Replace wildcard or grouped interface references with concrete interface anchors for each SLICE-A task.
3. Add at least one worked TDD evidence example to STD §18.
4. Confirm all P0/P1 implementation contracts listed by `EDUOPS-FR-067` exist and match SDD/IDD/STD references.
5. Keep RTM honest: `Grouped` rows may support planning, but they do not authorize production coding.

## 7. Implementation-start conclusion

Broad production code should **not** start from the current SRS-derived expansion alone. A narrow SLICE-A start can be prepared after converting selected rows into executable test cards and verifying the P0 contracts. The current package is suitable for planning and traceability indexing, not yet for general implementation execution.
