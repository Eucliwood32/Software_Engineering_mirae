---
title: HISYS EduOps Platform Risk Register
document_id: SWENG-EDUTECH-RISK
version: 2.4.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Risk Register

| ID | Risk | Cause | Impact | Initial controls | Traceability |
|---|---|---|---|---|---|
| EDUOPS-R-001 | Student work is overwritten during assignment synchronization. | Assignment update logic crosses into workspace area. | Loss of student work and trust. | Separate assignment/workspace paths; sync tests; backup before update. | FR-015, CON-003 |
| EDUOPS-R-002 | Students or tools modify assignment originals. | Permission model or UI boundary failure. | Academic integrity and grading inconsistency. | Read-only assignment area; blocked edit path; audit event. | FR-012, CON-003 |
| EDUOPS-R-003 | Git complexity harms adoption. | Users are not Git experts. | Poor usability and course disruption. | UI-driven workflow; hide CLI details; usability validation. | NFR-002, CON-005 |
| EDUOPS-R-004 | Automated C/C++ evaluation accesses unauthorized files or host resources. | Weak sandbox, process controls, or path validation. | Privacy/security breach or host instability. | Constrained execution profile; timeout/memory/process/path negative tests. | FR-017, NFR-005, NFR-007, CON-004 |
| EDUOPS-R-005 | Submission evidence is incomplete or ambiguous. | Missing assignment version, SHA, compiler metadata, student state, or evaluation profile. | Grading disputes cannot be resolved. | Machine-readable submission/evaluation/student-state evidence schema. | FR-014, FR-018, NFR-003 |
| EDUOPS-R-006 | Cross-platform desktop packaging fragments across Windows and Linux versions, toolchains, and webview runtimes. | Windows 10/11 differences, Linux distribution/display-session differences, compiler availability, path/encoding behavior. | Increased support cost and inconsistent behavior. | Select supported Windows versions, supported Linux distributions/session types, canonical C/C++ toolchain, and packaging V&V matrix. | NFR-001, CON-001, CON-009 |
| EDUOPS-R-007 | Student private data or GitHub credentials leak through logs, exports, repositories, or evaluation artifacts. | Overbroad logging/export or raw-token storage. | Legal, institutional, and account-security harm. | Privacy review; token-reference design; redaction and leak tests. | NFR-004, FR-021, CON-010, CON-011 |
| EDUOPS-R-008 | Assignment update creates confusing conflicts. | Instructor changes overlap with student assumptions. | Student errors and support burden. | Change notification with affected files/reason/action. | FR-016 |
| EDUOPS-R-009 | GitHub dependency disrupts classroom operation. | GitHub outage, API/rate limits, authentication failure, network restriction. | Students cannot sync/submit or instructors cannot evaluate. | Offline/local commits; retry queue; operational runbook; future self-hosted Git profile. | FR-023, FR-024, FR-028, NFR-006, CON-007 |
| EDUOPS-R-010 | LMS exclusion creates administrative friction. | Institutions expect roster/grade LMS workflows. | Adoption barrier. | Controlled CSV/JSON import/export; explicit no-LMS expectation in sales/onboarding. | FR-001, FR-002, FR-022, NFR-008, CON-008 |
| EDUOPS-R-011 | C/C++ undefined behavior, infinite loops, or platform-specific code makes evaluation unreliable. | Student code uses unsafe memory, nondeterminism, OS-specific APIs. | False grading results or evaluator instability. | Toolchain profile, resource limits, deterministic fixtures, manual review flag. | FR-017, FR-018, NFR-007 |
| EDUOPS-R-012 | GitHub identity does not match course roster identity. | Students use personal accounts or multiple accounts. | Misattributed submissions and grading disputes. | Identity-binding review, duplicate detection, roster mapping evidence, instructor approval gate. | FR-003, FR-004, FR-021 |
| EDUOPS-R-013 | Student lifecycle state is wrong or stale. | Roster changes, withdrawals, late exceptions, or archive transitions are not modeled. | Incorrect access, grading eligibility errors, privacy exposure. | Student lifecycle state machine, status-change audit, dashboard consistency tests. | FR-005, FR-008, NFR-009 |
| EDUOPS-R-014 | Operating mode confusion causes high-impact mistakes. | UI/backend does not clearly separate instructor, admin, student, TA, evaluator, sync, audit, and recovery modes. | Unauthorized publish, submit, grade release, export, or override. | Mode/permission matrix, visible context, confirmation gates, backend enforcement. | FR-025, FR-026, FR-027, NFR-010, CON-012 |
| EDUOPS-R-015 | Manual override corrupts evidence or creates unfair treatment. | Emergency repair lacks controlled reason/approval/before-after records. | Academic dispute and audit failure. | Override record schema and approval gate. | FR-029, CON-013 |

