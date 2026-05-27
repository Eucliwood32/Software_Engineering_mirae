---
title: Interface Design Description
document_id: SWENG-EDUTECH-IDD
version: 0.5.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Interface Design Description

## 1. Purpose

This document defines logical interfaces before binding to REST, IPC, local service calls, or desktop framework events. Implementations may use native calls, local loopback APIs, or packaged web UI calls if they preserve the same interface semantics and evidence controls.

## 2. Common interface fields

All high-impact interfaces should support these common fields where applicable:

| Field | Purpose |
|---|---|
| `actor_id` | User/system actor initiating the action |
| `role` | Student, instructor, TA, admin/operator, evaluator, sync worker |
| `course_id`, `section_id` | Course context |
| `assignment_instance_id` | Assignment operation context |
| `student_id` | Student context when applicable |
| `request_id` | Idempotency and audit correlation |
| `timestamp` | Event time |
| `source_ref` | Git ref/commit/source object |
| `result_status` | Accepted, rejected, queued, failed, confirmed |
| `audit_event_id` | Audit/evidence link |

## 3. Logical interfaces

| ID | Interface | Producer | Consumer | Main purpose |
|---|---|---|---|---|
| IF-001 | Course Configuration | Instructor/admin UI | Course service | Create/update course, section, due policy |
| IF-002 | Roster Import | Instructor/admin UI | Roster service | Validate/import CSV/JSON roster |
| IF-003 | Identity Binding | Student/instructor UI | Student service | Claim/approve GitHub identity |
| IF-004 | Problem Bank Authoring | Instructor UI | Problem Bank service | Create/version assignment originals |
| IF-005 | Assignment Publication | Instructor UI | Assignment Instance service | Publish assignment version to course/section |
| IF-006 | Workspace Provisioning | Admin/sync service | Workspace service | Create student workspace and submission namespace |
| IF-007 | Assignment Sync | Student UI/sync worker | Git Sync service | Pull assignment updates into read-only assignment area |
| IF-008 | Workspace Checkpoint | Student UI | Git Sync service | Commit student workspace changes |
| IF-009 | Submission | Student UI | Submission service | Create submission snapshot/branch/tag/metadata |
| IF-010 | Rendering Preview | Student/instructor UI | Rendering core | Render document/graph/table/image previews |
| IF-011 | Validation | UI/background worker | Validation service | Check required sections/assets/deadline/rules |
| IF-012 | Evaluation Run | Evaluator/scheduler | Evaluation service | Execute C/C++ profile and record evidence |
| IF-013 | Review Feedback | TA/instructor UI | Feedback service | Draft/release feedback and grade notes |
| IF-014 | Audit Export | Instructor/admin UI | Audit/evidence service | Export grade/evidence/audit package |
| IF-015 | Manual Override | Authorized instructor/admin | Recovery service | Repair identity/submission/sync state with audit |
| IF-016 | Authorization Decision | UI/service/worker | Access-control service | Decide allow/deny/confirm/approval/queue/read-only for protected actions |

## 4. Interface-specific validation seeds

| Interface | Validation seed |
|---|---|
| IF-002 | Reject duplicate/missing roster identifiers; record file hash and rejected rows |
| IF-003 | Duplicate GitHub identity requires explicit override evidence |
| IF-005 | Publication requires validated assignment version and release reason |
| IF-007 | Sync can modify `assignment/**` but not `workspace/**` |
| IF-008 | Checkpoint can modify only allowed student workspace paths |
| IF-009 | Submission metadata must include assignment version, workspace commit, submission commit, and timestamp |
| IF-010 | Rendering result must include renderer profile and fallback/error evidence if incomplete |
| IF-012 | Evaluation must include toolchain profile, limits, command/result/logs |
| IF-015 | Override requires actor, reason, scope, before/after state, and approval where applicable |
| IF-016 | Authorization decision requires subject, role, delegated scope, resource, action, context, decision, and reason code |

## 5. Transport stance

No single transport is fixed yet. Acceptable implementation bindings include:

