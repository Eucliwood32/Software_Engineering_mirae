---
title: HISYS EduOps Platform Usage Scenarios
document_id: SWENG-EDUTECH-USE-SCENARIOS
version: 0.5.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Usage Scenarios

## 1. Scenario baseline

This document defines end-to-end usage scenarios for HISYS EduOps Platform, beginning with student registration and continuing through assignment publication, workspace provisioning, submission, evaluation, feedback, exception handling, and course archive.

The baseline remains:

- Windows and Linux desktop application only.
- GitHub-first repository backend; self-hosted Git later.
- C/C++ assignment evaluation first.
- LMS excluded; roster/grade/audit exchange is local CSV/JSON import/export only.
- Student management and operating modes are first-class product controls.

## 2. Main happy-path scenario: from student registration to feedback release

| Step | Scenario | Primary mode | Main actor | State/evidence output |
|---|---|---|---|---|
| S0 | Course shell setup | Course operation/admin | Instructor/admin | Course/section record, due policy, GitHub context |
| S1 | Roster import | Course operation/admin | Instructor/admin | Roster import evidence, Imported student records |
| S2 | Student GitHub identity invitation | Course operation/admin | Instructor/admin | Invitation/binding request records, Invited state |
| S3 | Student identity claim | Student workspace / onboarding | Student | Claimed GitHub username, pending approval |
| S4 | Instructor/admin identity approval | Course operation/admin | Instructor/admin | Bound student records, duplicate-check evidence |
| S5 | Workspace and repository provisioning | Course operation/admin / sync | App/admin | Provisioned state, workspace path, submission namespace, GitHub permission evidence |
| S6 | Assignment instance publication | Instructor authoring | Instructor | Assignment Instance version, GitHub publication SHA |
| S7 | Student workspace activation | Student workspace | Student | Active state, local assignment cache, read-only assignment area |
| S8 | Student checkpoint work | Student workspace / offline-local | Student | Local Git commits, queued/pushed sync state |
| S9 | Student submission | Student workspace | Student | Submission snapshot SHA, assignment version, queued/pushed/confirmed status |
| S10 | Automated C/C++ evaluation | Evaluation runner | Evaluator | Compile/test/static-analysis evidence, compiler metadata |
| S11 | TA/instructor review | TA review / instructor review | TA/instructor | Review notes, rubric result, failure classification |
| S12 | Feedback release | Instructor/TA review | Instructor/TA | Feedback release record, visible student feedback |
| S13 | Grade/evidence export | Review/audit | Instructor/admin | Local CSV/JSON grade export and audit package |
| S14 | Course/archive closeout | Review/audit | Instructor/admin | Read-only archive, retention/export record |

## 3. Detailed scenarios

### SCN-001 Course shell setup

**Goal:** Create the local course operating context before any student data is imported.

| Field | Description |
|---|---|
| Actors | Instructor/admin |
| Mode | Course operation/admin mode |
| Preconditions | Windows desktop app installed; GitHub organization/repository policy selected; no LMS dependency |
| Main flow | Create course, term, section, instructor/TA list, due policy, GitHub context, local data directory |
| Evidence | Course record, actor/timestamp, GitHub context validation, no-LMS configuration marker |
| Postcondition | Course is ready for roster import |
| Requirements | EDUOPS-FR-001, EDUOPS-FR-021, EDUOPS-FR-023 |

### SCN-002 Roster import and validation

**Goal:** Convert controlled local roster input into auditable student records.

| Field | Description |
|---|---|
| Actors | Instructor/admin |
| Mode | Course operation/admin mode |
| Preconditions | Course shell exists; CSV/JSON roster file prepared |
| Main flow | Select roster file, validate schema, detect duplicate roster IDs, preview rows, approve import |
| Evidence | Roster file hash, schema version, validation report, accepted/rejected rows, Imported student records |
| Postcondition | Student records exist in Imported state |
| Failure/exception | Invalid rows are rejected without creating active students |
| Requirements | EDUOPS-FR-002, EDUOPS-FR-003, EDUOPS-NFR-009 |

