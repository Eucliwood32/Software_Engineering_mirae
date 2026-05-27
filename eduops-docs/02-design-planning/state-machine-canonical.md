---
title: Canonical State Machine Profile
document_id: SWENG-EDUTECH-STATE-MACHINE
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Canonical State Machine Profile

## 1. Purpose

Separate student lifecycle, submission state, and assignment release/update state so UI dashboards, APIs, audit records, and V&V fixtures use consistent vocabulary.

## 2. Student lifecycle state

```text
Imported → Invited → Bound → Provisioned → Active → Locked/Withdrawn → Archived
```

Submission and evaluation do not permanently replace lifecycle state. A student can be `Active` while having multiple assignment-specific submissions in different states.

## 3. Submission state

```text
draft → checkpointed → queued → pushed → confirmed → evaluated → review_pending → feedback_released → reopened → archived
```

Important invariant: `queued` and `pushed` are not `confirmed`. A submission becomes confirmed only after authoritative Git/evidence acknowledgement exists.

## 4. Assignment release/update state

```text
draft → reviewed → published → update_pending → update_published → student_ack_required → acknowledged → superseded/retired
```

Assignment release updates may change `assignment/**` and `rubric/**`; they shall never silently overwrite `workspace/**` or `knowledge/**`.

## 5. Cross-state examples

| Scenario | Student lifecycle | Submission | Assignment release |
|---|---|---|---|
| Student working offline | Active | checkpointed or queued | published |
| Network push completed but GitHub confirmation missing | Active | pushed | published |
| Assignment update requires student review | Active | draft/checkpointed | student_ack_required |
| Feedback returned | Active | feedback_released | published or superseded |
| Course closed | Archived | archived | retired |

## 6. Traceability

- Requirements: `EDUOPS-FR-005`, `EDUOPS-FR-013`, `EDUOPS-FR-014`, `EDUOPS-FR-057`
- Decision: `EDUOPS-DEC-030`
- Risks: `EDUOPS-R-013`, `EDUOPS-R-034`