- in-process application service calls;
- local helper process IPC;
- local loopback HTTP API;
- packaged desktop shell calling a local service;
- future platform-specific bindings.

Remote-only rendering or remote-only normal assignment operation is not accepted for the current product baseline.

## 6. Gap-closure interface additions

| Interface | Purpose | Required controls |
|---|---|---|
| `IF-KNOWLEDGE-001` | Create/update knowledge artifact | Enforce owner, privacy class, assignment context, evidence refs |
| `IF-KNOWLEDGE-002` | Select knowledge artifacts for submission | Validate assignment policy, redaction, manifest linkage |
| `IF-EDITOR-001` | Save canonical block document | Validate block schema version, stable block IDs, source payloads, privacy class |
| `IF-EXPORT-001` | Generate derived DOCX/HWPX/HWP/PDF output | Record source SHA, template, tool profile, hash, warnings |
| `IF-EVAL-001` | Run advisory or official evaluation | Distinguish advisory from authoritative runner evidence |
| `IF-STATE-001` | Transition lifecycle/submission/release state | Reject cross-family invalid transitions such as queued-as-confirmed |
| `IF-ROSTER-001` | Import roster and bind GitHub identity | Validate schema, encoding, duplicates, approval, and audit evidence |

## 7. Notion-style storage interfaces

| Interface | Purpose | Required controls |
|---|---|---|
| `IF-STORAGE-001` | Append edit operation | Permission check, base revision, operation payload, actor, resulting revision |
| `IF-STORAGE-002` | Materialize canonical revision | Deterministic JSON/Markdown projection, hash computation, schema validation |
| `IF-STORAGE-003` | Create Git checkpoint | Link revision hash, operation range, asset hashes, and commit SHA |
| `IF-STORAGE-004` | Rebuild local indexes | Recreate block/search/render indexes from canonical files |
| `IF-STORAGE-005` | Resolve document conflict | Record local/remote/base revisions, affected block IDs, resolution, audit event |

## 8. Storage gap-closure interfaces

| Interface | Purpose | Required controls |
|---|---|---|
| `IF-STORAGE-006` | Generate/clone block identity | Scoped ID, template-origin lineage, split/merge/tombstone records |
| `IF-STORAGE-007` | Generate Markdown projection | Pinned profile, NFC/LF normalization, lossy-block warnings, manifest output |
| `IF-STORAGE-008` | Migrate schema/storage version | Input/output hashes, downgrade rejection, failure quarantine |
| `IF-STORAGE-009` | Resolve block reference | Return live/tombstoned/snapshot-only/removed-after-retention state for comments/export/feedback |
| `IF-STORAGE-010` | Apply asset privacy policy | Remote/LFS eligibility, redaction, visibility, and search-index inclusion controls |

## 9. SRS-derived interface contract expansion

This section expands the logical interfaces from the SRS and SDD. Transport binding remains local/desktop controlled; remote-only operation is not accepted.

### 9.1 Additional controlled logical interfaces

| Interface | Purpose | Required inputs | Required outputs/evidence | Error/denial controls |
|---|---|---|---|---|
| IF-CONFIG-001 | Load effective configuration | app/system/user/course/repository/runtime scopes, schema version, actor/context | effective config hash, redacted source list, validation report | unknown protected key, unsafe migration, denied actor |
| IF-CONFIG-002 | Validate configuration fixture | fixture config set, expected hash, offline/live policy | pass/fail report, schema violations, redaction scan | fail closed on raw secret or live-call violation |
| IF-CONFIG-003 | Update controlled setting | actor, scope, key, redacted value/reference, reason | before/after hashes, audit event, effective config revision | deny protected scope without authorization |
| IF-CREDENTIAL-001 | Register credential reference | provider, reference label, expiry, actor, storage provider handle | credential reference ID, fingerprint, audit event | raw secret never returned or logged |
| IF-CREDENTIAL-002 | Rotate/revoke credential reference | credential reference ID, actor, reason | rotation/revocation event, dependent adapter invalidation | deny student actors and stale references |
| IF-TRACE-001 | Resolve requirement trace | requirement ID, implementation slice, artifact context | RTM row, design anchor, STD/fixture anchor, evidence status | block coding-ready state for Grouped/Gap rows |
| IF-TDD-001 | Record TDD evidence | requirement ID, test command, RED output, GREEN output, refactor command | evidence package record, hashes, commit/reference link | reject GREEN-only or missing RED evidence |

