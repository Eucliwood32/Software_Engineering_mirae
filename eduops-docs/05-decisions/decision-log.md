---
title: HISYS EduOps Platform Decision Log
document_id: SWENG-EDUTECH-DEC
version: 2.4.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Decision Log

## 1. Baseline decisions

| ID | Date | Decision | Status | Rationale | Affected docs |
|---|---|---|---|---|---|
| EDUOPS-DEC-001 | 2026-05-12 | HISYS EduOps Platform is a desktop application; web and mobile app delivery are excluded from the current baseline. | Accepted | User explicitly constrained composition to desktop app only. | README, SRS, CON, DDP, VVP, Risk |
| EDUOPS-DEC-002 | 2026-05-12 | Git-backed workflow is a core product mechanism for save, revision, submission, and evidence, not merely an implementation option. | Accepted | Initial idea defines Git workflow as differentiator from file-upload LMS. | SRS, Concept, VVP, Risk |
| EDUOPS-DEC-003 | 2026-05-12 | Problem Bank, Assignment Instance, Student Workspace, Assignment Synchronization, and Automated Evaluation are initial core entities/capabilities. | Accepted | User provided these as initial idea components. | SRS, Concept, DDP |
| EDUOPS-DEC-004 | 2026-05-12 | Assignment originals are read-only to students and student work is isolated in student-specific workspace areas. | Accepted | Protects source assignments and supports reproducible grading. | SRS, CON, VVP, Risk |
| EDUOPS-DEC-005 | 2026-05-12 | The target OS baseline is Windows only. | Revised by DEC-OS-001 | Superseded after user updated the target to Windows and Linux desktop on 2026-05-14. | README, SRS, Requirements Analysis, CON, DDP, VVP, Risk, DEC-OS-001 |
| EDUOPS-DEC-006 | 2026-05-12 | Repository backend sequence is GitHub first, self-hosted Git later. | Accepted | User selected GitHub first and later self-hosted Git. | README, SRS, Requirements Analysis, CON, Concept, DDP, VVP, Risk |
| EDUOPS-DEC-007 | 2026-05-12 | C/C++ code assignments are the initial automated-evaluation domain. | Accepted | User selected C/C++ code. | README, SRS, Requirements Analysis, CON, Concept, DDP, VVP, Risk |
| EDUOPS-DEC-008 | 2026-05-12 | LMS integration is excluded from the current baseline. | Accepted | User explicitly excluded LMS. | README, SRS, Requirements Analysis, CON, Concept, DDP, VVP, Risk |
| EDUOPS-DEC-009 | 2026-05-12 | Supported platform boundary and the exact UI framework/editor/rendering component remain open. | Partially closed by DEC-047 and DEC-OS-001 | Desktop-first scope is accepted, Windows/Linux OS target is accepted, and beta stack is selected in the technology stack decision record; exact supported Windows versions and Linux distributions remain open. | SRS, Requirements Analysis, DDP, VVP, Risk, UI Baseline, Tech Stack DR, DEC-OS-001 |
| EDUOPS-DEC-010 | 2026-05-12 | Canonical C/C++ toolchain and evaluation location remain open. | Closed by DEC-048 | Beta advisory toolchain/location are now selected; official grading remains gated by approved runner/sandbox profile. | SRS, Requirements Analysis, DDP, VVP, Risk, Tech Stack DR |
| EDUOPS-DEC-011 | 2026-05-12 | Student management is a first-class product capability covering roster import, GitHub identity binding, lifecycle status, workspace provisioning, progress visibility, feedback release, and archive controls. | Accepted | User identified student-management content as necessary. | README, SRS, Requirements Analysis, Requirements Breakdown, CON, Concept, DDP, VVP, Risk |
| EDUOPS-DEC-012 | 2026-05-12 | The product shall be separated into explicit operating modes with mode-specific permissions and evidence gates. | Accepted | User identified the need for multiple modes. | README, SRS, Requirements Analysis, Requirements Breakdown, CON, Concept, DDP, VVP, Risk |
| EDUOPS-DEC-014 | 2026-05-12 | End-to-end usage scenarios shall begin with student registration and proceed through identity binding, provisioning, activation, checkpointing, submission, evaluation, review, feedback release, export, and archive. | Accepted | User requested usage scenarios starting from student registration. | README, SRS, Requirements Analysis, Usage Scenarios, DDP, VVP, Risk |
| EDUOPS-DEC-015 | 2026-05-12 | The product core is a Git-backed, branch-based, document-first Notion-style assignment management system; C/C++ is retained as an evaluation profile rather than the sole product model. | Accepted | User provided prior requirements/design defining document-first outputs, assignment bank/version/instance/workspace/submission branch/snapshot chain, repository structures, permission model, APIs, document model, and validation checks. | README, SRS, Concept, Repository Workflow, Data API Document Model, DDP, VVP, Risk |
| EDUOPS-DEC-016 | 2026-05-12 | Next.js or web UI technology is conditionally acceptable if it satisfies the desktop/platform product boundary and passes rendering, evidence, offline, role-separation, security, package, and performance gates. | Revised accepted | User clarified that Next.js is acceptable; the real concern is whether graph/table/image rendering and related behavior work reliably. | README, SRS, Data API Document Model, UI Baseline, Rendering Engine Strategy, DDP, VVP, Risk |
| EDUOPS-DEC-017 | 2026-05-12 | Later platform-specific UI implementations are acceptable, but graph, table, and image rendering must be treated as a first-class controlled capability with consistent evidence/export behavior. | Accepted | User clarified that platform-specific UI divergence is acceptable; the key product risk is rendering quality for graph, table, and image artifacts. | README, SRS, UI Baseline, Rendering Profile, Data API Document Model, DDP, VVP, Risk |
| EDUOPS-DEC-018 | 2026-05-12 | Student and instructor/professor users shall have different UI surfaces and feature sets by default, with TA and admin/operator scopes separately permissioned. | Accepted | User identified that students and professors need different UI and functions. This reduces complexity for students and improves safety/control for instructor operations. | README, SRS, Role UI Model, UI Baseline, Requirements Breakdown, VVP, Risk |
| EDUOPS-DEC-019 | 2026-05-12 | EduOps shall prefer mature rendering substrates such as HTML5/CSS/SVG/Canvas/WebGL with a controlled rendering adapter before building a new rendering engine. | Accepted | User asked whether a new rendering engine would be better. Current analysis favors fixture-gated reuse first because graph/table/image correctness, evidence snapshots, and product workflow matter more than owning a low-level renderer. | Rendering Profile, Rendering Engine Strategy, SRS, DDP, VVP, Risk |
| EDUOPS-DEC-020 | 2026-05-12 | A reusable rendering capability is strategically valuable, but investment shall start with rendering contract, adapter SDK, fixture suite, and evidence snapshot pipeline before any full custom engine. | Accepted | Cost analysis estimates adapter MVP at 4-8 person-months, reusable core at 12-24 person-months, full custom renderer at 60-120 person-months, and production full engine at 108-216 person-months. | Rendering Engine Strategy, Rendering Cost Analysis, DDP, Risk |
| EDUOPS-DEC-021 | 2026-05-12 | EduOps completion shall proceed through a local-only vertical slice before live GitHub or live evaluation side effects. | Accepted | User asked to refocus on completing EduOps. The next practical completion baseline is SDD/IDD/STD/UI/RBAC/roadmap plus a local fixture MVP gate. | SDD, IDD, STD, UI Specs, RBAC, Roadmap, VVP, Risk |
| EDUOPS-DEC-022 | 2026-05-12 | Access control is a first-class product baseline: protected operations require scoped authorization decisions beyond role-separated UI. | Accepted | User identified that user permissions/access control are needed. EduOps must prevent UI, direct-call, worker, repository, and override bypasses. | Access Control Model, SRS, SDD, IDD, STD, RBAC, VVP, Risk |
| EDUOPS-DEC-013 | 2026-05-12 | Exact student registry fields, manual override authority, and detailed mode UI labels remain open. | Open | Requires privacy and operational review before implementation. | SRS, Requirements Breakdown, DDP, VVP, Risk, Role UI Model |
| EDUOPS-DEC-023 | 2026-05-13 | GitHub Classroom and Google Classroom shall be used as benchmark/reference systems to optimize student-management and course-management efficiency, not as live integrations in the current baseline. | Accepted | User asked to benchmark Git Classroom/Google Classroom for efficiency optimization; this preserves no-LMS and GitHub-first/local-first boundaries while capturing best-practice patterns. | Benchmark Analysis, Optimization Plan, README, INDEX, SRS, Requirements Analysis, DDP, VVP, Risk |
| EDUOPS-DEC-024 | 2026-05-13 | EduOps differentiation shall include Notion-style assignment execution, student-owned knowledge-system creation, and controlled DOCX/HWP/HWPX export. | Accepted | User clarified that differentiation should include Notion-style assignment performance, DOCX/HWP export, and each student's own knowledge system. | Student Knowledge Export Profile, README, INDEX, SRS, Requirements Analysis, Data API Document Model, Student UI, Instructor UI, Rendering Profile, VVP, STD, Risk |
| EDUOPS-DEC-025 | 2026-05-13 | The Notion-style editor shall be treated as a core controlled product capability with explicit block, autosave, validation, permission, Korean editing, and round-trip requirements. | Accepted | User correctly identified that the current knowledge/export differentiation requires formal editing requirements. | Editing Requirements Profile, README, INDEX, SRS, Data API Document Model, Student UI, Instructor UI, DDP, VVP, STD, Risk |