## Scenario-specific risk note

The usage scenarios in [Usage scenarios](../02-design-planning/usage-scenarios.md) are now part of risk analysis. In particular, SCN-003/004 mitigate identity mismatch risk, SCN-007/008 mitigate offline/confirmation ambiguity, SCN-009 mitigates untrusted C/C++ execution risk, SCN-013 mitigates uncontrolled override risk, and SCN-014 mitigates no-LMS export/privacy risk.

| EDUOPS-R-016 | Document/editor model diverges from Git/Markdown evidence. | Notion-style editor JSON and Markdown export are not kept equivalent. | Submission review or reproducibility becomes unreliable. | Round-trip tests, canonical Markdown export, editor JSON schema, submission snapshot checks. | FR-031, FR-032 |
| EDUOPS-R-017 | Branch/path permission model is bypassed. | Client or server accepts commits modifying `assignment/**` or tampering with metadata. | Assignment integrity and grading evidence fail. | Server-side validation, protected branches, path policy tests, metadata hash checks. | FR-012, FR-023, FR-030 |
| EDUOPS-R-018 | UI responsiveness fails under class-scale Git/document operations. | UI performs Git sync, diff rendering, validation, or evaluation-trigger operations synchronously, or selected native/web stack is too heavy for class-scale operation. | Student/instructor adoption fails, classroom operation stalls, and users bypass controlled workflows. | Conditional UI-stack gate; asynchronous job model; virtualized lists/diffs; responsiveness performance tests; reject Next.js/web candidate if budgets fail. | NFR-002, NFR-011, DEC-016 |
| EDUOPS-R-019 | Graph/table/image artifacts are rendered incorrectly or lost in evidence/export. | Platform-specific UI renderers diverge, asset paths fail silently, large tables/graphs degrade, or editor JSON and Markdown/export representations differ. | Student submissions, instructor review, and grading evidence become incomplete or misleading. | Controlled rendering profile; graph/table/image fixtures; fallback source/snapshot evidence; path validation; export/submission consistency tests. | FR-031, FR-033, NFR-012, DEC-017 |
| EDUOPS-R-020 | Student and instructor/professor capabilities are mixed in one confusing or unsafe UI. | Role surfaces are not separated, UI hiding is used without backend permission enforcement, or TA/admin scopes inherit excessive authority. | Students may see restricted controls, instructors may perform high-impact actions in the wrong context, and audit/academic integrity can fail. | Role-separated UI model; least-privilege navigation; backend permission checks; role fixtures; high-impact confirmation and audit. | FR-025, FR-034, NFR-010, NFR-013, DEC-018 |
| EDUOPS-R-021 | A custom rendering engine consumes excessive effort or produces unreliable rendering. | Product builds a new renderer before proving mature HTML5/SVG/Canvas/WebGL substrates are insufficient. | Schedule slips, rendering defects increase, export/evidence divergence appears, and educational workflow features are delayed. | Use mature renderers first; define rendering adapter contract; fixture-gate any custom engine; require build-vs-use decision record and cost gate. | FR-033, NFR-012, DEC-017, DEC-019, DEC-020 |
| EDUOPS-R-022 | Implementation starts from live GitHub/evaluation integrations before local fixture gates pass. | Team jumps from documents to live connectors without local vertical-slice evidence. | Credentials, student data, repository state, or grading evidence may be mishandled. | Local-only productization roadmap; STD fixture gates; no live external action until harness passes. | STD, Roadmap, DEC-021 |
| EDUOPS-R-023 | Access-control policy is incomplete or bypassed. | UI hiding is mistaken for authorization, scopes are missing, worker/service calls bypass checks, or direct-call routes ignore role/context. | Unauthorized access to submissions, grades, identity records, Git refs, feedback release, exports, or override operations. | Default-deny scoped authorization model; authorization decision records; direct-call bypass tests; protected resource inventory; high-impact action gates. | FR-035, NFR-014, ACM, STD-026..STD-028, DEC-022 |
| EDUOPS-R-024 | Benchmark-driven optimization accidentally expands scope into LMS/Google Classroom integration. | Team copies Google Classroom API concepts as live connectors instead of using them as reference patterns. | No-LMS product boundary weakens, privacy/auth risks increase, and implementation scope expands before fixture evidence exists. | Decision DEC-023; controlled benchmark docs; live-integration promotion gate; local fixtures before external side effects. | FR-036..041, NFR-015, DEC-023 |
| EDUOPS-R-025 | DOCX/HWP export diverges from canonical Git/Markdown/editor evidence. | Export converter loses formatting, code blocks, images, tables, Korean text, or metadata. | Submitted report output may misrepresent student work or review evidence. | Treat DOCX/HWP as derived output; export manifest with source SHA, tool profile, hash, warnings; fixture tests for DOCX/HWP/HWPX. | FR-044, FR-045, FR-046, NFR-016, DEC-024 |
| EDUOPS-R-026 | Student knowledge artifacts leak private/course-restricted information or blur academic-integrity boundaries. | Knowledge promotion/export lacks scope, redaction, citation/source tracking, or policy controls. | Privacy exposure, unfair reuse, or unclear authorship. | Student ownership/scope rules; redaction; citation/source fields; instructor policy; export/privacy fixtures. | FR-043, NFR-017, DEC-024 |

