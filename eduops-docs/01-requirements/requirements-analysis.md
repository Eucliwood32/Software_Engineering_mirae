---
title: HISYS EduOps Platform Requirements Analysis
document_id: SWENG-EDUTECH-REQ-ANALYSIS
version: 1.2.1
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Requirements Analysis

## 1. Analysis conclusion

The clarified baseline makes HISYS EduOps Platform a focused Windows and Linux desktop product for C/C++ programming courses. The main product value is not replacing an LMS; it is replacing file-upload assignment operation with a controlled GitHub-backed workflow that preserves source assignment integrity, student lifecycle management, student workspace isolation, reproducible submission snapshots, and C/C++ automated-evaluation evidence.

The requirements should therefore be organized as a **student-centered EduOps workflow**, not only as assignment storage. Student management, mode separation, and end-to-end usage scenarios starting from student registration are now first-class requirements.

## 2. Product boundary analysis

| Boundary | Accepted decision | Implication |
|---|---|---|
| Client form | Windows and Linux desktop only | Design, packaging, notifications, filesystem permissions, local toolchain integration, and platform webview/runtime evidence should be optimized for both supported desktop OS families. |
| Repository backend | GitHub first | Initial repository provisioning, branch protection, token handling, identity binding, and audit evidence must assume GitHub APIs and Git remotes. |
| Future backend | Self-hosted Git later | A backend abstraction is needed, but the first release should not overgeneralize beyond GitHub. |
| Assignment domain | C/C++ code | Problem packages must include starter source, headers, build files, tests, compiler profiles, runtime constraints, and evaluation evidence. |
| LMS | Excluded | Roster/grade exchange should be controlled import/export only; no LMS connector, grade-passback, LTI, or LMS dependency. |
| Student management | Included | Roster, GitHub identity binding, lifecycle status, workspace provisioning, submission eligibility, and feedback release need explicit data models. |
| Operating modes | Explicitly separated | Role/mode-specific permissions and distinct student/instructor UI context must prevent accidental high-impact actions. |

## 3. Operational workflow analysis

### 3.1 Course/admin workflow

1. Create course, term, section, instructor/TA roster, due policy, and GitHub organization/repository context.
2. Import roster from controlled CSV/JSON file.
3. Bind course roster identities to GitHub identities with approval and duplicate detection.
4. Provision per-student workspace and repository/branch permissions.
5. Monitor student lifecycle states and handle status changes, withdrawals, late allowances, and archive.

### 3.2 Instructor workflow

1. Create or update a C/C++ Problem Bank package.
2. Define compiler/toolchain profile, test fixtures, static-analysis rules, rubric, and release policy.
3. Create an Assignment Instance from a specific Problem Bank version.
4. Publish/update the assignment through GitHub-backed repositories.
5. Review student progress, submissions, compile/test evidence, rubric feedback, and audit records.
6. Release feedback/grades through controlled no-LMS export and in-app feedback visibility.

### 3.3 Student workflow

1. Open the Windows or Linux desktop app and authenticate/bind to course identity.
2. Receive assigned workspace after the student record is Bound and Provisioned.
3. Read assignment files in read-only assignment area.
4. Edit C/C++ files only in the writable workspace area.
5. Save/checkpoint through UI; app creates Git commits.
6. Submit; app records assignment version, student snapshot SHA, eligibility/late state, and GitHub confirmation state.
7. Receive synchronization notices and released feedback.

### 3.4 TA/evaluation workflow

1. Inspect student dashboard by course, assignment, status, submission, evaluation result, and feedback-release state.
2. Pull or receive student submission snapshot.
3. Execute configured C/C++ build/test/static-analysis profile under limits.
4. Store compiler version, command profile, logs, outputs, timeout/resource result, and feedback evidence.
5. Flag failures for TA/instructor review and feedback release.

## 4. Scenario-driven analysis

The primary scenario chain begins with student registration rather than assignment submission:

```text
Course setup
→ roster import
→ GitHub identity invitation/claim
→ identity approval and duplicate check
→ workspace/repository namespace provisioning
→ assignment publication and student activation
→ checkpoint work
→ submission with queued/pushed/confirmed states
→ automated C/C++ evaluation
→ TA/instructor review
→ feedback release
→ no-LMS export and archive
```

This scenario chain defines the minimum coherent product experience. It also creates verification gates: a student cannot become Active before binding/provisioning evidence exists, and a submission cannot be treated as confirmed until GitHub confirmation exists.

## 5. Mode analysis

