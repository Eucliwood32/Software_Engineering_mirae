---
title: HISYS EduOps Classroom Benchmark Analysis
document_id: SWENG-EDUTECH-CLASSROOM-BENCHMARK
version: 0.2.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Classroom Benchmark Analysis

## 1. Purpose and scope

This controlled analysis benchmarks GitHub Classroom and Google Classroom as reference systems for HISYS EduOps student-management and course-management efficiency. The user phrase `git classroom` is interpreted as **GitHub Classroom** unless later corrected.

The analysis is not a decision to integrate either service. It identifies patterns to emulate, gaps to exploit, and acceptance metrics for optimizing the EduOps product baseline.

## 2. Source registry

| Source ID | Source | Observed capability area | Use in this analysis |
|---|---|---|---|
| SRC-GHC-001 | GitHub Docs, "Teach with GitHub Classroom" | Classroom setup, individual/group assignments, template repositories, pull-request feedback, autograding, GitHub CLI, IDE/Codespaces integrations, LMS roster connection option | Reference for Git-native programming-course workflow |
| SRC-GC-001 | Google Classroom API get-started and REST resources | Courses, coursework, topics, rubrics, grades, rosters/teachers/students, invitations, guardians, student submissions, turn-in/return/reclaim, Google Drive attachment folders | Reference for general classroom/course operations API and roster/grade lifecycle |
| SRC-EDUOPS-001 | Current EduOps controlled baseline | Windows desktop, GitHub-first, C/C++ profile, no LMS dependency, branch-based evidence, student lifecycle, role-separated UI, access control | Product constraints for benchmark interpretation |

## 3. Benchmark dimensions

| Dimension | GitHub Classroom reference | Google Classroom reference | EduOps optimization implication |
|---|---|---|---|
| Course setup | GitHub organization/classroom and assignment setup; strong repository orientation | Course object, teachers/students, invitations, topics, guardians; strong classroom administration orientation | EduOps should provide Google-Classroom-like course/roster convenience while preserving GitHub-Classroom-like repository evidence. |
| Roster and identity | GitHub account identity and optional LMS roster import; identity mismatch remains a risk | Native course roster/teacher/student resources and invitations; institutional identity fits Google Workspace domains | EduOps should keep a roster-first identity-binding workflow: roster ID is primary, GitHub identity is bound/approved evidence. |
| Assignment authoring | Template repositories, starter code, individual/group assignment repositories, autograding | CourseWork/courseWorkMaterials, Drive attachments, rubrics, due dates, grading fields | EduOps should combine reusable Problem Bank/Assignment Version with rich document/course metadata and rubric controls. |
| Student workspace | Repository per assignment/student or group; Git history is natural evidence | Submission/attachment lifecycle; not Git-native | EduOps should keep isolated student workspaces and submission branches; this is a differentiator over Google Classroom. |
| Submission state | Git commit/repository evidence; deadlines/assignment overview/autograding | StudentSubmission states, late flag, draft/assigned grades, submission history, turn-in/return/reclaim | EduOps must explicitly model queued, pushed, confirmed, returned, reopened, and archived states with evidence. |
| Feedback and grading | Pull request feedback and autograding results | Draft/assigned grades, rubrics, return flow, grade APIs | EduOps should support PR/code-review-style technical feedback plus classroom-style rubric grade release. |
| Automation/API | GitHub APIs/CLI, repository actions, autograding workflows | Classroom REST API with courses/coursework/roster/grade/submission resources | EduOps should separate internal domain APIs from backend adapters so GitHub remains first backend and Classroom-style concepts remain optional references, not dependencies. |
| Offline/local operation | Git local commits help, but live classroom flows still rely on GitHub sync | Cloud-service oriented | EduOps should preserve Windows local-first work and delayed sync states as a product advantage. |
| Evidence/audit | Strong repository SHA evidence, code review traces, CI/autograding logs | Course/submission/grade histories and Drive attachment metadata | EduOps should produce a unified Evidence Ledger linking roster, Git SHA, submission state, evaluator logs, rubric/feedback, and export records. |
| Programming-course fit | Strong fit for code assignments and Git education | Strong fit for general assignment distribution and grading, weaker for Git-native code evidence | EduOps should position itself as programming-assignment operations, not generic LMS replacement. |

## 4. Efficiency target model

Efficiency should be measured from the instructor/admin, student, TA, and evaluator perspectives rather than only by feature count.

