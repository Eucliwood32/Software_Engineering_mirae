---
title: Editor Adapter Bridge TC-001 Fixture Source Contract Specification
document_id: EDUOPS-EDITOR-ADAPTER-BRIDGE-TC-001-FIXTURE-SOURCE-CONTRACT-SPECIFICATION
version: 0.1.0
status: draft
date: 2026-05-21
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-EDITOR-ADAPTER-BRIDGE-SPECIFICATION
    - EDUOPS-DEC-067
    - SWENG-EDUTECH-MODULE-LAYOUT
    - SWENG-EDUTECH-BLOCK-SCHEMA
  gaps_recorded:
    - Toolkit-neutral fixture editor-state JSON shape prerequisite for the `TC-M3-EDITOR-BRIDGE-001` canonical node export RED test bucket
---

# Editor Adapter Bridge TC-001 Fixture Source Contract Specification

## 0. Document scope

This specification defines only the controlled HOW-level toolkit-neutral fixture editor-state JSON contract that the future [Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) §12 `TC-M3-EDITOR-BRIDGE-001` (canonical node export) RED test bucket may consume as its input. The fixture JSON is a pure-data, vendor-neutral representation of a small editor document covering the baseline block types from bridge specification §6.2 (heading, paragraph, checklist, code, table).

This document does **not**:

- author any fixture JSON artifact under `fixtures/editor_adapter_bridge/`;
- author the future `TC-M3-EDITOR-BRIDGE-001` RED/GREEN test bucket at `crates/eduops_domain/tests/m3_editor_bridge_001_canonical_node_export.rs`;
- author the future `crates/eduops_domain/src/editor_bridge/mod.rs` sub-module or any of its sub-modules;
- adopt or install any editor toolkit runtime (Tiptap, ProseMirror, Lexical, Markdown-first, Monaco, or custom);
- invoke a real Tauri runtime, desktop window, IME capture, screenshot, screen-recording, host runtime install, installer publication, Git command, credential lookup, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, DEMO-1 acceptance, or user-managed external-repo action.

Acceptance of this specification is acceptance of the **fixture source contract only**. Fixture JSON authoring, bridge module authoring, RED/GREEN test authoring, GREEN implementation, and the companion STD/RTM addenda remain separately gated Ralph follow-ups, and each must preserve every bridge specification §2.2 non-claim.

## 1. Purpose

The bridge specification §12 anchor `TC-M3-EDITOR-BRIDGE-001` (canonical node export) requires that "a fixture editor-state JSON maps heading/paragraph/checklist/code/table nodes into `BlockDocument` with stable block IDs and deterministic order." Bridge specification §6.2 describes the mapping rules in prose but does not commit to a concrete fixture JSON syntax: a future RED test bucket cannot deterministically construct its input without a pinned shape.

This specification closes that prerequisite gap by defining:

1. the closed-key fixture JSON envelope;
2. the closed-key node shapes for the M3 baseline block types from bridge specification §6.2;
3. deterministic block-id and ordering rules per bridge specification §6.3;
4. the expected canonical `BlockDocument` projection that the future RED test bucket asserts on;
5. the future test bucket / module / fixture file placement boundary;
6. acceptance and non-claim boundaries for the future RED/GREEN cycle.

## 2. Authorized fixture-data boundary

The only fixture root admitted by this contract v0.1.0 is:

```text
fixtures/editor_adapter_bridge/tc-001-canonical-node-export/
```

This root is the natural fit for the `TC-M3-EDITOR-BRIDGE-001` anchor under the bridge fixture-data placement recorded in [Module and Package Layout](module-and-package-layout.md) §7. Adding sibling roots for `TC-M3-EDITOR-BRIDGE-002..006` requires a separate later contract or version bump.

Rules:

1. Every fixture JSON path shall be repo-relative and start with `fixtures/editor_adapter_bridge/`.
2. Every fixture JSON path shall use `/` separators and shall not contain `..`, absolute-path syntax, drive prefixes, NUL bytes, or shell metacharacter semantics.
3. Fixture JSON content shall be UTF-8 with NFC normalization already applied to text-bearing fields (Korean composition shall not appear in partial form). NFC re-normalization may also be asserted by the future GREEN code per bridge specification §8.
4. Fixture JSON shall not contain raw credentials, raw repository URLs with credentials, raw email addresses, GitHub PAT prefixes (`ghp_`/`github_pat_`), or any other live-secret form.
5. Fixture JSON shall not contain instructions to perform a network call, a Git command, a credential lookup, a desktop launch, an IME capture, a screenshot, a host-runtime install, an installer publication, or any user-managed external-repo action.

