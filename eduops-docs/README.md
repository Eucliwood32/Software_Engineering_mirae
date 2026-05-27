---
title: HISYS EduOps Platform Pre-Development Package
document_id: SWENG-EDUTECH-README
version: 2.4.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# HISYS EduOps Platform

HISYS EduOps Platform is a **Windows and Linux desktop** EduTech product concept that combines Git-based version control with a document-centered C/C++ programming-assignment environment. It is explicitly **not** a web app, **not** a mobile app, and **not** an LMS integration product in the current baseline.

## Accepted baseline

- Delivery form: desktop-first application. Next.js or web UI technology may be used when packaged/controlled as a desktop or platform-specific UI, but standalone web/mobile delivery is not the current product baseline.
- Education service focus: document-first/Notion-style assignment authoring, Notion-style assignment execution, student-owned knowledge-system creation, DOCX/HWP report export, distribution, synchronization, submission, automatic validation/evaluation, feedback, student management, and auditability. C/C++ remains an evaluation profile rather than the whole product boundary.
- UI direction: efficient role-separated UI with asynchronous Git/validation/evaluation jobs. Next.js is conditionally acceptable if rendering, offline, evidence, role, and performance contracts pass.
- Usage scenarios start with **student registration**: roster import, GitHub identity claim/approval, workspace provisioning, assignment activation, checkpointing, submission, evaluation, review, feedback release, export, and archive.
- Repository backend sequence: GitHub first; self-hosted Git later as a planned extension profile.
- LMS integration: excluded from the current baseline. Controlled local import/export may support rosters, grades, and audit records, but no LMS connector is planned.
- Student management is a first-class product capability: roster import, GitHub identity binding, lifecycle status, workspace provisioning, progress visibility, feedback release, and archive controls.
- Operating modes are explicit: instructor authoring, course/admin operation, student workspace, TA review, evaluation runner, offline/local, synchronization, review/audit, and recovery/manual override. Student and instructor/professor users have different UI surfaces and feature sets by default, and protected operations require scoped access-control decisions beyond UI hiding.
- Git-backed workflow is part of the product core, not an implementation detail. The controlled concept chain is Problem Bank → Assignment Bank Item → Assignment Version → Assignment Instance → Student Workspace → Submission Branch → Submission Snapshot.
- Graph, table, and image rendering is a first-class capability for authoring, student work, review, feedback, and evidence/export flows.
- Assignment originals remain immutable/read-only for students; student work is isolated in student-specific workspaces.
- Submission snapshots preserve the assignment version and student work state.
- GitHub Classroom and Google Classroom are benchmark/reference systems for optimizing student-management and course-management efficiency; they are not promoted as live integrations in the current no-LMS baseline. EduOps differentiation is Notion-style assignment execution plus student knowledge-system formation and controlled DOCX/HWP export; therefore the editor is a core controlled product capability, not a generic text box.
- Requirements consistency review found no critical product-direction contradiction, but identified stale open-question/status rows and traceability cleanup items that should be corrected before declaring the draft implementation-stable.

## Document map