## 2. Claude review gap-closure decisions

| ID | Date | Decision | Status | Rationale | Affected docs |
|---|---|---|---|---|---|
| EDUOPS-DEC-026 | 2026-05-13 | `knowledge/**` shall be first-class student-owned topology with explicit sync, submission, visibility, and privacy rules. | Accepted | Claude review found the knowledge workspace was not fully integrated into repository/submission evidence. | Knowledge topology, Repository Workflow, SRS, V&V, Risk |
| EDUOPS-DEC-027 | 2026-05-13 | Editor toolkit selection shall be fixture-gated, with a vendor-neutral canonical block schema. | Accepted | Editor is core product capability and cannot rely on hidden vendor state. | Editor Trade Study, Block Schema, SRS, V&V, Risk |
| EDUOPS-DEC-028 | 2026-05-13 | HWPX shall be the preferred controlled Korean document profile; legacy HWP is converter-dependent derived output. | Accepted | HWP/HWPX is a differentiator but must not replace canonical evidence or silently lose content. | HWP Export Strategy, Export Fidelity, SRS, Risk |
| EDUOPS-DEC-029 | 2026-05-13 | Official C/C++ grading evidence shall require an approved runner/sandbox profile; student local runs are advisory. | Accepted | Evaluation location and sandbox were open and affect safety/reproducibility. | Evaluation Execution Profile, SRS, V&V, Risk |
| EDUOPS-DEC-030 | 2026-05-13 | Student lifecycle, submission state, and assignment release/update state shall be separate canonical state families. | Accepted | Prevents queued/pushed/confirmed and lifecycle state confusion in UI/API. | State Machine, SRS, UI, V&V, Risk |
| EDUOPS-DEC-031 | 2026-05-13 | Student knowledge artifacts shall follow explicit privacy, reuse, retention, and promotion policy. | Accepted | Knowledge-system value creates academic-integrity and privacy obligations. | Knowledge Policy, Access Control, SRS, Risk |
| EDUOPS-DEC-032 | 2026-05-13 | Classroom efficiency KPIs are fixture targets until GitHub API feasibility and topology/token controls pass. | Accepted | Benchmark goals must be grounded in GitHub API/org/rate-limit evidence. | GitHub Feasibility, GitHub Topology, SRS, Risk |
| EDUOPS-DEC-033 | 2026-05-13 | Roster CSV/JSON schema and GitHub identity-binding rules shall be controlled before pilot. | Accepted | Student-management efficiency depends on safe identity attribution. | Roster Schema, SRS, V&V, Risk |
| EDUOPS-DEC-034 | 2026-05-13 | Productization performance claims shall use seed P50/P95 budgets and fixture measurement records. | Accepted | Qualitative responsiveness is not enough for D5/D6 gates. | Performance Budget, V&V, Risk |