### SCN-003 Student GitHub identity invitation and claim

**Goal:** Bind student roster identities to GitHub identities without LMS.

| Field | Description |
|---|---|
| Actors | Instructor/admin, student |
| Modes | Course operation/admin, student onboarding/workspace mode |
| Preconditions | Student is Imported; GitHub-first backend selected |
| Main flow | Instructor/admin issues binding request; student opens app, selects course/section, enters or confirms GitHub username; app records claim |
| Evidence | Invitation record, claimed GitHub username, claim timestamp, pending approval status |
| Postcondition | Student is Invited or pending Bound approval |
| Failure/exception | Missing/invalid GitHub username remains unbound; no workspace is provisioned |
| Requirements | EDUOPS-FR-004, EDUOPS-FR-021, EDUOPS-FR-023 |

### SCN-004 Identity approval and duplicate check

**Goal:** Prevent roster/GitHub identity mismatch before provisioning.

| Field | Description |
|---|---|
| Actors | Instructor/admin |
| Mode | Course operation/admin mode |
| Preconditions | Student has claimed GitHub identity |
| Main flow | Review roster identity and claimed GitHub username; run duplicate check; approve or reject; record reason if rejected |
| Evidence | Approval/rejection record, duplicate-check result, actor/timestamp |
| Postcondition | Approved student enters Bound state |
| Failure/exception | Duplicate GitHub account requires rejection or manual override evidence |
| Requirements | EDUOPS-FR-004, EDUOPS-FR-005, EDUOPS-FR-029 |

### SCN-005 Student workspace and GitHub namespace provisioning

**Goal:** Prepare isolated per-student workspaces and submission namespaces.

| Field | Description |
|---|---|
| Actors | Instructor/admin, app sync worker |
| Modes | Course operation/admin, synchronization mode |
| Preconditions | Student is Bound; assignment instance may exist or be queued |
| Main flow | Create workspace path; configure read-only assignment area and writable workspace area; create/validate GitHub branch/namespace/permission; record provisioning evidence |
| Evidence | Provisioning record, workspace path, GitHub repo/branch/permission evidence, student state transition to Provisioned |
| Postcondition | Student can become Active when assignment is available |
| Failure/exception | GitHub permission failure leaves student Bound with provisioning error; no false Active state |
| Requirements | EDUOPS-FR-006, EDUOPS-FR-011, EDUOPS-FR-023 |

### SCN-006 Assignment publication and student activation

**Goal:** Publish a C/C++ assignment instance and make it available to provisioned students.

| Field | Description |
|---|---|
| Actors | Instructor, sync worker, student |
| Modes | Instructor authoring, synchronization, student workspace |
| Preconditions | Problem Bank package exists; assignment instance metadata exists; students are Provisioned |
| Main flow | Instructor publishes assignment; GitHub publication SHA is recorded; sync worker updates student assignment area; student opens app and sees read-only assignment plus writable workspace |
| Evidence | Assignment version, publication SHA, student activation state, local assignment cache metadata |
| Postcondition | Student is Active for the assignment |
| Failure/exception | Student workspace is not activated until assignment version is locally available or sync failure is visible |
| Requirements | EDUOPS-FR-009, EDUOPS-FR-010, EDUOPS-FR-011, EDUOPS-FR-015, EDUOPS-FR-016 |

### SCN-007 Student work checkpoint and offline queue

**Goal:** Let students work without using Git CLI while preserving Git evidence.

| Field | Description |
|---|---|
| Actors | Student |
| Modes | Student workspace, offline/local mode |
| Preconditions | Student is Active; assignment area is read-only; workspace area exists |
| Main flow | Student edits C/C++ files in workspace; saves/checkpoints; app creates local Git commits; if offline, commits remain queued for remote sync |
| Evidence | Local commit SHA, action type, timestamp, queued/pushed state |
| Postcondition | Student work history exists locally and is ready to sync |
| Failure/exception | Offline queued commits must not be displayed as GitHub-confirmed submissions |
| Requirements | EDUOPS-FR-013, EDUOPS-FR-025, EDUOPS-FR-028, EDUOPS-NFR-006 |

