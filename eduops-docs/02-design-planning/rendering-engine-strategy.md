---
title: Rendering Engine Strategy
document_id: SWENG-EDUTECH-RENDER-ENGINE
version: 0.2.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Rendering Engine Strategy

## 1. Decision summary

Next.js or other web UI technology is acceptable when packaged inside the desktop product or used in a platform-specific UI, provided the product still satisfies the EduOps rendering, evidence, role, and performance contracts. The current baseline concern is not whether HTML/web technology is used; the concern is whether graph, table, image, document preview, export, and evidence rendering work reliably.

EduOps should **not build a completely new rendering engine first**. The recommended strategy is to define a controlled rendering contract and use mature rendering substrates such as HTML5/CSS/SVG/Canvas and WebGL selectively, with a thin EduOps rendering adapter around them. A custom engine should remain a later option only if fixture evidence shows that mature engines cannot satisfy required graph/table/image behavior. Because rendering capability may be reused by other projects, EduOps should first invest in a reusable rendering contract, adapter SDK, fixture suite, and evidence snapshot pipeline rather than a full custom engine.

## 2. Recommended rendering architecture

```text
Canonical document model
  -> block normalization and validation
  -> rendering adapter API
    -> HTML5/CSS/SVG renderer for text, tables, layout, diagrams
    -> Canvas/WebGL renderer for heavy or interactive graph views when needed
    -> image pipeline for local assets, captions, hashes, thumbnails
  -> preview surface in student/instructor UI
  -> export/evidence snapshot with renderer profile and hashes
```

The product should own:

- canonical block schema;
- validation rules;
- asset path/hash policy;
- renderer profile metadata;
- fallback/error evidence;
- snapshot/export consistency checks.

The product should not initially own:

- low-level text layout engine;
- general table layout engine;
- general GPU/WebGL scene engine;
- complete browser replacement;
- custom graph layout engine, unless later justified.

## 3. Technology stance

| Candidate | Stance | Rationale |
|---|---|---|
| Next.js | Conditionally allowed | Acceptable as UI/application layer if desktop packaging, offline behavior, role separation, performance, and evidence contracts pass. It is not mandatory. |
| HTML5/CSS | Preferred mature substrate for document layout | Strong table/text/image layout ecosystem and good cross-platform behavior. |
| SVG | Preferred first substrate for diagrams/graphs | Inspectable, exportable, deterministic enough for many educational diagrams. |
| Canvas | Allowed for high-volume interactive rendering | Useful for large graph/table visualizations, but needs snapshot/export controls. |
| WebGL | Optional profile for complex/large graph rendering | Use when graph complexity or interactivity needs GPU acceleration; require fallback snapshot and non-GPU fallback. |
| Rendering adapter/core | Build first | Reusable across projects while delegating low-level layout/GPU work to mature substrates. |
| Custom rendering engine | Defer | High cost and risk; only consider after fixture-driven failure of mature engines and cross-project commitment. |

## 4. Build-versus-use rule

Use existing engines first when they satisfy the contract. Build custom rendering only for narrow adapters or missing capabilities.

| Question | Preferred answer |
|---|---|
| Do we need a new full renderer now? | No. |
| Do we need an EduOps rendering contract? | Yes. |
| Do we need renderer fixtures and evidence snapshots? | Yes. |
| Do we need a custom graph/table/image adapter layer? | Yes, likely. |
| Do we need WebGL immediately? | Not for ordinary assignments; add as optional profile for large/interactive graphs. |

## 5. Acceptance gates before selecting Next.js or another stack

Any UI/rendering stack shall pass:

1. graph/table/image fixture rendering;
2. large table and large graph responsiveness tests;
3. Markdown/editor/export round-trip checks;
4. local image path validation and missing/stale image evidence;
5. role-separated student/instructor rendering views;
6. offline/local preview behavior;
7. deterministic enough exported evidence snapshots;
8. package-size, startup, update, and security review;
9. sandboxing or trust-boundary review for rendered content;
10. no silent rendering failure.

## 6. Traceability

| Decision / requirement | Rendering-engine implication |
|---|---|
| EDUOPS-DEC-016 | Next.js/web UI is conditionally allowed if rendering/evidence contracts pass |
| EDUOPS-DEC-017 | Platform-specific UI is acceptable if graph/table/image rendering is controlled |
| EDUOPS-DEC-019 | Mature rendering substrates are preferred before building a new engine |
| EDUOPS-DEC-020 | Rendering engine ownership should begin as reusable adapter/core, not a full custom renderer |
| EDUOPS-FR-033 | Graph/table/image rendering must be verified |
| EDUOPS-NFR-012 | Rendering performance/fallback behavior must be verified |


See also [Rendering engine cost and reuse analysis](rendering-engine-cost-reuse-analysis.md).
