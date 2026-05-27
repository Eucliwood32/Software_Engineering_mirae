---
title: M3 SLICE-B Canonical Document Gate Evidence
document_id: EDUOPS-M3-SLICE-B-CANONICAL-DOCUMENT-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-DOCUMENT-STORAGE
    - SWENG-EDUTECH-BLOCK-SCHEMA
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M3-BRIDGE-SPEC-BLOCKER
  tests:
    - eduops_domain::m3_block_document_contract
    - eduops_domain::m3_operation_journal_contract
    - eduops_domain::m3_projection_fixture_contract
    - eduops_storage::m3_document_materialization_contract
---

# M3 SLICE-B Canonical Document Gate Evidence

## 1. Gate result

M3 is accepted for the canonical document path under the constraint recorded in [`EDUOPS-M3-BRIDGE-SPEC-BLOCKER`](m3-bridge-spec-blocker.md).

```text
gate=GATE-SLICE-B-CANONICAL-DOCUMENT
status=accepted-constrained
scope=canonical BlockDocument/EditorBlock domain types, deterministic canonical JSON, deterministic Markdown projection, SHA-256 projection hashes, operation journal replay with stable block IDs and tombstone preservation, local document materialization (.eduops.json/.md/.manifest.json) with manifest hashes, Korean text/code/table projection fixtures
constraint=editor adapter bridge implementation deferred per EDUOPS-DEC-M3-BRIDGE-SPEC-DEFERRED
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
remote=none
```

M3 does not claim editor adapter bridge implementation, editor toolkit selection, Korean IME composition contract acceptance, live editor UI integration, assignment template clone with editor-attached lineage, comment/feedback attachment at the editor UI layer, image/diagram/experiment/decision/reflection/reference/export_placeholder block types, `move_block`/`attach_asset`/`validate_block`/`bind_export` journal operations, conflict resolution, autosave persistence, search index, asset upload, Git checkpoint linkage, or export rendering pipeline.

## 2. Implemented acceptance scope

Accepted M3 behavior:

- `eduops_domain` defines `BlockDocument`, `EditorBlock`, `BlockPayload` (`Heading`/`Paragraph`/`Checklist`/`Code`/`Table`), `BlockDocumentMetadata`, `OwnerScope`, `PrivacyClass`, `ValidationState`, `TableAlignment`, `BlockDocumentProjection`, and `BlockDocumentError` with `BLOCK_SCHEMA_VERSION = "eduops-block-schema/0.1"`.
- `eduops_domain::project_document` validates the block-schema version, rejects duplicate `block_id`, validates table header/alignment/row column counts, sorts blocks by `order_key` then `block_id`, emits deterministic canonical JSON with sorted keys, derives a deterministic Markdown projection with LF line endings, and returns SHA-256 hashes for both projections.
- `eduops_domain::replay_journal` validates the revision chain, rejects document-id mismatches, rejects duplicate inserts (including re-use of tombstoned block IDs), rejects updates on missing or tombstoned blocks, preserves `block_id`/`order_key` across updates, and tombstones deleted blocks so deletion evidence is preserved before checkpoint.
- `eduops_storage::LocalStorageAdapter::materialize_document` validates the adapter mode, rejects live external action, validates relative path against absolute and non-normal path components, maps `owner_scope` to `assignment`/`workspace`/`knowledge`/`report_templates` directories, writes `.eduops.json`/`.md`/`.manifest.json` with deterministic source/projection hashes and the projection-profile label `eduops-projection/0.1`, and records warnings as an explicit (currently empty) array.
- Korean text, code blocks with and without language, GFM tables with alignment row, and mixed Korean/code/table documents project deterministically.

## 3. RED to GREEN evidence

### M3-T1/M3-T2 canonical block document and projection

```text
RED command:    cargo test -p eduops_domain --test m3_block_document_contract -- --nocapture
RED result:     unresolved imports for BlockDocument/EditorBlock/projection types
GREEN command:  cargo test -p eduops_domain --test m3_block_document_contract -- --nocapture
GREEN result:   5 passed; 0 failed
Commit:         8c2226f
```

### M3-T3 operation journal replay with tombstone preservation

```text
RED command:    cargo test -p eduops_domain --test m3_operation_journal_contract -- --nocapture
RED result:     unresolved imports for EditOperation/EditOperationKind/replay_journal
GREEN command:  cargo test -p eduops_domain --test m3_operation_journal_contract -- --nocapture
GREEN result:   8 passed; 0 failed
Commit:         e441d71
```

### M3-T4 local document materialization

```text
RED command:    cargo test -p eduops_storage --test m3_document_materialization_contract -- --nocapture
RED result:     missing MaterializeDocumentRequest and materialize_document method
GREEN command:  cargo test -p eduops_storage --test m3_document_materialization_contract -- --nocapture
GREEN result:   6 passed; 0 failed
Commit:         92e0d26
```

### M3-T5 Korean text, code, and table projection fixtures

