---
title: State Machine Implementation Tables
document_id: SWENG-EDUTECH-STATE-TABLES
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CFR-007', 'EDUOPS-CFR-008', 'EDUOPS-CFR-009']
  related: ['SWENG-EDUTECH-STATE-MACHINE-CANONICAL']
---

# State Machine Implementation Tables

## 1. Rules

State transitions are owned by the application core. UI labels, adapter statuses, and worker phases may not directly replace these state values. Every accepted transition records an `AuditEvent` with actor, event, guard result, previous state, next state, authoritative time, and correlation ID.

## 2. Student lifecycle

| Current | Event | Guard | Next | Side effect |
|---|---|---|---|---|
| `invited` | `roster.import.accepted` | valid roster row | `invited` | Create roster entry. |
| `invited` | `identity.approved` | no duplicate approved binding | `active` | Enable provisioning eligibility. |
| `active` | `student.lock` | instructor/admin reason provided | `locked` | Block new submissions; preserve evidence. |
| `locked` | `student.unlock` | admin/instructor approval | `active` | Restore permitted operations. |
| `active` | `student.withdraw` | withdrawal effective time recorded | `withdrawn` | Block access; schedule cleanup/archive. |
| `withdrawn` | `student.archive` | retention package complete | `archived` | Close workspace. |
| `active` | `course.archive` | course archive gate passes | `archived` | Archive course-scoped evidence. |

## 3. Assignment release and update

| Current | Event | Guard | Next | Side effect |
|---|---|---|---|---|
| `draft` | `version.publish` | document validates | `scheduled` | Create immutable assignment version. |
| `scheduled` | `release.time_reached` | authoritative now >= release_at | `released` | Make assignment visible. |
| `released` | `instructor.publish_update` | new version validates | `update_available` | Notify affected workspaces. |
| `update_available` | `student.ack_update` | assignment-only diff applies cleanly | `released` | Update assignment scope, preserve workspace. |
| `released` | `due.time_reached` | authoritative now >= due_at | `closed` | Mark late submissions by policy. |
| `closed` | `late_exception.granted` | scoped approval exists | `released` | Record exception window. |
| `closed` | `course.archive` | retention gate passes | `archived` | Freeze assignment evidence. |

## 4. Submission lifecycle

| Current | Event | Guard | Next | Side effect |
|---|---|---|---|---|
| `draft` | `workspace.checkpoint` | workspace validates enough for checkpoint | `checkpointed` | Create local Git commit. |
| `checkpointed` | `submission.queue` | deadline/late policy allows attempt | `queued` | Create submission snapshot metadata. |
| `queued` | `fake_or_remote.push_succeeded` | target ref accepted | `pushed` | Record ref and commit SHA. |
| `pushed` | `backend.confirm_receipt` | evidence manifest validates | `confirmed` | Set authoritative received time. |
| `queued` | `push.failed_terminal` | terminal adapter error | `rejected` | Record error and remediation. |
| `confirmed` | `evaluation.completed` | result bound to snapshot | `evaluated` | Attach evaluation result. |
| `confirmed` | `submission.reopen` | instructor/admin reason | `reopened` | Create new attempt window. |

`queued` is never displayed as confirmed. `pushed` is transport evidence only; `confirmed` requires backend receipt and manifest validation.

## 5. Sync conflict handling

| Scope | Conflict detected when | Blocked action | Resolution |
|---|---|---|---|
| `assignment/**` | Local assignment file hash differs from released version without authorized update event | Student edit/save to assignment original | Restore assignment scope from immutable version or create diagnostic package. |
| `workspace/**` | Assignment update would alter student-owned path | Assignment update apply | Keep student file, create conflict notice, require student/instructor acknowledgement. |
| `knowledge/**` | Sync/export tries to include `student_private` artifact without promotion | Submission/export include | Block include and show privacy validation issue. |
| Git refs | Target submission ref already points to different commit | Submission confirmation | Mark `requires_manual_review`; do not overwrite. |

Conflict records include affected paths, base hash, local hash, incoming hash, actor, decision, and audit event ID.

## 6. Authoritative time semantics

| Time value | Source | Use |
|---|---|---|
| `authoritative_now` | Application core time service using UTC, with monotonic run clock for ordering | Release windows, deadline checks, audit ordering. |
| `client_display_time` | UI-local rendering of authoritative UTC in course timezone | Display only. |
| `git_commit_time` | Git commit metadata | Evidence context, not deadline authority by itself. |
| `submitted_at` | Time command accepted into local submission queue | Local attempt evidence. |
| `authoritative_received_at` | Backend confirmation time after manifest validation | Official receipt/late calculation in fake/local beta and future server-backed flows. |

Offline drift is recorded as diagnostic context. If clock drift exceeds policy threshold, deadline-sensitive commands become `requires_manual_review` rather than silently accepting or rejecting.
