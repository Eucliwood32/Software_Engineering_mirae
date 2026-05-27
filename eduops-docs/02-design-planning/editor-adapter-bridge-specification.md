---
title: Editor Adapter Bridge Specification
document_id: SWENG-EDUTECH-EDITOR-ADAPTER-BRIDGE
version: 0.1.0
status: draft
created: 2026-05-21
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-DEC-067
    - SWENG-EDUTECH-BLOCK-SCHEMA
    - SWENG-EDUTECH-DOCUMENT-STORAGE
    - SWENG-EDUTECH-EDITOR-TRADE
    - SWENG-EDUTECH-KOREAN-TEXT
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-INTERNAL-API
    - EDUOPS-M3-SLICE-B-CANONICAL-DOCUMENT-EVIDENCE
  downstream:
    - IF-EDITOR-001
    - IF-STORAGE-001
    - IF-STORAGE-002
    - IF-STORAGE-004
---

# Editor Adapter Bridge Specification

## 1. Purpose

This document defines the local-safe HOW-level bridge between the EduOps canonical block document model and a future desktop editor adapter. It converts the prior M3 editor-bridge blocker into an implementation-facing specification without adopting an editor runtime, installing dependencies, launching a desktop UI, capturing real IME behavior, or claiming DEMO-1 readiness.

The editor UI is not the source of truth. The bridge shall translate between an editor runtime document and EduOps-owned canonical structures: `BlockDocument`, `EditorBlock`, operation journals, deterministic projections, validation hooks, and materialized evidence files.

## 2. Scope and non-claims

### 2.1 In scope

This specification defines:

- editor toolkit selection criteria and the fixture-gated primary/fallback stance;
- canonical block to editor-node mapping rules;
- editor transaction import/export rules for operation-journal entries;
- Korean IME composition, autosave suppression, and undo grouping requirements;
- validation, privacy, export-binding, and required-block hook points;
- error and rollback behavior;
- fixture-local verification anchors for later RED/GREEN implementation tasks.

### 2.2 Out of scope

This checkpoint does not authorize or claim:

- runtime adoption of Tiptap, ProseMirror, Lexical, Markdown-first, Monaco, or a custom editor;
- package installation or external download;
- real Tauri runtime invocation, desktop launch, WebView2/WebKitGTK execution, screenshot capture, or screen-recording capture;
- live Korean IME capture or OS input-event testing;
- mutation of non-fixture or user data;
- credential lookup, credential storage, network call, GitHub API call, remote action, repository administration, push, publication, installer creation, or deployment;
- DEMO-1 acceptance or live editor integration.

## 3. Controlled anchors

| Anchor | Use in this specification |
|---|---|
| [Editor block schema baseline](block-schema.md) | Canonical block fields, initial block types, privacy/export/evidence fields, warning model, block identity rules. |
| [Notion-style document storage architecture](notion-style-document-storage-architecture.md) | Source-of-truth rule, operation journal, local-only autosaves/indexes, materialization, checkpoint, migration, tombstone, and Git inclusion rules. |
| [Editor stack trade study](editor-stack-trade-study.md) | Fixture-gated mature web-document substrate stance and storage conformance gates. |
| [Korean text handling profile](korean-text-handling-profile.md) | NFC normalization, composition safety, autosave suppression, and Korean text preservation. |
| [Process topology and IPC contract](process-topology-and-ipc-contract.md) | UI/backend boundary, command/query envelopes, no direct UI filesystem/Git/DB side effects. |
| [Internal API contract](internal-api-contract.md) | `document.saveOperation`, `document.materializeProjection`, `document.load`, and envelope/error conventions. |
| [M3 SLICE-B canonical document gate evidence](../06-implementation/m3-slice-b-canonical-document-evidence.md) | Accepted canonical document, projection, operation replay, local materialization, and Korean projection fixture scope. |
| [M3 bridge local-safe authority](../05-decisions/m3-editor-bridge-local-safe-spec-authority-2026-05-21.md) | Authority boundary for authoring this specification only. |

## 4. Bridge placement and responsibilities