### 9.2 Interface-to-SRS traceability table

| Requirement ID | Interface anchors | SRS section | Test anchors |
|---|---|---|---|
| `EDUOPS-FR-001` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-002` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-003` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-004` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-005` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-006` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-007` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-008` | IF-001, IF-002, IF-003, IF-006 | 4.1 Course and student management | STD-001..STD-005 |
| `EDUOPS-FR-009` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-010` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-011` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-012` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-013` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-014` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-015` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-016` | IF-004, IF-005, IF-007, IF-008, IF-009 | 4.2 Assignment and workspace management | STD-006..STD-013 |
| `EDUOPS-FR-017` | IF-012, IF-013, IF-014 | 4.3 Evaluation, grading, and evidence | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-018` | IF-012, IF-013, IF-014 | 4.3 Evaluation, grading, and evidence | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-019` | IF-012, IF-013, IF-014 | 4.3 Evaluation, grading, and evidence | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-020` | IF-012, IF-013, IF-014 | 4.3 Evaluation, grading, and evidence | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-021` | IF-012, IF-013, IF-014 | 4.3 Evaluation, grading, and evidence | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-022` | IF-012, IF-013, IF-014 | 4.3 Evaluation, grading, and evidence | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-023` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-024` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-025` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-026` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-027` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-028` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-029` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-030` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-031` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-032` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-033` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-034` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-035` | IF-010, IF-011, IF-015, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-019..STD-028 |
| `EDUOPS-FR-036` | IF-001, IF-002, IF-006, IF-014, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-029..STD-033 |
| `EDUOPS-FR-037` | IF-001, IF-002, IF-006, IF-014, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-029..STD-033 |
| `EDUOPS-FR-038` | IF-001, IF-002, IF-006, IF-014, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-029..STD-033 |
| `EDUOPS-FR-039` | IF-001, IF-002, IF-006, IF-014, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-029..STD-033 |
| `EDUOPS-FR-040` | IF-001, IF-002, IF-006, IF-014, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-029..STD-033 |
| `EDUOPS-FR-041` | IF-001, IF-002, IF-006, IF-014, IF-016 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-029..STD-033 |
| `EDUOPS-FR-042` | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-034..STD-038 |
| `EDUOPS-FR-043` | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-034..STD-038 |
| `EDUOPS-FR-044` | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-034..STD-038 |
| `EDUOPS-FR-045` | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-034..STD-038 |
| `EDUOPS-FR-046` | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-034..STD-038 |
| `EDUOPS-FR-047` | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-039..STD-044 |
| `EDUOPS-FR-048` | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-039..STD-044 |
| `EDUOPS-FR-049` | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-039..STD-044 |
| `EDUOPS-FR-050` | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-039..STD-044 |
| `EDUOPS-FR-051` | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | 4.4 Repository backend, operating modes, document model, and editor capabilities | STD-039..STD-044 |
| `EDUOPS-NFR-001` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-002` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-003` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-004` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-005` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-006` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-007` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-008` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-009` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-010` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-011` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-012` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-013` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-014` | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | 5. Non-functional requirements | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-015` | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | 5. Non-functional requirements | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-016` | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | 5. Non-functional requirements | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-017` | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | 5. Non-functional requirements | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-018` | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | 5. Non-functional requirements | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-019` | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | 5. Non-functional requirements | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-FR-052` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-053` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-054` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-055` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-056` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-057` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-058` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-059` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-060` | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-020` | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-021` | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-022` | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-023` | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-024` | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | 10. Claude review gap-closure requirements | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-061` | IF-STORAGE-001..010 | 11. Notion-style storage requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-062` | IF-STORAGE-001..010 | 11. Notion-style storage requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-063` | IF-STORAGE-001..010 | 11. Notion-style storage requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-025` | IF-STORAGE-001..010 | 11. Notion-style storage requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-026` | IF-STORAGE-001..010 | 11. Notion-style storage requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-064` | IF-STORAGE-001..010 | 12. Notion-style storage gap-closure requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-065` | IF-STORAGE-001..010 | 12. Notion-style storage gap-closure requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-066` | IF-STORAGE-001..010 | 12. Notion-style storage gap-closure requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-027` | IF-STORAGE-001..010 | 12. Notion-style storage gap-closure requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-028` | IF-STORAGE-001..010 | 12. Notion-style storage gap-closure requirements | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-067` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 13. Implementation executability requirements | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-068` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 13. Implementation executability requirements | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-NFR-029` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 13. Implementation executability requirements | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-069` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 14. Implementation requirements gap-register controls | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-070` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 14. Implementation requirements gap-register controls | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-071` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 14. Implementation requirements gap-register controls | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-072` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 14. Implementation requirements gap-register controls | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-073` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 15. Configuration requirements baseline | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-074` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 15. Configuration requirements baseline | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-075` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 15. Configuration requirements baseline | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-076` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 15. Configuration requirements baseline | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-077` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 15. Configuration requirements baseline | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-NFR-030` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 15. Configuration requirements baseline | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-NFR-031` | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | 15. Configuration requirements baseline | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-078` | IF-TRACE-001, IF-TDD-001 | 16. Traceability and TDD readiness baseline | STD-084..STD-085 |
| `EDUOPS-FR-079` | IF-TRACE-001, IF-TDD-001 | 16. Traceability and TDD readiness baseline | STD-084..STD-085 |
| `EDUOPS-NFR-032` | IF-TRACE-001, IF-TDD-001 | 16. Traceability and TDD readiness baseline | STD-084..STD-085 |
| `EDUOPS-NFR-033` | IF-TRACE-001, IF-TDD-001 | 16. Traceability and TDD readiness baseline | STD-084..STD-085 |


## 10. GitHub adapter interface anchors

| Interface anchor | Trace | Logical contract |
|---|---|---|
| IDD-GH-001 Clone adapter mode selection | EDUOPS-FR-080, EDUOPS-NFR-034 | `{adapter_mode, clone_readonly_enabled, approved_gate_ref?}` controls `fake-local`, `mock-http`, and future approved `clone-readonly` behavior only. |
| IDD-GH-002 Clone operation envelope | EDUOPS-FR-081 | GitHub clone operations use the internal `ResultEnvelope<T>` with idempotency, correlation, actor, source URL hash, expected ref/SHA, and `github_mutation_made=false`. |
| IDD-GH-003 Credential reference input | EDUOPS-FR-082 | Clone inputs contain `credential_ref_id`, provider, scope, and status only; raw token payload fields are forbidden. |
| IDD-GH-004 Clone evidence boundary | EDUOPS-FR-083 | Adapter output can include source ref/SHA and local clone manifest evidence, but submission/provisioning/workflow state promotion is performed by the application core. |
| IDD-GH-005 Non-clone operation denial | EDUOPS-FR-084 | Repository creation, push, collaborator/team mutation, branch protection, webhook/check-run writes, and GitHub administration requests are denied before an external request. |
| IDD-GH-006 Clone source privacy validation | EDUOPS-NFR-035 | Repository aliases, local target paths, and clone evidence labels are validated against pseudonymous ID policy before an external request. |
| IDD-GH-007 Clone error taxonomy | EDUOPS-NFR-036 | `GITHUB_AUTH_REQUIRED`, `GITHUB_SCOPE_DENIED`, `GITHUB_RATE_LIMITED`, `GITHUB_OUTAGE_OR_TIMEOUT`, `GITHUB_PRIVACY_POLICY_VIOLATION`, `GITHUB_NON_CLONE_OPERATION_BLOCKED`, and `GITHUB_LIVE_ACTION_BLOCKED` map to internal error classes. |
