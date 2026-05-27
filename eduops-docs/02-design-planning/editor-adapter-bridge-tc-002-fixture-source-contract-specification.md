---
title: Editor Adapter Bridge TC-002 Fixture Source Contract Specification
document_id: EDUOPS-EDITOR-ADAPTER-BRIDGE-TC-002-FIXTURE-SOURCE-CONTRACT-SPECIFICATION
version: 0.1.0
status: draft
date: 2026-05-21
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-EDITOR-ADAPTER-BRIDGE-SPECIFICATION
    - EDUOPS-EDITOR-ADAPTER-BRIDGE-TC-001-FIXTURE-SOURCE-CONTRACT-SPECIFICATION
    - EDUOPS-DEC-067
    - SWENG-EDUTECH-MODULE-LAYOUT
    - SWENG-EDUTECH-BLOCK-SCHEMA
  gaps_recorded:
    - Toolkit-neutral fixture editor-state JSON output shape prerequisite for the `TC-M3-EDITOR-BRIDGE-002` canonical state import (`BlockDocument` → editor-state JSON) RED test bucket
---

# Editor Adapter Bridge TC-002 Fixture Source Contract Specification

## 0. Document scope

This specification defines only the controlled HOW-level toolkit-neutral fixture editor-state JSON output contract that the future [Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) §12 `TC-M3-EDITOR-BRIDGE-002` (canonical state import — the inverse direction of TC-001) RED test bucket may emit. The input is a canonical `BlockDocument` already defined by [Editor block schema baseline](block-schema.md); the output is a pure-data, vendor-neutral editor-state JSON of the same shape pinned by [Editor Adapter Bridge TC-001 Fixture Source Contract Specification](editor-adapter-bridge-tc-001-fixture-source-contract-specification.md) v0.1.0.

This document does **not**:

- author any fixture JSON artifact under `fixtures/editor_adapter_bridge/`;
- author the future `TC-M3-EDITOR-BRIDGE-002` RED/GREEN test bucket at `crates/eduops_domain/tests/m3_editor_bridge_002_canonical_state_import.rs`;
- modify the existing `crates/eduops_domain/src/editor_bridge/mod.rs` module (the future GREEN cycle may add an export function under the same module per the placement note);
- adopt or install any editor toolkit runtime (Tiptap, ProseMirror, Lexical, Markdown-first, Monaco, or custom);
- invoke a real Tauri runtime, desktop window, IME capture, screenshot, screen-recording, host runtime install, installer publication, Git command, credential lookup, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, DEMO-1 acceptance, or user-managed external-repo action.

Acceptance of this specification is acceptance of the **fixture source contract only**. Fixture JSON authoring (if needed for a fixture-driven round-trip), bridge export-direction implementation, RED/GREEN test authoring, GREEN implementation, and the companion STD/RTM addenda remain separately gated Ralph follow-ups, and each must preserve every bridge specification §2.2 non-claim.

## 1. Purpose

The bridge specification §12 anchor `TC-M3-EDITOR-BRIDGE-002` (canonical state import) requires that "a canonical `BlockDocument` renders back into a fixture editor-state JSON that uses only the canonical fields admitted by the bridge mapping; no vendor-only authoritative fields are introduced into the editor-state output, and the import-export round trip is stable across repeated calls." Bridge specification §6.2 describes the mapping rules but does not commit to a concrete export JSON shape; the future RED test bucket cannot deterministically assert its output without a pinned shape.

This specification closes that prerequisite gap by defining:

1. the input contract (a canonical `BlockDocument` with the five M3 baseline `BlockPayload` kinds);
2. the output editor-state JSON envelope (reusing the TC-001 closed-key envelope);
3. the per-kind reverse mapping (canonical `EditorBlock` → fixture node);
4. the canonical-block-only field projection (no vendor-only authoritative fields are introduced into the output);
5. deterministic block-id and order-key reuse rules;
6. round-trip determinism between TC-001 (import) and TC-002 (export);
7. the future test bucket / module / fixture file placement boundary;
8. acceptance and non-claim boundaries for the future RED/GREEN cycle.

## 2. Authorized fixture-data boundary

The only fixture root admitted by this contract v0.1.0 is:

```text
fixtures/editor_adapter_bridge/tc-002-canonical-state-import/
```

This root is the natural sibling of the `tc-001-canonical-node-export/` root and is the appropriate placement for the `TC-M3-EDITOR-BRIDGE-002` anchor under the bridge fixture-data placement recorded in [Module and Package Layout](module-and-package-layout.md) §7. Adding sibling roots for `TC-M3-EDITOR-BRIDGE-003..006` requires a separate later contract or version bump.

