---
title: HISYS EduOps Platform Service Concept
document_id: SWENG-EDUTECH-CONCEPT
version: 0.5.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Service Concept

## 1. Concept summary

HISYS EduOps Platform is a Windows desktop service layer around Git-backed Notion-style assignment repositories, branch-based submission records, and student lifecycle records. It turns course assignments, student management, submissions, evaluations, feedback release, and audit operations into controlled Git/evidence artifacts. It does not depend on LMS integration.

## 2. Core entities

| Entity | Description | Controlled evidence |
|---|---|---|
| Course/Section | Operating context for term, instructor, TAs, roster, due policy, and GitHub context | Course metadata, section policy, import/export records |
| Student Record | Roster identity, GitHub identity, lifecycle status, privacy flags, assignment states | Registry row, binding approval, status history, audit record |
| Problem Bank | Reusable C/C++ source assignment packages | Problem package version, starter code, rubric, checks, references |
| Assignment Instance | Operational use of one problem version in a course/section | Instance metadata, release/due policy, GitHub repo/branch policy, evaluation profile |
| Student Workspace | Student-specific Windows working copy and activity record | Workspace commits, local checkpoints, sync state |
| Submission Snapshot | Frozen student C/C++ submission for grading/evaluation | Submission commit SHA, assignment version, eligibility/late status, confirmation state |
| Evaluation Run | Automated Automatic validation/evaluation execution, including C/C++ profile where configured | Input SHA, compiler/toolchain profile, commands, logs, result, feedback |
| Feedback Release | Controlled release of grading/feedback to students | Reviewer, rubric version, timestamp, visible result set |
| Local Exchange File | No-LMS roster/grade/audit import-export artifact | Validated CSV/JSON file, schema version, redaction status |
| Override Record | Controlled exceptional action | Actor, reason, scope, approval, before/after state |

## 3. Operating modes

The application shall separate instructor authoring, course/admin operation, student workspace, TA review, evaluation runner, offline/local, synchronization, review/audit, and recovery/manual override modes. Each mode has explicit allowed/blocked actions and visible UI context.

## 4. Repository workflow seed

```text
GitHub Problem Bank Repository
  problems/<problem_id>/
    assignment.md
    starter/
    include/
    tests/
    rubrics/
    checks/

GitHub Assignment Instance Repository
  assignment/                 # synchronized instructor-controlled area
  rosters/                    # controlled roster inputs, no LMS connector
  students/                   # controlled student registry snapshots or redacted metadata
  submissions/<student_id>    # branch or namespace for submitted snapshots
  evaluations/<run_id>        # evaluation evidence and feedback artifacts
  feedback/<release_id>       # released feedback evidence
  audits/<audit_export_id>    # controlled audit exports when approved

Windows Student Workspace
  assignment/                 # read-only synchronized assignment content
  workspace/                  # student writable C/C++ documents/code
  .eduops/                    # local metadata, assignment version, sync/submission state
```

## 5. Synchronization concept

- Instructor changes update the Assignment Instance assignment area in GitHub.
- Student Windows desktop app receives assignment update metadata when GitHub is reachable.
- App applies changes only to the assignment area.
- Student workspace is preserved.
- Offline/local mode distinguishes queued commits from GitHub-confirmed submissions.
- If workspace files depend on changed assignment files, the app creates a Windows/in-app notification and optional review task rather than overwriting work.

## 6. Automated C/C++ evaluation concept

- Evaluation pulls or receives a submission snapshot from GitHub.
- Evaluation executes declared compile, unit-test, run, and static-analysis checks against the snapshot in a constrained environment.
- Results are recorded as evidence linked to assignment version, submission SHA, student record, compiler/toolchain profile, timeout/resource policy, and log artifacts.
- Feedback is prepared for instructor/TA review before controlled release.

## 7. Document-first branch-based baseline

The service concept now adopts the controlled chain `Problem Bank → Assignment Bank Item → Assignment Version → Assignment Instance → Student Workspace → Submission Branch → Submission Snapshot`. Assignment originals are document-first Markdown/Notion-style artifacts. Student submissions are official only when committed to `submissions/{student_id}` with `submission_metadata.json` and an assignment snapshot. See [Git-backed Notion-style assignment concept](git-backed-notion-assignment-concept.md) and [Repository permission and assignment workflow](repository-permission-workflow.md).

## 8. Explicit non-goals in current baseline

- No web app.
- No mobile app.
- No LMS connector, LTI integration, LMS grade passback, or LMS authentication dependency.
- No additional language family until C/C++ evaluation evidence is stable.

## Classroom operations cockpit optimization

The benchmark-derived service concept is a programming-course operations cockpit: a Google-Classroom-like overview of course, roster, coursework, submissions, feedback, and grades, backed by GitHub-Classroom-like repository, branch, SHA, code-review, and evaluation evidence. EduOps remains no-LMS by default; Google Classroom is a reference model and not a live dependency.

The cockpit shall surface bottlenecks as exception queues and evidence-health indicators rather than forcing instructors to inspect raw repositories or spreadsheets for normal operations.

## Knowledge-work execution layer

EduOps adds a knowledge-work execution layer above raw Git repositories. Students solve assignments through structured blocks, linked notes, experiments, decisions, and reflections, then submit both code/work products and controlled report/knowledge evidence. The system can export report-style outputs to DOCX and HWP/HWPX while preserving canonical Git/Markdown/editor-JSON evidence.

## 9. Gap-closure service concept update

EduOps now treats knowledge-work as a governed service layer. The service concept shall provide: knowledge artifact indexing, block-schema validation, export manifest generation, official/advisory evaluation separation, canonical state transitions, roster identity binding, and GitHub operation evidence. Live multi-user co-editing remains outside the baseline; structured block editing and local/Git-backed evidence are the controlled product value.

## 10. Notion-style storage service concept

The product shall include a Document Storage Service. The UI emits edit operations; the storage service validates permissions, appends the operation journal, updates rebuildable indexes, materializes canonical JSON/Markdown, and creates Git checkpoints. This mirrors Notion-like block editing while preserving EduOps evidence and Git portability.
