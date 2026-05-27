---
title: Implementation Requirements Gap Register
document_id: SWENG-EDUTECH-IMPL-REQ-GAP
version: 0.7.0
status: draft
created: 2026-05-13
updated: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  iso9001: ['7.5', '8.3', '8.5', '9.1']
  related: ['SWENG-EDUTECH-SRS', 'SWENG-EDUTECH-IMPL-GAP', 'SWENG-EDUTECH-IMPL-EXEC-PLAN', 'SWENG-EDUTECH-CLAUDE-IMPL-REQ-GAP-REVIEW', 'SWENG-EDUTECH-CONFIG-CONTRACT', 'SWENG-EDUTECH-CREDENTIAL-STORAGE']
---

# Implementation Requirements Gap Register

## 1. Purpose

This register lists implementation capabilities required to build EduOps that are not yet fully represented as detailed product requirements, constraints, interface contracts, or verification cases. It is a control bridge between the SRS and implementation-contract documents.

Candidate IDs use `EDUOPS-CFR-*`, `EDUOPS-CNFR-*`, `EDUOPS-CIR-*`, or `EDUOPS-CVR-*`. A candidate may be partly promoted into a high-level SRS requirement while its detailed implementation-control document remains open.

## 2. Classification and status rules

| Candidate prefix | Meaning | Promotion destination |
|---|---|---|
| `EDUOPS-CFR-*` | Candidate functional requirement | Requirements record / requirements breakdown |
| `EDUOPS-CNFR-*` | Candidate non-functional requirement | Requirements record / performance/security/accessibility constraints |
| `EDUOPS-CIR-*` | Candidate interface/contract requirement | IDD / adapter contract / API contract |
| `EDUOPS-CVR-*` | Candidate verification requirement | STD / V&V plan / fixture harness |

| Status | Meaning | Implementation implication |
|---|---|---|
| `candidate` | Not yet promoted into controlled SRS/IDD/STD text. | Do not implement as product code except in throwaway spike. |
| `promoted-document-required` | Promoted at high level, but detailed control document is still required. | Implementation remains blocked until document gate closes. |
| `promoted` | Promoted and traceable to a controlled requirement/test/spec. | May be implemented when its gate is reached. |
| `merged` | Merged into another candidate/specification. | Follow the target candidate/spec. |
| `superseded` | Replaced by a better candidate or decision. | Do not implement from this row. |

## 3. P0 candidates — source-code start blockers

