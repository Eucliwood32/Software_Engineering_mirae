---
title: HISYS EduOps Platform Requirements Record
document_id: SWENG-EDUTECH-SRS
version: 1.9.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Requirements Record

## 1. Purpose

Define the product-level requirements for HISYS EduOps Platform, a Windows and Linux desktop EduTech platform for Git-backed, branch-based, document-oriented assignment management. This is a product SRS-style record, not an MVP-only scope statement.

## 2. Stakeholders and users

| Role | Need |
|---|---|
| Instructor | Reuse assignment originals, control versions, manage students, publish updates, review submissions and evaluation results through an instructor/professor UI surface |
| Teaching assistant | Support grading, inspect histories, triage compile/test failures, monitor student progress, provide rubric feedback |
| Student | Work in an isolated student UI focused on assignment viewing, workspace editing, validation, submission, update notices, and released feedback |
| Course operator/admin | Configure courses, sections, roster import, student identity binding, GitHub repositories, backup, and audit/export controls |
| Evaluation runner | Execute controlled C/C++ compile/test/static-analysis profiles and write evaluation evidence |

## 3. Accepted baseline assumptions

- The product is desktop-first in the current baseline. Standalone web/mobile delivery is excluded unless separately promoted, but Next.js or web UI technology is conditionally acceptable when packaged/controlled inside the desktop or platform-specific UI and verified against rendering, evidence, role, offline, and performance contracts.
- LMS integration is excluded from the current baseline. Roster, grade, and audit information may be handled through controlled local import/export only.
- GitHub is the first repository backend. Self-hosted Git is a later extension profile and shall not complicate the initial GitHub-first baseline.
- Assignment outputs are document-first Markdown/Notion-style artifacts. C/C++ programming assignments are an initial evaluation profile, but not the sole product model. The differentiated student experience includes Notion-style assignment execution, controlled editor behavior, student-owned knowledge artifacts, and controlled DOCX/HWP/HWPX export.
- Student management is a first-class product capability: roster import, identity binding, enrollment/status lifecycle, workspace provisioning, progress visibility, feedback release, and archive controls must be represented explicitly.
- The product shall be organized by operating modes with mode-specific permissions: instructor authoring, course/admin operation, student workspace, TA review, evaluation runner, offline/local, synchronization, review/audit, and recovery/manual override. Student and instructor/professor UIs shall differ by default because their tasks, risks, and permissions differ.
- Git repositories are the authoritative technical record for assignment bank versions, assignment instance releases, student workspace commits, submission branches, submission snapshots, and update logs.
- The user experience must hide unnecessary Git complexity while preserving inspectable Git evidence. The UI shall prioritize efficient native-desktop responsiveness with asynchronous Git, validation, synchronization, and evaluation jobs. Later platforms may use different UI implementations if they satisfy the same document/rendering/evidence contract.
- Student access to assignment originals is read-only; student writable activity occurs only inside a student workspace.
- Instructor assignment updates synchronize only the assignment area and preserve student workspace content.
- Automated evaluation periodically pulls student repositories or submission branches, executes configured C/C++ checks, and records results as evidence.
- GitHub Classroom and Google Classroom are benchmark/reference systems for course/student-management optimization. They do not change the current no-LMS/no-live-integration baseline unless explicitly promoted later.

## 4. Functional requirements

### 4.1 Course and student management

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-FR-001 | The system shall define courses, terms, sections, instructors, TAs, due policies, and GitHub organization/repository context without LMS dependency. | Fixture course metadata validates without LMS credentials. |
| EDUOPS-FR-002 | The system shall import and version roster records from controlled CSV/JSON files. | Roster import record includes file hash, schema version, actor, timestamp, validation result, and rejected rows. |
| EDUOPS-FR-003 | The system shall maintain student records linked to course roster ID, section, display name, contact identifier, GitHub identity, status, and privacy flags. | Student registry fixture validates required/optional fields and redaction behavior. |
| EDUOPS-FR-004 | The system shall support GitHub identity binding with instructor/admin approval and duplicate-account detection. | Two students cannot be approved with the same GitHub identity unless an override record exists. |
| EDUOPS-FR-005 | The system shall track student lifecycle states from Imported, Invited, Bound, Provisioned, Active, Submitted, Evaluated, Feedback Released, Locked/Withdrawn, to Archived. | State-transition tests reject invalid transitions. |
| EDUOPS-FR-006 | The system shall provision per-student workspace and submission namespace from an approved student record. | Provisioning evidence links roster ID, GitHub identity, workspace path, repository/branch, and assignment instance. |
| EDUOPS-FR-007 | The system shall expose instructor/TA views for each student's assignment progress, submission state, evaluation state, and feedback release state. | Student dashboard fixture shows consistent state across assignment, GitHub, and evaluation records. |
| EDUOPS-FR-008 | The system shall support student status changes such as active, late-allowed, locked, withdrawn, and archived. | Status changes affect submission eligibility and are audit logged. |