| EDUOPS-R-027 | Editor behavior is underspecified or diverges from evidence/export requirements. | Notion-style editor is treated as generic rich text without block schema, validation, checkpoint, permission, or round-trip controls. | Student submissions, knowledge artifacts, exports, and review evidence become inconsistent or unsafe. | Controlled editor profile; block schema; autosave/checkpoint; permission tests; JSON/Markdown/export round-trip fixtures. | FR-047..051, NFR-018..019, DEC-025 |
| EDUOPS-R-028 | Editor usability/performance failure disrupts classroom use. | Korean IME, large tables, diagrams, images, code blocks, logs, or Git diffs block the UI or lose input. | Students abandon the workflow or lose work during assignment execution. | Korean IME fixtures; large document/table/image performance tests; autosave/history recovery; controlled degradation warnings. | FR-048, FR-051, NFR-018 |

## 2. Claude review gap-closure risks

| ID | Risk | Cause | Impact | Initial controls | Traceability |
|---|---|---|---|---|---|
| EDUOPS-R-029 | `knowledge/**` is not integrated into submission/evidence topology. | Knowledge artifacts added after repository model baseline. | Grading evidence and privacy boundaries become ambiguous. | Knowledge topology and submission policy; submission metadata tests. | FR-052, NFR-020, DEC-026 |
| EDUOPS-R-030 | Student knowledge artifacts violate privacy or academic-integrity expectations. | Reuse, retention, visibility, or promotion policy is vague. | Student harm, plagiarism disputes, or legal exposure. | Student knowledge policy; redaction and visibility fixtures. | FR-058, NFR-017, DEC-031 |
| EDUOPS-R-031 | Editor stack cannot satisfy Korean IME, block schema, export, accessibility, or performance fixtures. | Toolkit selected before trade study evidence. | Rework or unusable Notion-style workflow. | Editor stack trade study; block schema; spike fixtures. | FR-053, FR-054, NFR-021, DEC-027 |
| EDUOPS-R-032 | HWP/HWPX export path is technically fragile or license-constrained. | Legacy HWP/proprietary tooling and converter drift. | Korean institutional report workflow fails. | HWPX-first strategy; converter profiles; export fidelity fixtures. | FR-055, NFR-022, DEC-028 |
| EDUOPS-R-033 | Official C/C++ evaluation is unsafe or non-reproducible. | Runner location/sandbox not controlled. | Security incidents or grading disputes. | Evaluation execution profile and sandbox evidence. | FR-056, DEC-029 |
| EDUOPS-R-034 | State labels are conflated across lifecycle, submission, and assignment release. | Dashboard/API vocabulary uses mixed states. | Users misinterpret queued/pushed/confirmed or assignment update status. | Canonical state machine profile and transition tests. | FR-057, DEC-030 |
| EDUOPS-R-035 | Classroom benchmark KPI is not feasible under GitHub API/org constraints. | Rate-limit, token, topology, and outage analysis incomplete. | Overpromised course-operation efficiency. | GitHub API feasibility and topology/token model. | FR-059, NFR-015, DEC-032 |
| EDUOPS-R-036 | Roster schema or identity binding causes misattribution. | Missing field/encoding/duplicate/approval policy. | Wrong grading identity and privacy exposure. | Roster schema and identity policy. | FR-060, DEC-033 |
| EDUOPS-R-037 | Performance claims remain qualitative. | No seed P50/P95 budgets or measurement fixtures. | Product feels slow or cannot pass pilot gate. | Performance budget and measurement records. | NFR-023, DEC-034 |
| EDUOPS-R-038 | Git repositories grow too large due to checkpoints/reports/assets/logs. | Generated artifacts and repeated snapshots stored without policy. | Slow Git operations, storage cost, archive difficulty. | Repository retention and LFS policy. | FR-046 |