Rules:

1. Every fixture JSON path shall be repo-relative and start with `fixtures/editor_adapter_bridge/`.
2. Every fixture JSON path shall use `/` separators and shall not contain `..`, absolute-path syntax, drive prefixes, NUL bytes, or shell metacharacter semantics.
3. Fixture JSON content shall be UTF-8 with NFC normalization already applied to text-bearing fields (Korean composition shall not appear in partial form).
4. Fixture JSON shall not contain raw credentials, raw repository URLs with credentials, raw email addresses, GitHub PAT prefixes (`ghp_`/`github_pat_`), or any other live-secret form.
5. Fixture JSON shall not contain instructions to perform a network call, a Git command, a credential lookup, a desktop launch, an IME capture, a screenshot, a host-runtime install, an installer publication, or any user-managed external-repo action.

The future TC-002 RED test bucket MAY take one of two equally acceptable shapes (acceptance does not require choosing one ahead of authoring):

- **Round-trip-only:** the test reuses the existing TC-001 fixture at `fixtures/editor_adapter_bridge/tc-001-canonical-node-export/baseline.json` at `cb5ce52` as input, projects it into a canonical `BlockDocument` via the existing `eduops_domain::editor_bridge::project_fixture_json` function at `fdc62d0`, exports the resulting `BlockDocument` back to fixture editor-state JSON via the future export function, and asserts byte-identity against the original TC-001 fixture bytes. In this shape no new fixture JSON artifact is authored.
- **Expected-output fixture:** the test constructs a canonical `BlockDocument` inline (or loads it from a canonical-document JSON fixture under `crates/eduops_domain/tests/` or `fixtures/`) and asserts the exported editor-state JSON byte-identity against a controlled expected fixture JSON at `fixtures/editor_adapter_bridge/tc-002-canonical-state-import/<name>.json`. In this shape one new fixture JSON artifact is authored under §2 rules and §8 validation.

## 3. Input contract: canonical `BlockDocument`

The input to the future TC-002 export function is a canonical `BlockDocument` (defined by [Editor block schema baseline](block-schema.md) and constructed today by `crates/eduops_domain/src/lib.rs`) carrying at least the five M3 baseline `BlockPayload` kinds:

| `BlockPayload` variant | `EditorBlock` fields used | Notes |
|---|---|---|
| `Heading { text }` | `block_id`, `role`, `order_key`, `payload.text` | `role` is `heading-<level>` per the existing TC-001 import direction; the future export reverses this into the fixture `level` integer per §5.1. |
| `Paragraph { text }` | `block_id`, `order_key`, `payload.text` | `role` is the existing canonical paragraph role; fixture omits a `role` field per §5.2. |
| `Checklist { items }` | `block_id`, `order_key`, each `items[i].text` / `items[i].checked` | The existing canonical `ChecklistItem` carries only `text` and `checked`; fixture `indent` is regenerated per §5.3. |
| `Code { language, source }` | `block_id`, `order_key`, `payload.language`, `payload.source` | The fixture `lines` array is derived from `source` per §5.4. |
| `Table { alignments, header_row, body_rows }` | `block_id`, `order_key`, `header_row`, `body_rows` | The fixture omits `alignments` per §5.5 because TC-001 v0.1 does not represent it in the fixture. |

Every other `BlockPayload` variant beyond the five baseline kinds is out of scope for this contract v0.1.0 and shall be rejected by the future export function with a `M3_EDITOR_BRIDGE_EXPORT_*` error code (the exact code is enumerated by the future export-direction implementation; this specification does not prescribe the exact identifier).

The input `BlockDocument` shall already be the canonical structure produced by the TC-001 import direction (or the equivalent inline constructor); the future export function shall not re-validate canonical schema invariants that are the existing M3-T1/T2 responsibility.

## 4. Fixture editor-state JSON envelope (output)

The output object shall use the **same** closed-key envelope as the TC-001 fixture input contract (see TC-001 spec §3), so that the round-trip TC-001-input → TC-001-import → TC-002-export is byte-stable. The top-level object shall contain these keys in alphabetical order when serialized as canonical JSON:

| Key | Type | Rule |
|---|---|---|
| `document_id` | string | Equals the input `BlockDocument.document_id`. |
| `editor_kind` | string | Literal `fixture-toolkit-neutral`. The export shall not emit a Tiptap / ProseMirror / Lexical / Monaco / Markdown-first runtime kind. |
| `nodes` | array | Sorted by `order_key` ascending. See §5 for per-kind shapes. |
| `schema_version` | string | Literal `0.1.0`. The fixture contract version, distinct from the bridge specification version and the canonical block schema version. |

