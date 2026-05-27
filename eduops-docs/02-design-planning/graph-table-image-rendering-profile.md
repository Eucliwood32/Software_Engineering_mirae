---
title: Graph Table Image Rendering Profile
document_id: SWENG-EDUTECH-RENDER
version: 0.2.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Graph Table Image Rendering Profile

## 1. Decision summary

The UI implementation may diverge by platform in later product lines. The current design constraint is therefore not "one UI stack everywhere". The critical product requirement is that **graphs, tables, and images render correctly, quickly, and reproducibly** in the assignment authoring, student workspace, review, feedback, and evidence/export flows.

This rendering profile is part of the document-first EduOps baseline. It preserves the Git-backed evidence model while allowing each platform to choose the most effective rendering implementation, including HTML5/CSS/SVG/Canvas/WebGL-based renderers when they satisfy the same controlled contract.

## 2. Rendering baseline

| Artifact type | Required behavior | Evidence boundary |
|---|---|---|
| Graphs/diagrams | Render controlled graph/diagram blocks from a declared source format; preserve fallback text/source; support preview, review, and export snapshots | Graph source, renderer version/profile, rendered snapshot/hash where applicable |
| Tables | Render Markdown and structured table blocks with stable row/column layout, alignment, wrapping, scrolling, and large-table handling | Canonical Markdown/structured table source plus rendered-view verification fixture |
| Images | Render local workspace images and assignment assets with path validation, missing-file indication, sizing, captions/alt text, and export inclusion | Asset path, file hash, metadata, and missing/blocked asset evidence |

The renderer shall prioritize correctness and reviewability over decorative fidelity. A student or instructor must be able to tell whether the submitted evidence includes the intended graph/table/image and whether any asset is missing or stale.

## 3. Platform-specific UI allowance

Different platform implementations may use different UI frameworks or rendering engines if they satisfy the same rendering contract:

```text
Document source / editor JSON / Markdown
  -> canonical normalized document model
  -> platform-specific renderer
  -> visible preview + export/evidence snapshot
  -> validation result and audit metadata
```

The following are allowed:

- Windows-specific fast desktop renderer in the current baseline.
- Next.js or other web UI renderers when packaged/controlled and fixture-verified.
- HTML5/CSS/SVG renderers for document, table, image, and diagram layout.
- Canvas/WebGL renderers for large or interactive graph views when needed.
- Later platform-specific renderers for other platforms.
- Embedded rendering components when they are sandboxed/bounded and preserve the desktop/product boundary.

The following are not accepted without separate review:

- platform-specific rendering that changes the submitted canonical content;
- graph/table/image blocks that render in the editor but disappear from Markdown/export/evidence;
- remote-only rendering dependencies for normal assignment review;
- silent image/path failures;
- large graph/table rendering that blocks normal UI operation.

## 4. Candidate graph formats

The first implementation does not need to support every graph language. It should define a small controlled set and expand only after fixture evidence exists.

| Candidate | Use case | Initial stance |
|---|---|---|
| Mermaid-style diagrams | Flowcharts, sequence diagrams, state diagrams | Good first candidate if renderer can be packaged and sandboxed |
| Graphviz DOT | Directed graphs and dependency graphs | Good for formal/technical diagrams; requires local renderer/package review |
| Structured JSON graph | Internal graph blocks and future visual editors | Good canonical internal format candidate |
| Image-only graph snapshots | Stable evidence/export fallback | Required fallback for submitted/reviewed evidence |

## 5. Table rendering expectations

Tables are first-class assignment artifacts, not plain text decoration. Verification shall include:

- Markdown pipe tables;
- structured editor table blocks;
- wide tables with horizontal scrolling or responsive column behavior;
- large tables with virtualization/incremental rendering where needed;
- Korean/English text, code snippets, formulas-as-text, and links inside cells;
- export consistency between editor view, Markdown, and submission snapshot.

## 6. Image rendering expectations

Image support shall include:

- relative-path image references inside assignment and workspace directories;
- captions and alt text;
- missing image warnings;
- blocked path traversal or external unsafe path references;
- thumbnails/previews for large images;
- evidence/export inclusion or explicit unsupported-asset evidence;
- hash-based stale/missing asset detection where feasible.

## 7. Verification fixtures

Initial rendering V&V shall include fixture assignments containing:

1. one simple graph/diagram;
2. one complex graph/diagram large enough to test responsiveness;
3. one normal table;
4. one wide table;
5. one large table;
6. one local image;
7. one missing image;
8. one invalid/blocked image path;
9. one mixed document containing graph + table + image + references;
10. one submission/export round-trip confirming the evidence snapshot preserves the rendered artifacts or controlled fallbacks.

## 8. Traceability

| Decision / requirement | Rendering implication |
|---|---|
| EDUOPS-DEC-015 | Document-first assignment model requires rich artifact rendering |
| EDUOPS-DEC-016 | Next.js/web UI may be used if rendering/evidence/performance gates pass |
| EDUOPS-DEC-017 | Platform-specific UI implementations are acceptable if graph/table/image rendering contracts are satisfied |
| EDUOPS-DEC-019 | Mature HTML5/SVG/Canvas/WebGL substrates are preferred before a new rendering engine is built |
| EDUOPS-FR-033 | Graph/table/image rendering is a controlled functional requirement |
| EDUOPS-NFR-012 | Rendering performance and fallback behavior are verified |

## DOCX/HWP/HWPX export rendering extension

Graph/table/image rendering evidence now extends to DOCX and HWP/HWPX report exports. Export fixtures must verify that rendered blocks in the editor and canonical Markdown either appear faithfully in DOCX/HWP/HWPX outputs or produce explicit warnings/fallback artifacts in the export manifest. HWPX should be preferred as the controlled Korean document interchange profile when feasible; legacy HWP requires an approved converter/tool profile and warning behavior.
