---
title: Role-Separated UI and Feature Model
document_id: SWENG-EDUTECH-ROLE-UI
version: 0.1.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Role-Separated UI and Feature Model

## 1. Decision summary

HISYS EduOps shall not present the same UI and feature set to students and instructors. The product shall provide **role-separated user experiences** with different navigation, visible functions, default workflows, and safety gates while preserving one controlled document/repository/evidence model underneath.

The student UI should be work-focused and simple. The instructor UI should be operation-focused and control-rich.

## 2. Role UI principles

| Principle | Baseline |
|---|---|
| Separate surfaces | Student and instructor/professor users shall see different primary UI surfaces |
| Same evidence model | Both UIs operate over the same Git-backed assignment/workspace/submission evidence model |
| Least privilege | A role shall not see or trigger functions outside its allowed actions by default |
| Different complexity | Student UI hides operational/Git/admin complexity; instructor UI exposes controlled course, assignment, roster, review, and audit controls |
| Context visibility | Current role, course, assignment, student, and mode context shall be visible before high-impact actions |
| Controlled switching | Role/mode switching requires authentication/authorization and is audit-relevant when high-impact controls become available |

## 3. Student UI surface

The student UI shall prioritize completing assignments without Git knowledge.

| Area | Student-facing capability |
|---|---|
| Dashboard | Current courses/assignments, due dates, status, unread update notices, feedback availability |
| Assignment viewer | Read-only assignment instructions, rubric, references, graph/table/image rendering, change notices |
| Workspace editor | Editable `workspace/**` document/code area, autosave/checkpoint, local history, validation feedback |
| Sync/update | View assignment update notice, inspect affected assignment files, sync read-only assignment area |
| Submission | Pre-submit validation, confirmation, submit, queued/pushed/confirmed status, submission receipt |
| Feedback | View released feedback, rubric result, evaluation logs visible to student, resubmission eligibility where allowed |
| Offline/local | Continue editing/checkpointing locally; clear distinction between local queued work and confirmed submission |

Student UI shall not expose roster management, Problem Bank authoring, assignment publication, other students' work, grading controls, audit export, token configuration, or manual override controls.

## 4. Instructor/professor UI surface

The instructor/professor UI shall prioritize authoring, class operation, monitoring, review, and controlled evidence.

| Area | Instructor-facing capability |
|---|---|
| Course dashboard | Course/section setup, roster status, assignment status, class progress, operational alerts |
| Problem Bank | Create/reuse/version assignment originals, rubrics, references, validation/evaluation profiles |
| Assignment Instance | Publish assignment version, configure due policy, release windows, sections, update reason, sync policy |
| Student management | Roster import, identity binding approval, duplicate detection, lifecycle/status changes, provisioning state |
| Monitoring | Per-student workspace/submission/evaluation/feedback status and exception queues |
| Review/grading | Inspect submission snapshot, rendered document, Git/evaluation evidence, rubric feedback, grade notes |
| Feedback release | Draft feedback, controlled release, release evidence, student-visible result boundary |
| Audit/export | Course evidence export, grade export, SHA/ref/tag verification, archive/retention controls |
| Recovery/override | Authorized identity repair, submission reopening, sync recovery, with reason/scope/before-after audit |

Instructor UI may expose Git evidence and repository state, but normal operation should still avoid requiring raw Git CLI use.

## 5. Shared but role-filtered components

Some components are shared conceptually but filtered by role:

| Component | Student view | Instructor view |
|---|---|---|
| Document renderer | Assignment/workspace/feedback rendering | Authoring/review/submission/evidence rendering |
| Diff viewer | Assignment update diff affecting the student | Assignment release/update diff and student-submission diff |
| Validation panel | Student-actionable errors and warnings | Assignment validation profile results and student-submission validation evidence |
| Git status | Human-readable local/queued/pushed/confirmed state | SHA/ref/tag/repository status, sync queues, exception diagnostics |
| Notifications | Due dates, assignment updates, submission/feedback status | Roster/provisioning/sync/evaluation/review/override alerts |

## 6. Minimum role-permission matrix seed

| Function | Student | Instructor/professor | TA | Admin/operator |
|---|---|---|---|---|
| View assigned instructions | Allow | Allow | Allow | Allow |
| Edit own workspace | Allow | Block except recovery path | Block | Block except recovery path |
| Submit own work | Allow | Block except authorized proxy/override | Block | Block except authorized recovery |
| Create Problem Bank item | Block | Allow | Optional draft-only | Optional/admin policy |
| Publish assignment instance | Block | Allow | Block or draft-only | Allow if delegated |
| Import roster | Block | Allow | Block | Allow |
| Approve GitHub identity | Block | Allow | Block or delegated | Allow |
| View all student submissions | Block | Allow | Allow if assigned | Allow if authorized |
| Grade/release feedback | View released only | Allow | Draft/grade per policy | Release only if delegated |
| Export grades/audit | Block | Allow | Block or limited | Allow |
| Manual override | Block | Allow with approval/audit | Block | Allow with approval/audit |

## 7. Verification fixtures

Role-separated UI verification shall include:

1. student account cannot see instructor navigation or controls;
2. instructor can create/publish an assignment that appears read-only to the student;
3. student can edit only `workspace/**` and submit through student UI;
4. instructor can monitor submission/evaluation/feedback state without editing student workspace content;
5. TA can review assigned submissions without roster/Problem Bank authority unless explicitly delegated;
6. admin/operator can perform roster/provisioning operations without grading authority unless explicitly delegated;
7. role switching requires authorization and records high-impact context changes;
8. graph/table/image rendering appears consistently in student and instructor views, subject to role visibility.

## 8. Traceability

| Decision / requirement | Role UI implication |
|---|---|
| EDUOPS-DEC-012 | Operating modes are explicit and permission-gated |
| EDUOPS-DEC-018 | Student and instructor/professor UIs differ by default |
| EDUOPS-FR-034 | Role-separated UI/function model is required |
| EDUOPS-NFR-010 | Mode boundaries must be understandable and enforceable |
| EDUOPS-NFR-013 | Role separation must be verified through UI and backend permission tests |
