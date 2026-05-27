---
title: Editor Adapter Bridge TC-003 Fixture Source Contract Specification
document_id: EDUOPS-EDITOR-ADAPTER-BRIDGE-TC-003-FIXTURE-SOURCE-CONTRACT-SPECIFICATION
version: 0.1.0
status: draft
date: 2026-05-21
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-EDITOR-ADAPTER-BRIDGE-SPECIFICATION
    - EDUOPS-EDITOR-ADAPTER-BRIDGE-TC-001-FIXTURE-SOURCE-CONTRACT-SPECIFICATION
    - EDUOPS-EDITOR-ADAPTER-BRIDGE-TC-002-FIXTURE-SOURCE-CONTRACT-SPECIFICATION
    - EDUOPS-DEC-067
    - SWENG-EDUTECH-MODULE-LAYOUT
    - SWENG-EDUTECH-BLOCK-SCHEMA
  gaps_recorded:
    - Toolkit-neutral fixture editor-transaction JSON input shape prerequisite for the `TC-M3-EDITOR-BRIDGE-003` journal operation derivation (editor transactions → canonical `EditOperation` candidates) RED test bucket
---

# Editor Adapter Bridge TC-003 Fixture Source Contract Specification

## 0. Document scope

This specification defines only the controlled HOW-level toolkit-neutral fixture editor-transaction JSON input contract that the future [Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) §12 `TC-M3-EDITOR-BRIDGE-003` (journal operation derivation per §7 operation journal import/export) RED test bucket may consume, and the deterministic derivation rules that produce canonical `EditOperation` candidates matching the existing canonical journal contract in `crates/eduops_domain/src/lib.rs` (the `EditOperationKind` enum, `EditOperation` struct, `DocumentJournalState` struct, and `replay_journal` function authored at the M3-T3 GREEN gate).

This document does **not**:

- author any fixture JSON artifact under `fixtures/editor_adapter_bridge/`;
- author the future `TC-M3-EDITOR-BRIDGE-003` RED/GREEN test bucket at `crates/eduops_domain/tests/m3_editor_bridge_003_journal_operation_derivation.rs`;
- modify the existing `crates/eduops_domain/src/editor_bridge/mod.rs` module (the future GREEN cycle may add a derivation function under the same module per the module placement note at `dd710a6`);
- modify the existing `crates/eduops_domain/src/lib.rs` canonical journal types `EditOperationKind`, `EditOperation`, `DocumentJournalState`, or the `replay_journal` function;
- adopt or install any editor toolkit runtime (Tiptap, ProseMirror, Lexical, Markdown-first, Monaco, or custom);
- invoke a real Tauri runtime, desktop window, IME capture, screenshot, screen-recording, host runtime install, installer publication, Git command, credential lookup, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, DEMO-1 acceptance, or user-managed external-repo action.

Acceptance of this specification is acceptance of the **fixture source contract only**. Fixture JSON authoring, bridge derivation-direction implementation, RED/GREEN test authoring, GREEN implementation, and the companion STD/RTM addenda remain separately gated Ralph follow-ups, and each must preserve every bridge specification §2.2 non-claim.

## 1. Purpose

The bridge specification §12 anchor `TC-M3-EDITOR-BRIDGE-003` (journal operation derivation) requires that "fixture insert / update / move / delete editor transactions deterministically produce operation candidates whose journal-entry shape matches the canonical journal contract; no editor toolkit runtime, no filesystem mutation outside the test sandbox, no real Tauri IPC, no live IME capture." Bridge specification §7 lists six editor intentions (insert / update / move / delete / attach asset / validate or bind export) with operation-candidate rules but does not commit to a concrete fixture transaction shape; the future RED test bucket cannot deterministically assert its output without a pinned input shape and a pinned derivation rule.

This specification closes that prerequisite gap by defining:

1. the input contract (a deterministic toolkit-neutral fixture editor-transaction JSON envelope);
2. the constrained derivation subset admitted by this contract v0.1.0 (insert / update / delete map directly to the existing canonical `EditOperationKind`; move / attach asset / validate or bind export are explicitly deferred);
3. the per-transaction shape and per-kind reverse-mapping rules;
4. the deterministic derivation rules that produce canonical `EditOperation` candidates;
5. the future test bucket / module / fixture file placement boundary;
6. validation rules for fixture JSON authoring;
7. acceptance and non-claim boundaries for the future RED/GREEN cycle.

## 2. Authorized fixture-data boundary

The only fixture root admitted by this contract v0.1.0 is:

```text
fixtures/editor_adapter_bridge/tc-003-journal-operation-derivation/
```

This root is the natural sibling of the `tc-001-canonical-node-export/` and `tc-002-canonical-state-import/` roots and is the appropriate placement for the `TC-M3-EDITOR-BRIDGE-003` anchor under the bridge fixture-data placement recorded in [Module and Package Layout](module-and-package-layout.md) §7. Adding sibling roots for `TC-M3-EDITOR-BRIDGE-004..006` requires a separate later contract or version bump.

Rules:

1. Every fixture JSON path shall be repo-relative and start with `fixtures/editor_adapter_bridge/`.
2. Every fixture JSON path shall use `/` separators and shall not contain `..`, absolute-path syntax, drive prefixes, NUL bytes, or shell metacharacter semantics.
3. Fixture JSON content shall be UTF-8 with NFC normalization already applied to text-bearing fields (Korean composition shall not appear in partial form).
4. Fixture JSON shall not contain raw credentials, raw repository URLs with credentials, raw email addresses, GitHub PAT prefixes (`ghp_`/`github_pat_`), or any other live-secret form.
5. Fixture JSON shall not contain instructions to perform a network call, a Git command, a credential lookup, a desktop launch, an IME capture, a screenshot, a host-runtime install, an installer publication, or any user-managed external-repo action.

The future TC-003 RED test bucket MAY take one of two equally acceptable shapes (acceptance does not require choosing one ahead of authoring):

- **In-memory transaction sequence:** the test constructs the fixture editor-transaction JSON inline as a Rust string literal (or reuses a small embedded fixture under `crates/eduops_domain/tests/`), derives the canonical `EditOperation` candidates via the future derivation function, and asserts that `replay_journal(initial_document, &candidates)` produces the expected `DocumentJournalState`. In this shape no new fixture JSON artifact is authored under §2.
- **Committed fixture artifact:** the test loads a controlled fixture JSON at `fixtures/editor_adapter_bridge/tc-003-journal-operation-derivation/<name>.json` and asserts the same derivation + replay invariants. In this shape one or more new fixture JSON artifacts are authored under §2 rules and §6 validation.

## 3. Input contract: toolkit-neutral fixture editor-transaction JSON envelope

The top-level object shall use a closed-key envelope that mirrors the TC-001/TC-002 envelopes for consistency. The top-level object shall contain these keys in alphabetical order when serialized as canonical JSON:

| Key | Type | Rule |
|---|---|---|
| `actor_id` | string | The fixture actor identifier consumed by the derivation function as the `EditOperation.actor_id` source. Shall be a non-empty NFC string with no PII / no raw credential form. |
| `base_revision_id` | string | The revision id that the first derived `EditOperation` shall use as `base_revision_id`. Subsequent derived operations chain via `resulting_revision_id`. The format mirrors the existing canonical journal's `rev_NNN` convention. |
| `document_id` | string | The target document identifier. Shall equal the `document_id` of the `initial_document` consumed in the future test bucket. |
| `editor_kind` | string | Literal `fixture-toolkit-neutral`. |
| `path_scope` | string | Closed-set token from `OwnerScope` canonical variants: one of `workspace`, `assignment`, `knowledge`. Drives the derived `EditOperation.path_scope` field. |
| `schema_version` | string | Literal `0.1.0`. The fixture contract version, distinct from the bridge specification version and the canonical block schema version. |
| `transactions` | array | Sorted by `sequence_index` ascending. Each element is a fixture transaction object per §4. |

Canonical JSON layout (illustrative envelope without `transactions` content):

```json
{
  "actor_id": "professor-tc003",
  "base_revision_id": "rev_000",
  "document_id": "doc-tc-003-journal-operation-derivation-baseline",
  "editor_kind": "fixture-toolkit-neutral",
  "path_scope": "workspace",
  "schema_version": "0.1.0",
  "transactions": []
}
```

The envelope shall not emit any vendor-only authoritative field, document-level metadata beyond these seven keys, document audit, owner-scope hierarchy, assignment binding, manifest, or operation journal output fields. Those fields remain canonical-`BlockDocument` / canonical-`EditOperation`-only.

## 4. Fixture transaction object

Each element of `transactions[]` shall be an object with these closed-key fields in alphabetical order:

| Key | Type | Rule |
|---|---|---|
| `kind` | string | Closed-set token: one of `insert`, `update`, `delete`. The bridge spec §7 also enumerates `move`, `attach_asset`, `validate_block`, and `bind_export`; those are explicitly out of scope for this contract v0.1.0 per §5.2 and shall fail validation at fixture-author time. |
| `op_id` | string | The fixture-supplied identifier for the derived `EditOperation.op_id`. Shall be non-empty NFC and unique within the document. |
| `payload` | object | Kind-specific payload. See §5.1. |
| `resulting_revision_id` | string | The revision id that the derived `EditOperation.resulting_revision_id` shall use. Subsequent transactions shall chain via this value. The format mirrors the existing canonical `rev_NNN` convention. |
| `sequence_index` | integer | Zero-based monotonically increasing transaction order within the document. The `transactions[]` array shall be sorted by this field ascending; gaps are not permitted. |
| `timestamp` | string | NFC string consumed as the derived `EditOperation.timestamp`. The format is not pinned by this contract v0.1.0 (the future derivation function passes through the string verbatim). |

No additional keys are admitted at the transaction level. Unknown keys shall be rejected at fixture-author time with a `M3_EDITOR_BRIDGE_TC003_*` error code (the exact code is enumerated by the future derivation-direction implementation; this specification does not prescribe the exact identifier).

## 5. Constrained derivation subset and per-kind rules

### 5.1 In-scope transaction kinds

This contract v0.1.0 admits exactly three transaction kinds, mirroring the three variants of the existing canonical `EditOperationKind`:

#### 5.1.1 `kind: "insert"`