| Mode | Why it is separate | Critical evidence/control |
|---|---|---|
| Instructor authoring | Changes source assignment baseline. | Problem version, publish approval, audit record. |
| Course operation/admin | Changes roster, identity, permissions, and eligibility. | Roster hash, identity binding approval, status-change audit. |
| Student workspace | Student creates protected work and submits. | Workspace isolation, commit trail, submission confirmation. |
| TA review | Reviews evidence without changing baselines. | Review notes, rubric state, no unauthorized source/roster mutation. |
| Evaluation runner | Executes untrusted C/C++ code. | Sandbox/resource limits, compiler metadata, immutable input SHA. |
| Offline/local | Allows local work under connectivity limits. | Queued vs confirmed state distinction. |
| Synchronization | Moves assignment updates and student commits. | No silent overwrite; sync log and conflict/notice record. |
| Review/audit | Supports dispute resolution and export. | Read-only audit trail and reproducible SHA evidence. |
| Recovery/manual override | Repairs exceptional cases. | Actor, reason, scope, approval, before/after state. |

## 6. Derived requirement groups

| Group | Derived requirements |
|---|---|
| Fast controlled UI and rendering | Next.js is conditionally acceptable; design must select an efficient UI toolkit/editor/rendering component, preserve desktop/platform packaging policy, local workspace path rules, notification support, file permission behavior, credential storage, offline behavior, and correct graph/table/image rendering. |
| Course/student management | Course/section metadata, roster import/versioning, student registry, GitHub identity binding, lifecycle states, status changes, workspace provisioning, student dashboard. |
| GitHub operations | Repository provisioning, branch/namespace rules, protected assignment source, student submission branches, permission isolation, token references, API error handling, offline/online sync. |
| C/C++ evaluation | Compiler profile, standard selection, build script format, unit-test harness, static-analysis profile, timeout/memory/process limits, artifact capture. |
| Mode/permission control | Mode-specific allowed/blocked actions, scoped access-control decisions, visible mode/context, high-impact confirmations, authorization decision records, manual override gates. |
| No-LMS operations | Roster import/export, grade export, audit export, course/section metadata without LMS dependency. |
| Audit/provenance | Git SHA, assignment version, actor/action records, student lifecycle events, evaluation input snapshot, review outcomes, override records, export records. |

## 7. Recommended initial release slice

The first implementation slice should be narrow and evidence-heavy:

1. Fast controlled UI shell with local course fixture, conditional Next.js/web-stack candidate if desired, and graph/table/image rendering fixtures.
2. Controlled course and student registry fixture.
3. Roster import and GitHub identity-binding workflow.
4. GitHub-backed Problem Bank and Assignment Instance repositories.
5. One C/C++ assignment template using a single approved compiler profile.
6. Student workspace creation, checkpoint commit, submission snapshot, and submission confirmation state.
7. Instructor/TA student dashboard and evaluation run with compile + unit-test fixture.
8. Controlled CSV roster import and grade/evaluation export.

## 8. Acceptance criteria for requirements closure

- A Windows/Linux packaging decision and supported OS versions/distributions are approved.
- A student registry schema and lifecycle state machine are approved.
- A mode/permission matrix and access-control authorization model are approved and fixture-tested.
- A GitHub repository/branch/permission model is documented and fixture-tested.
- C/C++ evaluation can compile, run tests, capture logs, and contain unsafe programs under resource limits.
- LMS exclusion is confirmed in architecture, configuration, and V&V evidence.
- Student work preservation is demonstrated across at least one instructor assignment update.

## 9. Analysis item status

| ID | Status | Item | Closure / why it matters |
|---|---|---|---|
| EDUOPS-OQ-001 | Partially closed | Select Windows versions and desktop framework. | Desktop framework closed by `EDUOPS-DEC-047`; exact supported Windows versions remain open for packaging/support policy. |
| EDUOPS-OQ-002 | Closed for beta | Select first C/C++ toolchain profile. | `EDUOPS-DEC-048` selects LLVM/Clang local advisory worker for beta; official grading profile remains gated. |
| EDUOPS-OQ-003 | Closed for beta | Decide evaluation execution location. | `EDUOPS-DEC-048` selects local advisory worker for beta; official runner/sandbox remains a later approval item. |
| EDUOPS-OQ-004 | Closed for baseline | Define GitHub identity binding. | Controlled by roster schema, identity policy, and GitHub topology/token documents. |
| EDUOPS-OQ-005 | Closed for baseline | Define GitHub organization/repository topology. | Controlled by GitHub topology/token model and repository workflow documents. |
| EDUOPS-OQ-006 | Closed for baseline | Define mandatory student registry fields and privacy rules. | Controlled by roster schema and identity policy; implementation fixtures still need exact validation data. |
| EDUOPS-OQ-007 | Open | Define allowed manual override actions and approvers. | Exceptional academic operations need control without corrupting evidence. |

