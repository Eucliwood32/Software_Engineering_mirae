---
title: HISYS EduOps Platform Design and Development Plan
document_id: SWENG-EDUTECH-DDP
version: 1.6.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Design and Development Plan

## 1. Design objective

Develop a Windows and Linux desktop EduTech platform that converts C/C++ assignment authoring, student management, student work, submission, synchronization, evaluation, grading, and audit into reproducible GitHub-backed workflows while excluding LMS integration.

## 2. Planned design stages

| Stage | Output | Review gate |
|---|---|---|
| D1 Requirements analysis baseline | Requirements, requirements analysis, requirements breakdown, constraints, service concept, risk register | Confirm Windows/Linux desktop, GitHub-first, C/C++ first, student-management, mode-separated, LMS-excluded scope |
| D2 Student/mode/scenario model | Usage scenarios, student registry schema, lifecycle state machine, identity-binding workflow, mode/permission matrix | Privacy, identity, permission, scenario completeness, override, and audit review |
| D3 GitHub repository model | Problem Bank, Assignment Instance, Student Workspace, submission namespace, branch/permission rules | Git evidence, GitHub permission, identity binding, and read-only/writeable boundary review |
| D4 C/C++ evaluation profile | Compiler/toolchain profile, build/test/static-analysis rule format, sandbox/resource limits | Safety/privacy and deterministic evidence review |
| D5 Fast controlled UI prototype | Instructor, admin, student, TA, evaluator, sync, audit, and recovery mode workflows using the selected UI/rendering stack | Usability/performance review without Git CLI exposure; notification/credential behavior review; rendering/evidence contract review; Next.js allowed only if gates pass |
| D6 Pilot package | Fixture course, roster, students, sample C/C++ assignments, sample submissions, exports | V&V readiness review before live classroom use |
| D7 Future backend assessment | Self-hosted Git extension profile | Only after GitHub baseline passes; no LMS expansion in this stage |

## 3. Required design records

- End-to-end usage scenarios beginning with student registration.
- Git-backed Notion-style concept model and repository structures.
- Permission model for instructor/student/system paths.
- Database, API, document editor JSON/Markdown, and automatic-validation model.
- Fast controlled UI baseline, performance budgets, editor/rendering component selection record, graph/table/image rendering profile, rendering engine strategy, rendering engine cost/reuse analysis, role-separated UI feature model, access-control authorization model, SDD, IDD, STD, role-permission matrix, and productization roadmap.
- Student registry schema and privacy/redaction policy.
- Student lifecycle state machine and status-change rules.
- GitHub identity-binding and duplicate-account resolution workflow.
- Mode/permission matrix and high-impact action confirmation model.
- Manual override audit record schema.
- GitHub repository architecture and branch/namespace rules.
- GitHub identity, token-reference, and permission model.
- Windows workspace path, permission, installer/update, and credential-storage model.
- C/C++ assignment package schema with starter code, build files, tests, and rubric.
- C/C++ evaluation sandbox, toolchain profile, resource limits, and result-evidence schema.
- Synchronization/conflict-notification design.
- Privacy, audit-log, and export policy.
- No-LMS import/export boundary.
- Future self-hosted Git backend boundary.

## 4. ISO 9001 design-control mapping

| ISO 9001 clause | Application |
|---|---|
| 4 | Context: C/C++ programming education workflow, student/course operations, LMS exclusion, GitHub-backed differentiator |
| 6 | Risks/opportunities: academic integrity, data loss, privacy, GitHub dependency, untrusted code execution, identity mismatch, mode misuse, usability |
| 7 | Documented information: Git evidence, student lifecycle records, audit records, controlled drafts |
| 8.3 | Design inputs, outputs, review, verification, validation, change control |
| 9 | Evaluation results, pilot metrics, student progress, grading-dispute evidence |
| 10 | Corrective actions from pilot defects, compile/test failures, identity issues, sync incidents, and operational incidents |

## 5. Immediate next design questions

1. Select supported platform boundary and exact UI framework/editor/rendering component, including whether Next.js inside a desktop shell is beneficial.
2. Define detailed student vs instructor/professor navigation, command labels, blocked-action messages, and role-specific fixture screens.
3. Start the local-only vertical slice described in the productization roadmap after fixture gates are accepted.
2. Review end-to-end usage scenarios from student registration to archive.
3. Define student registry schema and lifecycle state machine.
4. Define mode/permission matrix and manual override policy.
5. Define canonical GitHub organization/repository layout and branch naming.
6. Define document-first assignment package schema, including graph/table/image rendering fixtures, then define C/C++ evaluation profile as an optional validation/evaluation module.
7. Select first compiler/toolchain and sandbox execution strategy.
8. Define roster/GitHub identity binding without LMS.
9. Define minimum C/C++ pilot course scenario.

## Classroom benchmark optimization design input