| Candidate ID | Status | Candidate requirement needing formalization | Why it is needed for implementation | Suggested promotion / control output |
|---|---|---|---|---|
| EDUOPS-CFR-001 | promoted | The system shall implement a selected desktop shell/runtime/service stack from a controlled technology-stack decision. | Code layout depends on UI shell, runtime language, local DB, Git library, editor substrate, exporter substrate, and packaging tool. | Promoted by `EDUOPS-FR-067`; controlled in [Technology Stack Decision Record](../02-design-planning/technology-stack-decision-record.md). |
| EDUOPS-CFR-002 | promoted | The system shall run through a defined process topology: desktop shell, local service/core, Git worker, evaluation runner, export worker, and diagnostics path. | Side-effect ownership, lifecycle, crash recovery, and IPC must be fixed before code. | Promoted by `EDUOPS-FR-067`; controlled in [Process Topology and IPC Contract](../02-design-planning/process-topology-and-ipc-contract.md). |
| EDUOPS-CFR-003 | promoted | The codebase shall implement a controlled module/package layout with explicit dependency direction and forbidden dependencies. | Developers/agents need exact paths and layer boundaries. | Promoted by `EDUOPS-FR-067`; controlled in [Module and Package Layout](../02-design-planning/module-and-package-layout.md). |
| EDUOPS-CFR-004 | promoted | The system shall provide canonical domain schemas/IDL for Course, Section, RosterEntry, StudentIdentityBinding, Assignment, BlockDocument, EditOperation, SubmissionSnapshot, EvaluationRun, ExportJob, AuditEvent, and DiagnosticPackage. | Narrative entities are insufficient for validators, generated types, fixtures, and API signatures. | Promoted by `EDUOPS-FR-067`; controlled in [Canonical Domain IDL](../02-design-planning/canonical-domain-idl.md). |
| EDUOPS-CIR-001 | promoted | The system shall expose internal command/query contracts for UI-to-service and worker orchestration. | UI and service implementation cannot proceed independently without signatures, errors, idempotency, and audit hooks. | Promoted by `EDUOPS-FR-067`; controlled in [Internal API Contract](../02-design-planning/internal-api-contract.md). |
| EDUOPS-CVR-001 | promoted | SLICE-A/B/C local fixture gates shall define gate IDs, pass/fail criteria, required artifacts, hashes, manifests, logs, and commands. | `no-live-action-before-fixture-gates` cannot be enforced without explicit verification requirements. | Promoted to STD/V&V and [Fixture Corpus and Harness Plan](../03-verification-validation/fixture-corpus-and-harness-plan.md). |
| EDUOPS-CVR-002 | promoted | Fixture/test data shall be privacy-safe, deterministic, and free of real student PII or live credentials. | Test fixtures and CI evidence must not leak personal data. | Promoted to STD/V&V and [Fixture Corpus and Harness Plan](../03-verification-validation/fixture-corpus-and-harness-plan.md). |
| EDUOPS-CFR-007 | promoted | Student lifecycle, submission, and assignment release/update state machines shall be represented as code-authoritative transition tables. | Early implementation needs events, guards, side effects, persistence points, and error codes. | Promoted to [State Machine Implementation Tables](../02-design-planning/state-machine-implementation-tables.md); supersedes low-priority `EDUOPS-CIR-007`. |
| EDUOPS-CFR-008 | promoted | Synchronization shall define deterministic conflict detection, blocked-action behavior, user notification, acknowledgement, and rollback for `assignment/**`, `workspace/**`, and `knowledge/**`. | "Never overwrite" is insufficient to implement Git-backed sync safely. | Promoted to [State Machine Implementation Tables](../02-design-planning/state-machine-implementation-tables.md); later refined by Git/storage/editor adapters. |
| EDUOPS-CFR-009 | promoted | The system shall define an authoritative time/clock contract for deadlines, release windows, commit timestamps, late status, offline drift, and dispute reconstruction. | Time semantics affect submission eligibility and audit evidence. | Promoted to [State Machine Implementation Tables](../02-design-planning/state-machine-implementation-tables.md); later refined by audit/time service implementation. |
| EDUOPS-CFR-013 | promoted | The system shall define deterministic configuration scopes, precedence, override authority, schema versioning, validation, migration, and audit behavior. | Developers cannot safely implement boot, settings UI, profiles, or adapters when configuration is scattered across documents. | [Configuration Contract](../02-design-planning/configuration-contract.md) + requirements promotion. |
| EDUOPS-CFR-014 | promoted | The system shall define workspace-root resolution and zero-config first-run behavior. | SLICE-A boot and local fixture runs depend on deterministic workspace creation and safe invalid-root handling. | [Configuration Contract](../02-design-planning/configuration-contract.md). |
| EDUOPS-CFR-015 | promoted | The system shall manage credential references through an OS-protected credential adapter and shall never store raw secrets in configuration. | GitHub and future connector implementation needs testable secret boundaries before any auth flow. | [Credential Storage Contract](../02-design-planning/credential-storage-contract.md). |
| EDUOPS-CIR-018 | promoted | The internal API shall expose configuration get/set/list/validate/merge commands with audit, authorization, and redaction rules. | UI and backend cannot implement settings independently without command/query signatures. | [Internal API Contract](../02-design-planning/internal-api-contract.md). |
| EDUOPS-CVR-005 | promoted | Configuration fixture gates shall prove deterministic merge, secret non-leakage, migration behavior, invalid-config behavior, and offline isolation. | Configuration behavior must be verified before live GitHub/evaluation/export settings exist. | [Configuration Fixture Plan](../03-verification-validation/configuration-fixture-plan.md) and STD. |

## 4. P1 candidates — first vertical-slice blockers

