---
title: Editor Block Schema Baseline
document_id: SWENG-EDUTECH-BLOCK-SCHEMA
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Editor Block Schema Baseline

## 1. Purpose

Define the controlled canonical block schema used by EduOps editor documents before implementation. The schema prevents editor-vendor lock-in from becoming the canonical evidence format.

## 2. Canonical document envelope

```json
{
  "schema_version": "eduops-block-schema/0.1",
  "document_id": "uuid-or-controlled-id",
  "assignment_instance_id": "...",
  "owner_scope": "assignment|workspace|knowledge|report_template",
  "blocks": [],
  "metadata": {
    "created_by": "actor-ref",
    "updated_at": "iso-8601",
    "source_commit_sha": "optional-git-sha",
    "validation_profile": "profile-id"
  }
}
```

## 3. Common block fields

| Field | Required | Purpose |
|---|---|---|
| `block_id` | Yes | Stable identifier for validation, comments, feedback, and export mapping |
| `type` | Yes | Block type |
| `role` | Yes | `instruction`, `answer`, `knowledge`, `evidence`, `reflection`, `report` |
| `content` | Yes | Text or typed payload |
| `source_payload` | Conditional | Graph/table/image/code source data |
| `validation_state` | Yes | `unchecked`, `pass`, `warning`, `fail` |
| `export_binding` | Conditional | Mapping to report section/template |
| `evidence_refs` | Conditional | Commit, file, test, evaluation, or source references |
| `privacy_class` | Yes | `course`, `student_private`, `submission`, `public_example_candidate` |

## 4. Initial block types

| Type | Required behavior |
|---|---|
| `heading` | Stable hierarchy and export outline |
| `paragraph` | Korean/English text, citations, inline code |
| `checklist` | Required task progress and validation status |
| `code` | C/C++ syntax, indentation, line references, file binding |
| `table` | Structured cells, width hints, export fallback |
| `image` | Local asset ref, alt text, hash, DPI metadata |
| `diagram` | Mermaid/Graphviz/structured source plus fallback snapshot |
| `experiment` | Command, input SHA, output/log refs, result interpretation |
| `decision` | Student decision, alternatives, rationale, evidence refs |
| `reflection` | Prompt-linked reflection text |
| `reference` | Source/citation metadata with privacy/reuse flags |
| `export_placeholder` | Report template placeholder and binding rules |

## 5. Loss and warning model

No export tool may silently drop a block. Unsupported export behavior shall produce a manifest warning with `block_id`, `type`, `loss_category`, `severity`, and fallback artifact reference.

## 6. Traceability

- Requirements: `EDUOPS-FR-047`, `EDUOPS-FR-051`, `EDUOPS-FR-054`
- V&V: `STD-044`, `STD-046`
- Decision: `EDUOPS-DEC-027`

## 7. Storage architecture binding

The block schema is stored through the [Notion-style document storage architecture](notion-style-document-storage-architecture.md). Each block requires stable `block_id`, parent/order information, typed payload, privacy class, validation state, export binding, and canonical block hash. Ordering shall use stable `order_key`/parent relationships rather than relying on database row order.

## 8. Block identity and migration rules

The draft schema version remains `eduops-block-schema/0.1` until controlled promotion. Block identity follows [Notion-style document storage architecture](notion-style-document-storage-architecture.md): stable scoped IDs, lineage records for split/merge/clone, tombstone records for deletion, and explicit schema migration evidence. Markdown projections are derived from this schema and may be lossy for typed blocks; JSON remains the structured source of truth.
