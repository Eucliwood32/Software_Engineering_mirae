---
title: HISYS EduOps Platform Development Constraints
document_id: SWENG-EDUTECH-CON
version: 0.3.1
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Development Constraints

## 1. Baseline constraints

| ID | Constraint | Rationale | Verification |
|---|---|---|---|
| EDUOPS-CON-001 | The product shall be designed as a Windows and Linux desktop application; web and mobile application delivery are excluded from the current baseline. | User explicitly updated the desktop-only composition from Windows-only to Windows plus Linux. | Architecture and packaging review confirms Windows/Linux desktop scope and no web/mobile client scope. |
| EDUOPS-CON-002 | Git shall remain the authoritative version-control substrate for assignment origins, student snapshots, and submission evidence. | Git-backed workflow is the product differentiator. | Traceability from submission requirements to repository design and tests. |
| EDUOPS-CON-003 | Student writable paths shall be separated from read-only assignment-origin paths. | Prevents accidental or malicious source assignment modification. | Filesystem permission and app-level edit-blocking tests. |
| EDUOPS-CON-004 | Automated C/C++ evaluation shall execute in a constrained workspace/sandbox profile. | Protects privacy and host integrity when running untrusted student code. | Sandbox escape, timeout, memory, process, and path-access negative tests. |
| EDUOPS-CON-005 | The UI shall provide normal flows without requiring Git CLI knowledge. | EdTech adoption requires non-Git-expert usability. | Scenario testing with save/update/submit actions. |
| EDUOPS-CON-006 | Repository operations shall create machine-readable evidence records. | Supports auditability, dispute resolution, and ISO 9001 documented information controls. | Evidence schema validation and sample audit export. |
| EDUOPS-CON-007 | GitHub shall be the first supported repository backend; self-hosted Git shall be treated as a later extension profile behind a stable backend boundary. | Keeps first product focused while preserving future institutional deployment needs. | GitHub fixture tests pass; backend abstraction test uses a simulator/local self-hosted-Git profile only after GitHub semantics are stable. |
| EDUOPS-CON-008 | LMS connectors, LTI, LMS grade passback, and LMS credential dependencies shall be excluded from the current baseline. | User explicitly excluded LMS. | Configuration and architecture review show no LMS connector or required LMS credential. |
| EDUOPS-CON-009 | C/C++ shall be the first supported automated-evaluation language family. | User selected C/C++ code as the initial assignment domain. | C/C++ compile/run/unit-test/static-analysis fixtures pass before adding other languages. |
| EDUOPS-CON-010 | Raw GitHub tokens and credentials shall not be written into assignment repositories, logs, or export artifacts. | Protects institutional and student accounts. | Secret-redaction and leak-check tests. |
| EDUOPS-CON-011 | Student management records shall minimize personal data while preserving roster identity, GitHub identity binding, submission eligibility, feedback release, and audit traceability. | Student management is necessary, but privacy exposure must be bounded. | Student registry schema review, redaction tests, and audit-export checks. |
| EDUOPS-CON-012 | Mode permissions shall be enforced in backend logic and reflected in the Windows desktop UI. | Mode separation prevents accidental high-impact actions. | Permission matrix tests and UI context review. |
| EDUOPS-CON-013 | Manual override shall require actor, reason, scope, approval/authority, timestamp, and before/after state evidence. | Recovery must not corrupt auditability. | Override fixture and audit-log validation. |

## 2. Claude review gap-closure constraints

| ID | Constraint | Rationale |
|---|---|---|
| EDUOPS-CON-022 | `knowledge/**` shall never be silently overwritten by assignment synchronization. | Student-owned learning records require the same or stronger protection as `workspace/**`. |
| EDUOPS-CON-014 | Canonical evidence shall not depend on proprietary DOCX/HWP/HWPX output files. | Exports are derived artifacts; Git/editor JSON/Markdown/metadata remain authoritative. |
| EDUOPS-CON-015 | Legacy HWP output shall require an approved converter/tool profile and warning behavior. | HWP is proprietary/fragile compared with HWPX and must not silently lose evidence. |
| EDUOPS-CON-016 | Official C/C++ evaluation evidence shall require an approved runner/sandbox profile. | Student local pre-checks are useful but not authoritative grading evidence. |
| EDUOPS-CON-017 | GitHub automation shall use least-privilege short-lived or scoped credentials and shall not store raw tokens. | Prevents credential leakage in logs, repositories, exports, or student workspaces. |
| EDUOPS-CON-018 | Roster imports shall use controlled schema, encoding, duplicate detection, and privacy minimization. | Student-management efficiency depends on safe identity binding. |

## 3. Notion-style storage constraints

| ID | Constraint | Rationale |
|---|---|---|
| EDUOPS-CON-019 | Editor UI vendor state shall not be the only persisted source of truth. | Prevents lock-in and preserves evidence portability. |
| EDUOPS-CON-020 | Local indexes/search/render caches shall be rebuildable from canonical JSON/Markdown/assets. | Prevents cache corruption from becoming evidence corruption. |
| EDUOPS-CON-021 | Submission/export shall use a materialized canonical revision, not unsaved in-memory editor state. | Prevents stale or untraceable output. |
| EDUOPS-CON-023 | Operation journals, autosave files, and rebuildable indexes shall not be treated as authoritative evidence unless materialized into a canonical revision/checkpoint. | Prevents local recovery data from replacing controlled evidence. |
| EDUOPS-CON-024 | Local journals, autosave data, search indexes, and private knowledge caches shall use platform-appropriate at-rest protection and lifecycle cleanup rules. | Reduces privacy exposure from student-private drafts and withdrawn/archived workspaces. |
| EDUOPS-CON-025 | Editor toolkit selection shall prove storage architecture conformance before implementation lock-in. | Prevents vendor state from controlling canonical evidence. |


## 4. Identifier ordering note

Constraint IDs are historical controlled identifiers. Later gap-closure rows may appear out of numeric order to preserve existing traceability. New cleanup work should preserve existing IDs unless a separate migration table is approved.
