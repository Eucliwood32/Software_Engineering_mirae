---
title: Student UI Workflow Specification
document_id: SWENG-EDUTECH-STU-UI
version: 0.1.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Student UI Workflow Specification

## 1. Purpose

The student UI shall minimize operational complexity and support assignment completion without Git command-line knowledge.

## 2. Primary navigation

```text
Student Home
  -> My Courses
  -> Active Assignments
  -> Assignment Viewer
  -> Workspace Editor
  -> Validation Panel
  -> Submit
  -> Feedback
  -> Local History / Sync Status
```

## 3. Main flow

| Step | Student action | System response | Evidence/status |
|---|---|---|---|
| S-UI-001 | Open assigned course | Show active assignments and due state | Course/student context |
| S-UI-002 | Open assignment | Render read-only instructions/rubric/assets | Renderer profile, assignment version |
| S-UI-003 | Edit workspace | Save/autosave to `workspace/**` | Local checkpoint commit |
| S-UI-004 | Run validation | Show actionable errors/warnings | Validation result |
| S-UI-005 | Receive update | Show changed assignment files/reason | Update notice |
| S-UI-006 | Sync assignment | Update only `assignment/**` | Sync log |
| S-UI-007 | Submit | Confirm, snapshot, push/queue | Submission metadata |
| S-UI-008 | View feedback | Show released feedback/evaluation logs | Feedback release record |

## 4. Student blocked controls

The student UI shall not expose Problem Bank authoring, publication, roster management, other-student submissions, grading release, audit export, token administration, or manual override controls.

## 5. Rendering requirement

Student assignment and workspace views shall render graph/table/image blocks consistently with instructor review/export evidence. Rendering failures must be visible and actionable.

## Student knowledge workspace and report export flow

The student UI shall provide a lightweight knowledge workspace for assignment execution:

1. open assignment brief and required execution/report blocks;
2. create planning notes, implementation decisions, experiment logs, references, and reflection notes;
3. link notes to code/test evidence and assignment sections;
4. preview required report completeness;
5. export controlled DOCX and HWP/HWPX report outputs when allowed by assignment policy;
6. include export manifest and warnings in the submission evidence view.

The UI must keep this flow simple and must not expose instructor-only template, roster, grading, or export-policy controls.

## Student editor-specific requirements

The student editor shall support block insertion, required-block status, autosave/checkpoint, undo/redo, local history, validation panel, export preview, and recovery without requiring Git commands. It shall make the editable boundary visible: `assignment/**` is read-only, while authorized `workspace/**` and `knowledge/**` content is editable. Korean IME, C/C++ code blocks, tables, images, graph/diagram blocks, citations, experiment logs, decisions, and reflections are required fixtures.

## 8. Gap-closure student UI implications

The student UI shall show clear boundaries for `assignment/**` read-only content, `workspace/**` editable work, `knowledge/**` student-owned knowledge, and `reports/**` derived outputs. It shall display whether a submission is `queued`, `pushed`, or `confirmed`; it shall not imply GitHub confirmation before authoritative evidence exists. Export preview shall show DOCX/HWPX/HWP warnings and canonical evidence links.
