---
title: Roster Schema and Identity Policy
document_id: SWENG-EDUTECH-ROSTER-SCHEMA
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Roster Schema and Identity Policy

## 1. Purpose

Close the roster/identity open question by defining controlled CSV/JSON import fields, validation, privacy, and GitHub identity binding rules.

## 2. Minimal roster fields

| Field | Required | Notes |
|---|---|---|
| `course_id` | Yes | Controlled course identifier |
| `section_id` | Yes | Section/lab identifier |
| `student_internal_id` | Yes | Institutional ID stored in protected registry, not public branch name |
| `student_display_name` | Yes | Unicode-normalized display name |
| `email` | Conditional | Required when invitation email workflow is used |
| `github_username_claimed` | No | Student-provided claim before approval |
| `status` | Yes | Imported/Invited/Bound/etc. |
| `privacy_flags` | No | Redaction/export constraints |

## 3. File encoding and validation

Roster imports shall require UTF-8, normalize Korean text to the selected Unicode profile, detect duplicate institutional IDs, detect duplicate GitHub usernames, and create an import evidence record with file hash and accepted/rejected row counts.

## 4. Identity binding gates

1. Import roster.
2. Invite or allow student GitHub identity claim.
3. Detect duplicates/conflicts.
4. Instructor/admin approval.
5. Workspace provisioning.
6. Audit record linking roster row, approved GitHub identity, and provisioning evidence.

## 5. Traceability

- Requirements: `EDUOPS-FR-002`, `EDUOPS-FR-003`, `EDUOPS-FR-004`, `EDUOPS-FR-060`
- Decision: `EDUOPS-DEC-033`
- Risks: `EDUOPS-R-012`, `EDUOPS-R-036`