| Candidate ID | Status | Candidate requirement needing formalization | Why it is needed for implementation | Suggested promotion / control output |
|---|---|---|---|---|
| EDUOPS-CIR-002 | promoted | Git adapter shall expose clone/fetch/status/commit/checkpoint/branch/tag/submission transaction APIs with fake/local and GitHub-backed implementations. | Git transaction boundaries and conflict handling must be signature-level. | `git-adapter-specification.md` |
| EDUOPS-CIR-003 | promoted | Local storage adapter shall define SQLite/index schema, migration, locks, path normalization, and rebuild semantics. | Storage architecture exists but DDL/transaction behavior are not requirements. | `local-storage-adapter-specification.md` |
| EDUOPS-CIR-011 | candidate | Asset/binary adapter shall define image, diagram, DOCX/HWPX/HWP artifact storage, content hashes, LFS/external-storage eligibility, streaming, cleanup, and privacy behavior. | Asset handling crosses editor, export, Git, storage, and privacy boundaries. | `asset-binary-adapter-specification.md` or storage/export specs. |
| EDUOPS-CIR-004 | candidate | Editor adapter bridge shall define editor transaction import/export, node-to-block mapping, operation journal append API, validation hooks, and toolkit conformance. | Block schema alone is insufficient to integrate a real editor. | `editor-adapter-bridge-specification.md` |
| EDUOPS-CIR-015 | candidate | Korean IME/editor composition contract shall define composition-state preservation, autosave suppression during composition, undo grouping, and mixed Korean/code behavior. | Korean input quality is a product differentiator and cannot be left to generic editor behavior. | Editor bridge spec + Korean text handling profile. |
| EDUOPS-CIR-012 | candidate | Secret/credential storage adapter shall define OS-protected token/session read, write, rotate, revoke, and wipe APIs. | GitHub token handling should not be hidden inside GitHub adapter code. | `secret-storage-adapter-specification.md` |
| EDUOPS-CIR-006 | promoted | GitHub clone adapter shall define token-reference use, fake/mock/clone-readonly modes, clone-source allowlist, rate-limit handling, retries, privacy naming, and audit events. | GitHub clone module implementation needs safe fixture gates, no-secret leakage, and explicit blocking of non-clone operations before any approved clone-readonly action. | Promoted to [GitHub Adapter Specification](../02-design-planning/github-adapter-specification.md). |
| EDUOPS-CIR-005 | candidate | Evaluation runner shall accept a controlled runner manifest and emit deterministic result JSON, logs, resource-limit outcomes, and sandbox status. | C/C++ evaluation needs executable I/O and sandbox contract. | `evaluation-runner-io-contract.md` |
| EDUOPS-CIR-013 | candidate | Notification adapter shall define Windows toast and in-app notification channels, delivery evidence, deduplication, and disabled-notification fallback. | Assignment update notices are required but implementation channel is unspecified. | `notification-adapter-specification.md` |
| EDUOPS-CIR-014 | candidate | Search-index adapter shall define rebuildable build/query/invalidate APIs, privacy filtering, and stale-index behavior. | Search caches must not become evidence or leak student-private knowledge. | `search-index-adapter-specification.md` |
| EDUOPS-CFR-010 | candidate | Schema-migration runner shall define migration signatures, warning manifests, quarantine paths, downgrade rejection, and old-hash preservation. | Schema migration policy needs executable contracts. | `schema-migration-runner-specification.md` |
| EDUOPS-CFR-011 | candidate | Audit-event taxonomy and versioned schema shall define actor, action, object, before/after, SHA/hash, severity, and evolution rules. | Audit events need stable code values and required field semantics. | Domain IDL + observability/audit spec. |
| EDUOPS-CFR-012 | candidate | Error-code taxonomy shall define domain prefixes, retriable/terminal classification, user-display policy, and diagnostic binding. | Multi-worker implementation needs consistent machine-readable errors. | Internal API + observability spec. |
| EDUOPS-CFR-005 | merged | Export pipeline shall provide a controlled renderer/exporter job model for DOCX/HWPX/HWP derived artifacts. | Export job API and warning/loss emitter should evolve together. | Merge with `EDUOPS-CIR-010` into `exporter-implementation-specification.md`. |
| EDUOPS-CIR-010 | candidate | Exporter warning/loss emitter shall standardize warning codes and manifest binding for DOCX/HWPX/HWP output. | Export warnings must be machine-readable and tied to job outputs. | `exporter-implementation-specification.md` with `EDUOPS-CFR-005` merged. |
| EDUOPS-CFR-006 | candidate | Fixture corpus shall include deterministic fake Git, fake GitHub, editor documents, roster files, runner samples, export documents, malformed files, and privacy cases. | Executable fixtures and paths are not complete. | P0 gate aspect is `EDUOPS-CVR-001`; content detail goes to `fixture-corpus-and-harness-plan.md`. |
| EDUOPS-CNFR-001 | promoted | Build and packaging shall define Windows developer setup, package manager, lockfiles, lint/type/test commands, installer strategy, and versioning. | Product implementation needs reproducible local setup and agent/developer commands. | `build-packaging-release-engineering.md` |

## 5. P2 candidates — integration quality and hardening

