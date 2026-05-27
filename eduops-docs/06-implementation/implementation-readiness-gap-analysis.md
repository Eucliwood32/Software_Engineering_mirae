---
document_id: SWENG-EDUTECH-IMPL-GAP
title: Implementation Readiness Gap Analysis
version: 0.1
status: Draft
owner: SYSaI Lab
created: 2026-05-13
updated: 2026-05-13
traceability:
  iso9001: ['7.5', '8.3', '8.5', '9.1']
  related: ['SWENG-EDUTECH-SRS', 'SWENG-EDUTECH-DDP', 'SWENG-EDUTECH-ROADMAP']
---

# Implementation Readiness Gap Analysis

## 1. Purpose

This document records the combined Codex and Claude read-only implementation-readiness review of the EduOps controlled draft package. It converts advisory review output into controlled implementation gaps before source-code work starts.

## 2. Review inputs

| Reviewer | Mode | Evidence boundary | Limitation |
|---|---|---|---|
| Codex CLI | Read-only advisory architecture review | Focused on code-level executability: module boundaries, package layout, adapters, schemas, runner, fixtures, tooling. | Local sandbox could not read files directly; findings were based on the provided baseline summary and implementation-readiness prompt. |
| Claude Code | Read-only repository inspection and final synthesis | Inspected current controlled docs and identified remaining HOW-level gaps after storage architecture work. | Advisory only; Hermes performed final controlled-document synthesis. |
| Hermes | Orchestrator and document controller | Verified repository status and converted findings into draft controlled docs. | No source code implemented in this increment. |

## 3. Overall conclusion

The EduOps package is strong on **WHAT/WHY**: requirements, risks, decisions, storage policy, evidence boundaries, and V&V intent are present. It is not yet sufficient for autonomous implementation because the **HOW** contracts are under-specified.

The primary implementation risk is that the first developer or agent would make architecture choices inside code rather than through controlled design inputs. That would weaken ISO traceability and make the storage/editor/Git/evaluation baseline inconsistent.

## 4. Ranked implementation-readiness gaps

### P0 — coding start blockers

| Gap ID | Gap | Why it blocks coding | Required controlled output |
|---|---|---|---|
| IMPL-GAP-P0-001 | Technology stack is not fixed. | UI framework, runtime, IPC, editor embedding, packaging, local DB, and Git library choices shape all code layout. | `technology-stack-decision-record.md` |
| IMPL-GAP-P0-002 | Process topology and IPC contract are not fixed. | Desktop shell, local service, Git worker, evaluation runner, and export worker boundaries are unclear. | `process-topology-and-ipc-contract.md` |
| IMPL-GAP-P0-003 | Module/package layout is not fixed. | Developers do not know where domain, app, infra, adapters, fixtures, and tests belong. | `module-and-package-layout.md` |
| IMPL-GAP-P0-004 | Canonical domain IDL/schema is not machine-checkable. | Requirements name entities, but code cannot generate types/validators/fixtures from stable schemas. | `canonical-domain-idl.md` |
| IMPL-GAP-P0-005 | Internal command/query API is not signature-level. | UI and service implementation cannot proceed independently. | `internal-api-contract.md` |

### P1 — first vertical slice blockers

| Gap ID | Gap | Required controlled output |
|---|---|---|
| IMPL-GAP-P1-001 | Git adapter transaction/auth/conflict contract is missing. | `git-adapter-specification.md` |
| IMPL-GAP-P1-002 | Local storage adapter DDL/path/locking/migration contract is missing. | `local-storage-adapter-specification.md` |
| IMPL-GAP-P1-003 | Editor adapter bridge contract is missing. | `editor-adapter-bridge-specification.md` |
| IMPL-GAP-P1-004 | Evaluation runner I/O/sandbox contract is missing. | `evaluation-runner-io-contract.md` |
| IMPL-GAP-P1-005 | GitHub API adapter dry-run/live boundary is missing. | `github-adapter-specification.md` |
| IMPL-GAP-P1-006 | Fixture corpus and automated harness are not concrete. | `fixture-corpus-and-harness-plan.md` |
| IMPL-GAP-P1-007 | Build, packaging, dependency lock, and release engineering baseline is missing. | `build-packaging-release-engineering.md` |

### P2 — integration quality gaps

| Gap ID | Gap | Required controlled output |
|---|---|---|
| IMPL-GAP-P2-001 | State-machine transition tables are not code-ready. | `state-machine-implementation-tables.md` |
| IMPL-GAP-P2-002 | PDP/PEP authorization implementation contract is not signature-level. | `authorization-implementation-specification.md` |
| IMPL-GAP-P2-003 | Rendering adapter pipeline signatures are missing. | `rendering-pipeline-implementation-specification.md` |
| IMPL-GAP-P2-004 | DOCX/HWPX/HWP exporter adapter signatures are missing. | `exporter-implementation-specification.md` |
| IMPL-GAP-P2-005 | Observability, correlation IDs, and diagnostic package schema are missing. | `observability-and-diagnostics-specification.md` |

## 5. Implication for implementation

No live GitHub integration, live C/C++ grading, or classroom pilot should start until P0 docs exist and at least SLICE-A/B pass local fixture gates. Implementation should begin with a minimal vertical skeleton rather than a large horizontal component build.
