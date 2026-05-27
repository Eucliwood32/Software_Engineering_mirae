---
title: Software Design Description
document_id: SWENG-EDUTECH-SDD
version: 0.6.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Software Design Description

## 1. Purpose

This document turns the EduOps requirements baseline into a coherent software design baseline for implementation-readiness. It is not source code design yet; it defines the product architecture, component boundaries, data/evidence flow, and traceability needed before coding begins.

## 2. Accepted product baseline

EduOps is a desktop-first, Git-backed, document-first assignment management platform with role-separated student/instructor UI, controlled graph/table/image rendering, GitHub-first repository backend, C/C++ as an initial evaluation profile, no LMS dependency, and submission evidence recorded through Git commits, refs/tags, metadata, and audit records.

## 3. Architecture overview

```text
Role-separated UI shells
  -> Application service layer
    -> Course and roster service
    -> Problem Bank service
    -> Assignment Instance service
    -> Student Workspace service
    -> Git synchronization service
    -> Rendering/validation service
    -> Submission service
    -> Evaluation profile service
    -> Feedback/review service
    -> Access-control authorization service
    -> Audit/evidence service
  -> Local persistence/index
  -> Git backend adapter
    -> GitHub-first adapter
    -> later self-hosted Git adapter
```

## 4. Major components

| Component | Responsibility | Primary requirements |
|---|---|---|
| Course/Roster Manager | Course, term, section, roster import, identity binding | FR-001..FR-008 |
| Problem Bank Manager | Reusable assignment originals, rubrics, references, validation/evaluation profiles | FR-009, FR-010, FR-031..FR-033 |
| Assignment Instance Manager | Release assignment versions to course/section contexts | FR-010, FR-015, FR-016 |
| Student Workspace Manager | Provision and protect `assignment/**` and `workspace/**` | FR-011..FR-015 |
| Git Sync Engine | Pull/push/sync/checkpoint/submit with queued/pushed/confirmed state | FR-013, FR-014, FR-023, FR-028 |
| Rendering Adapter/Core | Render graph/table/image/document artifacts and evidence snapshots | FR-031..FR-034, NFR-012 |
| Submission Manager | Create submission branch/snapshot/tag/metadata | FR-014, FR-021 |
| Evaluation Profile Runner | Execute C/C++ compile/test/static-analysis profile | FR-017, FR-018 |
| Review and Feedback Manager | TA/instructor review, feedback release, grade notes | FR-019, FR-020, FR-022 |
| Audit/Evidence Manager | Record actor/action/SHA/state transitions/export packages | FR-021, NFR-003, NFR-004 |
| Role/Permission Gate | Enforce student/instructor/TA/admin capabilities independent of UI hiding | FR-025..FR-027, FR-034, NFR-010, NFR-013 |
| Access-Control Authorization Service | Evaluate scoped subject/resource/action/context decisions, high-impact gates, and authorization decision records | FR-035, NFR-014 |

## 5. Core data and evidence model

```text
Course -> Section -> Roster Student -> Git Identity Binding
Problem Bank Item -> Assignment Version -> Assignment Instance
Assignment Instance -> Student Workspace -> Workspace Commit
Workspace Commit -> Submission Branch/Tag -> Submission Snapshot
Submission Snapshot -> Evaluation Run -> Review/Feedback -> Export/Archive
```

Git remains the authoritative technical evidence for assignment versions, workspace commits, submission snapshots, and audit-relevant refs/tags. The local database/index is operational state and must reconcile to existing Git objects.

## 6. Repository topology baseline

| Repository/namespace | Controlled content |
|---|---|
| Problem Bank repository | `assignment-bank/<item>/main`, `versions/`, `instructions/`, `template/`, `rubric/`, `metadata.yaml` |
| Assignment Instance repository | `main`, `releases/v*`, `submissions/<student_id>`, submission tags |
| Student Workspace repository | `assignment/`, `workspace/`, `metadata/assignment_version.json`, `metadata/sync_status.json` |

## 7. State model summary

| State family | States |
|---|---|
| Student lifecycle | Imported, Invited, Bound, Provisioned, Active, Submitted, Evaluated, Feedback Released, Locked/Withdrawn, Archived |
| Submission status | Draft, Locally Checkpointed, Queued, Pushed, Confirmed, Evaluated, Feedback Released, Reopened, Archived |
| Assignment release | Draft, Validated, Published, Update Published, Sync Required, Archived |
| Evaluation | Pending, Running, Passed, Failed, Error, Manual Review Required |

