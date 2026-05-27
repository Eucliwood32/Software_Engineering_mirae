---
title: Implementation Milestones
document_id: EDUOPS-IMPLEMENTATION-MILESTONES
version: 0.1.0
status: draft
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
source_review: ../00-research-analysis/claude-design-milestone-analysis.md
---

# Implementation Milestones

## 1. Purpose

This document establishes the first develop-repository milestone structure for EduOps implementation. It converts the current design-document baseline into bounded implementation milestones with entry criteria, output artifacts, document anchors, acceptance gates, and risks/dependencies.

The milestone structure is based on the current controlled documents under `docs/` and the read-only Claude Code advisory review recorded in [Claude Design Milestone Analysis](../00-research-analysis/claude-design-milestone-analysis.md).

## 2. Baseline constraints

Implementation shall preserve the following constraints across all milestones:

1. No live external action until local fixture gates pass and a later explicit gate approves live behavior.
2. GitHub behavior is clone-only in the current baseline; non-clone operations are blocked before external request.
3. Adapter layers own external side effects; UI and domain layers remain isolated from external systems.
4. TDD evidence is required for implemented behavior: requirement ID, design anchor, test card or STD row, RED result, GREEN evidence, and regression/refactor validation.
5. Submission state advancement is owned by the application core, not by adapters.
6. Editor JSON is the source of truth; Markdown is a deterministic projection.
7. Configuration is deterministic and hashable; secrets are represented only as credential references.
8. Windows and Linux desktop are active product targets. Windows uses WebView2; Linux uses the Tauri-supported system webview runtime recorded in evidence.

## 3. Ralph execution alignment

Ralph shall execute these milestones as checkpointed local increments, not as one unbounded autonomous run. Each iteration starts with Prepare, performs at most one coherent RED/GREEN/reflection/commit unit by default, updates `ralph.md`, and stops when the next step changes milestone scope, requires a non-delegable action, fails validation, or drops below the 75% continuation-likelihood threshold.

The current executable order is:

```text
M0-COMPLETE
  -> M1-PREP
  -> M1-T1 RED contract for RequestEnvelope/ResultEnvelope and local course command
  -> M1-T2 GREEN domain/API envelope primitives
  -> M1-T3 local filesystem storage adapter
  -> M1-T4 fake-local Git adapter and clone-only mode gate hardening
  -> M1-T5 SLICE-A fixture runner and build/evidence/slice-a/<run-id>/run-summary.json
  -> M1-GATE GATE-SLICE-A-LOCAL-SKELETON
  -> M1A-PREP only after M1 gate passes
```

Ralph shall not start M1A, M2, or later milestones until the relevant prior gate is recorded in `ralph.md` and committed. M7 may run after M2 as a separate clone-only adapter branch of work, but live GitHub mode remains disabled unless a later user-executed approval gate is added.

### 3.1 Ralph task-size rule

Each Ralph task must be small enough to validate and commit independently. If a proposed task spans more than one crate boundary plus tests, split it before coding. Behavior tasks require observed RED first. Documentation-only alignment tasks may use validation-first checks instead of RED.

### 3.2 Ralph invariant gates

Every Ralph implementation task must preserve:

1. `live_external_action=false` in request/evidence paths until a later approved live gate exists.
2. No Git remote, push, repository creation, webhook, archive, or admin operation.
3. No credential lookup or raw secret persistence.
4. Generated evidence under `build/evidence/<slice>/<run-id>/`, with generated/transient build outputs kept out of Git unless explicitly controlled.
5. Local commit per coherent task after focused and repository-level validation pass.

## 4. Milestone sequence

### M0 — Repository scaffold and toolchain bootstrap

**Objective.** Initialize the implementation repository structure and toolchain without adding product behavior.

**Entry criteria.**

- Develop repo exists on `main`.
- Documentation baseline is available under `docs/`.
- No remote is configured unless explicitly approved.

**Output artifacts.**

- Cargo workspace root.
- `rust-toolchain.toml` or equivalent pinned toolchain record.
- `apps/desktop` Tauri 2 shell scaffold.
- `apps/desktop-ui` TypeScript UI scaffold.
- Node/package-manager pin or equivalent frontend toolchain record.
- Empty crate stubs matching [Module and package layout](../02-design-planning/module-and-package-layout.md), including the domain, API, core, storage, config, credentials, Git, export, runner, workers, diagnostics, and fixture/harness boundaries defined there.
- Initial checked-in fixture corpus copied or referenced from `docs/fixtures/` into the implementation fixture location selected by the repository layout.
- Baseline build/test commands for Rust, frontend typecheck/build, and Tauri launch/build smoke where applicable.
- Windows WebView2 or Linux webview/runtime prerequisite check, or documented runtime requirement.