### 4.2 Assignment and workspace management

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-FR-009 | The system shall provide a Problem Bank for reusable C/C++ assignment originals containing problem text, starter code, headers, fixtures, hints, rubric, references, and automated-check rules. | Instructor can version and reuse a C/C++ problem package across at least two assignment instances. |
| EDUOPS-FR-010 | The system shall create Assignment Instances from a selected Problem Bank version for a course, semester, and section. | Instance metadata records source problem version, course, section, release window, due date, and C/C++ evaluation profile. |
| EDUOPS-FR-011 | The system shall create an isolated Student Workspace for each enrolled/provisioned student. | Each workspace contains read-only assignment content and a writable C/C++ work area. |
| EDUOPS-FR-012 | The system shall prevent students from modifying assignment originals through the desktop application. | Attempted edits to assignment areas are blocked or redirected to the workspace area. |
| EDUOPS-FR-013 | The system shall represent student save, revision, checkpoint, and submission events as Git commits. | Commit metadata links student, assignment instance, assignment version, timestamp, and action type. |
| EDUOPS-FR-014 | On submission, the system shall create a submission snapshot in the Assignment Instance Repository under a student-specific submission branch or equivalent controlled namespace. | Submission evidence includes commit SHA, assignment version, student workspace snapshot, eligibility/late status, and confirmation state. |
| EDUOPS-FR-015 | The system shall synchronize instructor assignment updates into the assignment area without overwriting student workspace content. | Update test shows changed assignment files and unchanged student files, with conflict/notice record if needed. |
| EDUOPS-FR-016 | The system shall notify students of assignment changes and show the affected files, reason, and required action. | Windows desktop notification and in-app change log are generated for an assignment update. |

### 4.3 Evaluation, grading, and evidence

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-FR-017 | The system shall support automated C/C++ evaluation from configured compile, run, unit-test, and static-analysis rules. | Evaluation run records input snapshot SHA, compiler/toolchain profile, command, result, logs, and generated feedback. |
| EDUOPS-FR-018 | The system shall capture C/C++ build environment metadata for each evaluation. | Evaluation evidence includes compiler name/version, standard flag, build profile, OS, and timeout/resource limits. |
| EDUOPS-FR-019 | The system shall support instructor/TA review of submissions, evaluation outcomes, Git history, rubric feedback, and final grading notes. | Review view links submitted files, history, compile/test results, rubric entries, and feedback record. |
| EDUOPS-FR-020 | The system shall support controlled feedback release to students. | Feedback release evidence includes reviewer, rubric version, timestamp, visible result set, and affected student IDs. |
| EDUOPS-FR-021 | The system shall preserve audit trails for roster import, identity binding, problem publication, instance creation, workspace creation, synchronization, submission, evaluation, feedback, override, and grade export. | Audit export contains actor, action, timestamp, object ID, Git SHA where applicable, before/after state where applicable, and outcome. |
| EDUOPS-FR-022 | The system shall support controlled local export/import exchange for grade/evaluation records and audit roster snapshots instead of LMS integration, while primary roster import/versioning remains governed by `EDUOPS-FR-002`. | CSV/JSON exchange fixtures pass validation, redaction, and traceability checks without LMS credentials. |

