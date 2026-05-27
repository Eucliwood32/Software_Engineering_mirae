---
title: M3 Editor Adapter Bridge Local-Safe Specification Authority
id: EDUOPS-DEC-067
version: 0.1.0
status: accepted
created: 2026-05-21
owner: develop
quality_context: controlled decision packet
traceability:
  upstream:
    - EDUOPS-DEC-M3-BRIDGE-SPEC-DEFERRED
    - EDUOPS-M3-BRIDGE-SPEC-BLOCKER
    - SWENG-EDUTECH-BLOCK-SCHEMA
    - SWENG-EDUTECH-DOCUMENT-STORAGE
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
  downstream:
    - ralph.md
    - docs/02-design-planning/editor-adapter-bridge-specification.md
---

# M3 Editor Adapter Bridge Local-Safe Specification Authority

## 1. Request context

The user approved the next planning/specification work within the local-safe boundary after the Ralph queue reached `NEXT: stop preflight` at commit `fb937c9`.

The prior blocker record `EDUOPS-DEC-M3-BRIDGE-SPEC-DEFERRED` stated that Ralph was not authorized to author or accept the editor adapter bridge specification because the work required editor-toolkit, Korean IME, and design-owner decisions. This decision supersedes that deferral only for a bounded local-safe documentation/control pass.

## 2. Decision

`EDUOPS-DEC-067` authorizes Ralph/Hermes to author a controlled HOW-level editor adapter bridge specification as a local documentation/control checkpoint.

The authorized scope is limited to:

| Area | Authorized local-safe content | Boundary |
|---|---|---|
| Editor adapter contract | Define an implementation-facing bridge between the accepted canonical block/document model and a desktop editor adapter. | No live editor runtime, no dependency adoption, no desktop UI launch. |
| Toolkit decision handling | Use the existing editor stack trade study and accepted beta stack as anchors; record candidate criteria and a fixture-gated baseline without installing or invoking a toolkit. | No package installation, no external download, no runtime proof claim. |
| Korean IME behavior | Specify composition-state preservation, autosave suppression during composition, and undo grouping from the Korean text handling profile. | No real IME runtime test or OS-level input capture. |
| Journal and persistence contract | Define import/export, operation-journal append, revision-chain expectations, validation hooks, and rollback behavior from existing storage and block-schema anchors. | No mutation of non-fixture/user data. |
| Verification planning | Add validation/test anchors sufficient for a later RED/GREEN fixture-local implementation queue. | No editor integration or DEMO claim in this decision. |

## 3. Selected next Ralph path

The first selected path is `M3-EDITOR-ADAPTER-BRIDGE-SPEC-PREP` because it is the lowest-side-effect task that converts the prior M3 blocker into an executable local documentation/control specification.

Ralph shall seed this queue:

1. `M3-BRIDGE-SPEC-AUTHORITY-PREP` — record this local-safe authority and supersede the prior deferral for specification authoring only.
2. `M3-EDITOR-ADAPTER-BRIDGE-SPEC-PREP` — author `docs/02-design-planning/editor-adapter-bridge-specification.md` from existing controlled anchors.
3. `M3-EDITOR-ADAPTER-BRIDGE-SPEC-GATE` — accept only the local-safe specification checkpoint after documentation validation.
4. `QUEUE-REFILL-PREP-POST-M3-EDITOR-ADAPTER-BRIDGE-SPEC` — classify the next safe follow-up; implementation rows remain blocked until the specification gate passes.

## 4. Non-claims

This decision does not authorize:

- real editor runtime adoption or package installation;
- Tiptap/ProseMirror/Lexical runtime execution;
- real Tauri runtime invocation, desktop launch, or screenshot/screen-recording evidence;
- live Korean IME capture or OS input-event testing;
- live filesystem mutation outside fixture-local files;
- credential lookup, credential storage, network calls, remote actions, GitHub API calls, repository administration, push, publication, release, installer creation, or deployment;
- DEMO-1 acceptance;
- M5 scoped authorization implementation, live GitHub integration, or real exporter/converter execution.

## 5. Acceptance criteria

The authority checkpoint is accepted only when:

- this decision is linked from `docs/README.md`, `docs/INDEX.md`, and `docs/05-decisions/decision-log.md`;
- the prior M3 blocker record has a supersession notice rather than being deleted;
- `ralph.md` has exactly one `next` row and the §7 `NEXT:` pointer names that row;
- Markdown local links resolve;
- JSON files parse;
- `git diff --check` passes;
- `npm run m0:check` passes;
- no non-delegable action is executed.