The bridge belongs between the desktop UI shell and the application-core document storage service.

```text
Editor runtime document
  <-> EditorAdapterBridge
    <-> canonical BlockDocument / EditorBlock
    <-> EditOperation journal
    <-> materialized .eduops.json / .md / .manifest.json
```

The bridge shall:

1. receive editor-view transactions or serialized editor state from the UI shell;
2. normalize them into EduOps-owned block IDs, order keys, payloads, attributes, privacy classes, validation states, and export bindings;
3. emit `EditOperation` candidates for the application core to validate and append;
4. render canonical `BlockDocument` state back into editor runtime state without making vendor-internal state authoritative;
5. preserve Korean text and IME composition boundaries without creating partial journal evidence;
6. expose validation hooks so required-block, privacy, export, and evidence checks can run before materialization or checkpoint.

The bridge shall not:

- read or write the filesystem directly;
- call Git, GitHub, exporters, runners, credential stores, or network APIs;
- own authorization policy or product state-machine decisions;
- treat editor-vendor JSON as canonical evidence unless normalized into EduOps canonical JSON.

## 5. Toolkit stance and selection criteria

The initial implementation candidate is a ProseMirror/Tiptap-style editor substrate, with Markdown-first editing as fallback and Monaco limited to code-block subcomponents. This stance follows the editor trade study and remains fixture-gated.

A toolkit may be promoted from candidate to implementation dependency only when a separate controlled decision records fixture evidence for:

| Criterion | Required bridge evidence |
|---|---|
| Canonical schema control | Editor state exports to EduOps `BlockDocument` without hidden vendor-only authoritative fields. |
| Stable block identity | EduOps `block_id` persists across update, reorder, delete/tombstone, copy, and recovery flows. |
| Deterministic order serialization | Parent/order keys are exported deterministically without relying on hidden row order. |
| Operation derivation | Insert, update, move, delete, validate, asset attach, and export-bind intentions can be captured or derived as explicit operation candidates. |
| Korean IME stability | Composition events do not emit partial journal entries, duplicate characters, corrupt Hangul syllables, or split block boundaries. |
| Autosave and undo behavior | Autosave suppresses uncommitted composition text and undo groups composition into user-meaningful steps. |
| Code/table handling | Code indentation, language labels, line references, table headers, alignment, and cell shape round-trip through canonical payloads. |
| Accessibility | Keyboard navigation, focus state, and screen-reader semantics are testable through fixture or user-executed gates. |
| License/security | Dependency license and package risk are accepted by a separate controlled dependency decision. |

This document is not that dependency decision.

## 6. Canonical mapping rules

### 6.1 Document envelope

The adapter bridge shall map editor document state to canonical document fields as follows:

| Canonical field | Bridge source/rule |
|---|---|
| `document_id` | Supplied by application core; never generated from editor DOM order. |
| `schema_version` | Must equal the accepted block schema label for the implementation slice. Unsupported versions fail closed or open read-only. |
| `owner_scope` / `privacy_class` | Supplied by application core or validated block attributes; UI cannot escalate scope. |
| `root_block_ids` / block order | Derived from explicit parent/order keys controlled by EduOps. |
| `blocks` | Normalized from supported editor nodes into canonical `EditorBlock` records. |
| `asset_refs` | References only; asset write/upload behavior is out of scope for the bridge. |
| hashes | Computed by canonical storage/materialization code, not by the editor runtime. |

### 6.2 Block mapping

The bridge shall support the accepted M3 baseline first:

| Canonical block type | Editor-node expectation | Required mapping behavior |
|---|---|---|
| `heading` | Heading node with level attribute | Preserve text content, level, role, privacy class, validation state, and export binding. |
| `paragraph` | Paragraph/text node | Preserve Korean/English mixed text with NFC normalization before canonical hashing/projection. |
| `checklist` | Task-list item or equivalent structured node | Preserve checked state, required flag, role, validation state, and order key. |
| `code` | Code-block node or Monaco-backed code subcomponent | Preserve language label, exact text, indentation, and optional file/line binding metadata. |
| `table` | Table node or structured table submodel | Preserve header cells, row shape, alignment, and deterministic column order. |

