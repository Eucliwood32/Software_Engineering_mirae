---
title: M3 Editor Adapter Bridge Specification Gap Closure
document_id: EDUOPS-M3-BRIDGE-SPEC-BLOCKER
version: 0.1.0
status: superseded-for-local-safe-spec-authoring
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - SWENG-EDUTECH-IMPLEMENTATION-EXECUTABILITY-IMPROVEMENT
    - SWENG-EDUTECH-IMPLEMENTATION-READINESS-GAP-ANALYSIS
    - SWENG-EDUTECH-IMPLEMENTATION-REQUIREMENTS-GAP-REGISTER
    - SWENG-EDUTECH-DOCUMENT-STORAGE
    - SWENG-EDUTECH-BLOCK-SCHEMA
  gaps_recorded:
    - IMPL-GAP-P1-003
    - EDUOPS-CIR-004
---

# M3 Editor Adapter Bridge Specification Gap Closure

## 1. Purpose

This document records the controlled gap-closure decision for the editor adapter bridge specification before the M3 SLICE-B canonical document gate is claimed. The editor adapter bridge specification (`editor-adapter-bridge-specification.md`) was listed in the milestone-gated gap table as required before M3, and in the implementation readiness gap analysis as `IMPL-GAP-P1-003`. The specification document has not been authored yet.

Authoring or commissioning an editor adapter bridge specification crosses a design/decision boundary that requires human review, editor toolkit selection input, Korean IME composition contract decisions, and acceptance authority. The Ralph loop must not author or accept that specification directly under its non-delegable safety boundary.

## 2. Decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-M3-BRIDGE-SPEC-DEFERRED` |
| Decision date | 2026-05-15 |
| Status | blocker-recorded; M3 gate scope constrained |
| Authority required | human design owner with editor toolkit decision authority |
| Ralph delegation | not authorized to author the specification |

The editor adapter bridge specification is deferred to a separate controlled document/decision pass. The M3 SLICE-B canonical document gate proceeds with explicitly constrained scope so it does not overclaim editor integration.

## 3. M3 gate scope constraint

M3 acceptance under this gap-closure decision is limited to:

- canonical `BlockDocument`/`EditorBlock` types in `eduops_domain`;
- deterministic canonical JSON and Markdown projection with SHA-256 hashes;
- operation journal replay for `insert_block`, `update_block`, and `delete_block` with stable block IDs and tombstone preservation;
- local document materialization producing `.eduops.json`, `.md`, and `.manifest.json` under owner-scope directories with deterministic source and projection hashes in the manifest;
- Korean text, code, and table projection fixtures with deterministic stable-block-ID output.

M3 acceptance under this gap-closure decision does not claim:

- editor adapter bridge implementation;
- editor toolkit selection (TipTap, ProseMirror, Lexical, custom, etc.);
- editor transaction import/export, node-to-block mapping, IME composition contract, undo grouping, or autosave suppression during composition;
- live editor UI integration with the desktop shell;
- assignment template clone with editor-attached lineage;
- comment/feedback attach behavior at the editor UI layer;
- export rendering pipeline.

## 4. Required follow-up before claiming editor integration

The following work shall be completed by an authorized human owner before any milestone or gate claims editor integration:

1. author `docs/02-design-planning/editor-adapter-bridge-specification.md` covering:
   - editor toolkit selection or candidate scoring against the [editor stack trade study](../02-design-planning/editor-stack-trade-study.md);
   - editor-to-block node mapping for the [block schema](../02-design-planning/block-schema.md) `heading`/`paragraph`/`checklist`/`code`/`table` baseline and the deferred typed blocks;
   - editor transaction import/export to the operation journal `insert_block`/`update_block`/`delete_block` API;
   - Korean IME composition contract (composition-state preservation, autosave suppression during composition, undo grouping) consistent with the [Korean text handling profile](../02-design-planning/korean-text-handling-profile.md);
   - validation/event hooks for block-level required-flag, privacy-class, and export-binding checks;
   - operation journal append API with revision-chain expectations;
   - error model and rollback behavior;
2. author an explicit acceptance/decision record updating the milestone-gated gap table entry from open to closed;
3. update `EDUOPS-CIR-004` and `IMPL-GAP-P1-003` to `closed` with the new specification document as the resolution reference.

Only after these steps may a later Ralph or implementation pass create executable editor-adapter-bridge tasks (`M3-EDITOR-T*`) or claim editor integration in an updated M3 evidence summary.

## 5. Why this is a recorded blocker rather than a closed gap

The Ralph safety boundary prohibits live external action, destructive change, and any work that requires authority Ralph does not hold. Authoring the editor adapter bridge specification is a design decision pass that requires:

- editor toolkit selection authority that depends on team-level cost/time and Korean IME risk acceptance;
- design owner sign-off through the [decision log](../05-decisions/decision-log.md);
- coordination with the [Korean text handling profile](../02-design-planning/korean-text-handling-profile.md) for composition contracts.

Recording the gap as a controlled blocker preserves traceability without overclaiming acceptance or inventing implementation work outside Ralph's safety boundary.

## 6. Traceability

| Reference | Source |
|---|---|
| Milestone-gated gap table row | [Implementation milestones §6](implementation-milestones.md) |
| P1 gap row | [Implementation readiness gap analysis](implementation-readiness-gap-analysis.md) `IMPL-GAP-P1-003` |
| P1-3 backlog row | [Implementation executability improvement plan](implementation-executability-improvement-plan.md) |
| Candidate requirement | [Implementation requirements gap register](../01-requirements/implementation-requirements-gap-register.md) `EDUOPS-CIR-004` |
| Block schema | [Block schema](../02-design-planning/block-schema.md) |
| Storage architecture | [Notion-style document storage architecture](../02-design-planning/notion-style-document-storage-architecture.md) |
| Editor stack candidates | [Editor stack trade study](../02-design-planning/editor-stack-trade-study.md) |
| Korean IME contract | [Korean text handling profile](../02-design-planning/korean-text-handling-profile.md) |

## 7. Supersession notice

`EDUOPS-DEC-067` supersedes this blocker only for local-safe authoring of `docs/02-design-planning/editor-adapter-bridge-specification.md`. The original non-claim boundary remains active for editor runtime adoption, dependency installation, live UI integration, desktop launch evidence, DEMO-1 claims, and any non-fixture/user-data mutation.

## 8. Non-claims

This document does not author the editor adapter bridge specification, select an editor toolkit, accept any Korean IME composition contract, or close the editor adapter bridge gap. It records the deferral and constrains the M3 gate scope so the canonical document path can be accepted on its own merits.