```text
RED command:    cargo test -p eduops_domain --test m3_projection_fixture_contract -- --nocapture
RED result:     missing BlockPayload::Code, BlockPayload::Table, and TableAlignment
GREEN command:  cargo test -p eduops_domain --test m3_projection_fixture_contract -- --nocapture
GREEN result:   7 passed; 0 failed
Commit:         4ff534e
```

### M3-BRIDGE-SPEC editor adapter bridge gap closure

Editor adapter bridge specification deferral and M3 gate scope constraint recorded in [`EDUOPS-M3-BRIDGE-SPEC-BLOCKER`](m3-bridge-spec-blocker.md). Commit `6718659`.

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> passed=38 failed=0 ignored=0
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
docs link/JSON sweep                                                       -> markdown_files=99; json_files=9; bad_local_links=0; bad_json_parse=0
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Identical input produces identical projection hash | `m3_block_document_contract::projection_is_deterministic_for_canonical_block_order`, `projection_input_field_order_does_not_change_canonical_output`, `m3_projection_fixture_contract::korean_paragraph_projection_is_deterministic`, `mixed_korean_code_and_table_projection_is_stable` | accepted |
| Operation journal replays to the same canonical state | `m3_operation_journal_contract::replay_inserts_match_directly_built_document`, `replay_is_deterministic_across_repeats` | accepted |
| Block IDs remain stable across update fixtures | `m3_operation_journal_contract::replay_update_preserves_block_id_and_order_key`, `replay_delete_tombstones_block_without_erasing_evidence` | accepted within constrained scope (split/merge/migration deferred) |
| Korean text and code/table fixtures round-trip through the canonical model | `m3_projection_fixture_contract::korean_paragraph_projection_is_deterministic`, `code_block_emits_fenced_markdown_with_language`, `code_block_without_language_emits_plain_fence`, `table_block_emits_gfm_table_with_alignment_row`, `mixed_korean_code_and_table_projection_is_stable` | accepted |
| Local materialization writes paired source/projection/manifest with deterministic hashes | `m3_document_materialization_contract::materialize_writes_source_markdown_and_manifest_for_assignment_scope`, `materialize_is_deterministic_for_identical_inputs` | accepted |
| Live external action and non-local adapter mode are rejected | `m3_document_materialization_contract::materialize_rejects_live_external_action`, `materialize_rejects_non_local_adapter_mode` | accepted |
| Path-scope violations are rejected | `m3_document_materialization_contract::materialize_rejects_path_escape_attempt`, `materialize_rejects_absolute_relative_path` | accepted |

Block-ID split/merge and schema migration fixtures from `notion-style-document-storage-architecture.md` sections 13 and 14 remain deferred for a later increment; the constrained-scope wording above makes that deferral explicit.

## 6. Non-claims

This evidence summary does not claim:

- editor adapter bridge implementation or editor toolkit selection;
- Korean IME composition contract acceptance;
- live editor UI integration with the desktop shell;
- assignment template clone with editor-attached block lineage;
- comment/feedback attach at the editor UI layer;
- `image`/`diagram`/`experiment`/`decision`/`reflection`/`reference`/`export_placeholder` block-type behavior;
- `move_block`/`attach_asset`/`validate_block`/`bind_export` operation journal kinds;
- block split/merge lineage records or schema migration writers;
- Git checkpoint linkage between manifest, journal segment, and commit metadata;
- autosave persistence or crash recovery file format;
- conflict-record materialization or instructor feedback rebind;
- search index rebuild;
- asset upload, LFS handling, or content-addressed asset write;
- export pipeline (DOCX/HWPX/HWP), DEMO-1 evidence, or report rendering;
- roster/identity/workspace provisioning (M4), submission state machine (M5), evaluation runner (M6), GitHub clone-only behavior (M7), or export DEMO-1 (M8).

## 7. Follow-up

The following follow-up items are required before broader editor-related milestones may claim acceptance:

1. author `docs/02-design-planning/editor-adapter-bridge-specification.md` and update `IMPL-GAP-P1-003`/`EDUOPS-CIR-004` to `closed`;
2. add controlled tasks for block split/merge lineage records and schema migration writers when their tests exist;
3. add controlled tasks for `image`/`diagram`/`experiment`/`decision`/`reflection`/`reference`/`export_placeholder` block types with explicit projection-loss/warning evidence;
4. add controlled tasks for `move_block`/`attach_asset`/`validate_block`/`bind_export` journal operations;
5. add controlled tasks for Git checkpoint linkage, autosave persistence, conflict-record materialization, search index rebuild, and asset/LFS behavior;
6. proceed to M4 roster/workspace provisioning once roster schema and identity policy entry criteria are met.

## 8. Traceability

- [Notion-style document storage architecture](../02-design-planning/notion-style-document-storage-architecture.md)
- [Block schema](../02-design-planning/block-schema.md)
- [Implementation milestones](implementation-milestones.md)
- [M3 editor adapter bridge specification gap closure](m3-bridge-spec-blocker.md)
- [M2 configuration and credential reference evidence](m2-configuration-credential-evidence.md)
- [M1 SLICE-A local skeleton evidence](m1-slice-a-local-skeleton-evidence.md)
