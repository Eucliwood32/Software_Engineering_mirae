---
title: Fast Controlled Desktop UI Baseline
document_id: SWENG-EDUTECH-UI
version: 0.4.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Fast Controlled Desktop UI Baseline

## 1. Decision summary

Next.js is no longer categorically excluded from the HISYS EduOps product baseline. The product remains **desktop-first** for the current baseline, and web UI technology such as Next.js may be used if it is packaged/controlled within the desktop or platform-specific product boundary and passes rendering, evidence, offline, role-separation, security, and performance gates. Later product lines may choose platform-specific UI implementations, but they must preserve the same document and rendering contracts.

The document-first/Notion-style assignment model remains accepted. The UI decision changes the implementation layer, not the product concept:

- assignment authoring and student work remain document-first;
- canonical evidence remains Markdown export, Git commits, refs/tags, and controlled metadata;
- rich editing may use desktop-native, embedded web, or Next.js-based components if they pass the rendering/evidence contract;
- Git operations, validation, synchronization, and evaluation shall run asynchronously behind the UI.

## 2. UI baseline principles

| Principle | Baseline |
|---|---|
| Delivery | Desktop-first current baseline; platform-specific UI allowed later |
| Web-stack stance | Next.js/web UI is conditionally allowed; standalone web/mobile product delivery remains out of current baseline unless separately promoted |
| Responsiveness | Normal save, navigation, diff, validation-result display, and mode switching shall not block the UI thread |
| Document rendering | Markdown-first evidence with a fast rich editor/viewer layer; graph, table, and image rendering are first-class capability requirements |
| Git UX | Git operations hidden from normal users; progress, errors, and evidence links visible |
| Large-class usability | Student lists, submissions, logs, and diffs require virtualized/incremental rendering |
| Safety | Mode/context visibility and confirmation gates remain prominent |
| Role separation | Student and instructor/professor users shall have different primary UI surfaces and feature sets |
| Offline/local behavior | Local edits and queued commits remain usable when GitHub is unavailable |
| Platform-specific implementation | Later platforms may use different UI frameworks if they satisfy the same document/rendering/evidence contract |

## 3. Preferred implementation direction

The preferred direction is a **fast native Windows desktop UI** with a clearly separated application/service core:

```text
Fast controlled UI shell, native or web-based
  -> Application service layer
    -> Git synchronization engine
    -> Document model and Markdown export
    -> Validation/evaluation jobs
    -> Local persistence/indexing
    -> GitHub backend adapter
```

Candidate UI technologies may include native Windows/.NET desktop frameworks, Qt/Avalonia-style desktop toolkits, or Next.js/web-based UI packaged inside a controlled desktop or platform-specific shell. The selection criterion is not native-vs-web ideology; it is whether the stack passes graph/table/image rendering fidelity, evidence/export consistency, offline/local behavior, role separation, package-size/security review, startup/performance budgets, and background-job responsiveness. Platform-specific UI stacks are acceptable later, but graph/table/image rendering fidelity and evidence consistency are mandatory across implementations.

## 4. Performance expectations

Initial UI verification shall cover these acceptance seeds:

| Area | Acceptance seed |
|---|---|
| Startup | Desktop shell opens to course/role selection without loading Git history synchronously |
| Navigation | Course, assignment, student, and submission lists use virtualized/incremental rendering |
| Editing | Student document editing preserves input responsiveness while background autosave/checkpoint jobs run |
| Diff viewing | Assignment update diffs render incrementally and do not overwrite `workspace/**` |
| Git operations | Pull, sync, commit, submit, and evaluation-trigger operations run as cancellable/progress-reporting background jobs |
| Validation feedback | Document validation results display without blocking the editor |
| Graph rendering | Declared graph/diagram blocks render with controlled fallback source/snapshot evidence |
| Table rendering | Markdown and structured tables render with stable layout, scrolling/virtualization for large tables, and export consistency |
| Image rendering | Local images render with captions/alt text, missing-file warnings, path validation, and evidence/export inclusion |
| Audit/evidence view | SHA/ref/tag/evidence links are inspectable for instructors/admins without exposing Git CLI to students |
| Role-specific navigation | Student UI emphasizes workspace/submit/feedback; instructor UI emphasizes authoring/roster/monitoring/review/audit |

## 5. Traceability

| Decision / requirement | UI implication |
|---|---|
| EDUOPS-DEC-001 | UI must remain desktop-only, not web/mobile |
| EDUOPS-DEC-015 | Document-first assignment model remains active |
| EDUOPS-DEC-016 | Next.js/web UI is conditionally allowed if rendering/evidence/performance gates pass |
| EDUOPS-NFR-002 | Students must complete normal flows without Git CLI knowledge |
| EDUOPS-NFR-011 | UI responsiveness/performance must be verified |
| EDUOPS-FR-033 | Graph/table/image rendering contract must be verified |
| EDUOPS-NFR-012 | Rendering performance/fallback behavior must be verified |
| EDUOPS-FR-034 | Role-separated UI/function model must be verified |
| EDUOPS-NFR-013 | UI role separation must be backed by permission enforcement |

## 6. Open implementation questions

1. Which exact UI stack is selected first: WinUI 3/.NET, WPF/.NET, Qt, Avalonia, Next.js inside a desktop shell, or another toolkit?
2. Which rich-document editor/rendering component provides the best balance of speed, Markdown fidelity, Korean text input, graph/table/image support, and packaging simplicity?
3. Should the application service layer run in-process, as a local helper process, or as a local loopback service?
4. What are the first measured performance budgets for startup, assignment list rendering, autosave latency, diff rendering, and submission progress feedback?
5. What are the exact student vs instructor/professor navigation groups, command labels, and blocked-action messages?

See [Role-separated UI and feature model](role-separated-ui-feature-model.md) and [Rendering engine strategy](rendering-engine-strategy.md).