## 8. Critical design rules

1. Students cannot modify `assignment/**` through supported workflows.
2. Student work is confined to `workspace/**`.
3. Assignment updates affect assignment content only and never silently overwrite workspace content.
4. Official submission requires snapshot metadata linked to assignment version and workspace commit.
5. Rendering artifacts must preserve source, snapshot/evidence, renderer profile, and fallback/error evidence.
6. UI role separation is necessary but insufficient; scoped backend/application authorization decisions are authoritative and default-deny.
7. Offline/queued states cannot be represented as confirmed remote submissions.
8. LMS is not required; import/export is local controlled documented information.

## 9. Open implementation decisions

| Decision | Status |
|---|---|
| Exact UI stack: native, Next.js-in-shell, or hybrid | Open, fixture-gated |
| Exact Git library: git CLI, GitPython, pygit2/libgit2 | Open |
| C/C++ toolchain profile: MSVC, LLVM/MinGW, WSL, configurable | Open |
| Evaluation location: local, lab runner, GitHub Actions | Open |
| Rendering core Stage 1 vs Stage 2 investment boundary | Open |

## 10. Traceability

| Source | Design response |
|---|---|
| SRS FR-001..FR-008 | Course/Roster/Student services |
| SRS FR-009..FR-016 | Problem Bank, Assignment Instance, Workspace, Sync services |
| SRS FR-017..FR-022 | Evaluation, Review, Feedback, Export services |
| SRS FR-023..FR-030 | Git backend, permission, mode, submission topology |
| SRS FR-031..FR-034 | Document model, rendering, role-separated UI |
| NFR-010..NFR-013 | Mode/role clarity, responsiveness, rendering fallback, permission enforcement |

## 11. Gap-closure architecture updates

The architecture baseline is extended with these controlled components:

| Component/profile | Design impact |
|---|---|
| Knowledge workspace service | Manages `knowledge/**` indexing, privacy class, submission inclusion, redaction, and export linkage |
| Canonical block schema | Decouples editor evidence from editor-vendor internal state |
| Export fidelity service | Produces DOCX/HWPX/HWP/PDF derived outputs and manifests without replacing canonical source |
| Evaluation runner profile | Separates advisory local pre-checks from authoritative official evaluation evidence |
| State machine service | Separates student lifecycle, submission state, and assignment release/update state |
| GitHub topology/token service | Controls GitHub org/repo naming, pseudonymous branch refs, scoped credentials, and rate-limit handling |

These updates are controlled by [Knowledge topology and submission policy](knowledge-topology-submission-policy.md), [Editor block schema baseline](block-schema.md), [HWP and HWPX export strategy](hwp-export-strategy.md), [Evaluation execution profile](evaluation-execution-profile.md), and [Canonical state machine profile](state-machine-canonical.md).

## 12. Notion-style storage component update

Add a Document Storage Service between the editor UI and Git/evidence layers. It owns operation journaling, canonical JSON/Markdown materialization, block/asset indexes, revision graph, conflict records, and Git checkpoint boundaries. The service ensures that local persistence accelerates editing but canonical JSON/Markdown/assets/manifests remain durable evidence.

## 13. Repository topology refinement for Notion-style storage

Student workspace topology now includes `documents/`, `assets/`, and local `.eduops/` structures under each editable scope. `documents/*.eduops.json`, `documents/*.md`, and `documents/*.manifest.json` are controlled source/projection artifacts. `.eduops/autosave`, `.eduops/journals`, and `.eduops/indexes` are local recovery/cache structures unless materialized into a tracked checkpoint manifest. `knowledge/**` follows the same pattern but defaults to student-private visibility until promoted into submission/export evidence.

## 14. SRS-derived design baseline expansion

This section expands the SDD directly from `requirements-record.md` v1.6.0 and the RTM. It makes the design response explicit enough for implementation task selection while preserving the Windows/Linux desktop-first, GitHub-first, no-LMS, fixture-gated baseline.

### 14.1 Authoritative architectural decisions for this SRS baseline