**Document anchors.**

- [Module and package layout](../02-design-planning/module-and-package-layout.md)
- [Fixture corpus and harness plan](../03-verification-validation/fixture-corpus-and-harness-plan.md)
- [Build, packaging, and release engineering baseline](build-packaging-release-engineering.md)

**Acceptance gates.**

- `cargo check` or the selected equivalent build command runs on the empty workspace.
- Frontend typecheck/build command runs on the empty UI scaffold or records the expected initial RED result.
- Tauri launch/build smoke command is present or records the controlled platform-runtime prerequisite blocker.
- Fixture verification command is present, even if it returns the documented initial RED result.
- No live network behavior is present.
- Repository status is clean after commit.

**Risks/dependencies.**

- Risk of uncontrolled source-tree expansion; mitigate by enforcing the module/package layout and keeping this milestone behavior-free.

### M1 — SLICE-A local skeleton

**Status.** Accepted by `GATE-SLICE-A-LOCAL-SKELETON`; see [M1 SLICE-A local skeleton evidence](m1-slice-a-local-skeleton-evidence.md).

**Objective.** Implement the first local-only vertical skeleton: one empty course through the storage adapter and fake-local Git adapter, with deterministic evidence output and no live external action.

**Entry criteria.**

- M0 complete.
- RED output for `TC-SLICE-A-001` has been recorded.
- First-loop scope remains limited to `TC-SLICE-A-001..003` and `TC-GH-000`.

**Output artifacts.**

- Domain primitives for course and audit evidence.
- `RequestEnvelope` and `ResultEnvelope` implementation.
- `StorageAdapter` trait and local filesystem implementation.
- `GitAdapter` trait and fake-local implementation.
- GitHub mode gate that blocks non-clone operations before external request.
- Fixture runner commands for SLICE-A.
- Evidence package under the common evidence convention `build/evidence/slice-a/<run-id>/`.

**Document anchors.**

- [SLICE-A and GH-SLICE-0 executable test cards](../03-verification-validation/slice-a-executable-test-cards.md)
- [Internal API contract](../02-design-planning/internal-api-contract.md)
- [Git adapter specification](../02-design-planning/git-adapter-specification.md)
- [Local storage adapter specification](../02-design-planning/local-storage-adapter-specification.md)
- [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md)

**Acceptance gates.**

- `GATE-SLICE-A-LOCAL-SKELETON` passes.
- Evidence includes `live_external_action=false`.
- No remote URL or network call is observed.
- `run-summary.json` required gate fields validate against the controlled evidence checklist.
- RED-to-GREEN evidence is committed.

**Risks/dependencies.**

- Risk of scope creep into editor, roster, runner, or GitHub behavior; mitigate by enforcing the SLICE-A test-card scope.
- Risk of accidental live action; mitigate with adapter tests and explicit no-network checks.

### M1A — Desktop shell demonstration slice

**Status.** Accepted by `GATE-UI-SHELL-DEMO-SLICE-A` using controlled Linux desktop evidence; see [M1A desktop gate closure evidence](m1a-desktop-gate-closure-evidence.md). The earlier local prerequisite record remains available at [M1A local UI shell prerequisite evidence](m1a-local-ui-shell-prerequisite-evidence.md).

**Objective.** Implement the first demonstrable desktop UI shell over the SLICE-A fake/local backend path, proving that a user-visible Tauri/WebView2 application can invoke controlled backend commands and display evidence without live external action.

**Entry criteria.**

- M1 complete.
- `TC-UI-SHELL-001` expected RED result has been recorded.
- UI scope remains limited to shell launch, health/session query, SLICE-A local course action, evidence display, and controlled failure display.

**Output artifacts.**

- `apps/desktop` Tauri 2 shell implementation sufficient for local smoke execution.
- `apps/desktop-ui` TypeScript UI shell with local/fake mode indicator.
- IPC bridge from UI to the backend command/query envelope.
- UI shell test-card implementation for `TC-UI-SHELL-001..003`.
- Screenshot or screen-recording capture linked into the local evidence package.
- Evidence package under the common evidence convention `build/evidence/ui-shell-slice-a/<run-id>/`.

**Document anchors.**