### 4.4 Repository backend, operating modes, document model, and editor capabilities

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-FR-023 | The system shall provision and validate GitHub repositories, branches, permissions, and tokens needed for the assignment workflow. | A fixture GitHub configuration can be validated without exposing raw secrets. |
| EDUOPS-FR-024 | The system shall retain a backend abstraction boundary so self-hosted Git can be added later without changing assignment semantics. | Git backend interface tests pass against a GitHub fixture and a local/self-hosted-Git simulator. |
| EDUOPS-FR-025 | The system shall enforce mode-specific actions and blocked actions for instructor, admin, student, TA, evaluator, sync, audit, offline, and recovery modes. | Permission matrix tests cover allowed and blocked actions for each mode. |
| EDUOPS-FR-026 | The system shall display the current operating mode and active course/assignment/student context where safety or evidence depends on it. | UI scenario shows visible mode/context before publish, submit, evaluate, export, and override actions. |
| EDUOPS-FR-027 | The system shall require explicit confirmation for high-impact mode transitions, including publish, submit, release feedback, export grades, and manual override. | Confirmation evidence is recorded for high-impact transitions. |
| EDUOPS-FR-028 | The system shall prevent offline mode from representing queued commits as successful remote submissions until GitHub confirmation exists. | Offline submission queue test distinguishes queued, pushed, and confirmed states. |
| EDUOPS-FR-029 | The system shall support authorized manual override for identity repair, submission reopening, and recovery actions. | Override requires actor, reason, scope, timestamp, affected record, and before/after state. |
| EDUOPS-FR-030 | The system shall support the concept chain Problem Bank → Assignment Bank Item → Assignment Version → Assignment Instance → Student Workspace → Submission Branch → Submission Snapshot. | Traceability tests map a submission snapshot back to the bank item, assignment version, instance, workspace commit, and submission branch/tag. |
| EDUOPS-FR-031 | The system shall support document-first Notion-style editor JSON and Markdown export for assignment instructions and student submissions. | A fixture assignment round-trips editor JSON to Markdown export and submission branch snapshot. |
| EDUOPS-FR-032 | The system shall validate document submissions for minimum length, required sections, image existence, table existence, reference existence, deadline, and empty sections. | Automatic validation fixtures produce pass/fail evidence for each check. |
| EDUOPS-FR-033 | The system shall render graph/diagram, table, and image artifacts correctly in authoring, student workspace, review, feedback, and evidence/export flows. | Rendering fixtures verify graph fallback/source, table layout/large-table behavior, image path/caption/missing-file handling, and export/submission evidence consistency. |
| EDUOPS-FR-034 | The system shall provide role-separated UI surfaces and feature sets for at least student, instructor/professor, TA, and admin/operator roles. | Role UI fixtures verify that each role sees only allowed navigation/actions and that blocked functions are inaccessible through UI and backend permission checks. |
| EDUOPS-FR-035 | The system shall enforce scoped access-control decisions for protected resources and actions, including course, roster, identity, assignment, workspace, submission, evaluation, feedback, export, configuration, and manual override operations. | Access-control fixtures verify default-deny behavior, role/scope checks, high-impact confirmations, audit events, and direct-call denial independent of UI hiding. |
| EDUOPS-FR-036 | The system shall provide an instructor/admin course operations dashboard that summarizes roster completeness, identity binding, provisioning, submission states, evaluation states, feedback release, and export status. | Dashboard fixture shows counts, exceptions, and drilldowns for a 30-student course. |
| EDUOPS-FR-037 | The system shall expose repository/evidence status without requiring normal users to use Git CLI commands. | Instructor can inspect repository, branch, SHA, submission, and evaluation evidence from the UI. |
| EDUOPS-FR-038 | The system shall support bulk roster, invitation, identity-binding, provisioning, publication, evaluation, feedback-release, and export workflows with per-record exception handling. | Batch operation fixture completes valid records and isolates invalid records with reason/evidence. |
| EDUOPS-FR-039 | The system shall provide assignment publication/update previews that show affected students, repositories/branches, validation results, and rollback/evidence packets. | Publication/update fixture produces a preview and audit packet before applying changes. |
| EDUOPS-FR-040 | The system shall require assignment update diff, student notice, acknowledgement state, and no-overwrite evidence for updates affecting released assignments. | Correction fixture shows `assignment/**` changed, `workspace/**` unchanged, and acknowledgement records present. |
| EDUOPS-FR-041 | The system shall combine code/evaluation feedback and rubric/grade feedback into a controlled feedback release workflow. | Feedback release fixture keeps draft feedback hidden and records release/export evidence. |
| EDUOPS-FR-042 | The system shall support Notion-style assignment execution blocks for planning, explanation, code excerpt, table, graph, image, checklist, decision, experiment, and reflection content. | Editor JSON, canonical Markdown, and block-validation fixtures preserve required block semantics. |
| EDUOPS-FR-043 | The system shall support student-owned knowledge artifacts under a protected `knowledge/**` workspace area that can link notes, code, decisions, experiments, references, and reflections. | Knowledge fixture creates `knowledge/index.md`, linked notes, and source/evidence references without modifying `assignment/**`. |
| EDUOPS-FR-044 | The system shall support controlled DOCX export from assignment/knowledge/report templates. | DOCX fixture preserves headings, Korean/English text, tables, images, code blocks, citations, and export manifest/hash. |
| EDUOPS-FR-045 | The system shall support a controlled HWP/HWPX export profile for Korean institutional report submission, with explicit converter/version/fallback evidence. | HWPX/HWP fixture either validates generated output or records a controlled unsupported-profile warning without losing canonical evidence. |
| EDUOPS-FR-046 | The system shall generate export manifests linking derived DOCX/HWP/HWPX/PDF outputs to source commit SHA, template version, export tool profile, content hash, warnings, and redaction profile. | Export manifest fixture validates traceability and privacy/redaction fields. |
| EDUOPS-FR-047 | The system shall provide a controlled Notion-style block editor for assignment authoring, student assignment execution, student knowledge notes, report templates, and review/feedback views. | Editor fixture supports role-specific authoring/execution/review modes without exposing blocked actions. |
| EDUOPS-FR-048 | The editor shall support autosave, checkpoint, undo/redo, local history, and Git-backed recovery for student-owned `workspace/**` and `knowledge/**` content. | Student recovery fixture restores a prior checkpoint and links it to a Git commit without Git CLI use. |
| EDUOPS-FR-049 | The editor shall validate required blocks, citations/references, assets, report sections, deadlines, privacy/redaction, and export readiness before submission or report generation. | Validation fixture reports actionable missing/invalid blocks and blocks unsafe export/submission. |
| EDUOPS-FR-050 | The editor shall enforce role/path/scope editing permissions so students cannot edit assignment originals or protected metadata and instructors cannot silently modify student workspace content. | Direct-call and UI-bypass tests deny unauthorized edits independent of UI hiding. |
| EDUOPS-FR-051 | The editor shall support Korean/English mixed editing, C/C++ code blocks, tables, diagrams, images, references, experiment/evidence blocks, decision blocks, reflection blocks, and report placeholders. | Editor fixture preserves these blocks through editor JSON, canonical Markdown, rendered preview, and export mapping. |

## 5. Non-functional requirements

