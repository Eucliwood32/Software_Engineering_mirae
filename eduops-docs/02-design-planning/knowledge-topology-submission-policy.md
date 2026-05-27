---
title: Knowledge Topology and Submission Policy
document_id: SWENG-EDUTECH-KNOWLEDGE-TOPOLOGY
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Knowledge Topology and Submission Policy

## 1. Purpose

This document closes the controlled gap identified after the Claude review: `knowledge/**` is not only a student convenience folder. It is a governed student-owned knowledge workspace that must be integrated into repository topology, permissions, synchronization, submission evidence, export, privacy, and academic-integrity controls.

## 2. Controlled baseline decision

`knowledge/**` shall be a first-class student-owned workspace area, parallel to `workspace/**` and distinct from read-only `assignment/**`.

```text
student-workspace/
├─ assignment/                 # read-only assignment original synced from release
├─ rubric/                     # read-only rubric and grading guide
├─ workspace/                  # student-editable assignment work products
├─ knowledge/                  # student-owned notes, decisions, experiments, references
│  ├─ index.md
│  ├─ notes/
│  ├─ decisions/
│  ├─ experiments/
│  └─ references/
├─ reports/                    # generated derived report outputs
└─ metadata/                   # system-managed state, manifests, locks, sync metadata
```

## 3. Permission and synchronization rules

| Area | Student | Instructor/TA | System | Sync rule |
|---|---|---|---|---|
| `assignment/**` | Read-only | Author/update through assignment release | Sync from release | May be updated by official assignment sync |
| `rubric/**` | Read-only after publication | Author/update through controlled release | Sync from release | May be updated with visible change notice |
| `workspace/**` | Editable | Review/comment only unless authorized override | Checkpoint, submit, validate | Never silently overwritten by assignment sync |
| `knowledge/**` | Editable and exportable | Visible only according to assignment/course policy | Index, validate, submit/export selected scope | Never silently overwritten by assignment sync |
| `reports/**` | Generated/readable; not canonical | Review as derived output | Generate and hash | Re-generated from canonical source; not source of truth |
| `metadata/**` | Read-only | Review/admin through controlled tools | Owns authoritative state | System-managed only |

## 4. Submission inclusion policy

A submission snapshot shall include:

1. `assignment_snapshot/**` copied from the accepted assignment version;
2. `submission/workspace/**` for the official student work product;
3. `submission/knowledge/**` when the assignment policy marks knowledge evidence as required or student selects approved knowledge artifacts for submission;
4. `submission/reports/**` only as derived outputs with export manifests;
5. `submission_metadata.json` with workspace commit SHA, knowledge commit/index SHA, export manifest IDs, assignment version, student pseudonymous identifier, and warning records.

`knowledge/**` is not automatically public to future students. Its inclusion in grading, peer review, reuse, or course-level examples requires an explicit policy and redaction decision.

## 5. Metadata requirements

`submission_metadata.json` shall include at minimum:

| Field | Purpose |
|---|---|
| `student_id_ref` | Pseudonymous or internal reference; avoid exposing raw student number in branch names where possible |
| `assignment_instance_id` | Course assignment context |
| `assignment_version_id` | Immutable assignment release identifier |
| `workspace_commit_sha` | Canonical workspace evidence |
| `knowledge_index_sha` | Hash/SHA of submitted knowledge index and selected knowledge artifacts |
| `knowledge_scope` | `none`, `required`, `student_selected`, or `instructor_required` |
| `export_manifest_ids` | Derived output traceability |
| `privacy_redaction_profile` | Redaction profile used before export/review sharing |
| `sync_conflict_records` | Assignment update conflicts affecting workspace/knowledge |

## 6. V&V requirements

Verification shall include fixtures for:

- assignment update that modifies `assignment/**` but does not overwrite `workspace/**` or `knowledge/**`;
- submission with no knowledge evidence, required knowledge evidence, and student-selected knowledge evidence;
- export manifest linked to `knowledge/index.md` and selected notes;
- instructor review where derived DOCX/HWPX report is present but canonical evidence remains Git/Markdown/editor JSON;
- privacy redaction preventing accidental exposure of unrelated personal notes.

## 7. Traceability

- Requirements: `EDUOPS-FR-043`, `EDUOPS-FR-046`, `EDUOPS-FR-052`
- Non-functional requirements: `EDUOPS-NFR-017`, `EDUOPS-NFR-020`
- Decisions: `EDUOPS-DEC-026`
- Risks: `EDUOPS-R-029`, `EDUOPS-R-030`

## 8. Knowledge index authority

`knowledge/index.eduops.json` may be either an authored student index note or a generated backlink/search index, but the mode must be explicit in its manifest. Authored indexes are canonical student work. Generated indexes are rebuildable projections and must not be submitted as independent evidence unless their source notes and manifest are included.
