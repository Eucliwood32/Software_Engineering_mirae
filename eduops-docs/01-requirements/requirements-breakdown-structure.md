---
title: HISYS EduOps Platform Requirements Breakdown Structure
document_id: SWENG-EDUTECH-REQ-WBS
version: 0.8.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Requirements Breakdown Structure

## 1. Structuring conclusion

HISYS EduOps Platform requirements should be organized around two cross-cutting axes:

1. **Student lifecycle management**: roster import, identity binding, enrollment status, workspace provisioning, submission eligibility, evaluation history, feedback release, privacy, and course completion/archive.
2. **Operating modes**: the same product behaves differently when used by instructors, students, TAs, evaluators, admins, offline users, synchronization workers, and review/audit users.

This structure prevents the product from becoming only a Git assignment tool. It makes the platform an EduOps system for managing students, assignments, evaluation, and evidence under controlled workflows.

## 2. Requirement hierarchy

| Domain | Requirement group | Representative IDs | Purpose |
|---|---|---|---|
| Product boundary | Windows desktop, GitHub-first, C/C++ first, no LMS | EDUOPS-BND-* | Preserve accepted product scope |
| Course operations | Course, section, term, roster, policy setup | EDUOPS-COURSE-* | Define classroom operating context without LMS |
| Student management | Student records, identity binding, enrollment lifecycle, workspace state | EDUOPS-STU-* | Manage students as first-class operational entities |
| Assignment management | Problem Bank and Assignment Instance | EDUOPS-ASG-* | Manage reusable assignment source and section-specific operation |
| Workspace/submission | Local workspaces, commits, submission snapshots | EDUOPS-WS-* | Preserve student work and reproducible Git evidence |
| Synchronization | Assignment updates, GitHub sync, conflict notice | EDUOPS-SYNC-* | Keep assignment area current without overwriting student work |
| Evaluation | C/C++ compile/test/static analysis, sandbox, evidence | EDUOPS-EVAL-* | Execute safe, reproducible automated checks |
| Review/grading | TA/instructor review, rubric, feedback, grade export | EDUOPS-GRADE-* | Convert evidence into educational feedback and records |
| Audit/privacy | Traceability, personal data, token protection, archive | EDUOPS-AUD-* | Support dispute resolution and compliance controls |
| Modes/UX/access control | Mode-specific permissions, scoped access-control decisions, role-separated UI surfaces, and UI affordances | EDUOPS-MODE-* / EDUOPS-ROLE-UI-* / EDUOPS-AC-* | Separate roles, workflows, and authorization boundaries clearly |

## 3. Student lifecycle model

| Lifecycle state | Description | Required controls |
|---|---|---|
| Imported | Student appears in a controlled roster import but is not yet GitHub-bound. | Validate roster ID, name, section, email/identifier; no workspace until approved or queued. |
| Invited | Student has an invite or binding request. | Track invitation status, deadline, and GitHub username claim. |
| Bound | Roster identity is mapped to a GitHub identity. | Instructor/admin approval, duplicate-account check, audit record. |
| Provisioned | Student workspace and repository/branch permissions are prepared. | Read-only assignment area, writable workspace area, submission namespace. |
| Active | Student can receive updates, commit checkpoints, and submit. | Normal student mode permissions, sync notices, submission eligibility. |
| Submitted | Student has a recorded submission snapshot for an assignment. | Submission SHA, assignment version, timestamp, eligibility/late status. |
| Evaluated | Automated C/C++ evaluation evidence exists. | Compiler/toolchain metadata, logs, result status, failure classification. |
| Feedback released | Instructor/TA releases feedback/grade record. | Feedback release timestamp, reviewer, rubric version. |
| Locked/withdrawn | Student is suspended, dropped, or access is restricted. | Preserve evidence; block new submissions unless override is approved. |
| Archived | Course/assignment lifecycle ended. | Read-only archive, export package, retention policy. |

## 4. Operating modes

