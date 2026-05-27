---
title: Repository Retention and LFS Policy
document_id: SWENG-EDUTECH-REPO-RETENTION
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Repository Retention and LFS Policy

## 1. Purpose

Control repository growth caused by checkpoints, submission snapshots, generated reports, images, logs, and evaluation artifacts.

## 2. Baseline policy

Canonical evidence should remain lightweight and inspectable. Large/generated artifacts shall use controlled retention, artifact storage, or LFS profiles only after review. Generated DOCX/HWPX/HWP/PDF outputs are derived outputs and may be regenerated when canonical source and export profile remain available.

## 3. Initial controls

- Keep canonical Markdown/editor JSON/metadata under Git.
- Store generated reports only when submitted/released or required for audit.
- Hash and reference large logs/assets; avoid repeated binary duplication across checkpoints.
- Define course archive profile before pilot.
- Use LFS or artifact store only with explicit cost/privacy/offline review.

## 4. Traceability

- Requirements: `EDUOPS-FR-046`
- Risk: `EDUOPS-R-038`

## 4. Notion-style storage artifact policy

| Artifact | Default Git policy | LFS policy | Retention/privacy control |
|---|---|---|---|
| `*.eduops.json` | Track | No | Canonical source; include privacy class and schema/storage version |
| `*.md` | Track | No | Derived deterministic projection; regenerated from JSON when needed |
| `*.manifest.json` | Track | No | Required for projection/export/hash warnings |
| `assets/images/*`, `assets/diagrams/*`, `assets/attachments/*` | Track when evidence/export asset; ignore or local-only while private draft | LFS for large non-private binaries | Govern by asset privacy matrix and manifest hash |
| `.eduops/autosave/` | Ignore | No | Local crash recovery; cleanup on archive/withdrawal/device handoff |
| `.eduops/journals/` | Ignore by default; summarize operation ranges in manifest/checkpoint | No | Local recovery/audit diagnosis; not official evidence unless materialized |
| `.eduops/indexes/` and search indexes | Ignore | No | Rebuildable cache; privacy-class filtered |