| ID | Requirement | Acceptance seed |
|---|---|---|
| EDUOPS-NFR-001 | The system shall run as a Windows and Linux desktop application in the current product baseline. | Supported OS matrix states Windows and Linux, with packaging and desktop smoke tests for each supported OS family. |
| EDUOPS-NFR-002 | The system shall be usable by students without direct Git command-line knowledge for normal operations. | Scripted usability scenario shows save/submit/update flows through UI. |
| EDUOPS-NFR-003 | Git evidence shall remain inspectable by instructors/admins for reproducibility and dispute resolution. | Audit export can map a submission to Git SHAs and assignment source version. |
| EDUOPS-NFR-004 | The system shall protect student personal data, GitHub credentials, and grade data by default. | Local storage, export, logs, token references, and evaluation artifacts pass privacy review. |
| EDUOPS-NFR-005 | Automated C/C++ evaluation shall be sandboxed from instructor/student personal files. | Test harness demonstrates no access outside permitted workspace paths and no uncontrolled process execution. |
| EDUOPS-NFR-006 | The product shall support disconnected/local-first work for drafting and student workspace edits, with controlled synchronization when GitHub repositories are reachable. | Offline scenario records local commits and later syncs without data loss. |
| EDUOPS-NFR-007 | C/C++ evaluation shall enforce time, memory, process, and filesystem limits appropriate for untrusted student code. | Malicious/buggy fixture programs are contained and produce controlled failure evidence. |
| EDUOPS-NFR-008 | The current baseline shall not require LMS availability or LMS credentials. | Installation/configuration scenario completes without any LMS connector. |
| EDUOPS-NFR-009 | Student management operations shall remain auditable and privacy-preserving. | Student registry, roster import, identity binding, status changes, and export records pass privacy/audit checks. |
| EDUOPS-NFR-010 | Mode boundaries shall be understandable in the UI and enforceable in backend logic. | Mode-switching and permission tests pass for all defined modes. |
| EDUOPS-NFR-011 | The desktop UI shall remain responsive during navigation, editing, autosave/checkpoint, diff display, validation feedback, Git sync, submission, and evaluation-trigger operations. | UI responsiveness tests show long-running Git/validation/evaluation jobs execute asynchronously with progress/error reporting and no UI-thread blocking. |
| EDUOPS-NFR-012 | Graph, table, and image rendering shall remain performant, deterministic enough for review, and accompanied by controlled fallback/error evidence when rendering cannot complete. | Rendering performance/fallback tests pass for complex graph, wide/large table, local image, missing image, blocked path, and mixed-document fixtures. |
| EDUOPS-NFR-013 | Role separation shall be understandable in the UI and enforced independently by backend/application permission logic. | Student, instructor/professor, TA, and admin/operator permission tests confirm that UI hiding is not the sole access-control mechanism. |
| EDUOPS-NFR-014 | Access-control decisions shall be auditable for identity, grade, export, repository, token-reference, high-impact, and override operations. | Authorization decision records link actor, role, scope, resource, action, decision, reason, timestamp, and audit event where applicable. |
| EDUOPS-NFR-015 | Course/student-management efficiency shall be measured with benchmark fixtures covering setup, roster onboarding, assignment publication/update, submission/evaluation, feedback release/export, and dispute reconstruction. | Benchmark report records EDUOPS-BM-001..010 measurements and pass/fail evidence. |
| EDUOPS-NFR-016 | DOCX/HWP/HWPX export shall be deterministic enough for review and shall never replace canonical Git/Markdown/editor-JSON evidence. | Export tests compare source commit, manifest hash, rendered content, warnings, and canonical evidence links. |
| EDUOPS-NFR-017 | Student knowledge-system features shall preserve privacy, academic-integrity, course-scope, and student-ownership boundaries. | Knowledge promotion/export fixtures verify scope, redaction, citation/source fields, and instructor visibility policy. |
| EDUOPS-NFR-018 | Editor operations shall remain responsive and deterministic enough under large documents, wide tables, images, diagrams, code blocks, logs, and Git diffs. | Editor performance fixtures verify no normal UI blocking and controlled degradation/warnings. |
| EDUOPS-NFR-019 | Editor JSON, canonical Markdown, rendered preview, submission snapshot, and DOCX/HWP/HWPX export shall round-trip with explicit loss/warning records where perfect preservation is impossible. | Round-trip fixtures compare hashes, block IDs, assets, rendered output, and export warnings. |

## 6. Resolved requirements questions

| Question | Baseline decision | Decision ID |
|---|---|---|
| Which operating systems are required first? | Windows and Linux desktop; exact supported Windows versions and Linux distributions/session types remain to be selected. | EDUOPS-DEC-005, EDUOPS-DEC-009, DEC-OS-001 |
| What repository backend is first? | GitHub first; self-hosted Git later. | EDUOPS-DEC-006 |
| What programming-assignment languages are first? | C/C++ code. | EDUOPS-DEC-007 |
| What LMS interoperability is required? | LMS is excluded from the current baseline. | EDUOPS-DEC-008 |
| Is student management part of the product baseline? | Yes; it is a first-class product capability. | EDUOPS-DEC-011 |
| Are GitHub Classroom and Google Classroom part of the product baseline? | They are benchmark/reference systems for optimization; no live integration is added to the current no-LMS baseline. | EDUOPS-DEC-023 |
| What is the core differentiation beyond classroom-management efficiency? | Notion-style assignment execution, student-owned knowledge-system creation, and controlled DOCX/HWP/HWPX export. | EDUOPS-DEC-024 |
| Does the editor require controlled product requirements? | Yes; the editor is a core product capability for assignment execution, evidence, knowledge formation, validation, and export. | EDUOPS-DEC-025 |
| Should operating modes be explicitly separated? | Yes; mode-specific permissions and evidence gates are required. | EDUOPS-DEC-012 |
| Which beta UI/editor/application stack is selected? | Tauri 2 desktop shell, Rust local backend, TypeScript UI, ProseMirror/Tiptap-style editor adapter, SQLite, libgit2-backed Git adapter, canonical-to-DOCX/HWPX exporter path, and Tauri Windows/Linux packaging. Windows uses WebView2; Linux uses the Tauri-supported system webview runtime. | EDUOPS-DEC-047, DEC-OS-001 |
| Which beta C/C++ execution baseline is selected? | LLVM/Clang local advisory worker; official grading remains deferred until approved runner/sandbox profile. | EDUOPS-DEC-048 |

