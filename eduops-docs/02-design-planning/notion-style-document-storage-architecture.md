---
title: Notion-Style Document Storage Architecture
document_id: SWENG-EDUTECH-DOCUMENT-STORAGE
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Notion-Style Document Storage Architecture

## 1. Purpose

This document defines how EduOps shall store Notion-style editable documents. It closes the design gap that a block editor needs an explicit persistence method and system data structure, not only UI behavior.

## 2. Storage conclusion

EduOps shall use a **hybrid canonical-storage model**:

1. **Canonical editor JSON snapshot** is the single structured source of truth for block editing.
2. **Deterministic Markdown projection** is a derived, human-readable Git artifact for review, diff, export preparation, and long-term portability. It is not the only source of truth and may be lossy for typed blocks.
3. **Projection manifest** records the JSON source hash, Markdown projection hash, profile version, loss/warning entries, fallback artifacts, and unsupported block behavior.
4. **Block/asset indexes in local persistence** support fast UI queries, validation, search, rendering, and autosave but are rebuildable.
5. **Operation journal** records incremental edits for autosave, undo/redo, conflict recovery, and audit diagnosis.
6. **Git checkpoint commits** preserve durable milestones and submission evidence.

The local database/index is operational state. Durable evidence is the materialized JSON snapshot, deterministic Markdown projection, manifest, referenced assets, checkpoint metadata, and submission/export records.

## 3. Repository file layout

Editable documents shall be stored under the allowed path scope (`assignment/**`, `workspace/**`, `knowledge/**`, or `report_templates/**`) using a paired source/projection layout:

```text
workspace/
├─ documents/
│  ├─ main.eduops.json          # canonical editor JSON snapshot
│  ├─ main.md                   # deterministic Markdown projection
│  └─ main.manifest.json        # schema/version/hash/export bindings
├─ assets/
│  ├─ images/
│  ├─ diagrams/
│  └─ attachments/
└─ .eduops/
   ├─ autosave/                 # local transient snapshots, not canonical submission evidence
   ├─ journals/                 # operation journals/checkpoint deltas
   └─ indexes/                  # rebuildable local search/render/validation indexes
```

For `knowledge/**`, the same structure may be scoped per note or per knowledge package:

```text
knowledge/
├─ index.eduops.json
├─ index.md
├─ notes/<note-id>.eduops.json
├─ notes/<note-id>.md
└─ assets/
```

## 4. Core system data structures

### 4.1 `EditorDocument`

```json
{
  "document_id": "doc_...",
  "schema_version": "eduops-block-schema/0.1",
  "storage_version": "eduops-storage/0.1",
  "document_type": "assignment_brief|student_workspace|knowledge_note|report_template|feedback_note",
  "path_scope": "assignment|workspace|knowledge|report_template",
  "owner_ref": "actor-or-course-ref",
  "root_block_ids": ["blk_001"],
  "block_map": {"blk_001": {"type": "heading"}},
  "asset_refs": [],
  "validation_state": {},
  "export_bindings": {},
  "evidence_refs": {},
  "hashes": {
    "json_canonical_hash": "sha256:...",
    "markdown_projection_hash": "sha256:..."
  }
}
```

### 4.2 `EditorBlock`

Blocks are addressed by stable `block_id`. Ordering is represented by parent/child relationships and `order_key`, not by database row order.

| Field | Purpose |
|---|---|
| `block_id` | Stable block identity for comments, validation, export, feedback, and diffs |
| `parent_block_id` | Parent block or document root |
| `order_key` | Stable sortable key that supports insert/reorder without rewriting every block |
| `type` | paragraph, heading, code, table, image, diagram, experiment, decision, reflection, reference, export placeholder |
| `role` | instruction, answer, knowledge, evidence, reflection, report |
| `content` | Typed content payload |
| `source_payload` | Structured source for code/table/diagram/image/reference blocks |
| `attributes` | Presentation hints, required flags, rubric links, privacy class |
| `created_by`, `updated_by`, `updated_at` | Audit support |
| `hash` | Canonical block hash for diff/evidence |

### 4.3 `AssetRef`

Assets are content-addressed where feasible.

| Field | Purpose |
|---|---|
| `asset_id` | Stable asset identifier |
| `path` | Repository-relative asset path |
| `hash` | Content hash |
| `media_type` | MIME/media type |
| `origin` | user_upload, generated_diagram, evaluation_log, screenshot, export_fallback |
| `privacy_class` | student_private, submission_evidence, course_review, public_example_candidate |
| `alt_text` | Required for images/diagrams used as evidence/export |

### 4.4 `EditOperation`

Autosave and undo/redo shall use an operation journal. The MVP does not require live multi-user CRDT collaboration, but operations shall be structured so conflict handling and future collaboration are not blocked.