- [Codex Demo UI Readiness Analysis](../00-research-analysis/codex-demo-ui-readiness-analysis.md)
- [UI Shell Demonstration Test Cards](../03-verification-validation/ui-shell-demo-test-cards.md)
- [Technology stack decision record](../02-design-planning/technology-stack-decision-record.md)
- [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md)
- [Module and package layout](../02-design-planning/module-and-package-layout.md)
- [Working demonstration and evidence plan](../03-verification-validation/working-demonstration-evidence-plan.md)

**Acceptance gates.**

- `GATE-UI-SHELL-DEMO-SLICE-A` passes.
- Tauri desktop app launches in a controlled Windows or Linux desktop environment, with named evidence-capture environment, platform webview/runtime details, and reviewer/owner recorded before the gate is marked complete.
- Frontend typecheck and production build pass.
- UI startup performs a backend session or health query through IPC.
- UI action executes only the fake/local SLICE-A command path.
- UI displays local/fake mode, `live_external_action=false`, course ID, audit event ID, local evidence path, and fake Git checkpoint/status.
- Runtime contract test asserts that the UI path emits `RequestEnvelope.live_external_action=false` and that the evidence record preserves the same value.
- Minimal UI smoke checks cover keyboard focus on the first actionable control and a startup/render timing record; full accessibility and performance validation remain scoped to later role/editor milestones.
- Screenshot or screen-recording evidence is linked from `run-summary.json`.
- No direct UI filesystem, Git, network, runner, exporter, or credential side effects are observed.

**Risks/dependencies.**

- Risk that backend-only evidence is mistaken for a desktop product demonstration; mitigate by requiring captured UI evidence.
- Risk that Tauri/WebView2, frontend build, or IPC issues surface too late; mitigate by placing this milestone before configuration, editor, roster, and export expansion.

### M2 — Configuration and credential-reference services

**Objective.** Implement deterministic configuration precedence, effective configuration hashing, and credential-reference lifecycle without raw-secret persistence.

**Entry criteria.**

- M1A accepted by `GATE-UI-SHELL-DEMO-SLICE-A`; see [M1A desktop gate closure evidence](m1a-desktop-gate-closure-evidence.md).
- Credential implementation choice is selected or narrowed enough for a local fixture implementation.

**Output artifacts.**

- Configuration crate with schema validation, merge, migration, and effective-hash behavior.
- Credential-reference crate with register, rotate, revoke, and status behavior.
- Configuration and credential fixture corpus.
- Evidence packages for configuration and credential gates.

**Document anchors.**

- [Configuration contract](../02-design-planning/configuration-contract.md)
- [Credential storage contract](../02-design-planning/credential-storage-contract.md)
- [Internal API contract](../02-design-planning/internal-api-contract.md)
- [Configuration fixture plan](../03-verification-validation/configuration-fixture-plan.md)

**Acceptance gates.**

- Identical inputs produce byte-identical effective configuration hash.
- Raw tokens do not appear in logs, config records, manifests, diagnostics, or Git-tracked outputs.
- Offline mode produces zero network adapter calls.
- Invalid configuration enters safe read-only behavior with an explicit error code.

**Risks/dependencies.**

- Credential-backend choice can block later GitHub clone-only work.
- Secret leakage is a primary risk and must be tested before expanding scope.

### M3 — SLICE-B canonical document path

**Objective.** Implement the canonical block-document storage path: editor JSON source of truth, operation journal, deterministic Markdown projection, and Git checkpoint evidence.

**Entry criteria.**

- M1 complete.
- Editor adapter bridge specification is authored and accepted.

**Output artifacts.**

- `BlockDocument` and `EditOperation` domain types.
- Document storage service with operation journal, materialization, and manifest.
- Editor adapter bridge implementation.
- Deterministic Markdown projection fixtures.
- SLICE-B evidence package.

**Document anchors.**

- [Software design description](../02-design-planning/software-design-description.md)
- [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md)
- [Notion-style document storage architecture](../02-design-planning/notion-style-document-storage-architecture.md)
- [Block schema](../02-design-planning/block-schema.md)
- [Fixture corpus and harness plan](../03-verification-validation/fixture-corpus-and-harness-plan.md)

**Acceptance gates.**

- Identical input produces identical projection hash.
- Operation journal replays to the same canonical state.
- Block IDs remain stable across update, split, merge, and migration fixtures.
- Korean text and code/table fixtures round-trip through the canonical model.

**Risks/dependencies.**

- Editor underspecification and Korean IME behavior can destabilize this milestone.
- Projection/source-of-truth confusion must be prevented by manifest evidence.

### M4 — SLICE-C roster, identity, and workspace provisioning

**Objective.** Implement roster import, local identity binding, instructor approval, and per-student workspace provisioning through deterministic local fixtures.

**Entry criteria.**