### SCN-008 Student submission

**Goal:** Create an auditable assignment submission snapshot.

| Field | Description |
|---|---|
| Actors | Student, sync worker |
| Modes | Student workspace, synchronization mode |
| Preconditions | Student is Active; submission window/status permits submission; workspace contains work |
| Main flow | Student selects submit; app shows assignment version and included files; student confirms; app creates submission snapshot; pushes to GitHub namespace; records queued/pushed/confirmed state |
| Evidence | Submission snapshot SHA, assignment version, eligibility/late status, confirmation state, actor/timestamp |
| Postcondition | Student state enters Submitted after confirmed submission or queued-submission state if offline |
| Failure/exception | Locked/withdrawn students cannot submit unless manual override exists; failed push remains queued/pushed-error, not confirmed |
| Requirements | EDUOPS-FR-014, EDUOPS-FR-027, EDUOPS-FR-028, EDUOPS-FR-021 |

### SCN-009 Automated C/C++ evaluation

**Goal:** Compile/test/analyze confirmed student submissions under controlled limits.

| Field | Description |
|---|---|
| Actors | Evaluation runner, TA/instructor |
| Mode | Evaluation runner mode |
| Preconditions | Submission snapshot exists; evaluation profile is defined |
| Main flow | Pull snapshot; run compiler/build; execute unit tests; run static analysis; enforce timeout/memory/process/filesystem limits; write evidence |
| Evidence | Input SHA, compiler name/version, standard flag, build profile, commands, logs, result status, resource-limit events |
| Postcondition | Student assignment state enters Evaluated or evaluation-failed state |
| Failure/exception | Unsafe/infinite-loop code is contained and reported as controlled failure evidence |
| Requirements | EDUOPS-FR-017, EDUOPS-FR-018, EDUOPS-NFR-005, EDUOPS-NFR-007 |

### SCN-010 TA/instructor review and feedback release

**Goal:** Convert submission/evaluation evidence into controlled educational feedback.

| Field | Description |
|---|---|
| Actors | TA, instructor |
| Modes | TA review, instructor review |
| Preconditions | Submission and evaluation evidence exist |
| Main flow | Review code, compile/test logs, static-analysis results, rubric; draft feedback; instructor/TA releases feedback; student sees released feedback |
| Evidence | Review notes, rubric version, feedback release record, visible result set, release timestamp |
| Postcondition | Student assignment state enters Feedback Released |
| Failure/exception | Draft feedback is not visible to students until release action is confirmed |
| Requirements | EDUOPS-FR-019, EDUOPS-FR-020, EDUOPS-FR-027 |

### SCN-011 Instructor assignment update after release

**Goal:** Update assignment content without overwriting student work.

| Field | Description |
|---|---|
| Actors | Instructor, sync worker, student |
| Modes | Instructor authoring, synchronization, student workspace |
| Preconditions | Assignment already published; students may have workspace changes |
| Main flow | Instructor publishes corrected assignment version; sync worker applies changes to assignment area only; app creates change notice listing affected files and required action |
| Evidence | New assignment version, publication SHA, sync log, student notice record |
| Postcondition | Student assignment area is updated; workspace content is preserved |
| Failure/exception | Potential conflict creates notice/review task, not silent overwrite |
| Requirements | EDUOPS-FR-015, EDUOPS-FR-016 |

### SCN-012 Student status change: late, locked, withdrawn

**Goal:** Manage eligibility and access changes during a course.

| Field | Description |
|---|---|
| Actors | Instructor/admin |
| Mode | Course operation/admin mode |
| Preconditions | Student record exists |
| Main flow | Instructor/admin changes status; app shows affected permissions and submission eligibility; actor confirms; audit record is written |
| Evidence | Status-change record, before/after status, reason, actor/timestamp |
| Postcondition | Submission/review/evaluation behavior follows new status |
| Failure/exception | Locked/withdrawn student cannot submit unless override is approved |
| Requirements | EDUOPS-FR-008, EDUOPS-FR-021, EDUOPS-FR-029 |

