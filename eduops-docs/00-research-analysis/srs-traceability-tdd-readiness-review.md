---
title: SRS Traceability and TDD Readiness Review
document_id: SWENG-EDUTECH-SRS-TDD-REVIEW
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  related: ['SWENG-EDUTECH-SRS', 'SWENG-EDUTECH-RTM', 'SWENG-EDUTECH-STD', 'SWENG-EDUTECH-IMPL-REQ-GAP']
---

# SRS Traceability and TDD Readiness Review

## 1. Review question

This review answers whether the current HISYS EduOps SRS is sufficient to support requirement traceability and test-driven development.

## 2. Conclusion

The SRS is sufficient as a product-level design-input baseline, but it is not yet sufficient by itself for traceability-supported TDD implementation. It contains stable requirement IDs and acceptance seeds, and the package has V&V/STD fixture groups. However, it lacks a complete requirements traceability matrix and does not yet require RED--GREEN--REFACTOR evidence for implementation tasks.

Therefore, implementation may proceed only after each selected behavior is narrowed from SRS ID to design anchor to exact test/fixture command. Coding directly from grouped acceptance seeds would be traceable at the document level but not yet TDD-compliant.

## 3. Evidence checked

- `requirements-record.md` v1.4.1 contains 108 `EDUOPS-FR-*` / `EDUOPS-NFR-*` requirement IDs with acceptance seeds.
- `software-test-description.md` contains fixture tests `STD-001..083`, but exact requirement-ID mentions cover only part of the SRS.
- `verification-validation-plan.md` maps many requirement groups to planned evidence, but it is mostly group-level.
- No existing `requirements-traceability-matrix.md` file was present before this review.
- The checked SRS/STD/implementation-plan text did not contain explicit TDD terms such as `TDD`, `test-first`, `RED`, `GREEN`, or `failing test`.

## 4. Automated coverage snapshot

| Check | Result | Interpretation |
|---|---:|---|
| SRS FR/NFR IDs | 108 | Stable ID baseline exists. |
| Exact SRS IDs mentioned in STD | 22 / 108 | Many tests are grouped rather than exact per requirement. |
| Exact SRS IDs mentioned in V&V plan | 20 / 108 | V&V gives coverage intent but not full RTM. |
| Exact SRS IDs mentioned in requirements breakdown | 19 / 108 | Breakdown is useful but incomplete for full traceability. |
| Weak acceptance-seed heuristic | 14 rows | Some acceptance seeds need fixture command/pass-fail strengthening before TDD. |
| Explicit TDD/RED/GREEN language | 0 occurrences in checked core docs | TDD process is not yet controlled inside the package. |

## 5. Findings

| Finding ID | Severity | Finding | Required action |
|---|---|---|---|
| SRS-TDD-001 | Major | SRS requirements have IDs, but exact SRS-to-STD traceability is incomplete. | Maintain a controlled requirements traceability matrix and require exact test anchors before implementation. |
| SRS-TDD-002 | Major | STD tests exist, but many are scenario groups that do not reference every SRS ID. | Add per-requirement trace rows or generated RTM coverage checks. |
| SRS-TDD-003 | Major | TDD is not represented as a controlled implementation gate. | Add RED/GREEN evidence requirements to SRS/STD/implementation plan. |
| SRS-TDD-004 | Medium | Some acceptance seeds describe outcomes but not executable fixture commands or observable pass/fail artifacts. | Before coding, convert selected acceptance seeds into test commands and expected evidence. |
| SRS-TDD-005 | Medium | Traceability is spread across SRS, STD, V&V, WBS, design docs, and implementation gap register. | Use `requirements-traceability-matrix.md` as the single current index for SRS-to-test implementation readiness. |

## 6. TDD readiness rule

A requirement is TDD-ready only when all of the following exist:

1. SRS requirement ID and acceptance criterion.
2. Design or interface anchor that defines the behavior boundary.
3. Exact STD test ID or fixture gate command.
4. Expected RED failure condition before implementation.
5. Expected GREEN evidence and artifact path after implementation.
6. Refactor/regression command.
7. Link from implementation commit or evidence package back to the requirement and test.

## 7. Recommended next action

Use the new [Requirements Traceability Matrix](../01-requirements/requirements-traceability-matrix.md) as the control point. For the first implementation slice, select only the SLICE-A requirements, add exact test commands and expected RED/GREEN evidence, then implement with strict TDD.
