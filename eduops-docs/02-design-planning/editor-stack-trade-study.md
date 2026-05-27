---
title: Editor Stack Trade Study
document_id: SWENG-EDUTECH-EDITOR-TRADE
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Editor Stack Trade Study

## 1. Purpose

This document converts the open editor question into a fixture-gated trade study. The editor is a core capability because it produces canonical student work, knowledge artifacts, validation evidence, and exportable reports.

## 2. Candidate stack options

| Option | Strengths | Risks | Initial stance |
|---|---|---|---|
| ProseMirror/Tiptap-style block editor | Mature document model, schema plugins, collaboration optional, strong ecosystem | Desktop shell integration, Korean IME regressions, export adapters still custom | Primary candidate for spike |
| Lexical-style editor | Modern rich editor architecture, good performance potential | Fewer mature academic/export fixtures | Secondary candidate |
| Markdown-first editor + block extensions | Git-friendly, easier canonical diffs, simpler export | Harder Notion-style UX, tables/diagrams require extensions | Acceptable fallback |
| Monaco/code-centric hybrid | Excellent code blocks and diff | Weak long-form block document UX | Use only for code block subcomponent |
| Full custom editor | Maximum control | High cost, accessibility/export bugs, long schedule | Not first choice without failed mature-stack fixtures |

## 3. Selection criteria

| Criterion | Gate |
|---|---|
| Canonical schema control | Versioned block schema can be exported to JSON and Markdown without hidden editor state |
| Korean IME | Composition events do not trigger broken autosaves or duplicated characters |
| Large documents | P95 typing/autosave/rendering budget remains acceptable for class-scale fixtures |
| Code blocks | C/C++ code blocks preserve indentation, syntax, copy/paste, and line references |
| Tables/graphs/images | Source payloads and fallback evidence are preserved |
| Export binding | Blocks map to DOCX/HWPX sections with warnings for unsupported features |
| Desktop packaging | Works in the selected desktop shell without unapproved remote service dependency |
| Accessibility | Keyboard navigation and screen-reader semantics are testable |
| License/security | License allows commercial/institutional packaging and dependency risk is acceptable |

## 4. Recommended near-term decision

Use a **fixture-gated mature web-document substrate first**: ProseMirror/Tiptap-style editor as the primary spike, Markdown-first editor as fallback, Monaco embedded only for code block editing, and no full custom editor until mature stacks fail essential fixtures.

This is not a final implementation lock. It is a controlled spike baseline for D5 Fast controlled UI prototype.

## 5. Required spike fixtures

1. Korean/English mixed paragraph with IME composition and autosave.
2. C/C++ code block with indentation and line references.
3. Required blocks: problem understanding, plan, experiment, result, reflection.
4. Large table and graph/image block with fallback snapshot.
5. JSON → Markdown → preview → DOCX/HWPX export manifest.
6. Conflict recovery from checkpoint and Git commit.

## 6. Traceability

- Requirements: `EDUOPS-FR-047`..`EDUOPS-FR-051`, `EDUOPS-FR-053`
- Non-functional requirements: `EDUOPS-NFR-018`, `EDUOPS-NFR-019`, `EDUOPS-NFR-021`
- Decision: `EDUOPS-DEC-027`
- Risk: `EDUOPS-R-031`

## 7. Storage architecture conformance gate

Any candidate editor toolkit must pass the storage conformance gate before implementation lock-in:

| Gate | Required evidence |
|---|---|
| Stable block identity | Toolkit can preserve EduOps-owned `block_id` through edit/reorder/copy/delete |
| Order serialization | Parent/order keys can be exported deterministically without relying on hidden row order |
| External operation journal | Insert/update/move/delete operations can be captured or derived without losing semantics |
| Canonical JSON export | Toolkit state can be normalized into EduOps block schema without vendor-only fields becoming authoritative |
| Deterministic projection | Same canonical document produces the same Markdown projection/hash under the pinned profile |
| Korean IME stability | IME composition does not corrupt block boundaries or operation journal entries |
| Tombstone/feedback binding | Delete/recover flows preserve comment, validation, export, and feedback bindings |