Canonical JSON layout (illustrative envelope without `nodes` content):

```json
{
  "document_id": "doc-tc-002-canonical-state-import-baseline",
  "editor_kind": "fixture-toolkit-neutral",
  "nodes": [],
  "schema_version": "0.1.0"
}
```

The export shall not emit any vendor-only authoritative field, document-level metadata beyond these four keys, document audit, owner-scope, schema version, assignment binding, manifest, or operation journal fields. Those fields remain canonical-`BlockDocument`-only.

## 5. Per-kind reverse mapping

Each canonical `EditorBlock` shall be exported as a fixture node object with `kind` plus the kind-specific keys below, in alphabetical key order. The §4 `nodes` array shall reuse the canonical `order_key` exactly so that sort order is identical.

### 5.1 `heading`

| Fixture key | Source rule |
|---|---|
| `block_id` | Equals `EditorBlock.block_id`. |
| `kind` | Literal `heading`. |
| `level` | Integer parsed from the canonical `EditorBlock.role` string `heading-<level>`. Valid range is 1..=6 per TC-001 spec §4.1; the export shall reject roles outside this range. |
| `order_key` | Equals `EditorBlock.order_key`. |
| `text` | Equals `BlockPayload::Heading.text`. NFC-normalized; the export shall not re-normalize defensively (the canonical text is already NFC). |

### 5.2 `paragraph`

| Fixture key | Source rule |
|---|---|
| `block_id` | Equals `EditorBlock.block_id`. |
| `kind` | Literal `paragraph`. |
| `order_key` | Equals `EditorBlock.order_key`. |
| `text` | Equals `BlockPayload::Paragraph.text`. |

### 5.3 `checklist`

| Fixture key | Source rule |
|---|---|
| `block_id` | Equals `EditorBlock.block_id`. |
| `items` | Ordered array; see §5.3.1. |
| `kind` | Literal `checklist`. |
| `order_key` | Equals `EditorBlock.order_key`. |

#### 5.3.1 Checklist item shape

For each `ChecklistItem` in `BlockPayload::Checklist.items`:

| Fixture key | Source rule |
|---|---|
| `checked` | Equals `ChecklistItem.checked`. |
| `indent` | Integer `0`. The canonical `ChecklistItem` does not carry indent (per TC-001 spec §4.3.1, `indent` is fixture input-shape data only and is not persisted in the canonical structure). The export shall therefore emit `0` for every item; nested checklist rendering remains deferred to a later bridge increment. A TC-001 fixture whose items carry non-zero `indent` round-trips through TC-002 export with `indent` reset to `0`; the round-trip determinism contract in §6 does not require preservation of `indent` because the canonical structure does not carry it. |
| `order_key` | Deterministic order key inside the checklist. The export shall regenerate `order_key` values as zero-padded decimal strings (`"0001"`, `"0002"`, …) matching the position of the item in the canonical `items[]` array, since the canonical `ChecklistItem` does not carry an order key field. The future test bucket that exercises the TC-001 round-trip shall use a TC-001 fixture whose checklist items already follow this zero-padded scheme so the round-trip is byte-stable. |
| `text` | Equals `ChecklistItem.text`. |

### 5.4 `code`

| Fixture key | Source rule |
|---|---|
| `block_id` | Equals `EditorBlock.block_id`. |
| `kind` | Literal `code`. |
| `language` | Equals `BlockPayload::Code.language` if `Some(...)`, otherwise the literal string `text`. |
| `lines` | Ordered array of strings produced by splitting `BlockPayload::Code.source` on `\n` (LF). The split shall preserve every line, including empty trailing lines if the source ends with `\n`. Individual line strings shall not contain `\n` or `\r`. CR-only or CRLF line endings are not in scope for v0.1.0 (the canonical source is expected to use LF; the future export function MAY reject non-LF sources or MAY normalize them — this contract leaves the choice to the future implementation but the chosen behavior shall be deterministic across repeated calls). |
| `order_key` | Equals `EditorBlock.order_key`. |

### 5.5 `table`

| Fixture key | Source rule |
|---|---|
| `block_id` | Equals `EditorBlock.block_id`. |
| `body_rows` | Ordered array; see §5.5.1. The array length equals the canonical `BlockPayload::Table.body_rows.len()`. |
| `header_row` | Equals `BlockPayload::Table.header_row` (an array of cell strings). |
| `kind` | Literal `table`. |
| `order_key` | Equals `EditorBlock.order_key`. |

`BlockPayload::Table.alignments` is **not** emitted by the export per §4 (alignments are out of scope for the v0.1.0 fixture).