## 3. Notion-style storage risks

| ID | Risk | Cause | Impact | Initial controls | Traceability |
|---|---|---|---|---|---|
| EDUOPS-R-039 | Editor UI state diverges from canonical stored evidence. | Vendor editor state, local cache, JSON snapshot, and Markdown projection are not synchronized. | Submission/export/review may use wrong content. | Document storage architecture; deterministic materialization; storage V&V. | FR-061, NFR-025, DEC-035 |
| EDUOPS-R-040 | Operation journal or index corruption causes data loss or misleading recovery. | Autosave journal and rebuildable indexes are not clearly separated from canonical evidence. | Students lose work or recover wrong block versions. | Operation journal replay tests; canonical snapshot checkpoints; index rebuild tests. | FR-062, FR-063, NFR-026, DEC-035 |

## 4. Storage gap-closure risks

| ID | Risk | Cause | Impact | Initial controls | Traceability |
|---|---|---|---|---|---|
| EDUOPS-R-041 | Markdown projection is mistaken for the sole source of truth. | Derived projection called canonical without loss profile. | Typed block semantics may be lost in review/export. | JSON source-of-truth wording, projection profile, manifest warnings. | FR-061, NFR-027, DEC-036 |
| EDUOPS-R-042 | Block IDs break during clone/update/split/merge/delete. | No stable lineage and tombstone rules. | Comments, feedback, export bindings, and evidence point to wrong content. | Block identity model and lineage fixtures. | FR-064, NFR-026, DEC-037 |
| EDUOPS-R-043 | Schema/storage migration corrupts evidence. | Version mismatch or unsafe downgrade. | Old submissions become unreadable or hashes become unverifiable. | Migration policy, quarantine, hash-preserving manifests. | FR-065, DEC-038 |
| EDUOPS-R-044 | Local journals/indexes/autosaves leak private student work. | Local caches store student-private content without lifecycle controls. | Privacy breach on shared/classroom devices. | Local protection, cleanup, search filters, Git ignore policy. | FR-066, NFR-028, DEC-039 |

## 9. Implementation executability risks

