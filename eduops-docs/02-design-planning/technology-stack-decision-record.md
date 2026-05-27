---
title: Technology Stack Decision Record
document_id: SWENG-EDUTECH-TECH-STACK-DR
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  decisions: ['EDUOPS-DEC-009', 'EDUOPS-DEC-010', 'EDUOPS-DEC-047', 'EDUOPS-DEC-048', 'DEC-OS-001']
  candidates: ['EDUOPS-CFR-001']
---

# Technology Stack Decision Record

## 1. Purpose

This record selects the initial implementation stack for the local-first Windows and Linux desktop beta path. The selection is sufficient to start SLICE-A/B/C with fake/local adapters. It does not approve live GitHub, live classroom, or official grading side effects.

## 2. Accepted stack

| Area | Accepted option | Status | Beta rationale | Constraints |
|---|---|---|---|---|
| Desktop shell | Tauri 2 Windows/Linux desktop shell. Windows uses WebView2; Linux uses the Tauri-supported system webview runtime. | Accepted | Small desktop package, explicit command bridge, good fit for local-first app, compatible with HTML/CSS/SVG/Canvas rendering. | Web UI must be packaged as desktop; no standalone hosted web product. Platform runtime details must be recorded in gate evidence. |
| Runtime/core | Rust application core with TypeScript UI | Accepted | Rust owns file, Git, DB, worker, and process boundaries; TypeScript owns UI/editor integration. | UI cannot call filesystem, Git, DB, or worker APIs except through the command/query contract. |
| Editor substrate | ProseMirror/Tiptap-style editor adapter over canonical EduOps block schema | Accepted for beta spike | Mature schema/transaction model and ecosystem for document blocks, code, tables, images, diagrams, history, and IME fixtures. | Vendor/editor JSON is not source of truth; canonical `BlockDocument` remains authoritative. |
| Local DB | SQLite via Rust SQLx or equivalent typed Rust access layer | Accepted | Embedded, deterministic, transaction-capable, inspectable, suitable for local cache/index/evidence metadata. | Canonical documents and Git evidence remain file/Git artifacts; DB indexes are rebuildable unless declared evidence. |
| Git library | `git2`/libgit2 through a Git adapter, with Git CLI fallback only behind the same adapter | Accepted | Enables local fake/plain Git flows and later GitHub-first extension while preserving transaction boundaries. | No direct Git calls from UI/editor modules; fake/local adapter required before live remote actions. |
| Exporter substrate | Canonical document to HTML/Markdown intermediate, DOCX via document-generation library, HWPX via package/XML writer profile | Accepted for beta | Keeps exports derived from canonical evidence and supports Korean report formats without making converters authoritative. | Legacy HWP remains converter-dependent derived output with warning manifest. |
| Packaging tool | Tauri bundler for Windows MSI/NSIS and Linux package candidates | Accepted for beta | Windows/Linux desktop packaging path aligns with the local-first product boundary. | Signing/update channel and exact Linux distribution/package matrix remain later release-engineering work. |
| C/C++ toolchain | LLVM/Clang for beta fixture runner; MSVC detection is advisory compatibility work | Accepted for local advisory runner | Clang is scriptable and reproducible for initial fixtures; official grading still requires approved runner/sandbox. | Student local runs are advisory; official evidence requires accepted evaluation runner profile. |
| Evaluation location | Local advisory worker for SLICE-E; no official grading worker until fixture and sandbox gates pass | Accepted | Preserves no-live-action-before-fixture-gates and avoids premature host-risk claims. | Official evaluation cannot be inferred from local advisory results. |

## 3. Rejected or deferred options

| Option | Decision | Reason |
|---|---|---|
| Standalone hosted Next.js/web application | Rejected for current baseline | Violates desktop-first/local-first product boundary. |
| Electron as first shell | Deferred | Viable but heavier; Tauri better fits local command boundary and packaging footprint. |
| Fully native WinUI editor | Deferred | Higher custom-editor cost before block/schema/export behavior is proven. |
| Browser/editor state as source of truth | Rejected | Conflicts with canonical JSON, deterministic Markdown projection, and Git evidence baseline. |
| Direct GitHub Classroom or Google Classroom connector | Rejected for beta | Classroom systems are benchmarks, not live integrations. |
| Official grading on student workstation | Rejected | Local machine state is unsuitable as authoritative grading evidence. |

## 4. Decision closure

- `EDUOPS-DEC-009` is closed by selecting Tauri 2, Windows/Linux desktop target, Rust core, TypeScript UI, and ProseMirror/Tiptap-style editor adapter for the beta path.
- `EDUOPS-DEC-010` is closed for beta by selecting LLVM/Clang local advisory execution and deferring official grading to the approved runner/sandbox profile.

## 5. Implementation guardrails

- All external side effects start in fake/local mode.
- The adapter layer owns Git, exporter, runner, and later GitHub calls.
- The application core owns authorization, audit, idempotency, and state transitions.
- The UI shell owns presentation and user intent capture only.
- Stack replacements require an accepted decision row and fixture comparison evidence.
