---
title: HISYS EduOps Platform Verification and Validation Plan
document_id: SWENG-EDUTECH-VVP
version: 2.0.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Verification and Validation Plan

## 1. Verification objectives

Verify that the Windows desktop product preserves the controlled usage scenarios from student registration through archive, including student-management integrity, assignment integrity, student workspace isolation, GitHub-backed evidence, mode permissions, safe synchronization, no-LMS operation, and C/C++ automated-evaluation traceability.

## 2. Initial verification matrix

| Requirement/constraint | Planned evidence |
|---|---|
| SCN-001, SCN-002, EDUOPS-FR-001, FR-002, FR-022 | Course/section fixture, roster import/export schema tests, no-LMS configuration tests |
| SCN-003, SCN-004, SCN-012, EDUOPS-FR-003, FR-004, FR-005, FR-008, NFR-009, CON-011 | Student registry validation, identity-binding duplicate tests, lifecycle state-transition tests, status-change audit tests |
| SCN-005, SCN-006, EDUOPS-FR-006, FR-011, FR-012, CON-003 | Windows workspace provisioning and assignment-origin edit-blocking tests |
| SCN-007, SCN-008, EDUOPS-FR-013, FR-014, NFR-003 | Commit metadata and submission snapshot traceability tests |
| EDUOPS-FR-015, FR-016 | Assignment update synchronization and Windows/in-app notification scenario tests |
| SCN-009, EDUOPS-FR-017, FR-018, NFR-005, NFR-007, CON-004, CON-009 | C/C++ compile/run/unit-test/static-analysis fixtures, sandbox/resource-limit tests, malicious-program containment tests, result-schema validation |
| SCN-010, SCN-013, SCN-014, EDUOPS-FR-019, FR-020, FR-021 | Review, feedback-release, audit export, override-evidence tests |
| EDUOPS-FR-023, CON-007, CON-010, EDUOPS-CFR-015, EDUOPS-CNFR-006 | GitHub configuration validation, credential-reference fixture, permission fixture, token-reference/leak checks |
| EDUOPS-FR-024 | Backend boundary contract test using GitHub fixture and local/self-hosted-Git simulator |
| EDUOPS-FR-025, FR-026, FR-027, FR-029, FR-034, FR-035, NFR-010, NFR-013, NFR-014, CON-012, CON-013 | Mode/permission matrix tests, scoped authorization fixtures, role-separated UI fixtures, visible context tests, high-impact confirmation tests, manual override audit tests, authorization decision record tests |
| EDUOPS-FR-028, NFR-006 | Offline queued/confirmed state tests and later GitHub synchronization scenario |
| EDUOPS-CON-001, NFR-001 | Architecture and packaging review confirming desktop-first product boundary and absence of unapproved standalone web/mobile delivery |
| EDUOPS-NFR-011 | UI responsiveness/performance tests for navigation, editing, autosave/checkpoint, diff display, validation feedback, Git sync, submission, evaluation-trigger operations, and any Next.js/web-renderer candidate |
| EDUOPS-CFR-013..022, EDUOPS-CVR-005..009 | Configuration fixture tests for deterministic merge, workspace-root resolution, credential no-leak, migration, invalid-config behavior, and offline isolation |
| EDUOPS-FR-033, EDUOPS-NFR-012 | Rendering fixture tests for graph/diagram blocks, Markdown/structured tables, large/wide tables, local images, missing images, blocked image paths, mixed documents, fallback source/snapshot behavior, and export/submission evidence consistency |
| EDUOPS-CON-008, NFR-008 | No-LMS architecture search and installation/configuration test |
| EDUOPS-FR-036..041, EDUOPS-NFR-015 | Classroom benchmark fixtures for course dashboard, repository/evidence view, bulk operations, assignment publication/update preview, feedback release/export, and dispute reconstruction |
| EDUOPS-FR-042..046, EDUOPS-NFR-016..017 | Notion-style execution-block fixtures, student knowledge workspace fixtures, DOCX export fixtures, HWP/HWPX export/fallback fixtures, export manifest/hash/redaction checks |
| EDUOPS-FR-047..051, EDUOPS-NFR-018..019 | Editor block editing, autosave/checkpoint, undo/redo/history, permission enforcement, Korean IME, C/C++ code/table/graph/image/reference/experiment/decision/reflection blocks, export preview, and JSON/Markdown/export round-trip fixtures |

## 3. Validation objectives

- Instructor/admin can import a roster, bind GitHub identities, provision students, and monitor student states without LMS.
- Instructor can reuse and version C/C++ assignment packages without losing traceability.
- Student can edit and submit C/C++ work on Windows without learning Git commands.
- TA/instructor can resolve grading disputes using reproducible GitHub/evaluation/student-lifecycle evidence.
- Assignment corrections reach students without overwriting their work.
- Course operation succeeds without LMS credentials or connectors.