| Candidate ID | Status | Candidate requirement needing formalization | Why it is needed for implementation | Suggested promotion / control output |
|---|---|---|---|---|
| EDUOPS-CIR-007 | superseded | State machines shall be represented as transition tables with event, guard, side effect, persistence point, and error code. | This is too important for P2 and should be code-authoritative earlier. | Superseded by P0 `EDUOPS-CFR-007`. |
| EDUOPS-CIR-008 | candidate | Authorization shall define PDP/PEP request/decision JSON, scope encoding, cache rules, denial reason, and audit hook. | RBAC/mode rules need implementable policy decision contracts. | `authorization-implementation-specification.md` |
| EDUOPS-CIR-009 | candidate | Rendering pipeline shall define adapter signatures, cache keys, fallback snapshot generation, and renderer profile evidence. | Rendering requirements exist but implementation handoff contracts are incomplete. | `rendering-pipeline-implementation-specification.md` |
| EDUOPS-CNFR-002 | candidate | Observability shall define structured log schema, correlation ID propagation, error code taxonomy, and diagnostic bundle generation. | Debugging Git/editor/runner/export failures needs standard diagnostics. | `observability-and-diagnostics-specification.md` |
| EDUOPS-CNFR-003 | candidate | Local privacy protection shall define encryption/DPAPI use, cache cleanup, archive/withdrawal cleanup, and private search filtering. | Privacy controls need concrete implementation mechanisms. | Storage/security implementation specs. |
| EDUOPS-CIR-016 | candidate | Backup/archive operations shall define course archive, withdrawal cleanup, retention expiry, evidence export, and restore contracts. | Archive and cleanup policies need executable operations. | `backup-archive-operation-contract.md` |
| EDUOPS-CIR-017 | candidate | App update shall define Windows installer signing, update check, rollback, and version compatibility behavior. | Desktop delivery needs update governance. | `app-update-installation-contract.md` |
| EDUOPS-CVR-003 | candidate | Accessibility verification harness shall define keyboard/focus/screen-reader fixtures and pass criteria. | Accessibility baseline needs executable checks. | STD/V&V + fixture plan. |
| EDUOPS-CVR-004 | candidate | Performance benchmark harness shall define hardware profile, deterministic seeds, measurement commands, and P50/P95 reporting. | Performance budgets need reproducible measurement. | STD/V&V + performance budget. |
| EDUOPS-CNFR-004 | candidate | i18n/locale contract shall define ko-KR/en-US text, NFC normalization, date/number formatting, sorting, and export locale behavior. | Korean/English course operations need deterministic locale behavior. | Korean text handling + config specs. |
| EDUOPS-CNFR-005 | merged | System/user configuration contract shall define storage locations, defaults, precedence, migration, and redaction. | Configuration otherwise becomes scattered across modules. | Merged into P0 `EDUOPS-CFR-013`, `EDUOPS-CFR-014`, `EDUOPS-CFR-015`, and [Configuration Contract](../02-design-planning/configuration-contract.md). |
| EDUOPS-CFR-017 | candidate | Evaluation profile configuration shall select advisory/official runner, toolchain profile, resource limits, and evidence behavior. | Runner behavior must not be hidden inside evaluation code. | Configuration contract + evaluation runner I/O contract. |
| EDUOPS-CFR-018 | candidate | Export profile configuration shall select DOCX/HWPX/HWP converter path, template, license reference, warning policy, and fallback behavior. | Export implementation needs reproducible converter/profile settings. | Configuration contract + exporter implementation specification. |
| EDUOPS-CFR-019 | candidate | Rendering and Korean text configuration shall select renderer profile, font fallback, Unicode normalization, and fallback snapshot behavior. | Rendering consistency affects authoring, review, export, and submission evidence. | Configuration contract + rendering pipeline implementation specification. |
| EDUOPS-CFR-020 | candidate | Offline/sync configuration shall define offline mode, queue limits, retry/backoff, and network-call denial behavior. | Local-first and no-live-action gates depend on executable offline controls. | Configuration contract + Git/GitHub adapter specifications. |
| EDUOPS-CFR-021 | candidate | Diagnostics/audit configuration shall define log levels, retention, redaction profile, and diagnostic bundle boundaries. | Debug evidence must not leak private or credential material. | Configuration contract + observability specification. |
| EDUOPS-CFR-022 | candidate | App update configuration shall define update channel, signed update checks, rollback, and disable behavior. | Windows beta delivery needs controlled update behavior. | Configuration contract + app update installation contract. |
| EDUOPS-CNFR-006 | candidate | Raw credentials shall not be persisted in configuration, logs, Git files, exports, or diagnostic bundles. | Prevents token leakage and supports privacy/security requirements. | Credential storage contract + secret leak fixture. |
| EDUOPS-CNFR-007 | candidate | Protected configuration changes shall emit audit events with before/after hashes and redacted diff class. | Configuration changes affect product behavior and must be traceable. | Configuration contract + AuditEvent schema. |
| EDUOPS-CNFR-008 | candidate | First-run boot shall succeed from app defaults without live external services. | SLICE-A local skeleton must be zero-config and fixture-safe. | Configuration fixture plan. |
| EDUOPS-CNFR-009 | candidate | Configuration load and merge shall meet seed boot performance budget. | Settings should not slow classroom startup. | Performance budget + configuration fixture plan. |
| EDUOPS-CNFR-010 | candidate | Incompatible configuration schemas shall migrate explicitly or boot in safe read-only/quarantine mode. | Prevents destructive beta upgrades. | Configuration contract + migration fixture. |
| EDUOPS-CNFR-011 | candidate | Student actors shall not read credential keys or protected course/repository policy keys. | Settings UI must not bypass access-control baseline. | Credential storage contract + access-control fixtures. |
| EDUOPS-CIR-019 | candidate | Credential API shall define register, rotate, revoke, status, provider, fingerprint, expiry, and default-deny behavior. | Auth flows require implementation-level signatures separate from GitHub adapter code. | Credential storage contract + internal API. |
| EDUOPS-CIR-020 | candidate | Configuration JSON Schema publication path and schema-version contract shall be controlled. | Enables generated validators and fixture conformance. | Configuration contract. |
| EDUOPS-CIR-021 | candidate | `EDUOPS_*` environment variable whitelist and precedence shall be controlled. | Prevents hidden environment-dependent behavior. | Configuration contract. |
| EDUOPS-CVR-006 | candidate | Secret-leak scan shall prove no raw credential value appears in generated artifacts. | Required before GitHub or converter credential work. | Configuration fixture plan + STD. |
| EDUOPS-CVR-007 | candidate | Configuration schema migration shall preserve required keys and record before/after hashes. | Required before beta upgrades. | Configuration fixture plan. |
| EDUOPS-CVR-008 | candidate | Invalid/unknown protected configuration shall fail with explicit errors and safe boot behavior. | Prevents silent unsafe defaults. | Configuration fixture plan. |
| EDUOPS-CVR-009 | candidate | Offline mode fixtures shall prove zero live GitHub/network adapter calls. | Supports local-first and no-live-action baseline. | Configuration fixture plan. |
| EDUOPS-CVR-010 | candidate | Configuration schema fixtures shall prove that all required key families, owners, schema versions, and redaction classes are declared. | Configuration contract gates need uniform CVR traceability. | Configuration contract + configuration fixture plan. |
| EDUOPS-CVR-011 | candidate | Requirements traceability checks shall prove every SRS FR/NFR row appears in the RTM with a design/test/evidence status. | Traceability-supported implementation needs exact requirement-to-test control, not only grouped fixture intent. | Requirements traceability matrix + STD-084. |
| EDUOPS-CVR-012 | candidate | TDD evidence checks shall prove each implemented behavior records RED failure, GREEN pass, and refactor/regression validation against an exact requirement/test anchor. | Tests written after implementation do not satisfy TDD. | STD-085 + implementation evidence package. |