Deferred typed blocks (`image`, `diagram`, `experiment`, `decision`, `reflection`, `reference`, `export_placeholder`) shall be represented as unsupported/deferred canonical block payloads or read-only placeholders until their separate fixture tests exist. The bridge must not silently drop unsupported typed-block semantics; it shall emit validation warnings or fail closed according to the validation profile.

### 6.3 Identity and ordering

- `block_id` is EduOps-owned and stable. The bridge shall store it in editor node attributes when the toolkit supports custom attributes.
- Reorder operations preserve `block_id` and update only parent/order metadata.
- Delete operations produce tombstone-capable operation candidates; the bridge shall not hard-delete evidence before checkpoint policy permits it.
- Copy/clone, split, merge, and schema migration behavior remain deferred until explicit tests and lineage rules are promoted.

## 7. Operation journal import/export

The bridge translates editor transactions into operation candidates. The application core validates authorization, idempotency, base revision, schema version, and live-action gates before appending them to the journal.

| Editor intention | Operation candidate | Bridge rule |
|---|---|---|
| Insert supported block | `insert_block` | Include parent, order key, canonical block payload, role, privacy class, and validation state. |
| Edit supported block content or attributes | `update_block` | Preserve `block_id` and `order_key`; include before/after content hashes when available. |
| Reorder or nest block | `move_block` | Include source parent/order and target parent/order; do not rewrite unrelated block IDs. |
| Delete block | `delete_block` | Emit tombstone intent; do not erase comment/export/validation bindings. |
| Attach local asset reference | `attach_asset` | Emit reference-only candidate; actual asset persistence/privacy/LFS policy is handled by storage/export services. |
| Required/privacy/export validation update | `validate_block` or `bind_export` | Emit structured validation/export-binding candidates only after profile checks. |

The bridge may coalesce low-level editor transactions into one user-meaningful operation when the transaction sequence is atomic from the user perspective, including IME composition and undo groups.

Operation candidates shall include:

- `document_id`;
- `base_revision`;
- `actor` reference supplied by the application core;
- `operation_type`;
- canonical payload patch;
- idempotency or transaction correlation key;
- no-live-action marker inherited from the command envelope.

## 8. Korean IME, autosave, and undo contract

The bridge shall expose and preserve composition state.

| Event/state | Required behavior |
|---|---|
| `compositionstart` | Mark the active block/text range as composing; do not append an operation journal entry. |
| `compositionupdate` | Keep volatile editor state only; do not materialize canonical evidence from partial composition text. |
| `compositionend` | Normalize final text to NFC and emit one user-meaningful update operation if content changed. |
| Autosave timer during composition | Suppress canonical materialization and journal append for the composing range; may store local volatile recovery state outside controlled evidence. |
| Undo after composition | Undo the committed composition as one semantic text edit unless the editor runtime exposes a stricter user-visible boundary. |
| Block split/merge during composition | Fail closed or defer operation until composition ends; never create partial Hangul syllable journal entries. |

The future test fixture shall include Korean/English mixed paragraph text and Hangul syllable composition scenarios. This specification does not perform real OS IME capture.

## 9. Validation hooks

Before an operation candidate is accepted, the bridge/application-core boundary shall expose hooks for:

- schema-version validation;
- block ID uniqueness and scope prefix validation;
- required-block presence and checklist state;
- privacy-class validation and student/private/course visibility policy;
- export-binding validation and unsupported-block warning generation;
- code/table payload validation;
- Korean text NFC normalization check;
- path-scope and owner-scope validation for materialization requests;
- no-live-action and adapter-mode gates.

Validation results are canonical data, not UI-only styling. A UI indicator may display validation state, but authoritative validation is performed by application core/storage services and recorded through result envelopes, manifests, or operation evidence.

## 10. Error and rollback model