| Mode ID | Mode | Primary user/agent | Allowed actions | Explicitly blocked actions |
|---|---|---|---|---|
| EDUOPS-MODE-001 | Instructor authoring mode | Instructor | Create Problem Bank content, rubrics, C/C++ checks, release policies | Modify submitted student snapshots without audit/change record |
| EDUOPS-MODE-002 | Course operation/admin mode | Instructor/admin | Import roster, bind GitHub identities, provision workspaces, manage due policy | Edit student work content |
| EDUOPS-MODE-003 | Student workspace mode | Student | Read assignment area, edit workspace, checkpoint, submit, view notices/feedback | Modify assignment originals, view other students' work, alter evaluation evidence |
| EDUOPS-MODE-004 | TA review mode | TA | Inspect submissions, evaluation logs, rubric items, draft feedback | Change Problem Bank source or roster identity without permission |
| EDUOPS-MODE-005 | Evaluation runner mode | Local evaluator or controlled runner | Pull snapshot, compile/test/analyze, write evaluation evidence | Access personal files, alter source assignment, alter student workspace outside evaluation output |
| EDUOPS-MODE-006 | Offline/local mode | Student/instructor desktop app | Local checkpoint, view cached assignment, queue sync | Claim remote submission success before GitHub confirmation |
| EDUOPS-MODE-007 | Synchronization mode | App background worker | Pull assignment updates, push queued commits/submissions, create notices | Overwrite workspace files silently |
| EDUOPS-MODE-008 | Review/audit mode | Instructor/admin | Export audit, verify SHA, reproduce evidence, inspect history | Mutate operational records without change-control event |
| EDUOPS-MODE-009 | Recovery/manual override mode | Authorized instructor/admin | Correct identity binding, reopen submission, repair sync after incident | Perform override without reason, scope, timestamp, and actor evidence |

## 5. Controlled requirements by group

### 5.1 Course and roster requirements

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-COURSE-001 | The system shall define course, term, section, instructor, TA, due policy, and GitHub organization/repository context without LMS dependency. | Fixture course metadata validates without LMS credentials. |
| EDUOPS-COURSE-002 | The system shall import roster records from controlled CSV/JSON files. | Invalid/duplicate/missing roster fields are rejected with actionable diagnostics. |
| EDUOPS-COURSE-003 | The system shall version roster imports and preserve import evidence. | Roster import record includes file hash, schema version, actor, timestamp, and result. |

### 5.2 Student management requirements

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-STU-001 | The system shall maintain a student record linked to course roster ID, section, display name, contact identifier, GitHub identity, status, and privacy flags. | Student registry fixture validates required and optional fields. |
| EDUOPS-STU-002 | The system shall support GitHub identity binding with instructor/admin approval and duplicate-account detection. | Two students cannot be approved with the same GitHub identity unless an override record exists. |
| EDUOPS-STU-003 | The system shall track student lifecycle states from Imported through Archived. | State-transition tests reject invalid transitions, such as Active before Bound/Provisioned. |
| EDUOPS-STU-004 | The system shall provision per-student workspace and submission namespace from the approved student record. | Provisioning evidence links roster ID, GitHub identity, workspace path, repo/branch, and assignment instance. |
| EDUOPS-STU-005 | The system shall support student status changes such as active, late-allowed, locked, withdrawn, and archived. | Status changes affect submission eligibility and are audit logged. |
| EDUOPS-STU-006 | The system shall expose instructor/TA views for each student's assignment progress, submission state, evaluation state, and feedback release state. | Student dashboard fixture shows consistent state across assignment and evaluation records. |
| EDUOPS-STU-007 | The system shall prevent students from viewing or cloning other students' private work through the desktop workflow. | Permission fixture verifies per-student isolation. |
| EDUOPS-STU-008 | The system shall support authorized manual override for identity repair, submission reopening, and recovery actions. | Override requires actor, reason, scope, timestamp, affected record, and before/after state. |

### 5.3 Mode and permission requirements

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-MODE-REQ-001 | The system shall enforce mode-specific actions and blocked actions for instructor, admin, student, TA, evaluator, sync, audit, offline, and recovery modes. | Permission matrix tests cover allowed and blocked actions for each mode. |
| EDUOPS-AC-001 | The system shall make scoped authorization decisions for protected resources and actions using actor, role, resource, action, and context. | Authorization fixtures cover allow, deny, confirmation, approval, queued, and read-only decisions. |
| EDUOPS-AC-002 | The system shall record authorization/audit evidence for identity, grade, repository, export, override, and other high-impact operations. | Authorization decision records link to audit events and protected resources. |
| EDUOPS-MODE-REQ-002 | The system shall display the current operating mode and active course/assignment/student context where safety or evidence depends on it. | UI scenario shows visible mode/context before publish, submit, evaluate, export, and override actions. |
| EDUOPS-MODE-REQ-003 | The system shall require explicit confirmation for high-impact mode transitions, including publish, submit, release feedback, export grades, and manual override. | Confirmation evidence is recorded for high-impact transitions. |
| EDUOPS-MODE-REQ-004 | The system shall prevent offline mode from representing queued commits as successful remote submissions until GitHub confirmation exists. | Offline submission queue test distinguishes queued, pushed, and confirmed states. |

## 6. Traceability to existing SRS requirements