## 6. Existing areas with partial coverage and candidate mapping

| Area | Existing coverage | Missing refinement | Candidate mapping |
|---|---|---|---|
| Student/course management | SRS FR-001..008 | Command/API signature, roster schema validation fixtures, identity-binding error codes. | `EDUOPS-CIR-001`, `EDUOPS-CFR-004`, `EDUOPS-CFR-012`, `EDUOPS-CVR-001` |
| Assignment/workspace/submission | SRS FR-009..016 | Repository layout schema, adapter transaction semantics, submission snapshot manifest schema, conflict algorithm. | `EDUOPS-CIR-002`, `EDUOPS-CFR-004`, `EDUOPS-CFR-008`, `EDUOPS-CFR-009` |
| Evaluation | SRS FR-017..018, evaluation profile | Runner manifest/result JSON, Windows sandbox mechanism, compiler profile selection. | `EDUOPS-CIR-005`, `EDUOPS-CFR-012`, `EDUOPS-CVR-001` |
| GitHub/backend | SRS FR-023..024, FR-059, GitHub topology/feasibility docs, and [GitHub Adapter Specification](../02-design-planning/github-adapter-specification.md) | Exact executable `GH-FIX-*` test cards and optional clone-readonly evidence remain required before real GitHub clone actions. | `EDUOPS-CIR-006`, `EDUOPS-CIR-012`, `EDUOPS-CVR-001`, `EDUOPS-CVR-009` |
| Notion-style editor/storage | SRS FR-047..066, block/storage docs | Editor bridge signature, toolkit mapping, operation journal API, schema migration, Korean IME fixture. | `EDUOPS-CIR-003`, `EDUOPS-CIR-004`, `EDUOPS-CIR-015`, `EDUOPS-CFR-010` |
| Export | SRS FR-045..046, export docs | Export job API, warning/loss code schema, golden fixture comparison, asset/binary policy. | `EDUOPS-CFR-005`, `EDUOPS-CIR-010`, `EDUOPS-CIR-011`, `EDUOPS-CVR-001` |
| V&V | STD-001..070 | Executable harness scripts, fixture paths, deterministic seed policy, CI/dev commands, privacy-safe fixtures. | `EDUOPS-CVR-001`, `EDUOPS-CVR-002`, `EDUOPS-CVR-003`, `EDUOPS-CVR-004`, `EDUOPS-CNFR-001` |

