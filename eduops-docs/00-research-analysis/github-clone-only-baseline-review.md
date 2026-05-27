---
title: GitHub Clone-Only Baseline Review
document_id: SWENG-EDUTECH-GITHUB-CLONE-ONLY-REVIEW
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  requirements: ['EDUOPS-FR-080', 'EDUOPS-FR-081', 'EDUOPS-FR-083', 'EDUOPS-FR-084', 'EDUOPS-NFR-034', 'EDUOPS-NFR-036']
  related: ['SWENG-EDUTECH-GITHUB-ADAPTER-SPEC', 'SWENG-EDUTECH-GITHUB-ADAPTER-SDD']
---

# GitHub Clone-Only Baseline Review

## 1. Objective

Record the clarified baseline that EduOps shall use GitHub only as a read-only clone source in the current product baseline. EduOps shall not create repositories, push branches, invite collaborators, mutate branch protection, write webhooks/check-runs, or administer GitHub organizations.

## 2. Interpretation

The previous GitHub adapter baseline was broader than needed because it covered future provisioning, branch policy, submission-ref recording, and sandbox/live mutation paths. The clarified baseline narrows the GitHub boundary to clone-only access:

- allowed after gate: validate clone configuration, plan clone targets, perform read-only clone/fetch of approved repositories, record clone evidence;
- allowed before gate: fake-local and mock-http clone fixtures;
- forbidden: any GitHub mutation or administration action.

## 3. Review against objective

| Objective | Result |
|---|---|
| Make the clone-only boundary explicit. | Met by SRS §19, GitHub adapter specification, GitHub adapter SDD, IDD, STD, risk, decision, README, and INDEX updates. |
| Avoid accidental implementation of provisioning/mutation modules. | Met by replacing mutation-capable operations with clone-only operations and adding explicit forbidden-operation language. |
| Preserve no-secret/no-live-action gates. | Met. Raw credentials remain excluded, and clone-readonly mode still requires gate approval and evidence. |
| Preserve future extension control. | Met. Any GitHub mutation would require a future controlled baseline change, not a code-only extension. |

## 4. Remaining implementation boundary

The next implementation loop may still begin only from fake/local and mock clone fixtures. A real GitHub clone is not approved until clone-readonly gate evidence, credential-reference policy, and no-mutation assertions are accepted.
