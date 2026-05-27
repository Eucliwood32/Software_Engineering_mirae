---
title: Repository Permission and Assignment Workflow
document_id: SWENG-EDUTECH-REPO-WORKFLOW
version: 0.5.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Repository Permission and Assignment Workflow

## 1. Permission model

| Actor | Read/write scope | Blocked scope | Notes |
|---|---|---|---|
| Instructor | `assignment/**`, `rubric/**`, `metadata/**`, `settings/**` | Submitted student snapshots except through controlled review/override | Creates and updates official assignment originals. |
| Student | Read-only: `assignment/**`, `rubric/**`, `metadata/**`; editable: `workspace/**`, authorized `knowledge/**` | `assignment/**`, `rubric/**`, `metadata/**` writes; other students' work; unauthorized knowledge promotion | Student work and knowledge are isolated; `workspace/**` and policy-authorized `knowledge/**` are editable. |
| System | Assignment synchronization, metadata updates, submission management, export manifest generation | Any silent overwrite of `workspace/**` or `knowledge/**`; raw credential exposure | System writes must be auditable and bounded. |

## 2. Assignment workflow

### Step 1. Instructor creates assignment

Instructor creates:

- instructions;
- template;
- rubric;
- metadata.

Stored in:

```text
assignment-instance-repo/main
```

### Step 2. Student starts assignment

System creates student workspace:

```text
student-workspace/
 ├─ assignment/   ← copied from assignment instance
 └─ workspace/    ← empty editable area
```

Student only edits `workspace/`.

### Step 3. Student works on assignment

Student edits:

```text
workspace/submission.md
```

Autosave:

```bash
git commit -m "autosave"
```

Manual save:

```bash
git commit -m "save"
```

The product UI may hide these Git commands, but the Git commits remain the authoritative evidence.

### Step 4. Instructor updates assignment

Instructor modifies:

```text
assignment-instance-repo/main
```

Examples:

- add hints;
- update instructions;
- clarify rubric;
- add references.

New version created:

```text
v1.1
v1.2
...
```

### Step 5. Workspace synchronization

System updates only `assignment/` area.

Synchronization example:

```bash
git fetch upstream
git checkout upstream/main -- assignment/
git commit -m "sync assignment update v1.1"
```

Important: `workspace/` is never overwritten.

### Step 6. Student submission

Student clicks **Submit**.

System performs:

1. Validate workspace.
2. Checkout submission branch: `submissions/{student_id}`.
3. Copy workspace contents.
4. Commit submission.
5. Create submission tag.
6. Store metadata.

Example:

```bash
git checkout submissions/20240001
git add .
git commit -m "submit assignment"
git tag submit/20240001/v1
```

## 3. Submission branch structure

```text
submissions/student-20240001/
 ├─ assignment_snapshot/
 │   ├─ README.md
 │   ├─ hints.md
 │   └─ rubric.md
 │
 ├─ submission/
 │   ├─ submission.md
 │   └─ assets/
 │
 └─ submission_metadata.json
```

## 4. Submission metadata

```json
{
  "student_id": "20240001",
  "assignment_instance_id": "assignment-01",
  "assignment_version": "v1.2",
  "submitted_at": "2026-04-26T11:30:00+09:00",
  "workspace_commit_hash": "abc123",
  "submission_commit_hash": "def456"
}
```

## 5. Assignment update model

```text
Instructor updates assignment
    ↓
New assignment version generated
    ↓
System synchronizes student workspaces
    ↓
Students receive notifications
```

Assignment updates are applied only to:

```text
assignment/**
```

Student work remains unchanged:

```text
workspace/**
```

## 6. Student update notification

Example UI:

```text
[Assignment Updated]

Changes:
- Hint added
- Rubric clarified
- Example table added

[View Changes]
[Sync Update]
```

## 7. Conflict prevention

Students cannot modify:

```text
assignment/**
```

Only editable:

```text
workspace/**
```

Server-side validation:

- reject commits modifying `assignment/**`;
- reject metadata tampering;
- reject submission branches lacking `assignment_snapshot/`, `submission/`, or `submission_metadata.json`;
- reject submission metadata that does not match the submitted commit and assignment version.

## 9. Knowledge and report workflow update

Submission branches shall distinguish canonical evidence from derived reports:

```text
submissions/<pseudonymous-student-ref>/
├─ assignment_snapshot/
├─ submission/
│  ├─ workspace/
│  ├─ knowledge/              # only approved required or selected knowledge evidence
│  └─ reports/                # derived outputs with manifests
└─ submission_metadata.json
```

Assignment updates may change `assignment/**` and `rubric/**`, but shall not silently overwrite `workspace/**` or `knowledge/**`. Any update that invalidates a referenced assignment asset, rubric, or required block shall create a conflict/review task and acknowledgement requirement.

See [Knowledge topology and submission policy](knowledge-topology-submission-policy.md) and [Canonical state machine profile](state-machine-canonical.md).