## 7. Recommended promotion order

1. Maintain register status model and keep P0 rows synchronized with SRS promotions.
2. Close P0 implementation contract documents in dependency order: `canonical-domain-idl.md` → `internal-api-contract.md`; `technology-stack-decision-record.md` → `process-topology-and-ipc-contract.md` → `module-and-package-layout.md`.
3. Keep `EDUOPS-CVR-001` and `EDUOPS-CVR-002` synchronized with the fixture harness before SLICE-A.
4. Keep `EDUOPS-CFR-007`, `EDUOPS-CFR-008`, and `EDUOPS-CFR-009` synchronized with state-machine implementation tables before SLICE-B/C/D.
5. Promote P1 adapter contracts in this order: Git → local storage → asset/binary → editor bridge → Korean IME → secret store → GitHub → runner → notification → search.
6. Merge export job and warning/loss emitter under `exporter-implementation-specification.md` before SLICE-G.
7. Promote observability, audit taxonomy, error taxonomy, privacy, i18n/config, backup/update, accessibility, and performance hardening during integration slices.

## 8. Claude review trace

Claude Code read-only review on 2026-05-14 found that v0.1.0 of this register was directionally correct but incomplete. The v0.2.0 revision implemented that review by adding status fields, CVR candidates, reprioritized state-machine and fixture-gate work, and missing adapter/non-functional candidates. A later developer-perspective Claude configuration review found that configuration remained a P0 implementation-readiness gap; v0.3.0 adds configuration, credential, API, and verification candidates. Advisory reports are recorded in [Claude Implementation Requirements Gap Review](../00-research-analysis/claude-implementation-requirements-gap-review.md), [Claude Configuration Requirements Review](../00-research-analysis/claude-configuration-requirements-review.md), and [SRS Traceability and TDD Readiness Review](../00-research-analysis/srs-traceability-tdd-readiness-review.md).


## 9. GitHub integration implementation review

The 2026-05-14 [GitHub Integration Implementation Requirements Review](../00-research-analysis/github-integration-implementation-requirements-review.md) concluded that GitHub modules require implementation-level adapter requirements before coding. The later [GitHub Clone-Only Baseline Review](../00-research-analysis/github-clone-only-baseline-review.md) narrows `EDUOPS-CIR-006` to clone-only behavior controlled by [GitHub Adapter Specification](../02-design-planning/github-adapter-specification.md).


## 10. Ralph-loop closure update

The 2026-05-14 Ralph readiness supplementation promotes the remaining P0 configuration/credential rows because their controlled contracts now exist and are linked. It also promotes the minimum P1 rows required for the first fake/local loop:

- `EDUOPS-CIR-002` → [Git Adapter Specification](../02-design-planning/git-adapter-specification.md);
- `EDUOPS-CIR-003` → [Local Storage Adapter Specification](../02-design-planning/local-storage-adapter-specification.md);
- `EDUOPS-CNFR-001` → [Build, Packaging, and Release Engineering Baseline](../06-implementation/build-packaging-release-engineering.md).

The promotion only authorizes the bounded SLICE-A/GH-SLICE-0 fake/local loop described in [SLICE-A and GH-SLICE-0 Executable Test Cards](../03-verification-validation/slice-a-executable-test-cards.md). It does not authorize live GitHub, LMS, official evaluation, or beta-facing claims.