## 3. Notion-style storage decision

| ID | Date | Decision | Status | Rationale | Affected docs |
|---|---|---|---|---|---|
| EDUOPS-DEC-035 | 2026-05-13 | Notion-style editing shall use hybrid canonical storage: editor JSON snapshots, deterministic Markdown projections, operation journals, rebuildable local indexes, content-addressed assets, and Git checkpoints. | Accepted | User identified that Notion-like editing requires explicit save method and system data structures. | Storage Architecture, Block Schema, Data API, SRS, SDD, IDD, V&V, Risk |

## 4. Storage gap-closure decisions

| ID | Date | Decision | Status | Rationale | Affected docs |
|---|---|---|---|---|---|
| EDUOPS-DEC-036 | 2026-05-13 | Editor JSON is the structured source of truth; Markdown is a deterministic derived projection governed by a pinned profile and manifest warnings. | Accepted | Prevents typed Notion-style block semantics from being lost by treating Markdown as equal source. | Storage Architecture, SRS, V&V, Risk |
| EDUOPS-DEC-037 | 2026-05-13 | Block identity shall use stable scoped IDs with lineage and tombstone rules for clone, update, split, merge, and delete. | Accepted | Stable IDs are required for comments, feedback, export, validation, and evidence. | Block Schema, Storage Architecture, V&V, Risk |
| EDUOPS-DEC-038 | 2026-05-13 | Schema/storage migrations shall be explicit, hash-preserving, downgrade-rejecting, and quarantine-on-failure. | Accepted | Storage/schema version mismatch must not corrupt historical evidence. | Storage Architecture, Data API, V&V, Risk |
| EDUOPS-DEC-039 | 2026-05-13 | Local journals, autosaves, indexes, and private assets shall be local-only/protected by policy unless materialized into controlled evidence. | Accepted | Local recovery/cache data may contain student-private drafts and must not leak through Git/LFS/search/export. | Repository Retention, Knowledge Policy, SRS, V&V, Risk |

