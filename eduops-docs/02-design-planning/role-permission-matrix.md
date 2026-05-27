---
title: Role Permission Matrix
document_id: SWENG-EDUTECH-RBAC
version: 0.2.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Role Permission Matrix

## 1. Purpose

This matrix defines minimum role permissions. UI hiding is not sufficient; backend/application permission checks are required. The detailed authorization policy is controlled in [Access control and authorization model](access-control-authorization-model.md).

## 2. Permission matrix

| Capability | Student | Instructor | TA | Admin/operator | Evaluator | Sync worker |
|---|---|---|---|---|---|---|
| View assigned instructions | Allow own | Allow course | Allow assigned | Allow configured | Read snapshot | Read needed refs |
| Edit own workspace | Allow | Block except override | Block | Block except recovery | Block | Block |
| Submit own work | Allow own | Proxy only by override | Block | Recovery only | Block | Execute queued operation |
| Create Problem Bank item | Block | Allow | Draft-only if delegated | Policy | Block | Block |
| Publish assignment | Block | Allow | Block or draft-only | Delegated only | Block | Execute sync job |
| Import roster | Block | Allow | Block | Allow | Block | Block |
| Approve identity | Claim only | Allow | Block/delegated | Allow | Block | Block |
| View all submissions | Block | Allow course | Allow assigned | Allow authorized | Read for evaluation | Read for sync |
| Run evaluation | View result | Trigger/inspect | Inspect assigned | Configure runner | Allow | Block |
| Draft feedback | View released | Allow | Allow assigned | Block unless delegated | Block | Block |
| Release feedback | View released | Allow | Delegated only | Delegated only | Block | Block |
| Export grades/audit | Block | Allow | Limited if delegated | Allow | Block | Block |
| Manual override | Block | Allow with approval | Block | Allow with approval | Block | Block |

## 3. Enforcement notes

- Role claims must be evaluated with course/section/assignment/student scope.
- Privileged commands require audit event creation even when allowed.
- Offline mode cannot expand authority.
- TA/admin scopes are not equivalent to full instructor authority by default.
- Recovery actions require before/after state and reason.
- The application shall use default-deny scoped authorization for protected resources and actions.

## 7. Knowledge/export permission update

Students may edit authorized `workspace/**` and `knowledge/**`. Instructors define whether knowledge artifacts are required, optional, or excluded from submission evidence. The system owns `metadata/**`, export manifests, and official state transitions. No role may silently convert `queued` or `pushed` submission work into `confirmed` without authoritative evidence.
