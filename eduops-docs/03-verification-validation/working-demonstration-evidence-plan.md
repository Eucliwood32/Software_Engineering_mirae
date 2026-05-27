---
title: Working Demonstration and Evidence Plan
document_id: SWENG-EDUTECH-WORKING-DEMO-EVIDENCE-PLAN
version: 0.1.0
status: draft
created: 2026-05-14
updated: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  iso9001: ['7.5', '8.3', '8.5', '8.6', '9.1']
  related: ['SWENG-EDUTECH-SRS', 'SWENG-EDUTECH-STD', 'SWENG-EDUTECH-IMPL-EXEC-PLAN', 'SWENG-EDUTECH-IMPL-REQ-GAP']
---

# Working Demonstration and Evidence Plan

## 1. Purpose

This plan defines how EduOps shall show that the system works before productization. The demonstration is not a marketing mockup. It is a controlled, fixture-based vertical-slice demonstration that produces evidence a reviewer can inspect: commands, screenshots or screen recordings, JSON/Markdown/manifests, Git commits/refs, logs, and validation results.

## 2. Demonstration principle

EduOps shall demonstrate operation in three layers:

1. **User-visible flow**: what the instructor, student, TA, or admin sees.
2. **Backend/application evidence**: command result, state transition, authorization decision, audit event, and error code.
3. **Repository/evidence artifacts**: canonical editor JSON, deterministic Markdown projection, manifest, Git commit/ref/tag, evaluation result JSON, export file, and hash.

A feature is not considered demonstrated if it only shows a screen. A feature is demonstrated when the user-visible outcome and the controlled evidence agree.

## 3. Demo levels

| Level | Name | Goal | Live external action allowed? | Required evidence |
|---|---|---|---|---|
| DEMO-0 | Clickable storyboard | Explain user flow with static UI or prototype screens. | No | Scenario script, screenshots, reviewer notes. |
| DEMO-1 | Local fixture vertical slice | Prove one workflow end-to-end using fake/local adapters. | No | Local command log, fixture data, Git local repo evidence, manifests, validation result. |
| DEMO-2 | Local integrated pilot | Prove multiple roles and multiple students with fake GitHub/evaluation/export fixtures. | No | Multi-user scenario evidence, audit/event records, error cases. |
| DEMO-3 | Sandbox connector demonstration | Prove GitHub sandbox or approved runner integration after fixture gates pass. | Only approved sandbox | Gate approval, sandbox identifiers, no-production-data evidence, rollback record. |

The first credible demonstration should be `DEMO-1`, not a pure UI mockup.

## 4. Minimum DEMO-1 script

The minimum working demonstration should show one instructor, one assignment, one student, one workspace, one checkpoint, one submission snapshot, one advisory C++ evaluation, and one derived export using local/fake adapters.

```text
1. Instructor creates or imports one course fixture.
2. Instructor imports a privacy-safe roster fixture.
3. Instructor creates one assignment from a Problem Bank fixture.
4. System provisions one student workspace.
5. Student opens assignment and edits `workspace/documents/main.eduops.json` through the editor path.
6. System saves canonical editor JSON, deterministic Markdown projection, and manifest.
7. Student creates a local checkpoint commit.
8. Student queues and confirms a local fake submission snapshot.
9. System runs one advisory C++ evaluation fixture and emits result JSON/log hash.
10. Instructor/TA review page displays submission evidence and evaluation result.
11. System generates DOCX/HWPX-derived export fixture with export manifest and warning/loss report.
12. Validation command verifies state transitions, hashes, links, manifests, and no live external actions.
```

## 5. Demonstration slices

| Demo slice | What to show | Evidence to capture | Gate |
|---|---|---|---|
| DEMO-SLICE-A | Empty app skeleton can create a local course and save/load one empty document. | IPC ping, domain IDL validation, local DB/index file, local Git commit. | No live action; fixture IDs only. |
| DEMO-SLICE-B | Notion-style editor path saves blocks and creates deterministic Markdown projection. | `.eduops.json`, `.md`, `.manifest.json`, stable block IDs, hash comparison. | JSON is source of truth; Markdown is derived. |
| DEMO-SLICE-C | Roster import and student workspace provisioning. | Privacy-safe roster fixture, identity binding audit event, workspace folder tree. | No real student PII. |
| DEMO-SLICE-D | Assignment release, sync, checkpoint, and submission state. | state transition table row, Git commit/ref, queued/pushed/confirmed local evidence. | Offline queued never equals confirmed remote. |
| DEMO-SLICE-E | C/C++ advisory runner. | runner manifest, result JSON, stdout/stderr log hash, sandbox/advisory flag. | Official grading disabled unless approved runner gate exists. |
| DEMO-SLICE-F | Review/feedback evidence. | authorization decision, feedback release audit, student-visible feedback view. | UI hiding is not authorization. |
| DEMO-SLICE-G | DOCX/HWPX export. | export job record, produced artifact, manifest, warning/loss report, hash. | Export is derived evidence, not canonical source. |

## 6. Demo evidence package layout

Each demonstration run shall produce or link an evidence package under the shared local evidence convention:

```text
build/evidence/<slice>/<run-id>/
├── demo-script.md
├── run-summary.json
├── screenshots/
├── screen-recording/
├── commands.log
├── validation.log
├── artifacts/
│   ├── course-fixture.json
│   ├── roster-fixture.csv
│   ├── workspace-tree.txt
│   ├── main.eduops.json
│   ├── main.md
│   ├── main.manifest.json
│   ├── submission_snapshot.json
│   ├── evaluation_result.json
│   ├── export.docx
│   ├── export.hwpx
│   └── export.manifest.json
└── git/
    ├── git-log.txt
    ├── refs.txt
    └── diff-stat.txt
```

Slice names shall be stable identifiers such as `slice-a`, `ui-shell-slice-a`, `slice-b`, or `demo-1`. Older references to `build/demo-runs/<run-id>/` are superseded by `build/evidence/demo-1/<run-id>/`.

Demo evidence packages should be generated from privacy-safe fixtures. Heavy binary artifacts and recordings may stay local unless explicitly selected for controlled retention.

## 7. Acceptance criteria for saying "it works"

EduOps may be described as working for a slice only when all of the following are true:

1. The user-visible flow completes without manual database or Git repair.
2. The application/backend emits an expected command result and state transition.
3. Authorization decision evidence exists for protected actions.
4. Canonical editor JSON, Markdown projection, and manifest agree.
5. Git evidence exists for checkpoint/submission steps where applicable.
6. Evaluation/export outputs include manifests and hashes where applicable.
7. Validation commands pass.
8. The run summary states whether any live external action occurred; DEMO-1 and DEMO-2 must report `live_external_action=false`.
9. Known limitations are recorded as warnings, not hidden.

## 8. What not to claim

Do not claim product readiness from:

- a static Figma/HTML mockup alone;
- a screen recording without inspectable artifacts;
- a Git commit without UI/backend state evidence;
- a successful export without canonical source and loss/warning manifest;
- a local advisory C++ run as official grading evidence;
- a sandbox GitHub run as production integration evidence.

## 9. Next controlled outputs

The next controlled outputs should be:

1. `demonstration-usage-scenarios.md` defining the exact M1A and DEMO-1 presenter-facing scenario scripts.
2. `demo-fixture-corpus-and-script.md` describing the exact DEMO-1 fixtures and scenario script.
3. `demo-run-evidence-schema.md` defining `run-summary.json` and artifact manifest schema.
4. A local `scripts/run_demo_slice_a.py` or equivalent harness after P0 implementation contracts are accepted.