## 5. Implementation executability decisions

| ID | Date | Decision | Status | Rationale | Trace |
|---|---|---|---|---|---|
| EDUOPS-DEC-040 | 2026-05-13 | EduOps implementation shall not start production code until P0 HOW-level contracts are drafted: technology stack, process topology/IPC, module/package layout, domain IDL, and internal API contract. | Accepted | Codex and Claude review found that requirements are strong but executable implementation contracts are missing. | IMPL-GAP, IMPL-EXEC, DDP, Roadmap |
| EDUOPS-DEC-041 | 2026-05-13 | The implementation roadmap shall be reorganized around local vertical slices using fake/local adapters before live GitHub or official evaluation actions. | Accepted | Vertical slices reveal integration failures earlier and preserve no-live-action-before-fixture-gates. | IMPL-EXEC, Roadmap, VVP, STD-068..070 |

## 6. Gap-register improvement decisions

| ID | Date | Decision | Status | Rationale | Trace |
|---|---|---|---|---|---|
| EDUOPS-DEC-042 | 2026-05-14 | The implementation requirements gap register shall use explicit candidate status values and shall mark already-promoted P0 implementation-contract items as `promoted-document-required`. | Accepted | Claude review found that P0 candidates duplicated `EDUOPS-FR-067` unless their state is made explicit. | IMPL-REQ-GAP, CLAUDE-IMPL-REQ-GAP-REVIEW |
| EDUOPS-DEC-043 | 2026-05-14 | Local fixture gates, privacy-safe fixtures, state-machine transition tables, sync-conflict rules, and authoritative time semantics are elevated ahead of early implementation slices. | Accepted | These rules control live-action safety, submission eligibility, and dispute evidence. | EDUOPS-FR-070..071, STD-071..074 |
| EDUOPS-DEC-044 | 2026-05-14 | Secret storage, assets/binaries, notification, search, Korean IME, schema migration, audit taxonomy, and error-code taxonomy shall be tracked as explicit implementation candidates rather than hidden inside larger modules. | Accepted | Cross-cutting concerns need independently testable contracts. | EDUOPS-FR-072, IMPL-REQ-GAP |

## 7. Working demonstration decisions

| ID | Date | Decision | Status | Rationale | Trace |
|---|---|---|---|---|---|
| EDUOPS-DEC-045 | 2026-05-14 | EduOps working behavior shall be demonstrated through evidence-producing vertical slices, with DEMO-1 local fixture execution as the first credible working demonstration. | Accepted | A screen mockup alone cannot prove backend state, Git evidence, authorization, evaluation, or export behavior. | Working Demo Plan, STD-075..077 |
| EDUOPS-DEC-046 | 2026-05-14 | DEMO-1 and DEMO-2 demonstrations shall use fake/local adapters and report `live_external_action=false`; sandbox connectors are DEMO-3 only after explicit gate approval. | Accepted | Preserves no-live-action-before-fixture-gates and protects student/customer data. | Working Demo Plan, V&V, Risk |

## 8. P0 implementation contract decisions