1. The desktop shell is a controlled local application boundary; standalone hosted web delivery is outside the current baseline.
2. The local backend owns domain state, configuration, credential references, authorization decisions, audit events, and worker orchestration.
3. Git evidence is authoritative for assignment versions, workspace checkpoints, submission snapshots, refs/tags, and review/export evidence links.
4. The editor UI is not the source of truth; canonical document JSON, deterministic Markdown projection, manifests, operation journals, and Git checkpoints define the durable evidence boundary.
5. The C/C++ runner starts as a local advisory worker; official grading remains blocked until a separate approved runner/sandbox profile exists.
6. GitHub, export converters, and official evaluation remain behind fixture/dry-run/live approval gates.
7. Every implemented behavior must trace to an SRS ID, interface/design anchor, STD/fixture anchor, and RED--GREEN evidence.

### 14.2 Expanded component model

| Component | Owned concerns | Primary interfaces | First test anchors |
|---|---|---|---|
| Desktop Shell / Role UI | Student, instructor, TA, admin, and evaluator workflows; role-specific navigation; no hidden authority. | IF-001..IF-016, IF-TRACE-001 | STD-019..STD-028, STD-084..085 |
| Local Backend Application Service | Command/query routing, domain validation, idempotency, audit, authorization, state transitions. | IF-001..IF-016, IF-STATE-001 | STD-001..STD-028, STD-049 |
| Course/Roster/Identity Services | Course creation, roster import, GitHub identity claim/approval, lifecycle status. | IF-001, IF-002, IF-003, IF-ROSTER-001 | STD-001..STD-005, STD-053 |
| Problem Bank and Assignment Services | Assignment bank item, version, instance, publication/update, required blocks, rubrics. | IF-004, IF-005 | STD-006..STD-010, STD-032 |
| Workspace and Git Sync Services | Workspace provisioning, local checkpoint, queued/pushed/confirmed submission states, fake/local/live-gated adapters. | IF-006..IF-009 | STD-005, STD-008..STD-013 |
| Document Storage and Editor Adapter | Block schema, operation journal, canonical JSON, Markdown projection, migration, index rebuild. | IF-EDITOR-001, IF-STORAGE-001..010 | STD-039..STD-044, STD-056..STD-067, STD-084..STD-085 |
| Knowledge Workspace Service | Student-owned `knowledge/**`, privacy scope, submission inclusion, redaction, export linkage. | IF-KNOWLEDGE-001..002 | STD-034..STD-038, STD-045 |
| Rendering and Export Services | Graph/table/image rendering, fallback snapshots, DOCX/HWPX/HWP/PDF generation, warning/loss manifests. | IF-010, IF-EXPORT-001 | STD-021..STD-023, STD-036..STD-038, STD-047 |
| Evaluation Runner Service | Advisory C/C++ execution, toolchain profile, resource limit, result JSON, official-runner separation. | IF-EVAL-001, IF-012 | STD-014..STD-016, STD-048 |
| Review, Feedback, and Evidence Services | TA/instructor review, feedback release, grade/audit export, evidence package creation. | IF-013, IF-014 | STD-017..STD-018, STD-024, STD-033 |
| Authorization, Configuration, Credential, and Traceability Services | Scoped RBAC/PDP/PEP, config hierarchy, credential references, RTM/TDD evidence gates. | IF-016, IF-CONFIG-001..006, IF-CREDENTIAL-001..004, IF-TRACE-001, IF-TDD-001 | STD-026..STD-028, STD-078..STD-085 |

### 14.3 SRS-to-design traceability table

