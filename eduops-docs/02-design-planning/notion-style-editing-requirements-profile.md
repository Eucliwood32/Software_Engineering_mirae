---
title: HISYS EduOps Notion-Style Editing Requirements Profile
document_id: SWENG-EDUTECH-EDITING-PROFILE
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Notion-Style Editing Requirements Profile

## 1. Conclusion

Yes: once EduOps differentiates through Notion-style assignment execution, student knowledge-system creation, and DOCX/HWP/HWPX export, the editor is no longer a minor UI component. It is a core product capability and must have controlled requirements.

The editor must support three tightly linked responsibilities:

1. **assignment execution**: students complete work through structured blocks, notes, code, experiments, decisions, and reflections;
2. **evidence preservation**: editor content round-trips to canonical Markdown/editor JSON, Git commits, submission snapshots, and export manifests;
3. **report production**: the same source content can generate DOCX/HWP/HWPX/PDF outputs without replacing canonical evidence.

## 2. Editor scope

| Area | Required capability |
|---|---|
| Student assignment workspace | Edit student-owned `workspace/**` and `knowledge/**` content while assignment originals remain read-only. |
| Instructor assignment authoring | Author assignment brief, required blocks, rubric-linked reflection prompts, report templates, and allowed export formats. |
| TA/instructor review | Review canonical source, rendered view, Git/history evidence, generated reports, and export warnings. |
| Offline/local mode | Continue editing locally, autosave/checkpoint, and clearly distinguish local queued work from confirmed submission. |
| Export/reporting | Map blocks to Markdown, DOCX, HWP/HWPX, and optional PDF through versioned templates and export manifests. |

## 3. Block model requirements

| Block class | Examples | Required behavior |
|---|---|---|
| Text/structure | paragraph, heading, quote, callout, checklist | Preserve order, hierarchy, anchors, required-section validation, Markdown/export mapping. |
| Code | code snippet, file reference, compile command, output log | Preserve language, indentation, line references, file links, and safe rendering/export behavior. |
| Table | simple table, rubric table, experiment table | Support structured table editing, large/wide table handling, Markdown/DOCX/HWP export behavior. |
| Graph/diagram | Mermaid, graph JSON, image fallback | Preserve source, rendered snapshot/fallback, renderer profile, and export warnings. |
| Image/media | local image, screenshot, generated figure | Validate path, hash asset, alt/caption, missing/blocked path behavior, export inclusion. |
| Reference/citation | source link, textbook reference, file reference | Store citation/source fields and support academic-integrity review. |
| Experiment/evidence | hypothesis, method, result, observation, failure, conclusion | Link to code/test/evaluation evidence and optionally rubric criteria. |
| Decision/reflection | design choice, debugging decision, learning reflection | Link decision rationale to assignment section, code, experiment, or feedback. |
| Report placeholder | report section mapping, export-only field | Map source blocks into report templates without duplicating content manually. |

## 4. Editing behavior requirements

| Behavior | Requirement |
|---|---|
| Autosave/checkpoint | Student edits autosave locally and create meaningful checkpoints without requiring Git commands. |
| Undo/redo/version history | Local undo/redo and Git-backed checkpoint history must be available for student-visible recovery. |
| Conflict handling | Assignment sync must never overwrite `workspace/**` or `knowledge/**`; conflicts produce review tasks. |
| Required-block validation | Assignment templates may require planning, experiment, reflection, report, citation, or code-evidence blocks. |
| Collaborative boundary | Current baseline does not require live multi-user co-editing; instructor/TA review comments and feedback are separate controlled records. |
| Permission enforcement | Editor must enforce path/role/scope rules independent of UI hiding. |
| Korean editing | Korean IME, mixed Korean/English text, code blocks, fonts, and DOCX/HWP/HWPX export must be fixture-tested. |
| Accessibility/usability | Keyboard navigation, focus order, readable validation messages, and clear blocked-action messages are required before classroom pilot. |
| Performance | Large documents, tables, diagrams, images, logs, and Git diffs must not block normal UI operation. |
| Source/export round-trip | Editor JSON -> canonical Markdown -> rendered preview -> DOCX/HWP/HWPX/PDF export must preserve content or record explicit warnings. |

## 5. Editor data and evidence model

Each editable document should preserve:

| Field | Purpose |
|---|---|
| `document_id` | Stable document identifier |
| `document_type` | assignment_brief / student_workspace / knowledge_note / report_template / feedback_note |
| `owner_scope` | instructor / student / TA / system |
| `editable_paths` | Allowed repository paths for edits |
| `block_schema_version` | Editor block schema version |
| `canonical_markdown_hash` | Hash of canonical Markdown projection |
| `source_commit_sha` | Git commit linked to saved/checkpointed content |
| `validation_results` | Required block, asset, citation, report, privacy, and deadline checks |
| `export_bindings` | Template/report/export mappings |
| `audit_events` | High-impact edits, template changes, publish, submit, export, and override events |

## 6. Minimum V&V fixtures

1. Korean/English mixed text editing with IME.
2. C/C++ code block editing with indentation preserved.
3. Required planning/experiment/reflection blocks.
4. Table editing and wide-table rendering/export.
5. Mermaid/graph block source plus fallback snapshot.
6. Local image insert, missing image warning, blocked path rejection.
7. Citation/reference block and source-field validation.
8. Student autosave/checkpoint and Git history recovery.
9. Assignment update with no overwrite of `workspace/**` or `knowledge/**`.
10. DOCX export from report template.
11. HWPX/HWP export or controlled fallback warning.
12. Role/path permission bypass attempt.
13. Large document performance budget.
14. Canonical Markdown/editor JSON round-trip.

## 7. Explicit non-goals for current baseline

- No live Google-Docs-style multi-user co-editing in the initial baseline.
- No remote-only editor service dependency for normal assignment work.
- No uncontrolled plugin execution inside student/editor documents.
- No DOCX/HWP as authoritative source replacing canonical Markdown/editor JSON/Git evidence.

## 8. Open questions

1. Which editor stack should be fixture-spiked first: TipTap/ProseMirror in desktop shell, Lexical, Monaco+Markdown hybrid, native rich-text control, or a custom block editor?
2. Should code editing be embedded in the block editor or delegated to a Monaco-like code pane linked to blocks?
3. Which export path should be first-class for HWP: HWPX-first, LibreOffice/UNO conversion, Hancom automation profile, or server-side converter profile?

## 9. Gap-closure updates from Claude review

The editor requirements are now supported by a fixture-gated [Editor stack trade study](editor-stack-trade-study.md) and a vendor-neutral [Editor block schema baseline](block-schema.md). The editor shall not rely on hidden vendor state as canonical evidence. Korean IME handling is controlled by [Korean text handling profile](korean-text-handling-profile.md), and accessibility is controlled by [Accessibility baseline](accessibility-baseline.md).

## 10. Storage requirements update

The editor shall persist through [Notion-style document storage architecture](notion-style-document-storage-architecture.md). Notion-style editing requires explicit storage structures: canonical editor JSON, deterministic Markdown projection, operation journal, revision graph, content-addressed assets, rebuildable indexes, and Git checkpoints. Submission/export shall use materialized canonical revisions, not transient UI state.

## 11. Storage gap-closure requirements update

The editor shall expose or allow EduOps to control stable block identity, order keys, operation journal entries, projection materialization, schema migration state, tombstone lifecycle, and asset privacy. Toolkits that hide these structures behind opaque vendor state cannot pass the implementation-readiness gate.