## 3. Fixture editor-state JSON envelope

The top-level object shall contain these keys in alphabetical order when serialized as canonical JSON:

| Key | Type | Rule |
|---|---|---|
| `document_id` | string | Supplied by application core in the runtime path; in the fixture, a stable EduOps-owned identifier (e.g. `doc-tc-001-canonical-node-export`). Never derived from editor DOM order. |
| `editor_kind` | string | Literal `fixture-toolkit-neutral`. Marks the JSON as a vendor-neutral fixture, not a Tiptap / ProseMirror / Lexical / Monaco / Markdown-first runtime export. |
| `nodes` | array | Sorted by `order_key` ascending. See §4 for the closed-key node shapes. |
| `schema_version` | string | Literal `0.1.0`. The fixture contract version, distinct from the bridge specification version and the canonical block schema version. |

Canonical JSON layout (illustrative envelope without `nodes` content; see §4 for node-shape examples):

```json
{
  "document_id": "doc-tc-001-canonical-node-export",
  "editor_kind": "fixture-toolkit-neutral",
  "nodes": [],
  "schema_version": "0.1.0"
}
```

## 4. Node shapes

Each `nodes[]` element shall contain a `kind` field plus the kind-specific payload below. All node objects shall include the following common fields in alphabetical order: `block_id`, `kind`, `order_key`, plus kind-specific keys also in alphabetical order. The bridge specification §6.3 `block_id` and `order_key` rules apply.

### 4.1 `heading`

| Key | Type | Rule |
|---|---|---|
| `block_id` | string | EduOps-owned stable identifier. |
| `kind` | string | Literal `heading`. |
| `level` | integer | 1–6, matching bridge specification §6.2 heading-level mapping. |
| `order_key` | string | Deterministic order key per bridge specification §6.3. |
| `text` | string | Heading text, NFC-normalized. |

### 4.2 `paragraph`

| Key | Type | Rule |
|---|---|---|
| `block_id` | string | EduOps-owned stable identifier. |
| `kind` | string | Literal `paragraph`. |
| `order_key` | string | Deterministic order key. |
| `text` | string | Paragraph text. May include Korean/English mixed content. NFC-normalized per bridge specification §8. Inline-range structure is out of scope for v0.1.0; the fixture is a flat-text representation only. |

### 4.3 `checklist`

| Key | Type | Rule |
|---|---|---|
| `block_id` | string | EduOps-owned stable identifier. |
| `items` | array | Sorted by item `order_key` ascending. See §4.3.1 for item shape. |
| `kind` | string | Literal `checklist`. |
| `order_key` | string | Deterministic order key. |

#### 4.3.1 Checklist item shape

| Key | Type | Rule |
|---|---|---|
| `checked` | boolean | Initial checked state. |
| `indent` | integer | Non-negative indent level (0 for top-level items). The TC-001 v0.1 canonical `BlockDocument` projection validates this fixture field as input shape but does not persist indentation in `ChecklistItem`; nested checklist rendering semantics remain deferred to a later bridge increment. |
| `order_key` | string | Deterministic order key inside the checklist. |
| `text` | string | Item text, NFC-normalized. |

### 4.4 `code`

| Key | Type | Rule |
|---|---|---|
| `block_id` | string | EduOps-owned stable identifier. |
| `kind` | string | Literal `code`. |
| `language` | string | Language label (e.g. `rust`, `python`, `text`). May be `text` when no language hint is present. |
| `lines` | array | Ordered array of source-line strings. Lines are preserved verbatim including indentation. Trailing newlines are encoded by the array length and shall not appear inside individual line strings. |
| `order_key` | string | Deterministic order key. |

### 4.5 `table`