- [Requirements record](01-requirements/requirements-record.md)
- [Requirements analysis](01-requirements/requirements-analysis.md)
- [Implementation requirements gap register](01-requirements/implementation-requirements-gap-register.md)
- [Requirements breakdown structure](01-requirements/requirements-breakdown-structure.md)
- [Requirements traceability matrix](01-requirements/requirements-traceability-matrix.md)
- [Development constraints](01-requirements/development-constraints.md)
- [Classroom benchmark analysis](00-research-analysis/classroom-benchmark-analysis.md)
- [Claude implementation requirements gap review](00-research-analysis/claude-implementation-requirements-gap-review.md)
- [Claude configuration requirements review](00-research-analysis/claude-configuration-requirements-review.md)
- [Requirements consistency review](00-research-analysis/requirements-consistency-review.md)
- [SRS traceability and TDD readiness review](00-research-analysis/srs-traceability-tdd-readiness-review.md)
- [Beta readiness evaluator loop record](00-research-analysis/beta-readiness-evaluator-loop.md)
- [Claude design milestone analysis](00-research-analysis/claude-design-milestone-analysis.md)
- [Codex demo UI readiness analysis](00-research-analysis/codex-demo-ui-readiness-analysis.md)
- [Claude demo UI readiness validation](00-research-analysis/claude-demo-ui-readiness-validation.md)
- [Hisys codebase analysis](00-research-analysis/hisys-codebase-analysis.md)
- [Full source-inspection decision pass](00-research-analysis/full-source-inspection-decision-pass.md)
- [Design and development plan](02-design-planning/design-and-development-plan.md)
- [Service concept](02-design-planning/service-concept.md)
- [Git-backed Notion-style assignment concept](02-design-planning/git-backed-notion-assignment-concept.md)
- [Repository permission and assignment workflow](02-design-planning/repository-permission-workflow.md)
- [Data API and document model](02-design-planning/data-api-document-model.md)
- [Fast native desktop UI baseline](02-design-planning/fast-native-desktop-ui-baseline.md)
- [Graph table image rendering profile](02-design-planning/graph-table-image-rendering-profile.md)
- [Role-separated UI and feature model](02-design-planning/role-separated-ui-feature-model.md)
- [Rendering engine strategy](02-design-planning/rendering-engine-strategy.md)
- [Rendering engine cost and reuse analysis](02-design-planning/rendering-engine-cost-reuse-analysis.md)
- [Classroom efficiency optimization plan](02-design-planning/classroom-efficiency-optimization-plan.md)
- [Student knowledge system and export profile](02-design-planning/student-knowledge-export-profile.md)
- [Notion-style editing requirements profile](02-design-planning/notion-style-editing-requirements-profile.md)
- [Software design description](02-design-planning/software-design-description.md)
- [Interface design description](02-design-planning/interface-design-description.md)
- [Student UI workflow specification](02-design-planning/student-ui-workflow-spec.md)
- [Instructor UI workflow specification](02-design-planning/instructor-ui-workflow-spec.md)
- [Role permission matrix](02-design-planning/role-permission-matrix.md)
- [Access control and authorization model](02-design-planning/access-control-authorization-model.md)
- [Technology stack decision record](02-design-planning/technology-stack-decision-record.md)
- [Canonical domain IDL](02-design-planning/canonical-domain-idl.md)
- [Process topology and IPC contract](02-design-planning/process-topology-and-ipc-contract.md)
- [DEC-OS-001 Windows and Linux desktop target](02-design-planning/dec-os-001-windows-linux-desktop-target.md)
- [Desktop entrypoint dependency adoption decision specification](02-design-planning/desktop-entrypoint-dependency-adoption-decision-specification.md)
- [Desktop entrypoint dependency adoption authorized decision](02-design-planning/desktop-entrypoint-dependency-adoption-authorized-decision.md)
- [Desktop D6 user-observed launch evidence shape specification](02-design-planning/desktop-d6-launch-evidence-shape-specification.md)
- [Desktop IPC expansion specification](02-design-planning/desktop-ipc-expansion-specification.md)
- [Desktop fixture corpus manifest specification](02-design-planning/desktop-fixture-corpus-manifest-specification.md)
- [Desktop SLICE-A evidence summary source specification](02-design-planning/desktop-slice-a-evidence-summary-source-specification.md)
- [Blocker resolution authority](05-decisions/blocker-resolution-authority-2026-05-20.md)
- [M3 editor adapter bridge local-safe specification authority](05-decisions/m3-editor-bridge-local-safe-spec-authority-2026-05-21.md)
- [Editor adapter bridge specification](02-design-planning/editor-adapter-bridge-specification.md)
- [Editor adapter bridge TC-001 fixture source contract specification](02-design-planning/editor-adapter-bridge-tc-001-fixture-source-contract-specification.md)
- [Editor adapter bridge TC-002 fixture source contract specification](02-design-planning/editor-adapter-bridge-tc-002-fixture-source-contract-specification.md)
- [Editor adapter bridge TC-003 fixture source contract specification](02-design-planning/editor-adapter-bridge-tc-003-fixture-source-contract-specification.md)
- [Module and package layout](02-design-planning/module-and-package-layout.md)
- [Internal API contract](02-design-planning/internal-api-contract.md)
- [State machine implementation tables](02-design-planning/state-machine-implementation-tables.md)
- [Configuration contract](02-design-planning/configuration-contract.md)
- [Credential storage contract](02-design-planning/credential-storage-contract.md)
- [Productization roadmap](06-implementation/productization-roadmap.md)
- [Implementation milestones](06-implementation/implementation-milestones.md)
- [M0 source scaffold evidence](06-implementation/m0-source-scaffold-evidence.md)
- [M1 SLICE-A local skeleton evidence](06-implementation/m1-slice-a-local-skeleton-evidence.md)
- [M1A local UI shell prerequisite evidence](06-implementation/m1a-local-ui-shell-prerequisite-evidence.md)
- [M1A desktop gate closure evidence](06-implementation/m1a-desktop-gate-closure-evidence.md)
- [M2 configuration and credential reference evidence](06-implementation/m2-configuration-credential-evidence.md)
- [M3 editor adapter bridge specification gap closure](06-implementation/m3-bridge-spec-blocker.md)
- [M3 SLICE-B canonical document gate evidence](06-implementation/m3-slice-b-canonical-document-evidence.md)
- [M4 SLICE-C roster, identity, and workspace gate evidence](06-implementation/m4-slice-c-roster-identity-workspace-evidence.md)
- [M5 scoped submission and review authorization specification gap closure](06-implementation/m5-auth-spec-blocker.md)
- [M5 SLICE-D assignment publication, submission, and repository conflict gate evidence](06-implementation/m5-slice-d-assignment-submission-evidence.md)
- [M6 evaluation runner I/O contract specification gap closure](06-implementation/m6-runner-io-spec-blocker.md)
- [M6 evaluation runner I/O contract](02-design-planning/evaluation-runner-io-contract.md)
- [M6 SLICE-E advisory C/C++ runner gate evidence](06-implementation/m6-slice-e-advisory-cpp-runner-evidence.md)
- [M7 SLICE-F GitHub clone-only adapter gate evidence](06-implementation/m7-slice-f-github-clone-only-evidence.md)
- [M7 mock-http fixture replay gate evidence](06-implementation/m7-mockhttp-evidence.md)
- [GitHub clone-readonly integration-point boundary specification](02-design-planning/github-clone-readonly-integration-point-specification.md)
- [Clone-readonly human approval workflow UX specification](02-design-planning/clone-readonly-approval-workflow-ux-specification.md)
- [M7 clone-readonly integration-point gate evidence](06-implementation/m7-clone-readonly-evidence.md)
- [M7 clone-readonly approval workflow UX gate evidence](06-implementation/m7-approval-ux-evidence.md)
- [Professor CSV roster + repository URL intake specification](02-design-planning/professor-csv-intake-specification.md)
- [M7 professor CSV roster + repository URL intake gate evidence](06-implementation/m7-prof-csv-intake-evidence.md)
- [M7 professor CSV byte parser gate evidence](06-implementation/m7-prof-csv-intake-byte-evidence.md)
- [M7 approval UX predecessor reference integration gate evidence](06-implementation/m7-approval-ux-intake-link-evidence.md)
- [M7 professor CSV byte parser RFC 4180 grammar gate evidence](06-implementation/m7-prof-csv-intake-byte-rfc4180-evidence.md)
- [M7 professor CSV byte parser error-message redaction audit gate evidence](06-implementation/m7-prof-csv-intake-byte-error-msg-audit-evidence.md)
- [M7 approval UX predecessor block accessibility hardening gate evidence](06-implementation/m7-approval-ux-predecessor-a11y-harden-evidence.md)
- [Student pre-cloned local-checkout reader specification](02-design-planning/student-pre-cloned-local-checkout-reader-specification.md)
- [M7 student pre-cloned local-checkout reader gate evidence](06-implementation/m7-student-local-checkout-reader-evidence.md)
- [M7 student pre-cloned local-checkout reader post-construction evidence scan gate evidence](06-implementation/m7-student-local-checkout-reader-evidence-scan-evidence.md)
- [M7 student pre-cloned local-checkout reader READ_OUTSIDE_WORKSPACE guard gate evidence](06-implementation/m7-student-local-checkout-reader-read-outside-workspace-evidence.md)
- [Queue-end planning analysis](06-implementation/queue-end-planning-analysis.md)
- [M8 exporter implementation specification gap closure](06-implementation/m8-export-spec-blocker.md)
- [M8 SLICE-G export fixture gate evidence](06-implementation/m8-slice-g-export-fixture-evidence.md)
- [M1A desktop gate closure runbook](06-implementation/m1a-desktop-gate-closure-runbook.md)
- [Desktop app development plan](06-implementation/desktop-app-development-plan.md)
- [Desktop D6 user-observed launch capture runbook](06-implementation/desktop-d6-launch-capture-runbook.md)
- [Ralph milestone execution alignment](06-implementation/ralph-milestone-execution-alignment.md)
- [Milestone bootstrap package](milestone-bootstrap/index.md)
- [UI shell demonstration test cards](03-verification-validation/ui-shell-demo-test-cards.md)
- [Demonstration usage scenarios](03-verification-validation/demonstration-usage-scenarios.md)
- [Implementation readiness gap analysis](06-implementation/implementation-readiness-gap-analysis.md)
- [Implementation executability improvement plan](06-implementation/implementation-executability-improvement-plan.md)
- [Usage scenarios](02-design-planning/usage-scenarios.md)
- [Verification and validation plan](03-verification-validation/verification-validation-plan.md)
- [Software test description](03-verification-validation/software-test-description.md)
- [Fixture corpus and harness plan](03-verification-validation/fixture-corpus-and-harness-plan.md)
- [Configuration fixture plan](03-verification-validation/configuration-fixture-plan.md)
- [UI shell demonstration test cards](03-verification-validation/ui-shell-demo-test-cards.md)
- [Risk register](04-risk-management/risk-register.md)
- [Decision log](05-decisions/decision-log.md)