| ID | Risk | Cause | Impact | Mitigation | Trace |
|---|---|---|---|---|---|
| EDUOPS-R-045 | Implementation starts with unresolved technology stack and process topology. | Team moves from controlled docs directly into code without P0 HOW-level contracts. | Architecture decisions become hidden in code and later traceability is weak. | Use the accepted technology stack decision record and process topology/IPC contract before SLICE-A. | IMPL-GAP, Roadmap, DEC-040, DEC-047..048 |
| EDUOPS-R-046 | Developers or agents implement incompatible domain schemas and adapters. | No canonical domain IDL, internal API contract, package layout, or adapter contracts. | Editor, Git, storage, export, and evaluation components fail to integrate. | Use canonical domain IDL, internal API contract, module layout, and fake/local fixture harness before source-code slices. | IMPL-EXEC, STD-068..070, DEC-041 |

## 10. Gap-register control risks

| ID | Risk | Cause | Impact | Mitigation | Trace |
|---|---|---|---|---|---|
| EDUOPS-R-047 | Implementation candidates are misread because promoted, candidate, merged, and superseded states are not distinguished. | Gap register lacks explicit status governance. | Developers may encode temporary architecture decisions in code or ignore required documents. | Maintain register status fields and synchronize with SRS/IDD/STD promotions. | EDUOPS-FR-069, IMPL-REQ-GAP |
| EDUOPS-R-048 | Live actions occur before objective fixture gates exist. | Verification candidates are not promoted into V&V/STD. | GitHub, evaluation, or classroom side effects may bypass fixture evidence controls. | Enforce the fixture corpus and harness plan for `EDUOPS-CVR-001` and `EDUOPS-CVR-002` before SLICE-A. | EDUOPS-FR-070, STD-071..074, DEC-049 |
| EDUOPS-R-049 | Cross-cutting adapters leak privacy or create hidden coupling. | Secret, asset, notification, search, IME, audit, and error-code contracts are left to implementation modules. | Hard-to-test privacy leaks, inconsistent UX, and integration failures. | Promote P1/P2 adapter and taxonomy candidates before affected slices. | EDUOPS-FR-072, CIR-011..015 |

## 11. Working demonstration risks

| ID | Risk | Cause | Impact | Mitigation | Trace |
|---|---|---|---|---|---|
| EDUOPS-R-050 | A screen-only prototype is mistaken for working EduOps behavior. | Demo lacks backend state, Git evidence, validation logs, or artifact manifests. | Stakeholders overestimate implementation maturity and miss integration defects. | Use DEMO-1 evidence package acceptance before working claims. | EDUOPS-DEC-045, STD-075..077 |
| EDUOPS-R-051 | A sandbox connector demo is mistaken for production readiness. | Demo level and live-action boundary are not labeled. | Premature live integration, privacy exposure, or unsupported deployment claims. | Label DEMO-0..3 explicitly and require `live_external_action=false` for DEMO-1/2. | EDUOPS-DEC-046 |

## 12. Configuration contract risks

| ID | Risk | Cause | Impact | Mitigation | Trace |
|---|---|---|---|---|---|
| EDUOPS-R-052 | Configuration behavior is nondeterministic across machines, courses, or repositories. | Configuration scopes, precedence, workspace-root resolution, and migration are not controlled. | Developers implement incompatible defaults; classroom behavior differs across users; evidence hashes cannot be reproduced. | Configuration contract, deterministic merge fixture, effective-config hash, safe invalid-config behavior. | EDUOPS-CFR-013, CFR-014, CVR-005, CVR-008 |
| EDUOPS-R-053 | Credentials leak through configuration, logs, Git files, exports, or diagnostics. | Raw secrets are stored as settings or adapter logs. | Account compromise, privacy breach, and institutional adoption failure. | Credential storage contract, OS-protected credential references, secret-leak scan, student default-deny. | EDUOPS-CFR-015, CNFR-006, CNFR-011, CVR-006 |
| EDUOPS-R-054 | Offline/local fixture mode accidentally performs live GitHub or network calls. | Offline configuration and adapter gates are incomplete. | No-live-action-before-fixture-gates is violated and student/repository data may be exposed. | Offline configuration key, adapter-call log, zero-network fixture gate. | EDUOPS-CFR-020, CVR-009, DEC-055 |

