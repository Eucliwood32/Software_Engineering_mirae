---
title: HWP and HWPX Export Strategy
document_id: SWENG-EDUTECH-HWP-EXPORT
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# HWP and HWPX Export Strategy

## 1. Purpose

Define a controlled Korean institutional document-export strategy for DOCX/HWPX/HWP while preserving canonical evidence in Git, editor JSON, Markdown, metadata, and export manifests.

## 2. Controlled export baseline

HWPX shall be the preferred Korean institutional interchange profile. Legacy binary HWP shall be treated as a converter-dependent compatibility profile, not as the canonical evidence format.

## 3. Export route options

| Route | Use | Risks | Control |
|---|---|---|---|
| Canonical → HWPX generator | Preferred first-class path | HWPX coverage and rendering fidelity | Versioned generator profile and fixture suite |
| Canonical → DOCX → HWPX/HWP converter | Compatibility path | Formatting drift, converter dependency | Tool/version/hash/warning record |
| Hancom automation profile | Institution-specific optional path | License, installation, automation fragility | Explicit licensed profile only |
| LibreOffice/UNO profile | Optional DOCX/PDF helper | HWP support weak, Korean layout risk | Use only after fidelity fixture pass |
| Server-side converter | Deferred profile | Conflicts with offline/local baseline and privacy | Not MVP unless user promotes hosted service boundary |

## 4. Export manifest requirements

Every derived output shall record:

- source document IDs and commit SHA;
- block schema version;
- template ID and version;
- export tool route, tool version, OS, fonts, locale;
- output hash and generated timestamp;
- warnings, unsupported blocks, fallback artifacts;
- privacy/redaction profile;
- reviewer-visible canonical evidence link.

## 5. Initial fidelity fixtures

1. Korean title/paragraph with mixed English and code identifiers.
2. Multi-level headings and numbered sections.
3. Wide table with Korean headers and numeric results.
4. C/C++ code block with indentation and monospace fallback.
5. Local image with alt text, hash, and DPI metadata.
6. Diagram block with source and fallback snapshot.
7. Citations/references and appendix evidence table.

## 6. Traceability

- Requirements: `EDUOPS-FR-044`, `EDUOPS-FR-045`, `EDUOPS-FR-046`, `EDUOPS-FR-055`
- Non-functional requirements: `EDUOPS-NFR-016`, `EDUOPS-NFR-019`, `EDUOPS-NFR-022`
- Decision: `EDUOPS-DEC-028`
- Risk: `EDUOPS-R-032`