| ID | Date | Decision | Status | Rationale | Trace |
|---|---|---|---|---|---|
| EDUOPS-DEC-047 | 2026-05-14 | The beta implementation stack is Tauri 2 desktop shell, Rust local backend, TypeScript UI, ProseMirror/Tiptap-style editor adapter, SQLite, libgit2-backed Git adapter, canonical-to-DOCX/HWPX exporter path, and Tauri Windows/Linux packaging. Windows uses WebView2; Linux uses the Tauri-supported system webview runtime. | Revised by DEC-OS-001 | Selects a coherent Windows/Linux desktop-first/local-first stack and closes the open UI/editor/platform part of `EDUOPS-DEC-009` together with `DEC-OS-001`. | Technology Stack Decision Record, EDUOPS-CFR-001, DEC-OS-001 |
| EDUOPS-DEC-048 | 2026-05-14 | The beta C/C++ execution baseline is LLVM/Clang in a local advisory worker; official grading is deferred until an approved sandbox runner profile exists. | Accepted | Provides implementable local fixture behavior while preserving the distinction between advisory local runs and official grading evidence, closing `EDUOPS-DEC-010` for beta. | Technology Stack Decision Record, Evaluation Execution Profile |
| EDUOPS-DEC-049 | 2026-05-14 | SLICE-A/B/C development shall be gated by privacy-safe deterministic local fixtures with artifact manifests and `live_external_action=false`. | Accepted | Makes the no-live-action baseline enforceable before implementation starts. | Fixture Corpus and Harness Plan, STD-072..073 |
| EDUOPS-DEC-050 | 2026-05-14 | Student lifecycle, assignment release/update, submission, sync conflict, and authoritative time behavior shall be implemented from code-authoritative transition tables. | Accepted | Prevents UI/API ambiguity around lifecycle, queued/pushed/confirmed, conflict, and late/deadline semantics. | State Machine Implementation Tables, STD-074 |
| EDUOPS-DEC-051 | 2026-05-14 | Development may begin with SLICE-A local skeleton after Claude and Codex both approved beta-directed readiness at evaluator loop 2. | Revised by DEC-052 | A later developer-perspective configuration review identified configuration as an additional P0 contract needed before coding. | Beta Readiness Evaluator Loop, P0 Contract Docs |

## 9. Configuration contract decisions

| ID | Date | Decision | Status | Rationale | Trace |
|---|---|---|---|---|---|
| EDUOPS-DEC-052 | 2026-05-14 | EduOps beta implementation shall not start until a controlled configuration contract exists for scopes, precedence, workspace-root resolution, schema/versioning, migration, protected keys, and audit. | Accepted | Claude developer-perspective review found configuration was scattered and not yet implementation-executable. | Configuration Contract, IMPL-REQ-GAP |
| EDUOPS-DEC-053 | 2026-05-14 | EduOps configuration shall store credential references only; raw credentials shall be kept in OS-protected credential storage and excluded from logs, Git files, exports, and diagnostics. | Accepted | GitHub-first operation and future connectors require testable secret boundaries before auth code. | Credential Storage Contract, STD-079 |
| EDUOPS-DEC-054 | 2026-05-14 | Configuration verification shall include deterministic merge, secret leak scan, schema migration, invalid-config safe behavior, and offline zero-network gates. | Accepted | Configuration behavior affects boot, adapters, evidence, and no-live-action safety. | Configuration Fixture Plan, STD-078..083 |


## 4. SRS-derived downstream design/test decisions

| ID | Date | Decision | Status | Rationale | Affected docs |
|---|---|---|---|---|---|
| EDUOPS-DEC-056 | 2026-05-14 | Use SRS v1.6.0 as the source for synchronized SDD §14, IDD §9, STD §17, and RTM v0.2.0 expansions. | Accepted | The implementation baseline needs explicit requirement-to-design-to-test traceability before source-code tasks. | SRS, SDD, IDD, STD, RTM, V&V |
| EDUOPS-DEC-057 | 2026-05-14 | Treat exact SRS-derived test anchors as design/test controls, not as proof of executable software behavior until RED--GREEN fixture evidence exists. | Accepted | TDD requires observed failing tests before production implementation. | STD, RTM, implementation plan |


| EDUOPS-DEC-058 | 2026-05-14 | Treat current SRS-derived SDD/IDD/STD/RTM rows as grouped planning coverage until executable test cards exist. | Accepted | Claude read-only review found no baseline contradiction but identified that apparent exact coverage was not yet TDD-executable. | Claude review, RTM, STD, V&V, Risk |