| Failure | Required bridge behavior |
|---|---|
| Unsupported editor node | Reject the transaction or emit an explicit unsupported-block validation warning when the profile allows lossy representation. |
| Missing or duplicate `block_id` | Reject operation candidate before journal append. |
| Unsupported schema version | Open read-only or fail closed; do not silently migrate. |
| Operation replay conflict | Return conflict status through the application core; do not mutate canonical files. |
| Materialization failure | Preserve prior canonical snapshot; emit validation/error envelope with diagnostic reference when available. |
| Composition boundary violation | Suppress journal append and request user-visible retry or composition-end handling. |
| Rollback after rejected operation | Re-render from last accepted canonical revision; editor runtime transient state is discarded or marked unsaved. |

Rollback shall use the last accepted canonical document revision, not vendor runtime undo state as the source of truth.

## 11. Command/query binding

The initial implementation binding shall use the existing internal API contract rather than a direct editor-to-filesystem path.

| API surface | Bridge use |
|---|---|
| `document.load` | Load canonical `BlockDocument` and render editor runtime state. |
| `document.saveOperation` | Submit validated operation candidate for journal append. |
| `document.materializeProjection` | Request canonical JSON/Markdown/manifest materialization after accepted operations. |
| `job.getStatus` | Observe long-running materialization or validation jobs if later needed. |

All command/query calls use the process-topology `RequestEnvelope`/`ResultEnvelope` conventions. Protected commands include correlation, actor, dry-run/live-action flags, idempotency where applicable, and audit event identifiers.

## 12. Fixture-local verification anchors

Later implementation rows should start with RED tests before product code. Candidate test anchors are:

| Anchor | Expected fixture evidence |
|---|---|
| `TC-M3-EDITOR-BRIDGE-001` canonical node export | A fixture editor-state JSON maps heading/paragraph/checklist/code/table nodes into `BlockDocument` with stable block IDs and deterministic order. |
| `TC-M3-EDITOR-BRIDGE-002` canonical state import | A canonical `BlockDocument` renders back into fixture editor-state JSON without introducing vendor-only authoritative fields. |
| `TC-M3-EDITOR-BRIDGE-003` journal operation derivation | Insert/update/move/delete fixture transactions produce expected operation candidates without mutating files. |
| `TC-M3-EDITOR-BRIDGE-004` Korean composition suppression | Composition-start/update/end fixture events produce no partial journal entries and one final NFC-normalized update. |
| `TC-M3-EDITOR-BRIDGE-005` validation fail-closed | Duplicate IDs, unsupported schema, unsupported node loss, and privacy/export violations return validation errors or explicit warnings. |
| `TC-M3-EDITOR-BRIDGE-006` rollback | Rejected operation re-renders from the last accepted canonical revision. |

These are fixture-local test anchors only. They do not require a live editor runtime, OS IME capture, desktop launch, or package installation.

## 13. Acceptance criteria for this specification

This specification is ready for constrained gate acceptance when:

- it is linked from `docs/README.md` and `docs/INDEX.md`;
- it references the accepted M3 bridge authority and prior blocker without deleting their non-claim boundaries;
- local Markdown links resolve;
- JSON files parse;
- `git diff --check` passes;
- `npm run m0:check` passes;
- `ralph.md` records the PREP completion and the next gate/refill state;
- no live/editor/runtime/credential/network/remote action was executed.

## 14. Traceability

| Requirement/design/test family | Bridge coverage |
|---|---|
| `EDUOPS-FR-047`..`EDUOPS-FR-051` | Block editor and authoring runtime controls through canonical bridge, storage, validation, Korean text, and projection behavior. |
| `EDUOPS-NFR-018` | Korean text handling and composition safety. |
| `EDUOPS-NFR-019` | Editor/storage performance remains fixture-gated before runtime selection. |
| `IF-EDITOR-001` | Save canonical block document through controlled operation candidates. |
| `IF-STORAGE-001` | Append edit operation after validation and authorization. |
| `IF-STORAGE-002` | Materialize canonical revision after accepted operations. |
| `STD-039`..`STD-044` | Future editor/canonical document fixture tests. |
| `STD-056`..`STD-067` | Future storage, journal, projection, migration, and index tests. |

## 15. Change log

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-05-21 | Initial local-safe HOW-level editor adapter bridge specification authored under `EDUOPS-DEC-067`. |
