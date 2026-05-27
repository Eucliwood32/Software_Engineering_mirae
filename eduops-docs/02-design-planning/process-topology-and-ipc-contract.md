---
title: Process Topology and IPC Contract
document_id: SWENG-EDUTECH-PROCESS-IPC
version: 0.3.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CFR-002', 'EDUOPS-CFR-013', 'EDUOPS-CFR-014', 'EDUOPS-CFR-015']
  related: ['SWENG-EDUTECH-TECH-STACK-DR', 'SWENG-EDUTECH-INTERNAL-API']
---

# Process Topology and IPC Contract

## 1. Component topology

| Layer | Runtime boundary | Responsibilities | Forbidden responsibilities |
|---|---|---|---|
| Frontend/UI Shell | Tauri WebView2 UI process | Presentation, local routing, user intent, editor view, progress display. | Direct filesystem, Git, DB, runner, exporter, or network side effects. |
| Application Core/Local Backend | Tauri Rust command host | Authorization, command/query validation, state machines, audit, idempotency, orchestration, local DB transactions. | Rendering UI widgets or bypassing adapters for external side effects. |
| Worker Layer | Managed Rust worker tasks or child processes where isolation is required | Git jobs, export jobs, advisory evaluation jobs, diagnostic packaging, long-running CPU/file work. | Accepting unvalidated UI input or emitting unaudited state changes. |
| Adapter Layer | Rust traits plus fake/local/live implementations | Git, GitHub later, storage, exporter, runner, secret store, notification, search. | Owning product policy decisions. |
| Persistence/Evidence Layer | SQLite, canonical files, local Git repository, manifests, logs | Durable local state, canonical documents, projections, audit events, fixture artifacts. | Hidden source-of-truth caches. |

## 2. Lifecycle

1. UI shell starts and opens the local backend command host.
2. Backend loads app-default, system, user, course, repository, and runtime-override configuration according to [Configuration Contract](configuration-contract.md).
3. Backend validates configuration schema versions, workspace-root resolution, protected-key authorization, credential references, and offline/live-action gates.
4. Backend opens SQLite, checks schema version, and creates a boot `AuditEvent` containing the effective configuration hash and redacted merge trace.
5. Backend registers fake/local adapters by default in development and fixture modes.
6. UI queries session, effective capability profile, course list, pending jobs, and health status.
7. Long-running commands enqueue jobs and return a job handle.
8. Workers emit progress events and final result envelopes through the backend.
9. Shutdown drains cancellable jobs, checkpoints local state, closes DB/file handles, and writes a shutdown audit event.

Crash recovery uses persisted job records, idempotency keys, operation journals, and Git status checks. Ambiguous jobs resume only if their adapter contract declares resume-safe behavior; otherwise they become `requires_manual_review`.

## 3. External process rule

No external process may start unless an explicit backend command authorizes it and records an audit event. This includes Git CLI fallback, C/C++ compiler invocation, test runner invocation, DOCX/HWPX conversion, diagnostics packaging, or future network connector helpers.

## 4. Command/query envelope

```ts
interface RequestEnvelope<T> {
  request_id: string;
  correlation_id: string;
  actor: { actor_id: string; role: string; course_id?: string; workspace_id?: string };
  command_or_query: string;
  idempotency_key?: string;
  dry_run: boolean;
  live_external_action: false;
  payload: T;
}

interface ResultEnvelope<T> {
  request_id: string;
  correlation_id: string;
  status: 'ok' | 'accepted' | 'denied' | 'conflict' | 'validation_error' | 'failed';
  data?: T;
  error?: EduOpsError;
  audit_event_ids: string[];
  job_id?: string;
}

interface EduOpsError {
  code: string;
  message: string;
  retriable: boolean;
  user_visible: boolean;
  diagnostic_ref?: string;
}
```

## 5. Query behavior

Queries are side-effect-free except for bounded telemetry/audit reads explicitly declared in the API contract. Queries must not start Git, exporter, runner, or network work.

## 6. Command behavior

Commands validate authorization, state-machine guard, idempotency, fixture/live-action gate, and payload schema before side effects. Commands that may run longer than one UI interaction return `status='accepted'` with `job_id`.

## 7. Event contract

Progress events include `job_id`, `correlation_id`, `phase`, `percent_hint`, `state`, `message_code`, and optional `artifact_refs`. Events are informational until a final `ResultEnvelope` is persisted.


## 8. GitHub adapter runtime boundary

GitHub adapter execution is a worker-layer activity mediated by the application core. The UI shell can request a GitHub-related command only through the internal API. The application core validates authorization, configuration, credential-reference status, adapter mode, idempotency, and no-live-action gates before a worker invokes the adapter. The adapter returns evidence in a result envelope; the application core performs final state promotion and audit persistence.