| Operation | Meaning |
|---|---|
| `insert_block` | Insert block under parent with order key |
| `update_block` | Update content/attributes/source payload |
| `move_block` | Change parent/order key |
| `delete_block` | Tombstone block; do not immediately erase evidence before checkpoint |
| `attach_asset` | Link asset to block/document |
| `validate_block` | Record validation result |
| `bind_export` | Map block to report/export template section |

Each operation records `op_id`, `document_id`, `base_revision_id`, `actor_id`, `timestamp`, `path_scope`, `operation_type`, `payload`, and `resulting_revision_id`.

## 5. Revision and checkpoint model

```text
EditOperation journal
→ autosave revision
→ validation/index update
→ canonical JSON snapshot
→ Markdown projection
→ Git checkpoint commit
→ submission snapshot/export manifest when submitted
```

| Level | Durability | Purpose |
|---|---|---|
| In-memory editor state | Volatile | Smooth editing |
| Local operation journal | Local durable | Autosave, undo/redo, crash recovery |
| Canonical JSON snapshot | Durable file | Structured source of truth |
| Markdown projection | Durable file | Human-readable diff/review/export source |
| Git checkpoint | Durable evidence | Milestone, recovery, submission traceability |
| Submission snapshot | Controlled evidence | Official grading/review package |

## 6. Conflict model

EduOps MVP shall not require real-time multi-user co-editing. Conflict handling is required for:

- assignment template update while student document is in progress;
- offline edits queued locally;
- failed Git push requiring rebase/merge decision;
- instructor feedback/comment records attached to changed block IDs;
- report export generated from stale revision.

Conflicts shall be represented as structured `DocumentConflict` records with base revision, local revision, remote/assignment revision, affected block IDs, severity, suggested resolution, and audit state.

## 7. Local persistence tables/indexes

The application may use SQLite or another local embedded database for rebuildable indexes:

| Table/index | Purpose |
|---|---|
| `editor_documents` | Document metadata and current revision pointers |
| `editor_block_index` | Current rebuildable block index for fast rendering/search/validation |
| `editor_operations` | Autosave operation journal |
| `editor_revisions` | Revision graph, snapshot hashes, Git commit links |
| `editor_assets` | Asset metadata and content hashes |
| `editor_conflicts` | Structured conflict records |
| `editor_validation_results` | Required-block/privacy/export/deadline validation results |
| `editor_export_bindings` | Block-to-report/export mappings |
| `editor_search_index` | Rebuildable search index; not canonical evidence |

## 8. Save API sequence

```text
UI edit
→ validate path/role/scope permission
→ append EditOperation to local journal
→ update local index and autosave revision
→ periodically materialize canonical JSON and Markdown projection
→ create Git checkpoint on meaningful boundary
→ submission/export uses only materialized canonical revision
```

Meaningful checkpoint boundaries include explicit save, submit, assignment update acknowledgement, export generation, feedback release, and recovery/manual override.

## 9. Evidence and V&V requirements

Verification shall prove:

1. JSON snapshot and Markdown projection are deterministic for the same block graph.
2. Operation journal can recover the latest autosave after simulated crash.
3. Reordering/inserting blocks preserves stable block IDs and comment/export bindings.
4. Assignment sync never writes outside authorized `assignment/**` paths and never silently overwrites `workspace/**` or `knowledge/**` documents.
5. Submission and export use a materialized canonical revision, not stale in-memory state.
6. Search/index tables can be rebuilt from canonical files.
7. Git checkpoint links to `json_canonical_hash`, `markdown_projection_hash`, asset hashes, and operation journal range.

## 10. Traceability

- Requirements: `EDUOPS-FR-061`, `EDUOPS-FR-062`, `EDUOPS-FR-063`
- Non-functional requirements: `EDUOPS-NFR-025`, `EDUOPS-NFR-026`
- Decision: `EDUOPS-DEC-035`
- Risks: `EDUOPS-R-039`, `EDUOPS-R-040`
- V&V: `STD-056`..`STD-059`

## 11. Markdown projection profile

Markdown is a deterministic **derived projection**, not the sole source of truth. The pinned projection profile for draft implementation is:

| Rule | Baseline |
|---|---|
| Dialect | GitHub-Flavored Markdown compatible with CommonMark where possible |
| Line endings | LF, including on Windows; CRLF is normalized before hashing |
| Unicode | NFC normalization before hash/projection |
| Frontmatter | YAML keys sorted in a controlled order |
| Lists | `-` unordered marker and `1.` ordered marker normalization |
| Code fences | Triple backticks, explicit language when known, stable info string |
| Tables | GFM table projection with deterministic column order/alignment metadata in manifest when layout cannot be preserved |
| Diagrams | Source fenced block plus fallback asset reference in manifest |
| Images/assets | Relative path plus asset hash/alt text in manifest |
| Typed blocks | Lossless only when block semantics map to Markdown; otherwise emit warning and preserve full semantics in JSON |