| EDUOPS-DEC-059 | 2026-05-14 | GitHub integration modules require a controlled adapter specification and executable gates before source-code implementation. | Accepted | Existing SRS states product direction but does not define adapter operations, mode gates, credential-reference flow, retry/rate-limit behavior, or TDD fixture commands. | GitHub implementation review, GitHub adapter spec, STD, V&V, Risk |


## GitHub adapter SRS promotion note

`EDUOPS-DEC-059` is implemented by promoting GitHub adapter implementation requirements into SRS §19 and downstream design/test traceability.


| EDUOPS-DEC-060 | 2026-05-14 | GitHub adapter detailed design is controlled as a separate SDD under the main SDD. | Accepted | The main SDD contained only a summary; implementation handoff needs component, state, data, error, security, and slice design. | GitHub adapter SDD, main SDD, module layout, process topology, V&V |


| EDUOPS-DEC-061 | 2026-05-14 | Ralph loop shall first close documentation/test-card readiness before product-code implementation. | Accepted | Claude and Codex both found the package insufficient for a product-code Ralph loop because executable test cards, fixture harness details, and build/dev baseline are incomplete. | Ralph loop readiness review, STD, RTM, implementation plan |


| EDUOPS-DEC-062 | 2026-05-14 | Ralph-loop closure package may support only a bounded fake/local implementation loop after review. | Accepted | The supplementation adds executable test cards, concrete fixtures, build/dev command baseline, and minimal Git/storage adapter contracts, but still excludes live GitHub, LMS, official evaluation, and beta-facing claims. | Test cards, fixture harness, build baseline, adapter specs |


| EDUOPS-DEC-063 | 2026-05-14 | GitHub integration is clone-only in the current baseline. | Accepted | EduOps shall use GitHub only as a read-only repository source for clone/fetch evidence; repository creation, push, collaborator/team mutation, branch protection, webhook/check-run writes, archive/access-disable, and GitHub administration are out of scope. | SRS §19, GitHub adapter spec/SDD, IDD, STD, clone-only review |
| EDUOPS-DEC-064 | 2026-05-16 | Live GitHub clone-readonly integration assumes a professor-provisioned course repository for which the professor/authorized course owner holds all required access authority. | Accepted | User set the product/gate assumption that the professor creates the repository and holds the access authority needed for live clone-readonly integration. This narrows the first live integration target to read-only clone/fetch evidence from that authorized repository while preserving credential-reference, approval, audit, and user-executed live-run controls. | GitHub Topology, Clone-Readonly Approval UX Spec, M7 Clone-Readonly Evidence, Ralph |
| EDUOPS-DEC-065 | 2026-05-16 | Live GitHub credentials, remotes, and external Git execution are user-managed; EduOps receives already authorized repository location inputs and runs only within the approved local/clone boundary. | Accepted | User clarified that live GitHub, credentials, and remotes are handled outside EduOps automation. For professor use, roster plus GitHub repository URL are supplied by CSV and EduOps may clone those listed repositories under the controlled clone-only path. For student use, the student clones their own repository first and runs EduOps from that local checkout. | GitHub Topology, Clone-Readonly Integration Point Spec, Clone-Readonly Approval UX Spec, Ralph |

## 10. Blocker resolution decisions

| ID | Date | Decision | Status | Rationale | Trace |
|---|---|---|---|---|---|
| EDUOPS-DEC-066 | 2026-05-20 | Resolve the queue-end blocker by authorizing Ralph/Hermes to continue only with local-safe documentation/control and fixture-local blocker-resolution increments, starting with the D6 rule 7 schema-extension path. | Accepted | User requested blocker resolution after `EDUOPS-DEC-DESKTOP-D6-RULE-6-TRACE-COMPLETE`; this converts the stop into bounded local-safe authority without authorizing live desktop launch, credentials, remotes, host installs, GitHub API calls, or DEMO-1 claims. | Blocker Resolution Authority, Ralph, D6 Evidence Shape Spec |
| EDUOPS-DEC-067 | 2026-05-21 | Authorize Ralph/Hermes to perform a local-safe documentation/control pass for the M3 editor adapter bridge specification. | Accepted | User approved the next local-safe planning/spec work after `NEXT: stop preflight`; this supersedes the prior M3 bridge deferral only for specification authoring and preserves no runtime, no live UI, no credential, no remote, and no DEMO-1 boundaries. | M3 Bridge Spec Authority, Editor Adapter Bridge Spec, M3 Bridge Spec Blocker, Ralph |