| Metric ID | Metric | Baseline measurement method | Optimization target seed |
|---|---|---|---|
| EDUOPS-BM-001 | Course setup time | Time from new course shell to validated course/section/role config | <= 15 minutes for fixture course after first-time GitHub/org setup |
| EDUOPS-BM-002 | Roster-to-active conversion time | Time from CSV/JSON roster import to active/provisioned student workspaces | <= 3 minutes for 30-student fixture excluding student response latency |
| EDUOPS-BM-003 | Identity mismatch resolution effort | Number of manual checks/actions per mismatched GitHub identity | One instructor approval/reject screen with duplicate warning and audit record |
| EDUOPS-BM-004 | Assignment publication effort | Steps from approved Problem Bank version to per-student availability | Single publish workflow with preview, validation, and rollback evidence |
| EDUOPS-BM-005 | Assignment update safety | Whether update overwrites `workspace/**` or loses acknowledgement evidence | Zero overwrite in fixture; each update has diff/notice/acknowledgement record |
| EDUOPS-BM-006 | Submission confidence | Whether student and instructor see same submission state | Queued/pushed/confirmed/returned/reopened states match Git/evidence ledger |
| EDUOPS-BM-007 | Evaluation turnaround visibility | Time and status fidelity from confirmed submission to visible evaluation result | Async progress plus failure reason; no UI blocking |
| EDUOPS-BM-008 | Grade/feedback release effort | Steps from evaluated submission to controlled feedback release/export | Batch release with per-student exceptions and audit/export evidence |
| EDUOPS-BM-009 | Dispute reconstruction time | Time to reconstruct assignment version, student snapshot, evaluation profile, feedback decision | <= 5 minutes for fixture dispute packet |
| EDUOPS-BM-010 | Live-service dependency resilience | Ability to continue local work during GitHub outage or no LMS availability | Local authoring/student checkpointing continues; remote submission remains unconfirmed until GitHub evidence exists |

## 5. Recommended product optimization baseline

1. **Roster-first, GitHub-bound identity model**: use course roster ID as the stable academic identity and treat GitHub account binding as approved operational evidence.
2. **Two-pane course dashboard**: combine Google-Classroom-like course/student overview with GitHub-Classroom-like repository/evidence state.
3. **Assignment operation pipeline**: Problem Bank version -> assignment instance -> publication preview -> per-student workspace provisioning -> sync/update notice -> submission branch snapshot -> evaluation -> review -> feedback release -> export/archive.
4. **State vocabulary aligned to classroom operations**: `imported`, `invited`, `bound`, `provisioned`, `active`, `queued`, `pushed`, `confirmed`, `evaluated`, `returned`, `reopened`, `feedback_released`, and `archived`.
5. **Unified evidence ledger**: every high-impact transition links actor, role, source object, target object, Git SHA or file hash, timestamp, decision, and result.
6. **Bulk operations with exception handling**: instructors should batch invite/provision/publish/evaluate/release, but every exception must have a visible reason and override path.
7. **No LMS dependency remains active**: Google Classroom is a benchmark/reference, not a baseline integration target. Import/export remains controlled CSV/JSON unless explicitly promoted later.

## 6. ISO 9001 alignment

| Clause | Alignment |
|---|---|
| 4 Context | Identifies external reference systems and product differentiation boundary. |
| 6 Planning | Converts benchmark findings into risks, opportunities, and measurable objectives. |
| 7 Support | Adds controlled documented information and evidence records. |
| 8.3 Design and development | Turns benchmark results into design inputs and verification metrics. |
| 9 Performance evaluation | Defines measurable efficiency metrics and fixture benchmarks. |
| 10 Improvement | Captures opportunities to reduce instructor/student/TA workload while improving traceability. |

## 7. Open questions

1. Should EduOps ever offer an optional Google Classroom export/import adapter, or keep Google Classroom only as a benchmark reference?
2. What target class size should be used for first performance fixtures: 30, 60, 120, or 300 students?
3. Which workflow matters most for first optimization: roster onboarding, assignment publish/update, submission/evaluation, or feedback release/export?

## 8. Differentiation update

Following user clarification, the benchmark interpretation is updated: EduOps should not compete only on classroom-management efficiency. Its core differentiation over GitHub Classroom and Google Classroom is that assignment execution becomes a structured knowledge-work process. Student work should produce reusable personal knowledge artifacts and controlled DOCX/HWP/HWPX report exports while preserving Git-backed evidence.