The `payload` object shall carry a complete canonical `EditorBlock` shape (the same shape produced by TC-001's canonical node export — `block_id`, `role`, `order_key`, `payload` per the canonical `BlockPayload` enum, `parent_block_id`, `privacy_class`, `validation_state`). The derivation function shall produce a `EditOperationKind::InsertBlock { block }` whose `block` field is the canonical `EditorBlock` reconstructed from the fixture payload.

The derived `EditOperation` shall carry:

- `op_id` = fixture `op_id`;
- `document_id` = envelope `document_id`;
- `base_revision_id` = the envelope `base_revision_id` for `sequence_index == 0`, or the previous transaction's `resulting_revision_id` otherwise;
- `actor_id` = envelope `actor_id`;
- `timestamp` = fixture `timestamp`;
- `path_scope` = envelope `path_scope` mapped to `OwnerScope`;
- `kind` = `InsertBlock { block }`;
- `resulting_revision_id` = fixture `resulting_revision_id`.

#### 5.1.2 `kind: "update"`

The `payload` object shall carry exactly two keys in alphabetical order: `block_id` (string) and `payload` (the new canonical `BlockPayload` value — heading / paragraph / checklist / code / table per the canonical enum). The derivation function shall produce a `EditOperationKind::UpdateBlock { block_id, payload }`.

The derived `EditOperation` field-population rules mirror §5.1.1.

#### 5.1.3 `kind: "delete"`

The `payload` object shall carry exactly one key: `block_id` (string). The derivation function shall produce a `EditOperationKind::DeleteBlock { block_id }`.

The derived `EditOperation` field-population rules mirror §5.1.1.

### 5.2 Out-of-scope transaction kinds (deferred)

The bridge specification §7 table enumerates additional editor intentions that are **deferred** by this contract v0.1.0:

- `move_block` (reorder or nest): the existing canonical `EditOperationKind` exposes only `InsertBlock` / `UpdateBlock { payload }` / `DeleteBlock`; `UpdateBlock` does not currently carry an `order_key` or `parent_block_id` patch, so move cannot be derived under the existing canonical journal contract without either extending `EditOperationKind` (a product-scope change beyond this contract) or modeling move as a `DeleteBlock` + `InsertBlock` pair (which the existing `replay_journal` rejects via `EDUOPS_DOMAIN_JOURNAL_DUPLICATE_INSERT` when the deleted `block_id` is then re-inserted, because the deleted id enters `tombstoned_block_ids`). Therefore move support shall be enabled by either (a) a future canonical-journal extension to carry order/parent in `UpdateBlock`, or (b) a future canonical-journal extension introducing a dedicated `MoveBlock { block_id, new_order_key, new_parent_block_id }` variant; either choice requires its own PREP/T/GATE cycle.
- `attach_asset`: requires a controlled asset-reference contract that is not yet authored.
- `validate_block` / `bind_export`: requires the validation hooks per bridge specification §9 and the export-binding boundary per the canonical block schema, which are not authored as canonical journal candidates yet.

Authoring a fixture transaction with `kind` set to any of these deferred tokens shall fail validation at fixture-author time per §6 and shall not produce a canonical `EditOperation`.

### 5.3 Derivation determinism

The derivation function shall be a pure function of `(envelope, transactions[])` — no clock read, no random generation, no environment lookup, no filesystem read outside the explicit fixture path, no network call, no IPC. Identical inputs shall produce byte-identical canonical `EditOperation` candidate arrays.

The derived candidate array shall be returned in the same `sequence_index` order as the input. The derivation function shall not coalesce, reorder, split, or merge transactions; bridge spec §7's coalescing language ("the bridge may coalesce low-level editor transactions into one user-meaningful operation when the transaction sequence is atomic from the user perspective, including IME composition and undo groups") is explicitly out of scope for this contract v0.1.0 — TC-004 (Korean composition suppression) authors the coalescing rule.

### 5.4 Replay validity invariant

For an `initial_document` consumed alongside the derived candidate array, the invariant

```text
replay_journal(initial_document, &derived_candidates).is_ok()
```

shall hold whenever the fixture is authored to be replay-valid (i.e., the `base_revision_id`/`resulting_revision_id` chain is consistent, the inserted `block_id` values do not duplicate existing or tombstoned ids, updated/deleted `block_id` values reference live blocks). The future test bucket shall include at least one replay-valid fixture exercising all three in-scope `kind` variants.

The TC-003 RED test bucket MAY ALSO include negative fixtures that exercise the existing `replay_journal` rejection paths (`EDUOPS_DOMAIN_JOURNAL_DOCUMENT_MISMATCH`, `EDUOPS_DOMAIN_JOURNAL_REVISION_CHAIN`, `EDUOPS_DOMAIN_JOURNAL_DUPLICATE_INSERT`, `EDUOPS_DOMAIN_JOURNAL_TOMBSTONED_BLOCK`, `EDUOPS_DOMAIN_JOURNAL_UNKNOWN_BLOCK`). The derivation function shall pass through such fixtures unchanged; only `replay_journal` shall reject them. This separation preserves the §7 bridge rule that "the application core validates authorization, idempotency, base revision, schema version, and live-action gates before appending them to the journal".

## 6. Validation rules for fixture JSON authoring

Whether the future test bucket adopts the in-memory or committed-artifact shape, the fixture content shall pass these author-time checks:

1. Closed top-level key set per §3 (`actor_id`, `base_revision_id`, `document_id`, `editor_kind`, `path_scope`, `schema_version`, `transactions`); top-level keys appear in alphabetical order; no unknown top-level keys.
2. Closed transaction key set per §4 (`kind`, `op_id`, `payload`, `resulting_revision_id`, `sequence_index`, `timestamp`); transaction keys appear in alphabetical order; no unknown transaction keys.
3. `editor_kind == "fixture-toolkit-neutral"` and `schema_version == "0.1.0"` literals.
4. `path_scope` is one of `workspace`, `assignment`, `knowledge`.
5. `transactions[]` is sorted by `sequence_index` ascending, starts at zero, and has no gaps; no duplicate `sequence_index` value.
6. Every `kind` value is one of the three in-scope tokens (`insert`, `update`, `delete`); `move`, `attach_asset`, `validate_block`, and `bind_export` shall be rejected with a clear deferral-citation error.
7. Per-kind `payload` shape matches §5.1.1 / §5.1.2 / §5.1.3 exactly; no extra keys; required keys present; no `null` values for required keys.
8. For `insert`, the canonical `EditorBlock` shape inside `payload` follows the TC-001 baseline block kinds for `block.payload` (heading / paragraph / checklist / code / table); other variants are out of scope at the canonical level.
9. `op_id` is unique within `transactions[]`.
10. `block_id` referenced by `update` / `delete` (and by the inserted block in `insert`) is a non-empty NFC string with no raw credential / raw URL / PII form.
11. NFC normalization is applied to every text-bearing field (`actor_id`, `timestamp`, `payload` text content, table cells, code source).
12. No raw credential, raw repository URL with credential, raw email, GitHub PAT prefix, or other live-secret form anywhere in the document.
13. The `base_revision_id` and per-transaction `resulting_revision_id` form a consistent chain when replayed against the future `initial_document`; the future test bucket asserts this via `replay_journal`.

## 7. Future test bucket boundary

The future `TC-M3-EDITOR-BRIDGE-003` RED/GREEN test bucket shall be placed at:

```text
crates/eduops_domain/tests/m3_editor_bridge_003_journal_operation_derivation.rs
```

(sibling of `m3_editor_bridge_001_canonical_node_export.rs` at `fdc62d0` and `m3_editor_bridge_002_canonical_state_import.rs` at `076ecb9`.)

The future GREEN derivation function shall be added to the existing `crates/eduops_domain/src/editor_bridge/mod.rs` module per the module placement note at `dd710a6`. The function shape is illustrative only (the GREEN PREP/T/GATE cycle pins the exact signature):

```rust
pub fn derive_journal_operations_from_fixture_json(
    fixture_json: &str,
) -> Result<Vec<EditOperation>, BlockDocumentError>;
```

The future test bucket SHALL NOT:

- adopt a Cargo dependency for JSON parsing (the existing in-crate JSON value parser introduced at `fdc62d0` is reused);
- modify or extend the existing canonical `EditOperationKind` enum;
- modify or extend the existing `EditOperation` struct;
- modify or extend the existing `replay_journal` function;
- invoke a real Tauri runtime, desktop window, IME capture, or any live editor toolkit;
- read or write any file outside the explicit `fixtures/editor_adapter_bridge/tc-003-journal-operation-derivation/` path and `crates/eduops_domain/tests/` directory;
- perform a network call, a Git command, a credential lookup, an installer publication, or any user-managed external-repo action.

## 8. Relationship to controlled documents

- Upstream specification: [Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) v0.1.0 §7 (operation journal import/export) and §12 anchor `TC-M3-EDITOR-BRIDGE-003`.
- Sibling input-direction contract: [Editor Adapter Bridge TC-001 Fixture Source Contract Specification](editor-adapter-bridge-tc-001-fixture-source-contract-specification.md) v0.1.0.
- Sibling output-direction contract: [Editor Adapter Bridge TC-002 Fixture Source Contract Specification](editor-adapter-bridge-tc-002-fixture-source-contract-specification.md) v0.1.0.
- Block model: [Editor block schema baseline](block-schema.md) — defines the canonical `EditorBlock` shape that the `insert` transaction `payload` reconstructs.
- Module placement: [Module and Package Layout](module-and-package-layout.md) §7 — authorizes `crates/eduops_domain/src/editor_bridge/mod.rs` and `fixtures/editor_adapter_bridge/`.
- Local-safe authority: [M3 editor bridge local-safe specification authority](../05-decisions/m3-editor-bridge-local-safe-spec-authority-2026-05-21.md) (`EDUOPS-DEC-067`) — authorizes Ralph to author this specification under the fixture-local docs/control increment boundary.
- Canonical journal anchor: `crates/eduops_domain/src/lib.rs` (`EditOperationKind`, `EditOperation`, `DocumentJournalState`, `replay_journal`) authored at the M3-T3 GREEN gate.

## 9. Acceptance boundary

Acceptance of this specification:

- pins the TC-003 fixture editor-transaction JSON envelope shape per §3;
- pins the per-transaction object shape per §4;
- pins the constrained derivation subset (insert / update / delete) and explicitly defers move / attach_asset / validate_block / bind_export per §5.2;
- pins the deterministic derivation rules per §5.3 and the replay validity invariant per §5.4;
- pins the future test bucket placement and module placement boundary per §7;
- preserves every bridge specification §2.2 non-claim and every prior TC-001/TC-002 spec acceptance-boundary item.

Acceptance of this specification does **not**:

- author any fixture JSON artifact;
- author the future RED test bucket;
- author the future GREEN derivation function;
- adopt a Cargo dependency;
- modify the existing canonical `EditOperationKind`, `EditOperation`, `DocumentJournalState`, or `replay_journal`;
- adopt an editor toolkit runtime;
- invoke a real Tauri runtime, desktop window, IME capture, screenshot, screen-recording, host runtime install, installer publication, Git command, credential lookup, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, DEMO-1 acceptance, or user-managed external-repo action;
- enable move / attach_asset / validate_block / bind_export derivation (each requires its own future PREP/T/GATE cycle with a paired canonical-journal extension or a paired validation/binding contract).

## 10. Change log

| Version | Date | Change |
|---|---|---|
| 0.1.0 | 2026-05-21 | Initial draft authored under `EDUOPS-DEC-067` (M3 editor bridge local-safe specification authority) for the `TC-M3-EDITOR-BRIDGE-003` journal operation derivation fixture source contract. Constrained derivation subset (insert / update / delete) pinned; move / attach_asset / validate_block / bind_export explicitly deferred. |