## ISO 9001 alignment

This package supports early design-and-development controls under ISO 9001 clauses 4, 6, 7, 8.3, 9, and 10. It is a draft pre-development package and is not yet an approved product baseline.

## Claude review gap-closure baseline

The 2026-05-13 Claude read-only review identified that the recent differentiation baseline requires additional controlled closure before implementation. This package now adds controlled profiles for:

- `knowledge/**` topology, synchronization, submission inclusion, privacy, and policy;
- editor stack trade study and canonical block schema;
- HWP/HWPX export strategy and export fidelity acceptance;
- C/C++ evaluation execution/sandbox profile;
- canonical state machines for student lifecycle, submission, and assignment release;
- GitHub API feasibility, GitHub topology/token model, roster/identity policy, performance budget, Korean text handling, accessibility, and repository retention.

Clarification: "Notion-style" means structured block-based assignment execution and knowledge-work UX. Live Google Docs/Notion-style multi-user co-editing is not part of the current baseline unless separately promoted.

## Notion-style storage baseline

Notion-style editing now has an explicit storage architecture. EduOps uses canonical editor JSON snapshots, deterministic Markdown projections, content-addressed assets, local operation journals, rebuildable indexes, and Git checkpoint commits. The editor UI is therefore not the source of truth; the controlled storage/evidence model is. See [Notion-Style Document Storage Architecture](02-design-planning/notion-style-document-storage-architecture.md).