## 4. Pilot validation seed

A pilot validation should include one course, one section, one instructor, one TA, at least three students with different lifecycle/status cases, one C assignment, one C++ assignment, one instructor update after release, one late submission, one locked/withdrawn student, one compile failure, one runtime/unit-test failure, one static-analysis warning, one malicious/timeout fixture, one feedback release, and one manual override scenario.

## 5. Acceptance before classroom pilot

- No uncontrolled overwrite of student work in synchronization tests.
- No raw private data or GitHub tokens leak in logs, repositories, exports, or evaluation artifacts.
- Student lifecycle, identity binding, and status-change evidence is complete and privacy-bounded.
- Submission snapshot can be reproduced from stored Git SHA and assignment version.
- Evaluation results can be regenerated or explained from captured inputs, compiler/toolchain metadata, and configuration.
- Mode permissions, scoped access-control decisions, and role-separated UI/backend checks prevent students, TAs, evaluators, and sync workers from performing blocked actions.
- The system can complete roster import, identity binding, assignment publication, submission, evaluation, feedback release, and grade/evidence export with no LMS connection.
- The desktop UI remains responsive while Git, validation, synchronization, submission, and evaluation-trigger jobs run in the background.
- Graphs, tables, and images render correctly or produce controlled fallback/error evidence in authoring, student workspace, review, feedback, and export/submission flows.
- Classroom efficiency benchmark fixtures meet or explicitly document gaps against EDUOPS-BM-001..010 before live classroom pilot.
- Notion-style execution blocks, student knowledge artifacts, and DOCX/HWP/HWPX exports preserve canonical evidence and pass privacy/redaction/export-manifest checks before report exports are accepted as submission artifacts.
- Editor behavior passes block, autosave, history, permission, Korean IME, code/table/diagram/image, validation, and round-trip fixtures before the editor is used in a classroom pilot.

## 6. Software test description linkage

Concrete fixture test cases are controlled in [Software test description](software-test-description.md). The implementation-readiness gate requires each STD case to have executable or manually reproducible fixture evidence before live GitHub or live evaluation side effects.

## 7. Document model V&V note

Additional verification shall cover editor JSON to Markdown export, graph/table/image rendering fixtures, submission branch structure, `submission_metadata.json`, assignment snapshot preservation, automatic validation checks, and rejection of commits that modify `assignment/**` or tamper with `metadata/**`.

## 8. Claude review gap-closure verification additions

| Profile | Required fixture evidence |
|---|---|
| Knowledge topology | Sync does not overwrite `knowledge/**`; selected/required knowledge artifacts appear in submission metadata and privacy redaction works |
| Editor stack/block schema | Candidate editor passes Korean IME, block schema, code/table/diagram/image, autosave, accessibility, and export-binding fixtures |
| Export fidelity | DOCX/HWPX/HWP outputs map required block IDs, preserve canonical evidence links, and record all loss/warning records |
| Evaluation execution | Advisory pre-check and official runner evidence are distinguishable; sandbox/resource violations are recorded |
| State machine | Queued/pushed/confirmed submission states are not conflated; assignment update acknowledgement is separately tracked |
| GitHub feasibility | Sandbox/dry-run operation records cover rate limits, token references, retry, outage, and naming privacy |
| Roster identity | CSV/JSON imports validate encoding, duplicates, identity claim/approval, privacy flags, and provisioning evidence |
| Performance/accessibility/Korean text | Seed P50/P95 budgets, keyboard/focus/screen-reader behavior, and Unicode/IME/font fixtures are recorded |

## 9. Notion-style storage verification additions

| Storage behavior | Required evidence |
|---|---|
| Canonical JSON/Markdown materialization | Same block graph produces stable hashes and deterministic projection |
| Operation journal recovery | Simulated crash recovers latest autosaved revision |
| Block identity stability | Reorder/edit preserves comments, export bindings, validation, and feedback links |
| Index rebuild | Local indexes/search caches rebuild from canonical files |
| Git checkpoint linkage | Commit metadata references JSON hash, Markdown hash, asset hashes, operation range |
| Submission/export boundary | Derived exports and submission snapshots use materialized canonical revision only |

## 10. Storage gap-closure verification additions