#### 5.5.1 Table body row shape

For each row in canonical `BlockPayload::Table.body_rows[i]`:

| Fixture key | Source rule |
|---|---|
| `cells` | Equals the canonical row cells (an array of cell strings). The array length shall equal `header_row` length. |
| `order_key` | Deterministic zero-padded decimal string matching the row's position in the canonical `body_rows[]` array. Analogous to checklist item `order_key` reconstruction. |

Cell text is NFC-normalized. Cell-level alignment metadata is out of scope for v0.1.0 and is not represented in the fixture.

## 6. Round-trip determinism

For every canonical `BlockDocument` constructed from a TC-001-compliant fixture editor-state JSON:

1. `project_fixture_json(tc001_bytes) → BlockDocument` (existing TC-001 implementation at `fdc62d0`);
2. `export_block_document_to_fixture_json(block_document) → tc002_bytes` (future TC-002 implementation);
3. `tc002_bytes` shall be byte-identical to `tc001_bytes` when the original TC-001 fixture is **canonical-equivalent** to its export, meaning:
   - every `checklist.items[i].indent` in the original TC-001 fixture is `0`;
   - every `checklist.items[i].order_key` in the original TC-001 fixture follows the zero-padded decimal scheme `"0001"`, `"0002"`, … starting at `"0001"`;
   - every `table.body_rows[i].order_key` in the original TC-001 fixture follows the same zero-padded scheme;
   - every `code.lines[i]` joins back to the canonical `source` with `\n` separators and no trailing `\r`;
   - `BlockDocument.document_id` equals the original fixture `document_id`;
4. For TC-001 fixtures that are NOT canonical-equivalent (e.g. the existing `cb5ce52` baseline whose checklist items use indents 0 and 1), the round-trip shall produce a deterministic but **non-byte-identical** TC-002 export whose checklist `indent` values are all `0` and whose item / body-row `order_key` values follow the zero-padded scheme; the canonical `BlockDocument` is the round-trip invariant — that is, `project_fixture_json(tc002_bytes) == project_fixture_json(tc001_bytes)` — not the raw bytes.

Identical canonical `BlockDocument` inputs shall produce byte-identical TC-002 export output across repeated calls; the export shall be a deterministic pure function.

## 7. Future test bucket boundary

The future RED/GREEN cycle authorized by a separate later PREP/T/GATE row may add:

- a focused RED test bucket at `crates/eduops_domain/tests/m3_editor_bridge_002_canonical_state_import.rs` that constructs a canonical `BlockDocument` (or loads the TC-001 fixture and projects it via `project_fixture_json`), invokes the future export function, and asserts the §6 round-trip and §5 per-kind shape;
- the minimal export-direction function inside `crates/eduops_domain/src/editor_bridge/mod.rs` (e.g. `pub fn export_block_document_to_fixture_json(document: &BlockDocument) -> Result<String, BlockDocumentError>`) implementing the canonical state import (`BlockDocument` → fixture editor-state JSON) needed to make the RED test pass;
- one new optional fixture JSON artifact at `fixtures/editor_adapter_bridge/tc-002-canonical-state-import/<name>.json` ONLY if the test bucket takes the §2 "expected-output fixture" shape rather than the §2 "round-trip-only" shape.

The future RED/GREEN cycle shall preserve every bridge specification §2.2 non-claim and shall not adopt an editor toolkit runtime, install any package, perform any IME capture, launch any desktop window, mutate any non-fixture file, or perform any live external action.

## 8. Validation rules for fixture JSON authoring

A future fixture-authoring Ralph row that elects the §2 "expected-output fixture" shape shall validate the following before committing a fixture JSON file:

1. `editor_kind == "fixture-toolkit-neutral"`.
2. `schema_version == "0.1.0"`.
3. `document_id` is a non-empty EduOps-owned identifier and contains no raw repository URL, raw email, raw PAT, or any other live-secret form.
4. `nodes` is non-empty and sorted by `order_key` ascending with no duplicate `order_key` values.
5. Each node has a `kind` from the closed set `{heading, paragraph, checklist, code, table}` and matches the §5 per-kind shape exactly (no unknown keys, no missing required keys).
6. Each `block_id` is unique across the document.
7. Every text-bearing field is valid UTF-8 with NFC normalization already applied.
8. No text-bearing field contains a raw GitHub PAT prefix (`ghp_`/`github_pat_`), URL credential form (`://user:token@host`), raw HTTPS/HTTP/SSH URL with credentials, SSH PEM blob, or raw email address.
9. `table.body_rows[i].cells` length equals `header_row` length for every body row.
10. `checklist.items[i].indent == 0` for every item (since the canonical structure does not carry indent and the TC-002 export emits `0` per §5.3.1).
11. `code.lines[i]` does not contain `\n` or `\r` characters; line separation is represented by the array length.
12. `checklist.items[i].order_key` and `table.body_rows[i].order_key` follow the zero-padded decimal scheme matching position (`"0001"`, `"0002"`, …) per §5.3.1 / §5.5.1.
13. The validation output does not echo offending bytes when a rejection is raised; rejection codes (to be enumerated in the future test bucket) are sufficient.

