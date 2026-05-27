---
document_id: SWENG-EDUTECH-IMPL-EXEC-PLAN
title: Implementation Executability Improvement Plan
version: 0.6
status: Draft
owner: SYSaI Lab
created: 2026-05-13
updated: 2026-05-14
traceability:
  iso9001: ['7.5', '8.3', '8.5', '9.1']
  related: ['SWENG-EDUTECH-SRS', 'SWENG-EDUTECH-DDP', 'SWENG-EDUTECH-ROADMAP']
---

# Implementation Executability Improvement Plan

## 1. Goal

Make the EduOps controlled draft package executable by defining the missing HOW-level contracts before code implementation.

## 2. Execution principle

Use **controlled vertical-slice readiness**:

1. Close P0 architecture contracts.
2. Build a local-only empty vertical skeleton.
3. Add editor canonical persistence.
4. Add roster/identity and workspace provisioning through fake/local Git.
5. Add assignment sync/submission.
6. Add advisory C/C++ runner.
7. Only then evaluate live GitHub and export integrations behind fixture gates.

## 3. P0 controlled-document backlog

| Order | Document | Purpose | Acceptance gate |
|---|---|---|---|
| P0-1 | `technology-stack-decision-record.md` | Select desktop UI shell, runtime/service language, editor substrate, local DB, Git library, exporter substrate, packaging tool. | Reject/accept table exists; one baseline stack is selected; downstream docs reference it. |
| P0-2 | `process-topology-and-ipc-contract.md` | Define desktop shell, local service, Git worker, export worker, evaluation runner, lifecycle and crash recovery. | IPC transport and message envelope are defined; no live external process starts without explicit command. |
| P0-3 | `module-and-package-layout.md` | Define source tree, package names, layer dependency rules, forbidden dependencies, test fixture locations. | A new repo can be initialized from the layout without guessing paths. |
| P0-4 | `canonical-domain-idl.md` | Define machine-checkable schemas for Course, RosterEntry, Assignment, BlockDocument, EditOperation, SubmissionSnapshot, EvaluationRun, ExportJob, AuditEvent. | JSON Schema or equivalent IDL is complete enough to generate validators and fixtures. |
| P0-5 | `internal-api-contract.md` | Define command/query signatures for UI-to-service boundary and worker orchestration. | Command, input, output, error codes, audit event, and idempotency semantics are specified. |
| P0-6 | `fixture-corpus-and-harness-plan.md` | Define deterministic privacy-safe SLICE-A/B/C local fixture gates, artifacts, hashes, manifests, and no-live-action blockers. | Local fixture gates are enforceable before source-code slices and live side effects. |
| P0-7 | `state-machine-implementation-tables.md` | Define lifecycle, assignment, submission, conflict, and authoritative time transition tables. | Early slices can implement state guards without inventing labels in code. |
| P0-8 | `configuration-contract.md` | Define configuration scopes, precedence, workspace root, schema/versioning, profile key families, migration, and audit behavior. | SLICE-A boot, settings UI, adapter modes, and profile selection can be implemented without hidden defaults. |
| P0-9 | `credential-storage-contract.md` | Define OS-protected credential references, rotation, revocation, redaction, and student default-deny behavior. | GitHub and future connector credentials cannot be stored or logged as raw configuration values. |
| P0-10 | `configuration-fixture-plan.md` | Define deterministic merge, secret-leak, migration, invalid-config, zero-config, and offline-isolation gates. | Configuration behavior is verified before live GitHub/evaluation/export settings are enabled. |
| P0-11 | `requirements-traceability-matrix.md` | Map every SRS FR/NFR to design/interface anchors, STD/fixture tests, implementation slice, and evidence status. | SLICE-A tasks can be selected from exact requirement/test anchors instead of grouped requirements. |
| P0-12 | TDD evidence rule | Require RED failure, GREEN pass, and refactor/regression evidence for each implemented behavior. | Implementation commits can demonstrate test-first development. |

## 4. P1 controlled-document backlog