| Existing ID | Expanded by |
|---|---|
| EDUOPS-FR-002 | EDUOPS-COURSE-001, EDUOPS-COURSE-002, EDUOPS-COURSE-003 |
| EDUOPS-FR-003 | EDUOPS-STU-003, EDUOPS-STU-004, EDUOPS-STU-006 |
| EDUOPS-FR-006 | EDUOPS-STU-004, EDUOPS-STU-005, EDUOPS-MODE-REQ-004 |
| EDUOPS-FR-010 | EDUOPS-STU-006, EDUOPS-MODE-REQ-001 |
| EDUOPS-FR-012 | EDUOPS-COURSE-002, EDUOPS-COURSE-003 |
| EDUOPS-FR-013 | EDUOPS-STU-002, EDUOPS-STU-007 |
| EDUOPS-NFR-004 | EDUOPS-STU-001, EDUOPS-STU-007 |
| EDUOPS-NFR-006 | EDUOPS-MODE-006, EDUOPS-MODE-REQ-004 |

## 7. Next decomposition target

The next controlled design output should be a Software Design Description that defines:

- student registry schema;
- identity-binding workflow;
- mode/permission matrix;
- role-separated student/instructor/TA/admin UI feature matrix;
- GitHub repository topology for student isolation;
- workspace and submission state machine;
- manual override audit record.

## Classroom benchmark optimization work packages

| Work package | Scope | Parent trace |
|---|---|---|
| EDUOPS-BM-* | Course/student-management benchmark fixtures and measurements | EDUOPS-NFR-015 |
| EDUOPS-DASH-* | Instructor/admin course operations dashboard and drilldowns | EDUOPS-FR-036, FR-037 |
| EDUOPS-BULK-* | Bulk invitation, binding, provisioning, publish, evaluate, release, export operations with exception queue | EDUOPS-FR-038 |
| EDUOPS-PUB-* | Publication/update preview, diff, acknowledgement, rollback/evidence packet | EDUOPS-FR-039, FR-040 |
| EDUOPS-FEED-* | Unified code/evaluation/rubric feedback release and export | EDUOPS-FR-041 |

## Student knowledge and export work packages

| Work package | Scope | Parent trace |
|---|---|---|
| EDUOPS-BLOCK-* | Notion-style assignment execution blocks and required-block validation | EDUOPS-FR-042 |
| EDUOPS-KNOW-* | Student-owned knowledge notes, decisions, experiments, references, reflection links, and knowledge index | EDUOPS-FR-043, EDUOPS-NFR-017 |
| EDUOPS-REPORT-* | Report template mapping from assignment/knowledge blocks to export sections | EDUOPS-FR-044, FR-045 |
| EDUOPS-EXPORT-* | DOCX/HWP/HWPX/PDF export engines, manifests, hashes, warnings, and redaction profiles | EDUOPS-FR-046, EDUOPS-NFR-016 |

## 8. Gap-closure requirement packages

| Package | Child requirements | Controlled docs |
|---|---|---|
| EDUOPS-KNOWLEDGE-* | Knowledge topology, submission inclusion, visibility, retention, promotion, redaction | Knowledge topology and submission policy; Student knowledge policy |
| EDUOPS-EDITOR-* | Editor stack trade study, canonical block schema, Korean IME, accessibility, export binding | Editor stack trade study; Editor block schema baseline; Korean text handling profile; Accessibility baseline |
| EDUOPS-EXPORT-* | HWPX-first strategy, legacy HWP converter profile, DOCX/HWPX/HWP fidelity, export manifests | HWP and HWPX export strategy; Export fidelity acceptance criteria |
| EDUOPS-EVAL-* | Official runner profile, advisory pre-check, sandbox controls, evaluation evidence | Evaluation execution profile |
| EDUOPS-STATE-* | Student lifecycle, submission state, assignment release/update state | Canonical state machine profile |
| EDUOPS-GITHUB-* | API feasibility, topology, token model, rate-limit and outage handling | GitHub API feasibility analysis; GitHub topology and token model |
| EDUOPS-ROSTER-* | CSV/JSON schema, identity binding, privacy fields, duplicate detection | Roster schema and identity policy |
| EDUOPS-PERF-* | P50/P95 budgets and fixture measurements | Performance budget |

## 9. Notion-style storage package

| Package | Child requirements | Controlled docs |
|---|---|---|
| EDUOPS-STORAGE-* | Canonical JSON snapshot, Markdown projection, operation journal, asset refs, indexes, revisions, Git checkpoints, conflict records | Notion-style document storage architecture; Editor block schema baseline; Data API and document model |

## 10. Notion-style storage gap-closure package

| Package | Child requirements | Controlled docs |
|---|---|---|
| EDUOPS-STORAGE-GAP-* | JSON source-of-truth, deterministic derived projection, projection profile, artifact Git policy, block identity, schema migration, tombstone retention, asset privacy, local cache privacy | Document storage architecture; Block schema; Repository retention/LFS policy; Editor stack trade study; V&V plan |