A future fixture-authoring Ralph row that elects the §2 "round-trip-only" shape authors **no** new fixture JSON artifact and validates only the canonical round-trip invariant in §6.

## 9. Relationship to controlled documents

- [Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) v0.1.0 is the parent specification; §6.2 supplies the canonical block-mapping rules and §12 names the `TC-M3-EDITOR-BRIDGE-002` anchor that this contract serves.
- [Editor Adapter Bridge TC-001 Fixture Source Contract Specification](editor-adapter-bridge-tc-001-fixture-source-contract-specification.md) v0.1.0 is the sibling specification for the import direction; its closed-key envelope (§3) and per-kind shapes (§4) are the controlled prior art that TC-002's output envelope (§4) and per-kind reverse mapping (§5) intentionally mirror so the round-trip in §6 is well-defined.
- [Module and Package Layout](module-and-package-layout.md) §7 records the `crates/eduops_domain/` placement for the existing `editor_bridge` sub-module and the `tests/contract/editor_adapter_bridge/` / `fixtures/editor_adapter_bridge/` placements for contract fixtures / fixture-data.
- [Editor block schema baseline](block-schema.md) supplies the canonical `BlockDocument` / `EditorBlock` / `BlockPayload` / `ChecklistItem` / `TableAlignment` field set the future GREEN code reads as input.
- [Korean text handling profile](korean-text-handling-profile.md) supplies the NFC normalization rule applied to text-bearing fields. The TC-002 export shall not re-normalize defensively (the canonical text is already NFC).
- [M3 editor bridge local-safe specification authority](../05-decisions/m3-editor-bridge-local-safe-spec-authority-2026-05-21.md) (`EDUOPS-DEC-067`) supplies the authority boundary for authoring this fixture-local docs/control increment.

## 10. Acceptance boundary

Acceptance of this specification means:

- the v0.1.0 closed-key envelope and per-kind reverse mapping are the controlled baseline for a later TC-002 RED/GREEN cycle scoped to `TC-M3-EDITOR-BRIDGE-002` canonical state import only;
- the future RED test bucket shall be authored at `crates/eduops_domain/tests/m3_editor_bridge_002_canonical_state_import.rs` and assert either the §6 round-trip invariant against the existing TC-001 fixture at `cb5ce52` or the §6 byte-identity against an optional new fixture under `fixtures/editor_adapter_bridge/tc-002-canonical-state-import/<name>.json`;
- the future GREEN code shall extend `crates/eduops_domain/src/editor_bridge/mod.rs` with one export-direction function per the module placement note in [Module and Package Layout](module-and-package-layout.md) §7; no other source file shall be modified by the GREEN increment outside `crates/eduops_domain/src/lib.rs` re-exports if needed;
- no editor toolkit runtime adoption, package install, IME capture, real Tauri runtime invocation, desktop launch, WebKitGTK/WebView2 runtime installation, screenshot/screen-recording capture, end-to-end interactive accessibility audit, installer publication, DEMO-1 acceptance, credential resolution, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, or user-managed external-repo action per `EDUOPS-DEC-064`/`EDUOPS-DEC-065`/`EDUOPS-DEC-067` is authorized or implied by this document;
- the remaining bridge specification §12 anchors `TC-M3-EDITOR-BRIDGE-003..006` (journal operation derivation, Korean composition suppression, validation fail-closed, rollback) each require their own separate fixture source contract specification or scope extension before their RED test buckets can author input/output deterministically.

## 11. Change log

- **v0.1.0 (2026-05-21):** initial fixture-source-contract acceptance for the `TC-M3-EDITOR-BRIDGE-002` canonical state import prerequisite. Defines the input contract (canonical `BlockDocument` with the five M3 baseline `BlockPayload` kinds), the output envelope (reusing the TC-001 closed-key shape), the per-kind reverse mapping (heading, paragraph, checklist, code, table), deterministic block-id and order-key reuse rules, the round-trip determinism contract relative to TC-001 at `fdc62d0`, the future test bucket / module / fixture file placement boundary, fixture authoring validation rules, document relationships, and non-claims.