## 7. Controlled usage scenario baseline

The system shall support the end-to-end usage scenarios documented in [Usage scenarios](../02-design-planning/usage-scenarios.md), beginning with student registration and continuing through roster import, GitHub identity binding, workspace provisioning, assignment activation, checkpointing, submission, evaluation, review, feedback release, no-LMS export, and archive.

| Scenario group | Requirement impact |
|---|---|
| Student registration and identity binding | EDUOPS-FR-002 through EDUOPS-FR-006, EDUOPS-FR-021, EDUOPS-FR-023 |
| Student workspace activation and checkpointing | EDUOPS-FR-011 through EDUOPS-FR-016, EDUOPS-FR-028 |
| Submission, evaluation, review, and feedback | EDUOPS-FR-014, EDUOPS-FR-017 through EDUOPS-FR-020, EDUOPS-FR-027 |
| Status change, override, export, and archive | EDUOPS-FR-008, EDUOPS-FR-021, EDUOPS-FR-022, EDUOPS-FR-029 |

## 8. Remaining requirements questions

1. Which Windows versions are supported first, for example Windows 10/11 or Windows 11 only?
2. What exact student registry fields are mandatory vs optional under privacy constraints?
3. What manual override actions are allowed, and who may approve them?
4. Which official evaluation runner/sandbox profile should be approved after the beta advisory LLVM/Clang worker?

## 9. Git-backed Notion-style concept model baseline

The detailed concept, repository structure, permission workflow, data/API model, document model, validation model, and tech-stack caveats are controlled in [Git-backed Notion-style assignment concept](../02-design-planning/git-backed-notion-assignment-concept.md), [Repository permission and assignment workflow](../02-design-planning/repository-permission-workflow.md), [Data API and document model](../02-design-planning/data-api-document-model.md), [Fast native desktop UI baseline](../02-design-planning/fast-native-desktop-ui-baseline.md), [Graph table image rendering profile](../02-design-planning/graph-table-image-rendering-profile.md), [Role-separated UI and feature model](../02-design-planning/role-separated-ui-feature-model.md), [Access control and authorization model](../02-design-planning/access-control-authorization-model.md), and [Rendering engine strategy](../02-design-planning/rendering-engine-strategy.md).

## 10. Claude review gap-closure requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| EDUOPS-FR-052 | The system shall treat `knowledge/**` as a first-class student-owned workspace area with explicit sync, submission, privacy, and evidence rules. | Fixture proves assignment sync never overwrites `knowledge/**`, and submitted knowledge artifacts are traceable through submission metadata. |
| EDUOPS-FR-053 | The system shall select the editor stack through fixture-gated trade study criteria before implementation lock-in. | Editor spike compares candidate stack against Korean IME, schema, export, performance, accessibility, and packaging gates. |
| EDUOPS-FR-054 | The system shall maintain a versioned canonical block schema independent of editor-vendor hidden state. | Fixture validates block IDs, types, source payloads, privacy class, export bindings, and warning records. |
| EDUOPS-FR-055 | The system shall define export fidelity acceptance criteria for DOCX/HWPX/HWP/PDF as derived outputs. | Export fixture maps required blocks to output sections and records loss/warning categories. |
| EDUOPS-FR-056 | The system shall distinguish advisory student pre-checks from authoritative official C/C++ evaluation runner evidence. | Evaluation fixture records runner profile, sandbox policy, toolchain, logs, resource limits, and authoritative status. |
| EDUOPS-FR-057 | The system shall maintain separate canonical state machines for student lifecycle, submission state, and assignment release/update state. | UI/API tests reject treating queued/pushed work as confirmed submission and preserve assignment update acknowledgement state. |
| EDUOPS-FR-058 | The system shall apply a student knowledge policy for privacy, academic integrity, reuse, retention, redaction, and visibility. | Knowledge policy fixture verifies visibility levels and promotion/redaction decision evidence. |
| EDUOPS-FR-059 | The system shall qualify classroom efficiency KPIs against GitHub API feasibility, topology, token, rate-limit, and outage controls before production claims. | GitHub sandbox/dry-run evidence exists before KPI is marked production-ready. |
| EDUOPS-FR-060 | The system shall define controlled roster CSV/JSON schema and GitHub identity-binding validation. | Import fixture validates encoding, duplicates, required fields, privacy flags, approval, and provisioning evidence. |

