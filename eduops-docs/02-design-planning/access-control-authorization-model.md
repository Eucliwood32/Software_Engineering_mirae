---
title: Access Control and Authorization Model
document_id: SWENG-EDUTECH-ACM
version: 0.1.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Access Control and Authorization Model

## 1. Purpose

This document defines the EduOps authorization baseline. Role-separated UI and the role-permission matrix are necessary but not sufficient: every protected operation must pass an explicit access-control decision in application/backend logic and must produce audit evidence when the operation changes academic, repository, identity, grade, or evidence state.

## 2. Access-control model

EduOps shall use a scoped RBAC + policy-attribute model:

```text
Subject = actor identity + role + delegated scopes
Resource = course / section / assignment / workspace / submission / feedback / audit object
Action = view / create / update / publish / submit / evaluate / review / release / export / override
Context = course state + student lifecycle state + due policy + online/offline state + operation risk
Decision = allow / deny / allow-with-confirmation / allow-with-approval / queue / read-only
Evidence = authorization decision record + audit event where applicable
```

RBAC decides broad eligibility. Policy attributes decide whether the role may act in the current course, section, student, assignment, lifecycle, deadline, offline, and high-impact context.

## 3. Subject roles and scopes

| Subject | Scope rule |
|---|---|
| Student | Own courses, own assignment views, own workspace, own submissions, released feedback only |
| Instructor/professor | Assigned course/section authoring, publication, roster/identity approval, review, feedback release, export, controlled override |
| TA | Delegated course/section/assignment/student review scope only; no default publication, roster approval, or grade release |
| Admin/operator | Configuration, provisioning, recovery, audit/export according to assigned administrative scope; no automatic academic grading authority |
| Evaluator | Read assigned snapshots and write evaluation evidence; no feedback release or roster mutation |
| Sync worker | Execute queued sync/submission operations within pre-authorized job scope; no independent human authority |
| Audit/reviewer | Read-only evidence/export review scope unless separately authorized |

## 4. Protected resource classes

| Resource class | Examples | Protection reason |
|---|---|---|
| Course/section | course metadata, section membership, due policy | Academic operation boundary |
| Roster/student identity | roster row, GitHub identity binding, student lifecycle state | Privacy, eligibility, identity integrity |
| Assignment bank/version | instructions, rubric, references, validation/evaluation rules | Source assignment integrity |
| Assignment instance/release | release ref/SHA, update reason, due window | Versioned distribution integrity |
| Student workspace | `assignment/**`, `workspace/**`, metadata | Student work isolation and source protection |
| Submission/evidence | submission branch/tag/snapshot/metadata | Grading evidence and dispute resolution |
| Evaluation run | toolchain profile, logs, result, feedback candidates | Safety and academic evidence |
| Feedback/grade/export | rubric notes, released feedback, grade export | Academic authority and privacy |
| Audit/override | audit events, recovery records, manual overrides | ISO 9001 traceability and fairness |
| Configuration/secrets | GitHub token references, repository settings, runner settings | Security and repository integrity |

## 5. Decision rules

| Rule ID | Rule |
|---|---|
| AC-001 | Default deny. Missing role, scope, resource, or context denies the action. |
| AC-002 | UI hiding is not authorization. All protected actions require an application/backend authorization check. |
| AC-003 | Student write actions are limited to own `workspace/**` and own submission intent. |
| AC-004 | Student read access to assignment/rubric/metadata is read-only and scoped to assigned courses/instances. |
| AC-005 | TA authority is delegated and bounded; TA does not inherit full instructor/admin authority. |
| AC-006 | Instructor authority is scoped to assigned course/section/assignment contexts. |
| AC-007 | Admin/operator authority does not automatically include academic grading or feedback-release authority. |
| AC-008 | Evaluator and sync-worker subjects operate only under pre-authorized job scope and cannot expand authority. |
| AC-009 | Offline mode may allow local work/checkpointing but cannot promote queued operations to confirmed remote/evidence state. |
| AC-010 | High-impact actions require visible context and confirmation. Some require approval before execution. |
| AC-011 | Manual override requires actor, reason, scope, approval/authority, before/after state, and audit event. |
| AC-012 | Git/repository adapter actions must enforce the same resource policy before branch/ref/path operations. |
| AC-013 | Access decisions involving grade, identity, token references, override, or export must be audit logged. |
| AC-014 | Rendering/view authorization may filter or redact content by role, but submitted canonical evidence must remain traceable. |

## 6. High-impact actions

| Action | Required control |
|---|---|
| Publish assignment instance | Instructor scope + validated assignment version + confirmation + audit |
| Approve identity binding | Instructor/admin scope + duplicate check + audit |
| Change student lifecycle status | Instructor/admin scope + reason + audit |
| Reopen/repair submission | Authorized override + reason + before/after + audit |
| Release feedback/grade result | Instructor or delegated release authority + confirmation + audit |
| Export grade/audit package | Instructor/admin scope + redaction policy + audit |
| Configure GitHub token/reference | Admin/operator scope + no raw secret exposure + audit |
| Run live evaluation profile | Authorized evaluator/instructor trigger + resource/safety profile |

## 7. Authorization decision record

Minimum fields:

| Field | Purpose |
|---|---|
| `decision_id` | Unique authorization decision identifier |
| `actor_id`, `subject_role` | Who requested the action |
| `delegated_scope` | Course/section/assignment/student scope held by actor |
| `resource_type`, `resource_id` | Protected object |
| `action` | Requested operation |
| `context` | Lifecycle/due/offline/high-impact state |
| `decision` | allow, deny, allow-with-confirmation, allow-with-approval, queue, read-only |
| `reason_code` | Policy rule or denial reason |
| `timestamp` | Decision time |
| `audit_event_id` | Audit link when created |

## 8. Test requirements

The access-control fixture suite shall include:

1. student cannot view another student's workspace/submission;
2. student cannot modify `assignment/**`;
3. student cannot access instructor publication/review/export controls via UI or direct call;
4. TA can review only delegated submissions;
5. TA cannot release feedback unless explicitly delegated;
6. admin can provision/recover but cannot grade unless delegated;
7. evaluator can read snapshots and write evaluation evidence only;
8. sync worker cannot perform arbitrary repository operations;
9. offline queued submission is not confirmed until authorized sync evidence exists;
10. manual override creates before/after audit evidence;
11. Git adapter rejects unauthorized ref/path operations;
12. export applies role/redaction controls.

## 9. Traceability

| Source | Access-control implication |
|---|---|
| EDUOPS-FR-025 | Mode-specific actions require enforceable policy decisions |
| EDUOPS-FR-029 | Manual override must be authorized and audited |
| EDUOPS-FR-034 | Role-separated UI must map to enforceable backend/application authorization |
| EDUOPS-NFR-010 | Mode boundaries must be understandable and enforceable |
| EDUOPS-NFR-013 | UI hiding is not sufficient access control |
| EDUOPS-DEC-022 | Access control is a first-class product baseline |

## 8. Knowledge and export access update

`knowledge/**` resource classes shall use visibility levels `student_private`, `submission_evidence`, `course_review`, and `public_example_candidate`. Instructors/TA may review submitted knowledge artifacts only within the approved assignment submission scope or authorized override/recovery flow. Derived exports shall expose canonical evidence links and redaction profiles but shall not expose raw credentials or unrelated private notes.