## 10. SRS-derived design/test traceability risks

| Risk ID | Risk | Cause | Impact | Mitigation | Trace |
|---|---|---|---|---|---|
| EDUOPS-R-056 | SDD, IDD, STD, and RTM diverge from SRS. | Downstream documents are updated manually after SRS changes. | Developers may implement stale interfaces or tests that no longer prove requirements. | Treat SDD §14, IDD §9, STD §17, and RTM as synchronized controlled outputs; run RTM coverage checks before implementation commits. | EDUOPS-FR-078, STD-084 |
| EDUOPS-R-057 | TDD becomes nominal because exact test anchors exist but fixture commands are not executable. | Test-design rows are mistaken for implemented tests. | Passing documentation checks may be confused with behavior validation. | Require RED--GREEN command/output evidence before production code is accepted. | EDUOPS-FR-079, EDUOPS-NFR-032, STD-085 |


| EDUOPS-R-058 | Grouped SRS-derived anchors are mistaken for executable TDD readiness. | SDD/IDD/STD/RTM tables contain one row per requirement but many rows still share grouped anchors and generic expected-RED text. | Production code may start without real RED--GREEN evidence. | Mark RTM rows as grouped planning coverage, require executable SLICE-A test cards, and preserve Claude review disposition. | CLAUDE-SRS-DESIGN-002, EDUOPS-NFR-032, STD-085 |


| EDUOPS-R-059 | GitHub integration is implemented directly from high-level SRS intent without adapter-level requirements. | `EDUOPS-FR-023` and `EDUOPS-FR-024` define direction but not exact adapter operations, gates, retry/rate-limit behavior, or audit fields. | Live side effects, credential leakage, or non-reproducible GitHub behavior. | Require GitHub adapter specification and `GH-FIX-*` executable TDD gates before implementation. | EDUOPS-CIR-006, STD-086..091 |


## GitHub adapter SRS promotion note

SRS §19 reduces `EDUOPS-R-059` by making GitHub adapter requirements explicit, but risk remains until `GH-FIX-*` executable tests exist.


| EDUOPS-R-060 | GitHub adapter design is implemented without preserving the application-core state boundary. | Adapter details are translated directly into code without respecting core-owned authorization, audit, and state promotion. | Queued/pushed/confirmed states or live-action gates could be bypassed. | Use [GitHub Adapter Software Design Description](../02-design-planning/github-adapter-software-design-description.md) and require core-mediated adapter calls in `GH-SLICE-*` tests. | EDUOPS-FR-080..084, EDUOPS-NFR-034..036 |


| EDUOPS-R-061 | Ralph-style implementation loop starts before executable test cards and fixture harness are concrete. | Agent loop starts from grouped RTM/STD planning anchors and incomplete harness commands. | Agent may invent requirements, write code without RED/GREEN evidence, or bypass no-live-action gates. | Run `RALPH-DOC-LOOP-001` first; require executable SLICE-A/GH-SLICE-0 test cards, harness schema, and build/dev baseline before product-code loop. | RALPH-REVIEW, STD-085, RTM |


| EDUOPS-R-062 | Ralph-loop closure artifacts are treated as approval for broad implementation. | Test cards and fixture contracts are misread as full implementation readiness. | Agents may expand from SLICE-A/GH-SLICE-0 into editor, runner, export, or live GitHub without review. | Restrict first implementation loop to `TC-SLICE-A-001..003` and `TC-GH-000`; require re-review before expanding scope. | RALPH-CLOSURE, DEC-062 |


| EDUOPS-R-063 | GitHub clone-only boundary is accidentally expanded during implementation. | Prior broader adapter wording or developer assumptions lead to repository creation, push, collaborator, branch protection, webhook/check-run, or admin features. | Scope creep creates external side effects and privacy/security risks not intended by the baseline. | SRS §19, GitHub adapter spec, SDD, IDD, STD, and test cards now require clone-only behavior and block non-clone operations before external request. | GITHUB-CLONE-ONLY, DEC-063 |