### SCN-013 Manual override and recovery

**Goal:** Repair exceptional academic/technical states without corrupting auditability.

| Field | Description |
|---|---|
| Actors | Authorized instructor/admin |
| Mode | Recovery/manual override mode |
| Preconditions | Exception exists, such as wrong GitHub identity, failed sync, submission reopening request, or late exception |
| Main flow | Select override type; enter reason/scope; review before/after state; confirm; app writes override evidence and applies bounded change |
| Evidence | Override record with actor, reason, scope, approval/authority, timestamp, affected record, before/after state |
| Postcondition | Corrected state is visible and traceable |
| Failure/exception | Override without required evidence is blocked |
| Requirements | EDUOPS-FR-029, EDUOPS-FR-021, EDUOPS-FR-027 |

### SCN-014 No-LMS grade/evidence export and archive

**Goal:** Close the assignment/course with controlled local exports.

| Field | Description |
|---|---|
| Actors | Instructor/admin |
| Modes | Review/audit mode |
| Preconditions | Feedback/evaluation states are complete or explicitly marked incomplete |
| Main flow | Generate grade/evaluation CSV/JSON; generate audit package; verify redaction; archive course/assignment records read-only |
| Evidence | Export file hash, schema version, redaction result, archive timestamp |
| Postcondition | Course/assignment is archived with reproducible evidence |
| Failure/exception | Export is blocked if privacy/redaction checks fail unless controlled override policy allows partial export |
| Requirements | EDUOPS-FR-022, EDUOPS-FR-021, EDUOPS-NFR-004, EDUOPS-NFR-008 |

## 4. Scenario-to-mode matrix

| Scenario | Instructor authoring | Course/admin | Student | TA review | Evaluation | Offline | Sync | Audit | Recovery |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| SCN-001 |  | X |  |  |  |  |  |  |  |
| SCN-002 |  | X |  |  |  |  |  | X |  |
| SCN-003 |  | X | X |  |  |  |  |  |  |
| SCN-004 |  | X |  |  |  |  |  | X | X |
| SCN-005 |  | X |  |  |  |  | X | X |  |
| SCN-006 | X |  | X |  |  |  | X |  |  |
| SCN-007 |  |  | X |  |  | X | X |  |  |
| SCN-008 |  |  | X |  |  | X | X | X |  |
| SCN-009 |  |  |  |  | X |  |  | X |  |
| SCN-010 |  |  | X | X |  |  |  | X |  |
| SCN-011 | X |  | X |  |  |  | X | X |  |
| SCN-012 |  | X |  |  |  |  |  | X | X |
| SCN-013 |  | X |  |  |  |  |  | X | X |
| SCN-014 |  | X |  |  |  |  |  | X |  |

## 5. Scenario acceptance gates

- Student registration must not become Active before identity binding and provisioning evidence exist.
- Student workspace provisioning must not grant access to other students' work.
- Submission success must distinguish queued, pushed, and GitHub-confirmed states.
- Assignment updates must never silently overwrite student workspace files.
- Evaluation runner must record input SHA, toolchain metadata, commands, logs, and resource-limit outcomes.
- Feedback must remain draft-only until controlled release.
- Manual override must be impossible without actor, reason, scope, timestamp, authority, and before/after state.
- No scenario may require LMS credentials or LMS availability.

## 6. Open scenario questions

1. What is the exact identity-binding user experience: invite code, GitHub username entry, QR/link, or instructor-admin mapping?
2. Should students create GitHub accounts outside the app, or should the app guide account creation without storing credentials?
3. What are the exact submission confirmation labels in Korean/English UI?
4. Which scenarios must work fully offline, and which only queue work until GitHub is reachable?
5. Who can approve manual override: instructor only, instructor+admin, or two-person review for grade-impacting overrides?