| Key | Type | Rule |
|---|---|---|
| `block_id` | string | EduOps-owned stable identifier. |
| `body_rows` | array | Sorted by row `order_key` ascending. Each row is an array of cell strings whose length equals the `header_row` length. |
| `header_row` | array | Ordered array of header cell strings. Establishes the column count and order. |
| `kind` | string | Literal `table`. |
| `order_key` | string | Deterministic order key. |

#### 4.5.1 Table body row shape

A body row is an object:

| Key | Type | Rule |
|---|---|---|
| `cells` | array | Ordered cell strings; the array length shall equal the `header_row` length. |
| `order_key` | string | Deterministic order key inside the table body. |

Cell text is NFC-normalized. Cell-level alignment metadata is out of scope for v0.1.0 and is not represented in the fixture.

## 5. Deterministic block-id and ordering rules

Per bridge specification §6.3:

1. `block_id` values are EduOps-owned, stable strings. Fixture authors shall use human-readable identifiers (e.g. `blk-heading-1`, `blk-para-1`, `blk-checklist-1`). The block ID shall be stable across reorder/update/delete operations in any future test bucket.
2. `order_key` values are deterministic strings. The future GREEN code sorts top-level `nodes` by `order_key` ascending; the resulting block sequence is the canonical document order. Inside `checklist.items` and `table.body_rows`, the same rule applies.
3. The fixture shall use lexicographically distinct `order_key` values so that sort order is unambiguous (e.g. `0001`, `0002`, `0003`).
4. The future GREEN code shall not invent or rewrite `block_id` values when mapping the fixture into the canonical `BlockDocument`; it shall reuse the fixture-supplied identifiers.

## 6. Expected canonical `BlockDocument` projection

For each `nodes[]` element, the bridge shall produce a canonical `EditorBlock` entry in the resulting `BlockDocument` with:

| Canonical field | Source rule |
|---|---|
| `BlockDocument.document_id` | Equals the fixture `document_id`. |
| `BlockDocument.schema_version` | Set by the future GREEN code to the accepted M3 baseline block schema version per bridge specification §6.1; not derived from the fixture envelope `schema_version`. |
| `BlockDocument.root_block_ids` | Lists every fixture `block_id` in `order_key` ascending order. |
| `EditorBlock.block_id` | Equals the fixture `block_id`. |
| `EditorBlock.kind` | Equals the fixture `kind`. |
| `EditorBlock.payload` | Canonical payload derived from the kind-specific fields per §4: `heading` → `{level, text}`; `paragraph` → `{text}`; `checklist` → `{items: [{text, checked}]}` ordered by item `order_key` after validating each item `indent` as input-shape data only; `code` → `{language, lines}`; `table` → `{header_row, body_rows: [{cells}]}` ordered by row `order_key`. |
| `EditorBlock.order_key` | Equals the fixture `order_key`. |

Korean text in `text`/`lines`/cell strings shall round-trip without re-composition. The future GREEN code may NFC-re-normalize defensively per bridge specification §8 even though the fixture already requires NFC.

The projection shall be deterministic: identical fixture JSON shall produce a byte-identical canonical `BlockDocument` projection and identical canonical-JSON output across repeated calls.

## 7. Future test bucket boundary

The future RED/GREEN cycle authorized by a separate later PREP/T/GATE row may add:

- a fixture JSON artifact at `fixtures/editor_adapter_bridge/tc-001-canonical-node-export/<name>.json` covering at least one of each of the five baseline kinds (`heading`, `paragraph`, `checklist`, `code`, `table`);
- a focused RED test bucket at `crates/eduops_domain/tests/m3_editor_bridge_001_canonical_node_export.rs` that loads the fixture, invokes the bridge, and asserts the §6 expected canonical projection;
- the minimal `crates/eduops_domain/src/editor_bridge/mod.rs` sub-module per [Module and Package Layout](module-and-package-layout.md) §7 implementing the canonical node export needed to make the RED test pass.

The future RED/GREEN cycle shall preserve every bridge specification §2.2 non-claim and shall not adopt an editor toolkit runtime, install any package, perform any IME capture, launch any desktop window, mutate any non-fixture file, or perform any live external action.

## 8. Validation rules for fixture JSON authoring

A future fixture-authoring Ralph row shall validate the following before committing a fixture JSON file:

1. `editor_kind == "fixture-toolkit-neutral"`.
2. `schema_version == "0.1.0"`.
3. `document_id` is a non-empty EduOps-owned identifier and contains no raw repository URL, raw email, raw PAT, or any other live-secret form.
4. `nodes` is non-empty and sorted by `order_key` ascending with no duplicate `order_key` values.
5. Each node has a `kind` from the closed set `{heading, paragraph, checklist, code, table}` and matches the §4 kind-specific shape exactly (no unknown keys, no missing required keys).
6. Each `block_id` is unique across the document.
7. Every text-bearing field is valid UTF-8 with NFC normalization already applied.
8. No text-bearing field contains a raw GitHub PAT prefix (`ghp_`/`github_pat_`), URL credential form (`://user:token@host`), raw HTTPS/HTTP/SSH URL with credentials, SSH PEM blob, or raw email address.
9. `table.body_rows[i].cells` length equals `header_row` length for every body row.
10. `checklist.items[i].indent` is a non-negative integer.
11. `code.lines[i]` does not contain `\n` or `\r` characters; line separation is represented by the array length.
12. The validation output does not echo offending bytes when a rejection is raised; rejection codes (to be enumerated in the future fixture-authoring spec or test bucket) are sufficient.

## 9. Relationship to controlled documents

- [Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) v0.1.0 is the parent specification; §6.2 supplies the canonical block-mapping rules and §12 names the `TC-M3-EDITOR-BRIDGE-001` anchor that this contract serves.
- [Module and Package Layout](module-and-package-layout.md) §7 records the `crates/eduops_domain/` placement for the future `editor_bridge` sub-module and the `tests/contract/editor_adapter_bridge/` / `fixtures/editor_adapter_bridge/` placements for contract fixtures / fixture-data.
- [Editor block schema baseline](block-schema.md) supplies the canonical `BlockDocument` / `EditorBlock` field set the future GREEN code projects into.
- [Korean text handling profile](korean-text-handling-profile.md) supplies the NFC normalization rule applied to text-bearing fields.
- [M3 editor bridge local-safe specification authority](../05-decisions/m3-editor-bridge-local-safe-spec-authority-2026-05-21.md) (`EDUOPS-DEC-067`) supplies the authority boundary for authoring this fixture-local docs/control increment.

## 10. Acceptance boundary

Acceptance of this specification means:

- the v0.1.0 closed-key envelope and node shapes are the controlled baseline for a later fixture JSON authoring row scoped to `TC-M3-EDITOR-BRIDGE-001` canonical node export only;
- the future fixture JSON artifact shall be authored at `fixtures/editor_adapter_bridge/tc-001-canonical-node-export/<name>.json` under the constraints in §2;
- the future RED test bucket shall be authored at `crates/eduops_domain/tests/m3_editor_bridge_001_canonical_node_export.rs` and assert the §6 expected canonical projection;
- the future GREEN code shall be added at `crates/eduops_domain/src/editor_bridge/mod.rs` per the module placement note in [Module and Package Layout](module-and-package-layout.md) §7;
- no editor toolkit runtime adoption, package install, IME capture, real Tauri runtime invocation, desktop launch, WebKitGTK/WebView2 runtime installation, screenshot/screen-recording capture, end-to-end interactive accessibility audit, installer publication, DEMO-1 acceptance, credential resolution, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, or user-managed external-repo action per `EDUOPS-DEC-064`/`EDUOPS-DEC-065`/`EDUOPS-DEC-067` is authorized or implied by this document;
- the remaining bridge specification §12 anchors `TC-M3-EDITOR-BRIDGE-002..006` (canonical state import, journal operation derivation, Korean composition suppression, validation fail-closed, rollback) each require their own separate fixture source contract specification or scope extension before their RED test buckets can author input deterministically.

## 11. Change log

- **v0.1.0 (2026-05-21):** initial fixture-source-contract acceptance for the `TC-M3-EDITOR-BRIDGE-001` canonical node export prerequisite. Defines the closed-key envelope, the five baseline node shapes (heading, paragraph, checklist, code, table), deterministic block-id/order rules, the expected canonical `BlockDocument` projection, the future test bucket / module / fixture file placement boundary, fixture authoring validation rules, document relationships, and non-claims.