| ID | Non-functional requirement | Acceptance criterion |
|---|---|---|
| EDUOPS-NFR-020 | Knowledge artifacts shall remain privacy-scoped and submission-scoped according to policy without accidental cohort or public exposure. | Redaction/visibility tests pass for student-private, submission-evidence, course-review, and example-candidate levels. |
| EDUOPS-NFR-021 | Editor stack selection shall meet fixture evidence for Korean IME, large documents, accessibility, export binding, and desktop packaging. | Candidate cannot pass D5 unless all critical editor fixtures pass or have accepted mitigations. |
| EDUOPS-NFR-022 | HWPX/HWP/DOCX export shall record converter, font, locale, warning, hash, and unsupported-feature evidence. | Export manifest fixture contains all required fields and no silent loss of required blocks. |
| EDUOPS-NFR-023 | Performance budgets shall have P50/P95 seed thresholds for editor, autosave, Git checkpoint, dashboard, export, and evaluation operations. | Performance fixture records hardware profile and verifies seed thresholds or controlled warnings. |
| EDUOPS-NFR-024 | Core role-separated UI and editor workflows shall support keyboard navigation, focus visibility, screen-reader labels, and non-color-only status indicators. | Accessibility fixture validates core workflows before classroom pilot. |

References: [Knowledge topology and submission policy](../02-design-planning/knowledge-topology-submission-policy.md), [Editor stack trade study](../02-design-planning/editor-stack-trade-study.md), [Editor block schema baseline](../02-design-planning/block-schema.md), [HWP and HWPX export strategy](../02-design-planning/hwp-export-strategy.md), [Export fidelity acceptance criteria](../02-design-planning/export-fidelity-acceptance.md), [Evaluation execution profile](../02-design-planning/evaluation-execution-profile.md), [Canonical state machine profile](../02-design-planning/state-machine-canonical.md), [Student knowledge policy](../02-design-planning/knowledge-policy.md), [GitHub API feasibility analysis](../00-research-analysis/github-api-feasibility.md), [Roster schema and identity policy](../02-design-planning/roster-schema-and-identity-policy.md), [Performance budget](../02-design-planning/performance-budget.md).

## 11. Notion-style storage requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| EDUOPS-FR-061 | The system shall store Notion-style editable documents as canonical editor JSON snapshots plus deterministic derived Markdown projections. | Fixture saves one document and verifies JSON hash, Markdown hash, stable block IDs, and Git checkpoint metadata. |
| EDUOPS-FR-062 | The system shall maintain an operation journal for autosave, undo/redo, crash recovery, and conflict diagnosis. | Crash-recovery fixture replays journal operations to restore the latest autosaved revision. |
| EDUOPS-FR-063 | The system shall separate canonical evidence files from rebuildable local indexes/search/render caches. | Fixture deletes local indexes and rebuilds them from canonical JSON/Markdown/assets without evidence loss. |

| ID | Non-functional requirement | Acceptance criterion |
|---|---|---|
| EDUOPS-NFR-025 | Save/checkpoint behavior shall be deterministic enough to avoid unnecessary Git noise while preserving student work after crashes. | Repeated materialization of the same block graph produces identical JSON/projection hashes under the pinned projection profile: GFM/CommonMark-compatible Markdown, LF line endings, NFC Unicode normalization, stable frontmatter order, deterministic table/list/code-fence formatting, and explicit lossy-block warnings. |
| EDUOPS-NFR-026 | Storage structures shall preserve stable block IDs, asset hashes, privacy classes, export bindings, and evidence references across reorder, edit, autosave, checkpoint, schema migration, tombstone/delete, and submission. | Reorder/edit fixture keeps comments, validation, export mappings, and evidence links attached to the intended block IDs. |

Reference: [Notion-style document storage architecture](../02-design-planning/notion-style-document-storage-architecture.md).

## 12. Notion-style storage gap-closure requirements

| ID | Requirement | Acceptance criterion |
|---|---|---|
| EDUOPS-FR-064 | The system shall define and enforce block identity generation, namespace, clone, split, merge, and tombstone rules. | Fixtures preserve comment, feedback, export, validation, and evidence bindings through template cloning, update, reorder, split/merge, and deletion. |
| EDUOPS-FR-065 | The system shall define schema/storage migration rules for editor documents, operation journals, assets, and manifests. | Migration fixtures upgrade an older schema, reject unsafe downgrade, quarantine failed migration, and preserve hashes/audit records. |
| EDUOPS-FR-066 | The system shall define Git inclusion, `.gitignore`, LFS, and privacy handling for canonical files, journals, autosaves, indexes, and assets. | Repository-policy fixture verifies which artifacts are tracked, ignored, LFS-managed, local-only, encrypted, or exportable by privacy class. |

| ID | Non-functional requirement | Acceptance criterion |
|---|---|---|
| EDUOPS-NFR-027 | Markdown projection shall be deterministic but explicitly derived from JSON, with loss/warning records for typed blocks not fully representable in Markdown. | Projection manifest lists lossless/lossy/fallback blocks with severity and the JSON source hash. |
| EDUOPS-NFR-028 | Local storage of student-private drafts, journals, indexes, and assets shall preserve privacy across device lock, archive, withdrawal, and cleanup flows. | Fixture verifies at-rest protection setting, lifecycle deletion trigger, and no instructor/global search exposure for `student_private` content. |

## 13. Implementation executability requirements

