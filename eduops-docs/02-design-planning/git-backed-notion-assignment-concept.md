---
title: Git-backed Notion-style Assignment Management Concept
document_id: SWENG-EDUTECH-CONCEPT-MODEL
version: 0.5.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Git-backed Notion-style Assignment Management Concept

## 1. Analysis conclusion

The user's earlier design reframes HISYS EduOps Platform from a C/C++-only programming-assignment tool into a broader **Git-backed, branch-based, document-oriented assignment management system**. The C/C++ evaluation baseline remains useful as one evaluation profile, but the core product model should be document-first: assignments and submissions are Notion-style/Markdown-first artifacts with Git as the version-control and reproducibility backend.

## 2. Final system definition

A Git-backed assignment management platform where reusable assignments are stored in a problem bank, instantiated for courses and semesters, distributed to students as read-only originals, edited in isolated student workspaces, synchronized automatically when assignments are updated, and officially submitted through dedicated submission branches with full version tracking and reproducibility.

## 3. Core principles

| Principle | Controlled interpretation |
|---|---|
| Document-first output | Assignment outputs are Markdown/Notion-style documents, optionally with assets, tables, images, references, and structured editor JSON. |
| Git backend | Git is the authoritative backend version-control engine for assignment versions, workspace commits, submission snapshots, and reproducibility evidence. |
| Protected originals | Students do not directly modify assignment originals. |
| Isolated workspaces | Students work in isolated workspace areas/repositories. |
| Branch-based submissions | Official submissions are commits in assignment instance submission branches. |
| Reusable assignments | Assignments are reusable through a Problem Bank / Assignment Bank structure. |
| Versioned evaluation | Evaluation is based on a submission snapshot plus assignment version. |

## 4. Core concept model

```text
Problem Bank
    ↓
Assignment Bank Item
    ↓
Assignment Version
    ↓
Assignment Instance
    ↓
Student Workspace
    ↓
Submission Branch
    ↓
Submission Snapshot
```

## 5. Entity semantics

| Entity | Meaning | Key evidence |
|---|---|---|
| Problem Bank | Repository/catalog of reusable assignments | Assignment bank item list, categories, tags, latest versions |
| Assignment Bank Item | Reusable assignment source unit | Title, description, category, tags, difficulty, author |
| Assignment Version | Immutable version of a bank item | Version ID, repo commit hash, change summary, rubric snapshot |
| Assignment Instance | Course/term/section-specific operational assignment | Bank item/version, course, term, section, open/due dates, status |
| Student Workspace | Student-specific editable environment | Repo URL, current assignment version, current commit, sync status |
| Submission Branch | Official branch namespace for a student submission | `submissions/{student_id}` branch, submission tag |
| Submission Snapshot | Frozen submitted content plus assignment snapshot | Submission metadata JSON, assignment snapshot, submitted workspace contents |

## 6. Repository structure baseline

### 6.1 Problem Bank Repository

```text
assignment-bank/
 └─ ai-ethics-case-analysis/
     ├─ main
     ├─ versions/
     ├─ instructions/
     ├─ template/
     ├─ rubric/
     └─ metadata.yaml
```

### 6.2 Assignment Instance Repository

```text
assignment-instance-repo/
 ├─ main
 ├─ releases/v1.0
 ├─ releases/v1.1
 ├─ submissions/student-20240001
 ├─ submissions/student-20240002
 └─ submissions/student-20240003
```

- `main`: instructor-controlled assignment original.
- `releases/*`: assignment release snapshots.
- `submissions/*`: official student submission branches.

### 6.3 Student Workspace Repository

```text
student-workspace/
 ├─ assignment/
 │   ├─ README.md
 │   ├─ hints.md
 │   ├─ rubric.md
 │   └─ assets/
 │
 ├─ workspace/
 │   ├─ submission.md
 │   ├─ notes.md
 │   └─ assets/
 │
 └─ metadata/
     ├─ assignment_version.json
     └─ sync_status.json
```

- `assignment/`: read-only assignment original copied/synchronized from assignment instance.
- `workspace/`: editable student area.
- `metadata/`: system-managed files.

## 7. Important baseline adjustment

The earlier C/C++ requirement set should be interpreted as a **first evaluation profile** rather than the only assignment-output model. The product core is document-first assignment management. C/C++ checks can attach to assignments as automatic validation/evaluation modules.

## 10. Knowledge topology integration update

The concept chain now includes a first-class student knowledge workspace:

```text
Problem Bank → Assignment Version → Assignment Instance → Student Workspace
  → workspace/** + knowledge/** + reports/**
  → Submission Branch → Submission Snapshot
```

`knowledge/**` is student-owned and editable, is never overwritten by assignment synchronization, and is included in submission snapshots only according to assignment policy or approved student-selected scope. `reports/**` remains derived output generated from canonical editor JSON/Markdown/assets and export profiles.

See [Knowledge topology and submission policy](knowledge-topology-submission-policy.md), [Student knowledge policy](knowledge-policy.md), and [Export fidelity acceptance criteria](export-fidelity-acceptance.md).