Projection manifests shall record `projection_profile`, `json_canonical_hash`, `markdown_projection_hash`, `loss_category`, `affected_block_ids`, `fallback_refs`, and warning severity.

## 12. Git inclusion and local artifact policy

| Artifact | Git tracked | Local-only | LFS candidate | Evidence role |
|---|---:|---:|---:|---|
| `*.eduops.json` | Yes | No | No | Canonical structured source |
| `*.md` | Yes | No | No | Derived deterministic projection |
| `*.manifest.json` | Yes | No | No | Projection/export/hash/evidence manifest |
| `assets/images/*`, `assets/diagrams/*` | Conditional | No | Yes for large/binary non-private assets | Referenced evidence/export assets |
| `.eduops/indexes/` | No | Yes | No | Rebuildable cache |
| `.eduops/autosave/` | No by default | Yes | No | Crash recovery, not submission evidence |
| `.eduops/journals/` | No by default; checkpoint range summarized in manifest | Yes | No | Operation recovery/audit diagnosis |
| Search indexes | No | Yes | No | Rebuildable cache with privacy filters |

Local-only artifacts must not be required to validate a submitted checkpoint. If a journal segment is needed as evidence, it must be summarized or materialized into a tracked manifest/checkpoint record rather than relying on raw local journal files.

## 13. Block identity model

Block IDs are stable evidence handles. The draft baseline uses scoped UUIDv7/ULID-style IDs with path-scope prefixes, for example `wk_blk_...`, `kn_blk_...`, `asg_blk_...`.

| Case | Required rule |
|---|---|
| New block | Generate globally unique scoped ID; never infer identity from row order or heading text |
| Reorder | Preserve `block_id`; update only parent/order metadata |
| Assignment template clone | Preserve template-origin reference and create student-scope block ID when the block becomes student-editable; read-only assignment blocks keep assignment-scope ID |
| Assignment update | Match by template-origin reference and block lineage; never break student feedback/export bindings silently |
| Split block | Keep original ID on first resulting block and create child/sibling lineage records for new blocks |
| Merge blocks | Preserve primary block ID and record merged block IDs as lineage/tombstone references |
| Delete block | Tombstone first; hard deletion only after retention/export rules allow it |

## 14. Schema and storage migration policy

Schema versions shall be explicit and migration-controlled.

| Scenario | Rule |
|---|---|
| Open older supported schema | Run deterministic migration and write migration evidence record |
| Unsupported older schema | Open read-only and request controlled migration review |
| Downgrade attempt | Reject by default; never silently write older format |
| Migration failure | Quarantine document copy, keep original unchanged, emit validation failure |
| Journal migration | Journal entries include operation schema version; replay only through supported migration path |
| Manifest migration | Preserve old hashes and add new hashes rather than overwriting evidence |

The current draft schema label is `eduops-block-schema/0.1` and storage label is `eduops-storage/0.1` until promoted by controlled decision.

## 15. Deletion, tombstone, and feedback retention

Deleted blocks shall be represented as tombstones until retention rules allow removal. Comments, rubric feedback, export bindings, validation results, and submission evidence resolve block IDs through these states:

| Resolution state | Meaning |
|---|---|
| `live` | Block exists in current canonical document |
| `tombstoned` | Block is deleted from live view but retained for evidence/undo/review |
| `snapshot_only` | Block exists only in a prior checkpoint/submission/export snapshot |
| `removed_after_retention` | Block content removed after retention policy, with metadata/hash/audit evidence retained where required |

Official submission snapshots preserve the block state at submission even if the live workspace later deletes the block.

## 16. Asset privacy, LFS, and content addressing

Asset storage shall consider both content hash and permission scope.

| Privacy class | Remote/LFS policy | Notes |
|---|---|---|
| `student_private` | Do not upload to shared remote/LFS unless explicitly promoted into submission/export evidence | Default for personal knowledge drafts |
| `submission_evidence` | May be tracked or LFS-managed with manifest hash and course visibility | Used for official evidence |
| `course_review` | Instructor/TA visible; redaction required for external export | Feedback/review assets |
| `public_example_candidate` | Requires explicit review before reuse | Teaching examples |

Content-addressed hashes prove integrity; path scope still controls visibility. A hash match does not grant access.

## 17. Local protection and lifecycle cleanup

Local journals, autosaves, indexes, and private knowledge caches may contain sensitive student content. They shall use platform-appropriate at-rest protection where available, privacy-class filtering, and lifecycle cleanup triggers for withdrawal, archive, device handoff, and course deletion. Instructor/global search shall not index `student_private` content outside authorized scope.