## Storage gap-closure baseline

The storage baseline now distinguishes source of truth from projection: editor JSON is the structured source of truth; Markdown is a deterministic derived projection with a pinned profile and manifest warnings. Canonical JSON/Markdown/manifest/assets are durable evidence; local journals, autosaves, and indexes are recovery/cache structures unless materialized into a checkpoint. Block identity, schema migration, tombstone retention, asset privacy, and Git inclusion policy are controlled before editor implementation.

## Implementation executability gate

Codex and Claude advisory reviews concluded that EduOps has sufficient WHAT/WHY-level controlled requirements, but needs HOW-level implementation contracts before production code starts. The implementation gate now has P0 documents for technology stack, process topology, module/package layout, canonical domain IDL, internal API contracts, fixture gates, and state/time/conflict tables before SLICE-A local skeleton work begins. See [Implementation readiness gap analysis](06-implementation/implementation-readiness-gap-analysis.md), [Implementation executability improvement plan](06-implementation/implementation-executability-improvement-plan.md), [Fixture corpus and harness plan](03-verification-validation/fixture-corpus-and-harness-plan.md), and [State machine implementation tables](02-design-planning/state-machine-implementation-tables.md).

## Implementation requirements gap register v0.2

The implementation requirements gap register now distinguishes candidate, promoted-document-required, promoted, merged, and superseded items. It also adds Claude-identified CVR verification candidates and cross-cutting adapter/taxonomy candidates that must be promoted before the affected implementation slices.

