---
title: Instructor UI Workflow Specification
document_id: SWENG-EDUTECH-INS-UI
version: 0.1.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Instructor UI Workflow Specification

## 1. Purpose

The instructor/professor UI shall support course operation, assignment authoring, controlled publication, monitoring, review, feedback, and evidence export.

## 2. Primary navigation

```text
Instructor Home
  -> Courses / Sections
  -> Roster & Identity Binding
  -> Problem Bank
  -> Assignment Instances
  -> Student Progress Monitor
  -> Submission Review
  -> Evaluation Results
  -> Feedback Release
  -> Audit / Export / Archive
  -> Recovery / Override
```

## 3. Main flow

| Step | Instructor action | System response | Evidence/status |
|---|---|---|---|
| I-UI-001 | Create course/section | Course shell created | Course metadata |
| I-UI-002 | Import roster | Validate and import students | Roster import evidence |
| I-UI-003 | Approve identities | Bind GitHub identities | Binding audit |
| I-UI-004 | Create Problem Bank item | Draft assignment/rubric/profile | Problem version |
| I-UI-005 | Publish instance | Release assignment to section | Release SHA/ref |
| I-UI-006 | Monitor progress | Show workspace/submission/evaluation state | Dashboard state |
| I-UI-007 | Review submission | Render snapshot and evidence | Review record |
| I-UI-008 | Release feedback | Publish feedback to students | Release audit |
| I-UI-009 | Export/archive | Create controlled package | Export manifest |
| I-UI-010 | Override/recover | Repair state with approval | Override audit |

## 4. High-impact gates

Publication, feedback release, grade export, manual override, and archive closeout require visible context, confirmation, and audit evidence.

## 5. Rendering requirement

Instructor authoring and review views shall show the same canonical graph/table/image content that students see, plus additional renderer/evidence diagnostics where needed.

## Instructor report-template and knowledge-evidence flow

The instructor/professor UI shall allow authorized assignment authors to define required execution blocks, reflection prompts, report templates, and allowed export formats such as DOCX and HWP/HWPX. Review screens shall distinguish canonical evidence from derived report exports and shall display export warnings, hashes, and converter/tool profiles.

## Instructor editor-specific requirements

The instructor editor shall support assignment brief authoring, required execution-block templates, rubric-linked reflection prompts, report templates, export-format policy, publication preview, and blocked-action diagnostics. Instructor review may annotate or comment on student artifacts but must not silently edit student `workspace/**` or `knowledge/**` content outside an authorized override/recovery flow.

## 8. Gap-closure instructor UI implications

The instructor UI shall let authorized instructors define whether `knowledge/**` artifacts are required, optional, or excluded from submission evidence. It shall display export warnings, runner authority status, state-family labels, roster identity conflicts, and GitHub operation readiness before classroom rollout.
