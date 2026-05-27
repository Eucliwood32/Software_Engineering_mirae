---
title: Student Knowledge Policy
document_id: SWENG-EDUTECH-KNOWLEDGE-POLICY
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Student Knowledge Policy

## 1. Purpose

Define privacy, academic-integrity, reuse, retention, and visibility rules for student-owned `knowledge/**` artifacts.

## 2. Policy baseline

Student knowledge artifacts are student-owned learning records. They may become grading evidence only when assignment policy or student-approved submission scope includes them. They shall not become future course examples, peer-review material, or model answers without explicit instructor policy, student consent where required, and redaction.

## 3. Visibility levels

| Level | Meaning | Default |
|---|---|---|
| `student_private` | Visible only to the student and authorized recovery/admin process | Default for private notes |
| `submission_evidence` | Visible to instructor/TA for the submitted assignment | Used when included in submission scope |
| `course_review` | Visible for controlled course review/feedback | Requires course policy |
| `public_example_candidate` | Candidate for anonymized future teaching example | Requires explicit promotion/redaction decision |

## 4. Reuse and academic integrity

- Students may reuse their own knowledge as learning support unless an assignment explicitly restricts prior work reuse.
- Reuse shall be declared when it materially contributes to a submitted answer.
- Knowledge artifacts from other students or prior cohorts shall be treated as external sources requiring citation and permission.
- Promotion of student knowledge to example material requires redaction and decision evidence.

## 5. Retention and export

Course packages shall define retention periods for workspace, knowledge, submission, reports, audit, and export manifests. Students should have an approved personal export path for their own knowledge artifacts after course completion, subject to privacy and institutional policy.

## 6. Traceability

- Requirements: `EDUOPS-FR-043`, `EDUOPS-FR-058`
- Non-functional requirement: `EDUOPS-NFR-017`
- Decision: `EDUOPS-DEC-031`
- Risk: `EDUOPS-R-030`

## 8. Local storage privacy and lifecycle

Student-private knowledge drafts, local journals, autosaves, and search indexes shall remain scoped to the student's authorized device/session unless promoted into submission/export evidence. Withdrawal, archive, device handoff, or course deletion shall trigger cleanup or protected archival according to institutional retention policy. Instructor/global search shall not index `student_private` knowledge content.