| ID | Requirement | Rationale | Acceptance |
|---|---|---|---|
| EDUOPS-FR-067 | The product baseline shall define P0 implementation contracts before source-code implementation: technology stack decision, process topology/IPC, module/package layout, canonical domain IDL, internal API contract, configuration contract, and credential-reference/storage contract. | Prevents developers from making untraceable architecture, configuration, and security-boundary decisions inside code. | All P0 documents, including `configuration-contract.md` and `credential-storage-contract.md`, exist, are linked from INDEX, and are referenced by the roadmap before SLICE-A implementation. |
| EDUOPS-FR-068 | The implementation plan shall proceed through local vertical slices with fake/local adapters before live GitHub or live evaluation actions. | Preserves no-live-action-before-fixture-gates discipline. | SLICE-A/B fixture gates pass before any live connector is enabled. |
| EDUOPS-NFR-029 | Implementation contracts shall be machine-checkable where practical, including schemas, API signatures, fixture manifests, adapter contracts, and deterministic test harness commands. | Enables autonomous agents and developers to implement without guessing. | P0/P1 documents include schemas/signatures/commands or explicitly justify manual-only controls. |

## 14. Implementation requirements gap-register controls

| ID | Requirement | Rationale | Acceptance |
|---|---|---|---|
| EDUOPS-FR-069 | The implementation requirements gap register shall maintain explicit status for each implementation candidate: candidate, promoted-document-required, promoted, merged, or superseded. | Prevents already-promoted P0 items from being mistaken for unresolved product decisions. | Register rows for P0 candidates include status and promotion trace. |
| EDUOPS-FR-070 | The system baseline shall define local fixture gates and privacy-safe deterministic fixture data before any live GitHub, live classroom, or official evaluation side effect. | Makes no-live-action-before-fixture-gates enforceable rather than advisory. | `EDUOPS-CVR-001` and `EDUOPS-CVR-002` are promoted into STD/V&V before SLICE-A. |
| EDUOPS-FR-071 | The implementation baseline shall promote code-authoritative state-machine transition tables, deterministic sync-conflict resolution, and authoritative time semantics before student workspace/submission slices. | These rules affect eligibility, late status, conflict handling, and audit dispute reconstruction. | P0/P1 documents or SRS sections cover transition tables, sync conflict rules, and time service semantics. |
| EDUOPS-FR-072 | The implementation baseline shall define adapter contracts for assets/binaries, secret storage, notifications, search indexing, Korean IME composition, schema migration, audit taxonomy, and error taxonomy before the affected feature slices. | Prevents cross-cutting implementation details from being hidden in unrelated modules. | Gap register maps each adapter/taxonomy to a candidate ID and target control document. |

## 15. Configuration requirements baseline

| ID | Requirement | Rationale | Acceptance |
|---|---|---|---|
| EDUOPS-FR-073 | The system shall define a controlled configuration contract for app-default, system, user, course, repository, and runtime-override scopes. | Developer implementation depends on deterministic settings precedence and override authority. | [Configuration Contract](../02-design-planning/configuration-contract.md) defines scopes, precedence, protected keys, schema versioning, migration, and audit behavior. |
| EDUOPS-FR-074 | The system shall resolve workspace roots through a deterministic algorithm and support zero-config first-run boot without live external services. | SLICE-A local skeleton needs repeatable boot and safe fixture setup. | Configuration fixture proves first-run boot and invalid-root handling. |
| EDUOPS-FR-075 | The system shall store credential references only and shall keep raw credentials in OS-protected credential storage. | GitHub-first and future connector flows require a testable no-raw-secret boundary. | [Credential Storage Contract](../02-design-planning/credential-storage-contract.md) and secret-leak fixtures pass. |
| EDUOPS-FR-076 | The system shall expose backend-owned configuration and credential APIs rather than allowing the UI or workers to mutate settings directly. | Configuration affects product behavior, evidence, security, and adapter modes. | [Internal API Contract](../02-design-planning/internal-api-contract.md) includes configuration and credential command/query signatures. |
| EDUOPS-FR-077 | The system shall configure evaluation, export, rendering, offline/sync, diagnostics/audit, and update-channel profiles through controlled key families. | These profiles affect safety, evidence, privacy, and reproducibility. | Configuration fixture plan covers the key families before affected implementation slices. |
| EDUOPS-NFR-030 | Configuration merge, validation, migration, invalid-key handling, and offline isolation shall be verifiable through deterministic fixtures. | Prevents hidden defaults and accidental live actions. | [Configuration Fixture Plan](../03-verification-validation/configuration-fixture-plan.md) defines `CFG-FIX-001..007` and STD-078..083. |
| EDUOPS-NFR-031 | Protected configuration changes shall produce audit events and shall respect role/scope authorization, including student default-deny for credential and protected policy keys. | Configuration is a controlled design input during operation. | Access-control and configuration fixtures record allowed/denied `ConfigSet` and credential queries. |


## 16. Traceability and TDD readiness baseline

| ID | Requirement | Rationale | Acceptance |
|---|---|---|---|
| EDUOPS-FR-078 | The product baseline shall maintain a controlled requirements traceability matrix that maps every SRS functional and non-functional requirement to design/interface anchors, STD or fixture tests, implementation slice, and evidence status. | Requirement IDs alone are insufficient for ISO traceability and developer handoff. | [Requirements Traceability Matrix](requirements-traceability-matrix.md) exists, is linked from README/INDEX, and marks each SRS requirement as Exact, Grouped, or Gap before implementation. |
| EDUOPS-FR-079 | Each implementation task shall start from a selected requirement ID and exact test/fixture anchor before production behavior is written. | Enables TDD and prevents developers from coding from broad grouped requirements. | Implementation task evidence records requirement ID, design anchor, test command, expected RED failure, GREEN pass result, and refactor/regression command. |
| EDUOPS-NFR-032 | TDD evidence shall preserve RED--GREEN--REFACTOR order for production behavior changes unless a controlled exception is approved. | A passing test written after code does not prove that the test can catch missing behavior. | Commit or evidence package includes failing-test evidence before the implementation change and passing-test evidence after the minimal implementation. |
| EDUOPS-NFR-033 | A grouped requirement shall not be treated as coding-ready until it is narrowed to an exact fixture/test command and observable pass/fail artifact. | Group-level STD/V&V coverage is useful for planning but too broad for TDD execution. | RTM row status is Exact or a slice-specific test card exists before coding starts. |