| Requirement ID | Design area | Components | Interface anchors | Test anchors |
|---|---|---|---|---|
| `EDUOPS-FR-001` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-002` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-003` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-004` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-005` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-006` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-007` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-008` | Course, roster, identity, and workspace provisioning | Course/Roster Manager; Identity Binding Service; Workspace Provisioning Service | IF-001, IF-002, IF-003, IF-006 | STD-001..STD-005 |
| `EDUOPS-FR-009` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-010` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-011` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-012` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-013` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-014` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-015` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-016` | Problem bank, assignment instance, workspace, sync, and submission state | Problem Bank Manager; Assignment Instance Manager; Student Workspace Manager; Git Sync Engine | IF-004, IF-005, IF-007, IF-008, IF-009 | STD-006..STD-013 |
| `EDUOPS-FR-017` | Evaluation, review, feedback, evidence, and exports | Evaluation Runner; Review/Feedback Manager; Audit/Evidence Manager | IF-012, IF-013, IF-014 | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-018` | Evaluation, review, feedback, evidence, and exports | Evaluation Runner; Review/Feedback Manager; Audit/Evidence Manager | IF-012, IF-013, IF-014 | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-019` | Evaluation, review, feedback, evidence, and exports | Evaluation Runner; Review/Feedback Manager; Audit/Evidence Manager | IF-012, IF-013, IF-014 | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-020` | Evaluation, review, feedback, evidence, and exports | Evaluation Runner; Review/Feedback Manager; Audit/Evidence Manager | IF-012, IF-013, IF-014 | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-021` | Evaluation, review, feedback, evidence, and exports | Evaluation Runner; Review/Feedback Manager; Audit/Evidence Manager | IF-012, IF-013, IF-014 | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-022` | Evaluation, review, feedback, evidence, and exports | Evaluation Runner; Review/Feedback Manager; Audit/Evidence Manager | IF-012, IF-013, IF-014 | STD-014..STD-018, STD-024 |
| `EDUOPS-FR-023` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-024` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-025` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-026` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-027` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-028` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-029` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-030` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-031` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-032` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-033` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-034` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-035` | Repository backend, operating modes, document model, rendering, and authorization | Git Backend Adapter; Mode Controller; Rendering Core; Authorization Service | IF-010, IF-011, IF-015, IF-016 | STD-019..STD-028 |
| `EDUOPS-FR-036` | Classroom operations cockpit and benchmark-derived efficiency | Course Operations Cockpit; Bulk Operation Service; Evidence Dashboard | IF-001, IF-002, IF-006, IF-014, IF-016 | STD-029..STD-033 |
| `EDUOPS-FR-037` | Classroom operations cockpit and benchmark-derived efficiency | Course Operations Cockpit; Bulk Operation Service; Evidence Dashboard | IF-001, IF-002, IF-006, IF-014, IF-016 | STD-029..STD-033 |
| `EDUOPS-FR-038` | Classroom operations cockpit and benchmark-derived efficiency | Course Operations Cockpit; Bulk Operation Service; Evidence Dashboard | IF-001, IF-002, IF-006, IF-014, IF-016 | STD-029..STD-033 |
| `EDUOPS-FR-039` | Classroom operations cockpit and benchmark-derived efficiency | Course Operations Cockpit; Bulk Operation Service; Evidence Dashboard | IF-001, IF-002, IF-006, IF-014, IF-016 | STD-029..STD-033 |
| `EDUOPS-FR-040` | Classroom operations cockpit and benchmark-derived efficiency | Course Operations Cockpit; Bulk Operation Service; Evidence Dashboard | IF-001, IF-002, IF-006, IF-014, IF-016 | STD-029..STD-033 |
| `EDUOPS-FR-041` | Classroom operations cockpit and benchmark-derived efficiency | Course Operations Cockpit; Bulk Operation Service; Evidence Dashboard | IF-001, IF-002, IF-006, IF-014, IF-016 | STD-029..STD-033 |
| `EDUOPS-FR-042` | Knowledge workspace and controlled report export | Knowledge Workspace Service; Export Fidelity Service; Evidence Manifest Service | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | STD-034..STD-038 |
| `EDUOPS-FR-043` | Knowledge workspace and controlled report export | Knowledge Workspace Service; Export Fidelity Service; Evidence Manifest Service | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | STD-034..STD-038 |
| `EDUOPS-FR-044` | Knowledge workspace and controlled report export | Knowledge Workspace Service; Export Fidelity Service; Evidence Manifest Service | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | STD-034..STD-038 |
| `EDUOPS-FR-045` | Knowledge workspace and controlled report export | Knowledge Workspace Service; Export Fidelity Service; Evidence Manifest Service | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | STD-034..STD-038 |
| `EDUOPS-FR-046` | Knowledge workspace and controlled report export | Knowledge Workspace Service; Export Fidelity Service; Evidence Manifest Service | IF-KNOWLEDGE-001, IF-KNOWLEDGE-002, IF-EXPORT-001 | STD-034..STD-038 |
| `EDUOPS-FR-047` | Block editor and authoring runtime | Editor Adapter; Document Storage Service; Validation Service | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | STD-039..STD-044 |
| `EDUOPS-FR-048` | Block editor and authoring runtime | Editor Adapter; Document Storage Service; Validation Service | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | STD-039..STD-044 |
| `EDUOPS-FR-049` | Block editor and authoring runtime | Editor Adapter; Document Storage Service; Validation Service | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | STD-039..STD-044 |
| `EDUOPS-FR-050` | Block editor and authoring runtime | Editor Adapter; Document Storage Service; Validation Service | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | STD-039..STD-044 |
| `EDUOPS-FR-051` | Block editor and authoring runtime | Editor Adapter; Document Storage Service; Validation Service | IF-EDITOR-001, IF-STORAGE-001..005, IF-011 | STD-039..STD-044 |
| `EDUOPS-NFR-001` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-002` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-003` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-004` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-005` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-006` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-007` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-008` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-009` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-010` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-011` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-012` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-013` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-014` | Cross-cutting quality: usability, audit, privacy, local-first, no-LMS, resilience, role clarity, rendering, authorization | All services via policy, audit, authorization, and evidence layers | IF-014, IF-015, IF-016, IF-CONFIG-*, IF-TRACE-001 | STD-001..STD-028, STD-084..STD-085 |
| `EDUOPS-NFR-015` | Benchmark, export, knowledge, editor, and round-trip quality | Operations Cockpit; Export Fidelity Service; Editor Adapter; Knowledge Workspace Service | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-016` | Benchmark, export, knowledge, editor, and round-trip quality | Operations Cockpit; Export Fidelity Service; Editor Adapter; Knowledge Workspace Service | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-017` | Benchmark, export, knowledge, editor, and round-trip quality | Operations Cockpit; Export Fidelity Service; Editor Adapter; Knowledge Workspace Service | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-018` | Benchmark, export, knowledge, editor, and round-trip quality | Operations Cockpit; Export Fidelity Service; Editor Adapter; Knowledge Workspace Service | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-NFR-019` | Benchmark, export, knowledge, editor, and round-trip quality | Operations Cockpit; Export Fidelity Service; Editor Adapter; Knowledge Workspace Service | IF-KNOWLEDGE-*, IF-EDITOR-001, IF-EXPORT-001 | STD-029..STD-044, STD-084..STD-085 |
| `EDUOPS-FR-052` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-053` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-054` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-055` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-056` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-057` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-058` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-059` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-060` | Gap-closure profiles: knowledge, schema, export, evaluation, state, GitHub, roster, locale, accessibility, retention | Profile-specific services and adapters under controlled design docs | IF-KNOWLEDGE-*, IF-EDITOR-*, IF-EXPORT-*, IF-EVAL-001, IF-STATE-001, IF-ROSTER-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-020` | Claude gap-closure quality: privacy, performance, accessibility, retention, locale | Profile-specific policy and verification adapters | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-021` | Claude gap-closure quality: privacy, performance, accessibility, retention, locale | Profile-specific policy and verification adapters | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-022` | Claude gap-closure quality: privacy, performance, accessibility, retention, locale | Profile-specific policy and verification adapters | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-023` | Claude gap-closure quality: privacy, performance, accessibility, retention, locale | Profile-specific policy and verification adapters | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-NFR-024` | Claude gap-closure quality: privacy, performance, accessibility, retention, locale | Profile-specific policy and verification adapters | IF-STORAGE-010, IF-CONFIG-*, IF-TRACE-001 | STD-045..STD-055, STD-084..STD-085 |
| `EDUOPS-FR-061` | Notion-style storage and storage gap closure | Document Storage Service; Projection Service; Asset Policy Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-062` | Notion-style storage and storage gap closure | Document Storage Service; Projection Service; Asset Policy Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-063` | Notion-style storage and storage gap closure | Document Storage Service; Projection Service; Asset Policy Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-025` | Storage quality: source/projection, privacy, migration, recovery | Document Storage Service; Projection Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-026` | Storage quality: source/projection, privacy, migration, recovery | Document Storage Service; Projection Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-064` | Notion-style storage and storage gap closure | Document Storage Service; Projection Service; Asset Policy Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-065` | Notion-style storage and storage gap closure | Document Storage Service; Projection Service; Asset Policy Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-066` | Notion-style storage and storage gap closure | Document Storage Service; Projection Service; Asset Policy Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-027` | Storage quality: source/projection, privacy, migration, recovery | Document Storage Service; Projection Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-NFR-028` | Storage quality: source/projection, privacy, migration, recovery | Document Storage Service; Projection Service; Migration Service | IF-STORAGE-001..010 | STD-056..STD-067, STD-084..STD-085 |
| `EDUOPS-FR-067` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-068` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-NFR-029` | Implementation/configuration quality | Configuration Service; Credential Reference Service; Fixture Harness | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-069` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-070` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-071` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-072` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-073` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-074` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-075` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-076` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-077` | Implementation executability, configuration, and credential controls | Configuration Service; Credential Reference Service; Fixture Harness; Contract Gate | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-NFR-030` | Implementation/configuration quality | Configuration Service; Credential Reference Service; Fixture Harness | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-NFR-031` | Implementation/configuration quality | Configuration Service; Credential Reference Service; Fixture Harness | IF-CONFIG-001..006, IF-CREDENTIAL-001..004 | STD-068..STD-083, STD-084..STD-085 |
| `EDUOPS-FR-078` | Traceability and TDD governance | Traceability Controller; TDD Evidence Gate | IF-TRACE-001, IF-TDD-001 | STD-084..STD-085 |
| `EDUOPS-FR-079` | Traceability and TDD governance | Traceability Controller; TDD Evidence Gate | IF-TRACE-001, IF-TDD-001 | STD-084..STD-085 |
| `EDUOPS-NFR-032` | Traceability and TDD quality | Traceability Controller; TDD Evidence Gate | IF-TRACE-001, IF-TDD-001 | STD-084..STD-085 |
| `EDUOPS-NFR-033` | Traceability and TDD quality | Traceability Controller; TDD Evidence Gate | IF-TRACE-001, IF-TDD-001 | STD-084..STD-085 |


## 15. GitHub adapter design response

The GitHub integration module is designed as an adapter behind the application core, not as UI-owned GitHub logic. The application core remains responsible for authorization, state guards, audit decisions, and no-live-action gates. The adapter implements the mode-specific repository/backend behavior defined in [GitHub Adapter Specification](github-adapter-specification.md). The detailed component, state, data-flow, error, security, module-placement, and slice design is controlled in [GitHub Adapter Software Design Description](github-adapter-software-design-description.md).

| SRS ID | Design response |
|---|---|
| EDUOPS-FR-080 | `eduops_git` shall expose a GitHub adapter implementation behind the repository adapter trait; `fake-local` is the default mode and sandbox/live modes are configuration-gated. |
| EDUOPS-FR-081 | Adapter orchestration is split into validation, plan, provisioning, branch policy, assignment sync, submission-ref, evidence query, and archive/access-disable use cases. |
| EDUOPS-FR-082 | Credential access is routed through `eduops_credentials`; adapter inputs contain `credential_ref_id` and status/fingerprint hints only. |
| EDUOPS-FR-083 | Submission state transitions remain authoritative in the application core; adapter evidence can advance pushed/confirmed states but cannot collapse queued into confirmed. |
| EDUOPS-FR-084 | Sandbox/live mutation paths pass through authorization, configuration gate, idempotency, and audit guards before adapter execution. |
| EDUOPS-NFR-034 | Fake-local and mock-http tests are part of the adapter contract and must pass before any sandbox/live connector. |
| EDUOPS-NFR-035 | Naming policy is evaluated before external call planning so privacy violations fail before any GitHub request. |
| EDUOPS-NFR-036 | GitHub error classes map to the internal API error model and preserve retriable/terminal classification. |


### 15.1 GitHub adapter detailed SDD control

The detailed SDD fixes the architecture for GitHub adapter implementation without enabling live GitHub behavior. It defines:

- adapter facade, mode gate, operation planner, privacy naming policy, credential-reference resolver, backend slots, retry/rate-limit controller, evidence normalizer, and audit binder;
- adapter mode state transitions from `fake-local` through future `live`;
- operation preconditions and state/evidence outputs for validation, planning, provisioning, branch policy, assignment sync, submission refs, remote evidence query, and archive/access-disable;
- request/result data structures with no raw credential fields;
- submission state boundary where the adapter reports evidence and the application core owns state promotion;
- `GH-SLICE-0..5` implementation order tied to `GH-FIX-*` and `STD-086..091`.


## 16. GitHub clone-only design clarification

[GitHub Adapter Software Design Description](github-adapter-software-design-description.md) v0.2.0 narrows GitHub integration to clone-only repository-source behavior. The application core may consume clone evidence, but GitHub mutation/provisioning/submission workflows are not part of the current baseline.