## Traceability and TDD readiness baseline

A 2026-05-14 SRS traceability/TDD review found that the SRS is adequate as product-level design input, but not sufficient by itself for TDD implementation. The package now adds a controlled [Requirements traceability matrix](01-requirements/requirements-traceability-matrix.md), [SRS traceability and TDD readiness review](00-research-analysis/srs-traceability-tdd-readiness-review.md), `EDUOPS-FR-078..079`, `EDUOPS-NFR-032..033`, and `STD-084..085`. Implementation tasks must now link requirement ID, design anchor, test command, expected RED failure, GREEN evidence, and refactor/regression validation before coding.

## Configuration requirements baseline

The 2026-05-14 Claude developer-perspective review found that configuration requirements were still too scattered for beta implementation. The package now adds a controlled [Configuration contract](02-design-planning/configuration-contract.md), [Credential storage contract](02-design-planning/credential-storage-contract.md), and [Configuration fixture plan](03-verification-validation/configuration-fixture-plan.md). Configuration is now treated as product behavior covering hierarchy, workspace-root resolution, JSON schema/versioning, credential references, evaluation/export/rendering/offline/diagnostic/update profiles, API/IDL records, and fixture gates before SLICE-A implementation.

## Working demonstration baseline

EduOps should show that it works through controlled vertical-slice demonstrations, not through a screen mockup alone. The first credible demonstration is DEMO-1: a local fixture run that proves course creation, privacy-safe roster import, assignment provisioning, Notion-style editor save/projection, local Git checkpoint/submission evidence, advisory C++ evaluation, review evidence, and DOCX/HWPX derived export without live external actions. The concrete presenter-facing scenario set is defined in [Demonstration Usage Scenarios](03-verification-validation/demonstration-usage-scenarios.md). See [Working demonstration and evidence plan](03-verification-validation/working-demonstration-evidence-plan.md).


## Working demonstration UI readiness baseline

The 2026-05-14 Codex read-only review found that M0..M8 were sufficient for backend/evidence implementation but insufficient to guarantee a demonstrable UI because early gates did not require a Tauri/WebView2 shell, TypeScript UI build, IPC smoke, or captured UI evidence. The milestone sequence now adds M1A Desktop Shell Demonstration Slice and [UI Shell Demonstration Test Cards](03-verification-validation/ui-shell-demo-test-cards.md). Claude Code validated this correction as `PASS_WITH_FINDINGS`; the non-blocking findings are recorded in [Claude Demo UI Readiness Validation](00-research-analysis/claude-demo-ui-readiness-validation.md). See [Codex Demo UI Readiness Analysis](00-research-analysis/codex-demo-ui-readiness-analysis.md).

The 2026-05-14 Hisys codebase-domain run preserved the EduOps codebase analysis request and returned `needs_more_evidence` because the current Hisys codebase adapter does not yet execute a full source-inspection decision pass. The local advisory synthesis records that the repository is documentation/control-baseline ready for M0 scaffold work, but not build-ready or demo-executable because no Cargo workspace, Tauri shell, TypeScript UI, Rust crates, or fixture runner source exists yet. A follow-up [Full Source-Inspection Decision Pass](00-research-analysis/full-source-inspection-decision-pass.md) explicitly inspected the repository tree, required source paths, document anchors, links, JSON syntax, and executable prerequisites and returned `NO_GO_FOR_EXECUTABLE_UI_DEMO`; the next controlled increment remains M0. See [Hisys Codebase Analysis](00-research-analysis/hisys-codebase-analysis.md).

## SRS-derived design and STD baseline

SRS v1.6.0 is now expanded into synchronized downstream controls: SDD §14, IDD §9, STD §17, and RTM v0.2.0. These documents provide exact SRS-to-design-to-test anchors for all current FR/NFR rows. They are still design/test controls; implementation requires executable fixture commands and RED--GREEN evidence before production behavior is accepted.


## Claude SRS-derived design/STD review