## 17. Downstream design and test outputs

The SRS baseline is now expanded into downstream design and test controls. [Software Design Description](../02-design-planning/software-design-description.md) §14 defines the SRS-derived component/design response, [Interface Design Description](../02-design-planning/interface-design-description.md) §9 defines the SRS-derived logical interface anchors, [Software Test Description](../03-verification-validation/software-test-description.md) §17 defines exact SRS-derived test anchors, and [Requirements Traceability Matrix](requirements-traceability-matrix.md) v0.2.0 indexes every SRS FR/NFR row against those anchors. Production implementation shall not start from this SRS alone; it shall start from an RTM row, design/interface anchor, exact test/fixture command, and RED--GREEN evidence record.


## 18. Claude review of downstream design/test baseline

Claude read-only review on 2026-05-14 found no baseline contradiction in the SRS-derived SDD/IDD/STD/RTM package, but classified the downstream expansion as grouped planning coverage rather than executable TDD readiness. Production code shall not start broadly from the SRS-derived tables alone. Selected SLICE-A rows shall first be converted into executable test cards with fixture path, command, requirement-specific RED failure, GREEN evidence, and no-live-action assertion. See [Claude SRS-derived design and STD review](../00-research-analysis/claude-srs-design-std-review.md).


## 19. GitHub adapter implementation requirements baseline

The GitHub-first product direction in `EDUOPS-FR-023`, `EDUOPS-FR-024`, and `EDUOPS-FR-059` is promoted into implementation-level requirements for the GitHub adapter. This section does not authorize live GitHub actions; it defines the controlled requirements that must be satisfied before GitHub integration source-code work proceeds beyond fake/local fixtures.

| ID | Requirement | Rationale | Acceptance |
|---|---|---|---|
| EDUOPS-FR-080 | The system shall implement GitHub integration only as a controlled clone-source adapter with fake-local, mock-http, and separately approved clone-readonly modes. | The current product baseline needs GitHub only to clone approved repositories; broader GitHub provisioning or administration would add unnecessary side effects. | [GitHub Adapter Specification](../02-design-planning/github-adapter-specification.md) defines clone-only modes, and fake-local remains the default until a clone-readonly gate is approved. |
| EDUOPS-FR-081 | The GitHub adapter shall expose only clone-related operations: clone configuration validation, clone planning, read-only repository clone/fetch, and clone evidence query. | Developers need exact boundaries so they do not implement repository creation, branch protection, push, webhook, or collaborator-management modules. | The adapter specification lists clone-only operations, inputs, outputs, side-effect class, result envelope fields, and audit requirements. |
| EDUOPS-FR-082 | The GitHub clone adapter shall consume credential references and credential status only; raw tokens or secrets shall not pass through configuration, UI payloads, logs, result envelopes, exports, diagnostics, or Git files. | Private repository clone may require credentials, but the adapter must remain no-raw-secret by design. | `GH-FIX-004`/`STD-089` prove no raw credential fixture value leaks through adapter-visible artifacts. |
| EDUOPS-FR-083 | The GitHub clone adapter shall distinguish planned, cloned, and verified clone evidence and shall not treat a local clone as submission, provisioning, or remote confirmation. | Clone evidence is an input/evidence fact, not a GitHub-side workflow mutation or official submission state. | `GH-FIX-005`/`STD-090` prove clone-state evidence remains separate from submission/workflow state. |
| EDUOPS-FR-084 | GitHub mutation shall be out of scope for the current baseline; repository creation, push, branch/tag creation, collaborator invitation, branch protection mutation, webhook/check-run writes, and archive/access-disable actions shall be blocked. | Prevents accidental implementation of live GitHub management when the intended integration is clone-only. | `GH-FIX-006`/`STD-091` blocks any non-clone GitHub operation even when credentials or network are configured. |
| EDUOPS-NFR-034 | GitHub clone behavior shall be verifiable through deterministic fake-local and mock-http fixtures before any approved clone-readonly connector action. | TDD and no-live-action controls require repeatable tests that do not depend on live GitHub. | `GH-FIX-001..002`/`STD-086..087` pass with exact commands and no network calls except the local mock server. |
| EDUOPS-NFR-035 | GitHub repository and visible clone source identifiers shall avoid raw student identifiers or visible PII unless a controlled exception is approved. | Repository URLs/names may be visible in logs or evidence. | `GH-FIX-003`/`STD-088` blocks raw student IDs and requires pseudonymous controlled IDs in clone evidence. |
| EDUOPS-NFR-036 | GitHub clone adapter errors shall classify authentication, scope denial, rate limit, outage/timeout, privacy-policy violation, non-clone-operation denial, and live-action gate denial with retriable/terminal behavior. | Retry, queueing, and user-visible messages must be consistent while keeping mutation paths denied. | The adapter specification defines required error classes and retry behavior, and mock-http fixtures cover them. |