## 10. Classroom benchmark implications

The GitHub Classroom / Google Classroom benchmark confirms that EduOps should optimize for a hybrid value proposition rather than generic LMS replacement:

- borrow GitHub Classroom's repository-native assignment, starter-code, pull-request feedback, and autograding evidence patterns;
- borrow Google Classroom's course, roster, coursework, rubric/grade, and submission-lifecycle convenience patterns;
- preserve EduOps-specific Windows/Linux desktop, local-first, no-LMS, GitHub-first, C/C++ evaluation, student-workspace isolation, and controlled evidence-ledger baseline.

Derived requirement families are `EDUOPS-FR-036..041` and `EDUOPS-NFR-015`. Their intent is to reduce instructor/admin/TA/student workload while strengthening traceability rather than adding a Google Classroom or LMS connector.

## 11. Differentiation: student knowledge system and report export

The new differentiation baseline shifts EduOps from "Git-backed assignment management" alone to "Git-backed assignment management plus knowledge-work execution".

Design implications:

- GitHub Classroom remains strong for repository distribution and autograding, but it does not normally create a student's structured knowledge system as a first-class artifact.
- Google Classroom remains strong for course/coursework/submission/grade lifecycle, but it is not Git-native and does not preserve code/evidence/knowledge links at repository depth.
- EduOps should therefore make the student workspace a learning workspace: `workspace/**` for work products and `knowledge/**` for notes, decisions, experiments, references, and reflections.
- DOCX and HWP/HWPX export are required differentiation features for report-style Korean university workflows, but exports are derived outputs. Canonical evidence remains Git SHA, editor JSON, Markdown, metadata, and export manifest.

Derived requirement families are `EDUOPS-FR-042..046` and `EDUOPS-NFR-016..017`.

## 12. Claude review gap-closure analysis

The Claude read-only review confirmed that the product direction is strong but that the differentiation features now require controlled closure. The highest-priority analysis outcomes are:

1. `knowledge/**` must be treated as first-class topology and submission/evidence scope, not a convenience folder.
2. Editor implementation must be selected through a fixture-gated trade study, and canonical block schema must remain independent of vendor internals.
3. HWPX-first export and legacy HWP converter-dependent behavior must be explicitly controlled through manifest and fidelity criteria.
4. Official C/C++ evaluation must distinguish advisory student pre-checks from authoritative runner evidence.
5. Student lifecycle, submission state, and assignment release state are separate state families and shall not be mixed in dashboards or APIs.
6. GitHub Classroom benchmark KPIs remain fixture targets until GitHub API feasibility and token/topology controls pass.
7. Roster CSV/JSON schema and identity-binding fields must be defined before student-management efficiency can be validated.

These outcomes close `EDUOPS-OQ-003` and `EDUOPS-OQ-006` at the design-input level by adding controlled profile documents. Together with `EDUOPS-DEC-047` and `EDUOPS-DEC-048`, the beta stack, beta C/C++ toolchain, and beta evaluation location are closed for implementation planning; exact Windows version support and final official runner approval remain separate controlled decisions.

## 13. Notion-style storage analysis

A Notion-style editor cannot be specified only as UI behavior. EduOps needs a controlled persistence model because grading, feedback, export, and Git evidence depend on stable block identity. The accepted storage baseline is hybrid: canonical editor JSON as the single structured source of truth, deterministic derived Markdown projection for human-readable Git review, operation journals for autosave/recovery, rebuildable local indexes for speed, content-addressed assets for evidence, and Git checkpoint commits for durable milestones.

## 14. Storage gap-closure analysis

Claude review identified that the storage model must distinguish source-of-truth status from human-readable projection status. The accepted refinement is: editor JSON is the single structured source of truth; Markdown is a deterministic derived projection governed by a pinned profile and a projection manifest. Operation journals, autosaves, local indexes, and search caches are local recovery/performance aids unless materialized into a canonical revision and checkpoint. Block identity, schema migration, tombstone retention, asset privacy, and Git inclusion policies must be controlled before editor implementation.

## 15. Implementation executability analysis

Codex and Claude review found that EduOps has adequate requirements and policy coverage but lacks code-start contracts. The analysis therefore separates design-input maturity from implementation executability. Product code shall start only after P0 contracts reduce ambiguity for technology stack, process topology, package layout, domain IDL, and internal APIs.