| Verification item | Required evidence |
|---|---|
| Projection profile | Same document on Windows/Linux produces same LF/NFC/GFM-compatible projection hash |
| Lossy projection warning | Typed block not representable in Markdown appears in projection manifest with fallback reference |
| Artifact Git policy | `.gitignore`/retention fixture shows canonical files tracked and indexes/autosaves ignored |
| Block identity lineage | Template clone/update, split, merge, reorder, and delete preserve traceable lineage |
| Schema migration | Supported upgrade succeeds with hashes; downgrade/failure quarantines safely |
| Asset privacy/LFS | `student_private` assets do not enter shared remote/LFS/export without promotion |
| Local privacy cleanup | Archive/withdrawal/device handoff cleans or protects local journals/indexes/autosaves |

## 11. Implementation executability verification

The implementation-readiness gate now includes verification that P0 HOW-level contracts exist before code implementation: [Technology stack decision record](../02-design-planning/technology-stack-decision-record.md), [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md), [Module and package layout](../02-design-planning/module-and-package-layout.md), [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md), [Internal API contract](../02-design-planning/internal-api-contract.md), [Fixture corpus and harness plan](fixture-corpus-and-harness-plan.md), and [State machine implementation tables](../02-design-planning/state-machine-implementation-tables.md). V&V shall check that each vertical slice has fixture evidence, fake/local adapter coverage, and no live external side effects until explicit gates pass.

## 12. Gap-register verification candidates

The implementation requirements gap register now defines explicit candidate verification requirements (`EDUOPS-CVR-*`). V&V shall treat promoted `EDUOPS-CVR-001` local fixture gates and `EDUOPS-CVR-002` privacy-safe deterministic fixtures, controlled in the fixture harness plan, as preconditions for SLICE-A. Accessibility and performance harness candidates (`EDUOPS-CVR-003`, `EDUOPS-CVR-004`) shall be promoted before UI hardening claims.

## 13. Working demonstration evidence

EduOps working claims shall be made by demonstration level. DEMO-0 may explain the user flow, but DEMO-1 is the first credible working demonstration because it combines user-visible flow, backend/application state evidence, and repository/evidence artifacts. DEMO-1 and DEMO-2 shall report `live_external_action=false`. DEMO-3 requires explicit sandbox approval and fixture-gate evidence.


## 14. Traceability and TDD verification

Before a source-code behavior is implemented, V&V shall confirm that the selected SRS requirement has an RTM row, a design/interface anchor, an exact STD or fixture test, and a defined RED failure condition. The implementation evidence package shall preserve RED--GREEN--REFACTOR order and shall not rely on tests written only after production behavior is complete.


## 15. SRS-derived design/test coverage review

V&V shall verify that SDD §14, IDD §9, STD §17, and RTM v0.2.0 remain synchronized with SRS v1.6.0. A source-code task is blocked when its RTM row lacks an executable fixture command or when RED--GREEN evidence cannot be captured.


## 16. Claude SRS-derived design/test review gate

The 2026-05-14 Claude review classifies the SRS-derived SDD/IDD/STD/RTM expansion as grouped planning coverage. V&V shall therefore reject implementation evidence that cites only `STD-SRS-*` planning anchors without an executable fixture command, expected RED output, GREEN evidence artifact, and no-live-action assertion where applicable.


## 17. GitHub adapter verification gate

GitHub integration modules shall not proceed from product-level SRS text alone. Before coding, the implementation task shall cite [GitHub Adapter Specification](../02-design-planning/github-adapter-specification.md), one or more `GH-FIX-*` gates, exact fixture commands, expected RED output, expected GREEN evidence, and a no-live-action assertion. Sandbox or live GitHub mutation remains blocked until fake-local and mock-http gates pass and a separate approval record exists.


## GitHub adapter SRS promotion note

The SRS now includes `EDUOPS-FR-080..084` and `EDUOPS-NFR-034..036`; verification of these requirements is through `STD-086..091` and `GH-FIX-*` gates before sandbox/live GitHub actions.


## GitHub adapter detailed SDD verification update

Verification for GitHub adapter implementation shall use the detailed component and slice boundaries in [GitHub Adapter Software Design Description](../02-design-planning/github-adapter-software-design-description.md). `GH-SLICE-0..3` remain fake-local/mock/non-leak/state/gate verification stages. `GH-SLICE-4..5` require separate approval before any sandbox/live action.


## Ralph-loop executable evidence gates

The first fake/local implementation loop is constrained by [SLICE-A and GH-SLICE-0 Executable Test Cards](slice-a-executable-test-cards.md). V&V acceptance requires exact RED failure evidence, GREEN pass evidence, `run-summary.json` schema validation, fixture hash verification, no remote URL, and `live_external_action=false`.


## GitHub clone-only verification boundary

GitHub verification now targets clone-only behavior: clone configuration validation, clone planning, fake/mock clone results, and denial of every non-clone operation. No V&V gate approves repository creation, push, collaborator management, branch protection mutation, webhook/check-run writes, or GitHub administration.
