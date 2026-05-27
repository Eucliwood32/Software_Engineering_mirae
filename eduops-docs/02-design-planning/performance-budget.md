---
title: Performance Budget
document_id: SWENG-EDUTECH-PERFORMANCE-BUDGET
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Performance Budget

## 1. Purpose

Convert qualitative performance language into initial measurable budgets for desktop-first productization.

## 2. Initial measurement budgets

These are seed targets for fixture design; they may be revised after spike evidence.

| Operation | P50 seed | P95 seed | Notes |
|---|---:|---:|---|
| Editor keystroke-to-render | <= 50 ms | <= 120 ms | Excluding heavy export jobs |
| Autosave local checkpoint | <= 1 s | <= 3 s | For typical assignment document |
| Git checkpoint commit | <= 2 s | <= 8 s | Local repo; excludes network push |
| 60-student dashboard load | <= 2 s | <= 5 s | Cached local data |
| Assignment update preview diff | <= 3 s | <= 10 s | Typical assignment; large diff warns |
| DOCX export | <= 10 s | <= 30 s | Typical report fixture |
| HWPX export/fallback | <= 15 s | <= 45 s | Fixture dependent; warnings allowed |
| C/C++ evaluation feedback | <= 30 s | <= 120 s | Small assignment profile |

## 3. Measurement rules

Performance tests shall record hardware profile, OS version, data fixture size, repository size, renderer profile, and whether network operations were simulated or live. Marketing claims shall not use fixture-only measurements without qualification.

## 4. Traceability

- Non-functional requirements: `EDUOPS-NFR-011`, `EDUOPS-NFR-012`, `EDUOPS-NFR-018`, `EDUOPS-NFR-023`
- Decision: `EDUOPS-DEC-034`
- Risk: `EDUOPS-R-037`

## 5. Storage performance budget seeds

| Operation | Seed budget |
|---|---:|
| Append edit operation | P95 under 100 ms for normal text/code/table edits |
| Autosave materialization | P95 under 2 s for normal assignment document |
| Index rebuild from canonical files | P95 under 10 s for one student workspace package |
| Projection generation | P95 under 5 s for normal document; warning if large media/diagram fallback dominates |
| Git checkpoint creation | P95 under 10 s excluding remote network push |
