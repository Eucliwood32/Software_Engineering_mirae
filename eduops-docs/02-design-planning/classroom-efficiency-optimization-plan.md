---
title: HISYS EduOps Classroom Efficiency Optimization Plan
document_id: SWENG-EDUTECH-CLASSROOM-OPT
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Classroom Efficiency Optimization Plan

## 1. Optimization conclusion

EduOps should not copy GitHub Classroom or Google Classroom one-to-one. The optimized product direction is a **programming-course operations cockpit**: Google-Classroom-like course/student management efficiency, GitHub-Classroom-like repository evidence, and EduOps-specific Windows desktop/local-first safety.

## 2. Target workflow architecture

```text
Course Shell
-> Roster Import
-> Identity Binding Queue
-> Workspace Provisioning
-> Assignment Publication
-> Student Checkpointing
-> Submission Branch Confirmation
-> C/C++ Evaluation
-> TA/Instructor Review
-> Feedback Release
-> Grade/Evidence Export
-> Archive
```

Each stage must support:

- bulk action;
- exception queue;
- role-scoped permission check;
- audit/evidence record;
- visible progress state;
- rollback or manual override when safe.

## 3. Product capabilities to add or strengthen

| Capability | Benchmark source | EduOps design action | Trace seed |
|---|---|---|---|
| Course/student overview | Google Classroom | Create dashboard widgets for roster completeness, identity binding, provisioning, submissions, evaluation, feedback release, and export status. | EDUOPS-FR-036 |
| Repository/evidence overview | GitHub Classroom | Show repository/branch/SHA/autograding/evaluation state without requiring Git CLI use. | EDUOPS-FR-037 |
| Bulk roster operations | Google Classroom | Batch import/invite/bind/provision with per-row validation and exception queue. | EDUOPS-FR-038 |
| Assignment publication pipeline | Both | Provide publish preview, repository operation preview, affected-student count, validation gates, and rollback packet. | EDUOPS-FR-039 |
| Update diff and acknowledgement | GitHub Classroom plus classroom UX gap | Require assignment update diff, affected workspace notice, acknowledgement status, and no-overwrite proof. | EDUOPS-FR-040 |
| Unified feedback release | Both | Combine code-review/evaluation feedback with rubric/grade release and export evidence. | EDUOPS-FR-041 |
| Benchmark evidence pack | EduOps | Generate fixture metrics for setup, onboarding, publication, update, submission, evaluation, feedback, export, and dispute reconstruction. | EDUOPS-NFR-015 |

## 4. UI optimization pattern

The instructor dashboard should prioritize operational bottlenecks:

1. **Needs action**: identity collisions, failed provisioning, late/locked exceptions, failed sync, failed evaluation, unreleased feedback.
2. **Class progress**: active students, queued/pushed/confirmed submissions, evaluated, reviewed, feedback released.
3. **Evidence health**: missing Git SHA, missing roster hash, missing evaluation profile, missing feedback release record.
4. **Batch controls**: invite selected, provision ready, publish assignment, run evaluation, release feedback, export grade/evidence.
5. **Audit drilldown**: every count opens the related records and evidence.

The student dashboard should minimize Git concepts:

1. assignment status and due information;
2. workspace save/checkpoint status;
3. update notice and required acknowledgement;
4. validation/evaluation feedback;
5. submission state: queued -> pushed -> confirmed;
6. released feedback and resubmission/reopen status.

## 5. Verification fixtures

| Fixture | Purpose | Pass criterion |
|---|---|---|
| 30-student onboarding | Measure roster import, identity binding queue, provisioning, and exception handling | All valid students provisioned; invalid rows isolated with clear reasons |
| 60-student assignment publish | Measure bulk publication and repository/evidence preview | Publish plan shows affected students, repositories/branches, and rollback packet |
| Assignment correction | Verify no-overwrite synchronization | `workspace/**` unchanged; update diff and acknowledgement records exist |
| Offline submission | Verify state clarity | Queued work is never shown as confirmed until remote Git evidence exists |
| Batch evaluation | Verify UI responsiveness and evidence completeness | Evaluation runs asynchronously; every result links snapshot SHA and toolchain profile |
| Feedback release/export | Verify grade/feedback controls | Draft feedback remains hidden until release; export includes evidence references |
| Dispute packet | Verify audit reconstruction | Assignment version, student snapshot, evaluation profile, rubric, feedback, and override history reconstruct within target time |

## 6. Implementation gate

This optimization plan should be implemented first as local fixtures and UI/data mockups. No live Google Classroom integration, LMS connector, or live GitHub side effect is authorized until the local benchmark fixture gates pass and the user explicitly promotes a live integration.
