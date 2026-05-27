---
title: Export Fidelity Acceptance Criteria
document_id: SWENG-EDUTECH-EXPORT-FIDELITY
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Export Fidelity Acceptance Criteria

## 1. Purpose

Clarify what EduOps means by export round-trip and define acceptance criteria for DOCX/HWPX/HWP/PDF derived outputs.

## 2. Round-trip meaning

The controlled baseline requires **canonical-to-derived traceability**, not lossless reverse import from DOCX/HWPX/HWP into the canonical editor model.

Required path:

```text
Editor JSON + Markdown + assets + metadata
→ rendered preview
→ DOCX/HWPX/HWP/PDF derived output
→ export manifest with warnings and hashes
→ reviewer can trace every derived section back to canonical block IDs
```

Reverse import from DOCX/HWPX/HWP is a future optional profile and shall not be required for MVP acceptance.

## 3. Loss categories

| Category | Examples | Acceptance |
|---|---|---|
| Forbidden silent loss | Missing code block, dropped image, missing required reflection, wrong student identity | Fail |
| Warned visual drift | Table width change, font fallback, diagram rasterization | Pass with warning if canonical evidence preserved |
| Allowed derived limitation | Legacy HWP cannot preserve interactive graph source | Pass only with fallback snapshot and source link |
| Privacy redaction | Removed private note or raw token | Pass if manifest records redaction profile without exposing secret |

## 4. Quantitative acceptance seeds

| Artifact | Seed threshold |
|---|---|
| Required text blocks | 100% present by block ID mapping |
| Code block text | Exact text preservation except normalized line endings |
| Korean text | Unicode normalized to selected profile; no character loss |
| Images | Hash-matched source or declared resized derivative with dimensions |
| Tables | Cell text 100% present; layout drift warning when width/page overflow occurs |
| Diagrams | Source preserved in canonical evidence; output has rendered image or warning |
| Export manifest | Source SHA, block schema, template, tool profile, output hash, warnings all present |

## 5. Traceability

- Requirements: `EDUOPS-FR-046`, `EDUOPS-FR-055`
- Non-functional requirements: `EDUOPS-NFR-016`, `EDUOPS-NFR-019`, `EDUOPS-NFR-022`
- V&V: `STD-047`