| Order | Document | Purpose | Acceptance gate |
|---|---|---|---|
| P1-1 | `git-adapter-specification.md` | Define plain Git operations, GitHub-first extension points, branch/checkpoint/submission transaction semantics. | Fake Git adapter and real Git CLI/lib adapter can be tested against the same contract. |
| P1-2 | `local-storage-adapter-specification.md` | Define SQLite/local index DDL, path normalization, file locks, migrations, rebuild policy. | Storage round-trip and index rebuild fixture can be executed. |
| P1-3 | `editor-adapter-bridge-specification.md` | Define editor transaction/event bridge, node-to-block mapping, IME hooks, operation journal append API. | Editor toolkit candidates can be scored with storage conformance gates. |
| P1-4 | `evaluation-runner-io-contract.md` | Define runner manifest, workdir layout, compiler discovery, timeout, result JSON, sandbox boundaries. | A single C++ fixture can run in advisory mode and emit deterministic result JSON. |
| P1-5 | `github-adapter-specification.md` | Define GitHub auth, dry-run/live boundaries, rate-limit, retry, token storage, mock server. | Dry-run GitHub fixture passes without network or credentials. |
| P1-6 | Fixture corpus expansion | Extend P0 fixtures for GitHub dry-run, runner samples, export documents, malformed files, accessibility, and performance. | Expanded fixture paths and commands are specified before the affected slices. |
| P1-7 | `build-packaging-release-engineering.md` | Define dev environment, package manager, lockfiles, lint/type/test commands, Windows/Linux packaging. | A developer can bootstrap a local dev environment from the document. |

## 5. Proposed vertical slices

| Slice | Name | Purpose | Key proof |
|---|---|---|---|
| SLICE-A | Empty vertical skeleton | Desktop shell/service/workers/local Git/local index can round-trip one empty course. | IPC ping, empty document save/load, empty checkpoint. |
| SLICE-B | Editor canonical path | Heading/paragraph blocks round-trip through editor JSON, Markdown projection, manifest, checkpoint. | Stable block IDs and deterministic hashes. |
| SLICE-C | Roster and identity | CSV roster import, pseudonymous student ID, local workspace provisioning. | Roster fixture and identity-binding audit event. |
| SLICE-D | Assignment sync and submission | Problem bank to assignment instance to student workspace to submission branch/snapshot. | queued/pushed/confirmed states proven against fake Git. |
| SLICE-E | C/C++ advisory runner | Single C++ submission builds/runs with resource/time limits and result JSON. | Deterministic result manifest and log hash. |
| SLICE-F | GitHub dry-run then sandbox | GitHub adapter passes mock server before optional sandbox org live test. | No live action until dry-run evidence passes. |
| SLICE-G | Export fixture | DOCX/HWPX derived export generated from canonical document and manifest. | Export fidelity fixture and loss warning manifest. |

## 6. Immediate recommendation

Do not start production code until the P0 architecture, state-machine, configuration, credential, fixture-gate, RTM, and TDD evidence controls are accepted. After P0 is accepted, implement SLICE-A with fake/local adapters only and record RED--GREEN--REFACTOR evidence for each behavior.


## 7. Ralph-loop readiness update

The [Ralph Loop Readiness Review](../00-research-analysis/ralph-loop-readiness-review.md) concluded that the next Ralph loop should produce documentation/test-card closure artifacts before product source code. The first approved loop target is `RALPH-DOC-LOOP-001`: executable SLICE-A/GH-SLICE-0 test cards, concrete fixture/harness schema, no-live-action assertions, and build/dev command baseline.


## 8. Ralph-loop closure package

`RALPH-DOC-LOOP-001` has been supplemented with exact test cards, concrete fixtures, build/dev commands, and minimal Git/storage adapter contracts. A bounded product-code loop may target only the cards in [SLICE-A and GH-SLICE-0 Executable Test Cards](../03-verification-validation/slice-a-executable-test-cards.md) after Claude/Codex re-review or explicit human approval.


## GitHub clone-only implementation constraint

Any implementation task that touches `crates/eduops_git/src/github/` shall implement only clone-source behavior unless a future controlled decision expands scope. Non-clone operations must fail before external request and produce `GITHUB_NON_CLONE_OPERATION_BLOCKED`.