- M3 complete.
- Roster schema and identity policy are accepted.

**Output artifacts.**

- Roster import command/query handlers.
- Local identity claim and approval flow.
- Workspace provisioning handler.
- PII-safe roster and identity fixtures.
- SLICE-C evidence package.

**Document anchors.**

- [Roster schema and identity policy](../02-design-planning/roster-schema-and-identity-policy.md)
- [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md)
- [Access control and authorization model](../02-design-planning/access-control-authorization-model.md)
- [Software test description](../03-verification-validation/software-test-description.md)

**Acceptance gates.**

- Cleartext student PII is absent from generated evidence except where explicitly allowed by schema.
- Duplicate identity binding is rejected unless override evidence exists.
- Privacy denylist scan passes.
- Student actor cannot read another student's protected binding or workspace state.

**Risks/dependencies.**

- Student identity mismatch and PII leakage are primary risks.
- Access-control tests must be executable before using this milestone for classroom-like demos.

### M5 — SLICE-D assignment publication, sync, and submission state machine

**Objective.** Implement the controlled Problem Bank to Submission Snapshot chain against fake-local Git, preserving assignment immutability and distinct queued, pushed, and confirmed states.

**Entry criteria.**

- M2, M3, and M4 complete.
- State machine implementation tables are accepted as code-authoritative.

**Output artifacts.**

- Assignment publish and release use cases.
- Workspace checkpoint use case.
- Submission queue and local confirmation use cases.
- Assignment update and conflict evidence fixtures.
- SLICE-D evidence package.

**Document anchors.**

- [State machine implementation tables](../02-design-planning/state-machine-implementation-tables.md)
- [Repository permission and assignment workflow](../02-design-planning/repository-permission-workflow.md)
- [Software design description](../02-design-planning/software-design-description.md)
- [Software test description](../03-verification-validation/software-test-description.md)

**Acceptance gates.**

- Assignment update does not overwrite `workspace/**` or `knowledge/**`.
- Queued, pushed, and confirmed states are separately represented in evidence.
- Submission snapshot links workspace SHA, assignment version, commit SHA, and timestamp.
- Adapter evidence cannot advance state without core validation.

**Risks/dependencies.**

- Workspace overwrite, incomplete submission evidence, assignment update conflict, and state conflation are the main risks.

### M6 — SLICE-E advisory C/C++ runner

**Objective.** Implement advisory local C/C++ compile/run behavior with resource limits and deterministic result evidence. Official grading remains excluded.

**Entry criteria.**

- M5 submission evidence accepted.
- Evaluation runner I/O contract is authored and accepted: [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md).

**Output artifacts.**

- Runner adapter trait and local advisory runner implementation.
- Toolchain, flags, limits, command, exit, and log-hash manifest.
- Timeout, memory, path traversal, and unsafe-input fixtures.
- SLICE-E evidence package.

**Document anchors.**

- [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md)
- [Evaluation execution profile](../02-design-planning/evaluation-execution-profile.md)
- [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md)
- [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md)
- [Software test description](../03-verification-validation/software-test-description.md)

**Acceptance gates.**

- Advisory results cannot be promoted to official grading evidence.
- Timeout, memory, and path traversal negative fixtures pass.
- Runner emits audit evidence before external process start.
- Runner cannot touch host files outside the permitted workspace boundary.

**Risks/dependencies.**

- Unsafe C/C++ execution and official/advisory evidence confusion are primary risks.

### M7 — SLICE-F GitHub clone-only adapter

**Objective.** Implement GitHub clone-only planning, privacy naming, mode gates, credential-reference resolution, retry/rate-limit controls, and evidence normalization. Live mode remains disabled unless separately approved.

**Entry criteria.**

- M2 credential-reference behavior accepted.
- GitHub adapter SDD and clone-only baseline remain accepted.

**Output artifacts.**

- GitHub clone planner.
- Privacy naming evaluator.
- Fake-local, mock-http, dry-run, sandbox, and live mode gates, with live disabled by default.
- Retry and evidence normalization components.
- Contract tests for `GH-FIX-*` and `GH-SLICE-*` fixtures.

**Document anchors.**

- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub adapter software design description](../02-design-planning/github-adapter-software-design-description.md)
- [GitHub mock-HTTP fixture format specification](../02-design-planning/github-mock-http-fixture-specification.md)
- [GitHub clone-readonly integration-point boundary specification](../02-design-planning/github-clone-readonly-integration-point-specification.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [Software test description](../03-verification-validation/software-test-description.md)

**Acceptance gates.**

- Non-clone operation returns `GITHUB_NON_CLONE_OPERATION_BLOCKED` before external request.
- Mock-http fixture matches dry-run plan with deterministic retry/backoff schedule and no wall-clock sleep.
- Privacy naming rejects PII before any network plan.
- Adapter evidence cannot promote submission state by itself.

**Risks/dependencies.**

- GitHub outage, rate limits, privacy naming, and scope expansion beyond clone-only are primary risks.

### M8 — SLICE-G export fixture and DEMO-1 evidence package

**Objective.** Implement controlled DOCX/HWPX export fixtures from canonical block documents and assemble the local-only DEMO-1 evidence package.

**Entry criteria.**

- M3 canonical document path complete.
- M5 submission path complete.
- M6 advisory evaluation complete.
- Exporter implementation specification is authored and accepted for the constrained fixture-local scope: [Exporter implementation specification](../02-design-planning/exporter-implementation-specification.md).

**Output artifacts.**

- Export adapter and manifest-only DOCX/HWPX placeholder writer profile contracts.
- Export manifest with source SHA, template reference, tool profile, content hash, and warning codes.
- DEMO-1 candidate evidence package shape, with no DEMO-1 acceptance claim.

**Document anchors.**

- [Exporter implementation specification](../02-design-planning/exporter-implementation-specification.md)
- [HWP and HWPX export strategy](../02-design-planning/hwp-export-strategy.md)
- [Export fidelity acceptance](../02-design-planning/export-fidelity-acceptance.md)
- [Working demonstration and evidence plan](../03-verification-validation/working-demonstration-evidence-plan.md)
- [Software test description](../03-verification-validation/software-test-description.md)

**Acceptance gates.**

- Korean and English text, headings, code blocks, tables, images, and citations are represented through canonical block IDs, manifest records, placeholder/fallback artifacts, and explicit warning codes within the constrained fixture-local loss profile.
- Export manifest is hash-linked to the canonical source.
- DEMO-1 candidate evidence remains local-only with `live_external_action=false`, `host_process_invoked=false`, and `demo_claim_made=false`.
- Prior slice gates pass together in the consolidated fixture run.

**Risks/dependencies.**

- DOCX/HWPX fidelity, converter licensing, demo overclaim, and placeholder-output misinterpretation are primary risks. Real converter integration remains outside this constrained milestone unless a later human-owned decision authorizes it.

## 5. Recommended first development milestone

The first actual development milestone is **M1 — SLICE-A local skeleton**, with **M0** performed first or in the same controlled implementation branch if the implementation repository has not yet been scaffolded.

This is the recommended start because the existing controlled documents already define the required stack, module layout, domain/API boundary, adapter contracts, fixture commands, evidence shape, and no-live-action constraints for SLICE-A. Later milestones depend on the runtime and evidence shape produced by M1.

## 6. Milestone-gated gap closure

The following specifications are not blockers for M1, but they must be closed before the indicated milestone:

| Gap | Required before | Rationale |
|---|---:|---|
| Editor adapter bridge specification | M3 | The editor is the front-end for canonical document operations and projection evidence. |
| Credential backend implementation decision | M2/M7 | GitHub clone-only and credential-reference behavior depend on a concrete protected-store strategy. |
| Evaluation runner I/O contract | M6 | The runner must define command layout, resource limits, sandbox boundary, and evidence schema before code. |
| Exporter implementation specification | M8 | DOCX/HWPX output needs controlled writer behavior and fidelity thresholds before implementation. |
| Authorization implementation specification | M5 | Submission/review workflows require executable authorization behavior, not only UI hiding. |
| GitHub mock-http fixture format specification | M7 follow-up | Mock replay, deterministic retry/backoff, and rate-limit/error fixture evidence must be closed before mock-http adapter behavior is claimed beyond clone-only envelope evidence. |
| GitHub clone-readonly integration-point boundary specification | M7 follow-up | Allowlist record, gate approval envelope, credential-reference status contract, dry-run clone plan envelope, and fail-closed safety guards must be closed as a fixture-local boundary before any live `clone-readonly` execution is considered under separate user-executed approval. |
| Rendering pipeline implementation specification | M8 | Export/demo evidence depends on rendering and projection behavior. |
| Observability and diagnostics specification | M5 | State, submission, sync, and recovery flows require diagnosable evidence. |

## 7. Traceability update rule

RTM rows may remain grouped planning coverage until their milestone produces executable tests and evidence. After each milestone, update the RTM and affected STD rows from grouped planning coverage to exact implementation evidence only when the corresponding RED/GREEN records, command outputs, evidence manifests, and risk-control checks exist.