The classroom benchmark package adds a design input that EduOps should combine Google-Classroom-like course/student management efficiency with GitHub-Classroom-like repository/evidence workflows. This affects DDP planning by adding fixture-gated optimization before live integration:

1. benchmark fixture definition for 30/60-student onboarding, publication, update, submission, evaluation, feedback, export, and dispute reconstruction;
2. dashboard and exception-queue design for instructor/admin bottlenecks;
3. evidence-ledger checks that preserve Git SHA/file hash/audit records for high-impact transitions;
4. explicit prohibition on live Google Classroom/LMS integration until separately promoted.

Controlled details are in [Classroom benchmark analysis](../00-research-analysis/classroom-benchmark-analysis.md) and [Classroom efficiency optimization plan](classroom-efficiency-optimization-plan.md).

## Student knowledge-system/export design input

EduOps differentiation now includes Notion-style assignment execution, student-owned knowledge-system creation, and DOCX/HWP/HWPX export. This adds these design tasks before classroom pilot:

1. define block schema and canonical Markdown/report mapping for assignment execution blocks;
2. define `knowledge/**` workspace ownership, sync, submission, privacy, and promotion rules;
3. define DOCX and HWP/HWPX export profiles, converter/tool version capture, and fallback/warning behavior;
4. add export manifests to submission/evidence records;
5. verify knowledge/export fixtures before treating report exports as acceptable submission artifacts.

Controlled details are in [Student knowledge system and export profile](student-knowledge-export-profile.md).

## Editor requirements design input

The Notion-style editor is now a core product capability. Before implementation, EduOps shall define and fixture-test block schema, autosave/checkpoint, undo/redo/history, validation, permission enforcement, Korean IME/code/table/diagram/image editing, export preview, and JSON/Markdown/DOCX/HWPX/HWP round-trip behavior. Controlled details are in [Notion-style editing requirements profile](notion-style-editing-requirements-profile.md).

## 9. Claude review gap-closure work package

Before implementation lock-in, D2-D6 shall include a gap-closure package:

1. Integrate `knowledge/**` topology into repository, permission, submission, privacy, and export controls.
2. Run an editor stack trade study and create a canonical block schema before committing to a toolkit.
3. Define HWPX-first export, legacy HWP converter policy, and export fidelity acceptance.
4. Define official/advisory C/C++ evaluation runner profiles and Windows sandbox controls.
5. Normalize state machines for student lifecycle, submission, and assignment release/update.
6. Qualify GitHub API feasibility and token/topology model before production KPI claims.
7. Define roster schema, performance budgets, Korean text handling, accessibility, and repository retention.

These are not optional refinements; they are design-input closure gates before classroom pilot.

## 10. Notion-style storage design gate

Before editor implementation, D5 shall include a storage spike that verifies operation journaling, canonical JSON/Markdown materialization, local index rebuild, Git checkpoint linkage, crash recovery, block reorder stability, and submission/export from materialized revision. This gate is required before choosing the final editor toolkit.

## 14. Implementation executability gate from Codex/Claude review

Before product code starts, the design/development baseline shall close the P0 implementation contracts identified by Codex and Claude review: technology stack decision, process topology and IPC, module/package layout, canonical domain IDL, and internal API contract. These documents are controlled design inputs, not optional developer notes.

The next development phase shall use vertical slices rather than broad horizontal component construction. SLICE-A shall use fake/local adapters only and prove shell/service/worker/local Git/local index round-trip before any live GitHub or live evaluation side effect.

## 15. Gap-register controlled promotion plan

The implementation requirements gap register v0.2.0 becomes the design-control bridge for implementation-readiness. DDP review shall not treat a candidate row as implementation-ready until its status is `promoted` or `promoted-document-required` with the required control document available. The immediate next design work is to close local fixture gates, privacy-safe fixture data, transition tables, sync-conflict rules, and authoritative time semantics before source-code slices.


## SRS-derived SDD/IDD/STD expansion baseline

The design phase now treats SDD §14, IDD §9, STD §17, and RTM v0.2.0 as synchronized downstream controls from SRS v1.6.0. Design review shall check that every added or revised SRS FR/NFR row has a component/design response, interface anchor, test anchor, and TDD evidence expectation before implementation tasks are opened.


## GitHub adapter detailed SDD planning update

Before GitHub adapter source code starts, implementation tasks shall cite [GitHub Adapter Software Design Description](github-adapter-software-design-description.md), [GitHub Adapter Specification](github-adapter-specification.md), a specific `GH-SLICE-*`, the corresponding `GH-FIX-*` fixture, and RED--GREEN evidence expectations. Sandbox/live GitHub behavior remains outside the current implementation-start boundary.


## GitHub clone-only development boundary

Development work involving GitHub shall implement fake-local/mock clone fixtures first. Real GitHub use, when separately approved, is limited to read-only clone/fetch from approved sources. Mutation-capable GitHub features require a future controlled baseline change.