[Claude SRS-derived design and STD review](00-research-analysis/claude-srs-design-std-review.md) records a read-only advisory review of the SRS-derived SDD/IDD/STD/RTM baseline. The verdict is `PASS_WITH_FINDINGS`: no accepted-baseline contradiction, but current SRS-derived rows remain grouped planning coverage. Broad production code is blocked until selected rows become executable test cards with fixture paths, commands, expected RED output, GREEN evidence, and no-live-action assertions.


## GitHub integration implementation requirements

[GitHub Integration Implementation Requirements Review](00-research-analysis/github-integration-implementation-requirements-review.md) concludes that the current product SRS is directionally sufficient but not enough by itself for GitHub module implementation. The controlled implementation handoff is [GitHub Adapter Specification](02-design-planning/github-adapter-specification.md), with fake/mock/dry-run/sandbox/live mode gates and `GH-FIX-*` TDD fixture requirements.


## GitHub adapter SRS promotion note

SRS §19 now promotes GitHub adapter implementation requirements `EDUOPS-FR-080..084` and `EDUOPS-NFR-034..036`; implementation still starts from the adapter spec plus `GH-FIX-*` gates, not from live GitHub actions.


## GitHub adapter SDD progress

[GitHub Adapter Software Design Description](02-design-planning/github-adapter-software-design-description.md) now details the GitHub adapter component decomposition, mode state machine, operation design, request/result data structures, submission-state boundary, privacy naming design, retry/outage/rate-limit handling, security/audit design, module placement, and `GH-SLICE-0..5` implementation order. It is linked from the main [Software Design Description](02-design-planning/software-design-description.md).


## Ralph-loop readiness review

[Ralph Loop Readiness Review](00-research-analysis/ralph-loop-readiness-review.md) records Claude and Codex advisory evaluation of whether the package is sufficient for an autonomous Ralph-style result-producing loop. The consolidated decision is insufficient for product-code implementation loops, but sufficient for a controlled documentation/test-card closure loop that produces executable SLICE-A/GH-SLICE-0 test-card and harness artifacts before code implementation.


## Ralph-loop closure package

The Ralph-loop readiness gaps are now supplemented with [SLICE-A and GH-SLICE-0 Executable Test Cards](03-verification-validation/slice-a-executable-test-cards.md), concrete fixture files under `fixtures/`, [Build, Packaging, and Release Engineering Baseline](06-implementation/build-packaging-release-engineering.md), [Git Adapter Specification](02-design-planning/git-adapter-specification.md), and [Local Storage Adapter Specification](02-design-planning/local-storage-adapter-specification.md). These artifacts only authorize a bounded fake/local implementation loop after review; live GitHub, LMS, official evaluation, and beta-facing claims remain blocked.


## GitHub clone-only clarification

GitHub is now explicitly limited to **clone-only** repository-source behavior in the current EduOps baseline. The GitHub adapter may validate clone configuration, plan clone targets, perform approved read-only clone/fetch, and record clone evidence. It shall not create repositories, push branches, invite collaborators, mutate branch protection, write webhooks/check-runs, archive repositories, or administer GitHub organizations. See [GitHub Clone-Only Baseline Review](00-research-analysis/github-clone-only-baseline-review.md), [GitHub Adapter Specification](02-design-planning/github-adapter-specification.md), and [GitHub Adapter Software Design Description](02-design-planning/github-adapter-software-design-description.md).

## M8 constrained export specification

- [Exporter implementation specification](02-design-planning/exporter-implementation-specification.md) — constrained fixture-local M8 export type contract and manifest-only evidence boundary.

## M7 mock-http fixture specification

- [GitHub mock-HTTP fixture format specification](02-design-planning/github-mock-http-fixture-specification.md) — constrained fixture-local M7 mock replay, deterministic retry/backoff, and no-live/no-mutation evidence boundary.

## M7 clone-readonly integration-point boundary specification

- [GitHub clone-readonly integration-point boundary specification](02-design-planning/github-clone-readonly-integration-point-specification.md) — constrained fixture-local allowlist/approval/credential-status/dry-run-plan boundary, fail-closed safety guards, and user-executed live-run runbook delegation. Live `clone-readonly` execution remains separately approved by a human-executed runbook and is not authorized by this specification.
