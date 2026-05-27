---
title: Korean Text Handling Profile
document_id: SWENG-EDUTECH-KOREAN-TEXT
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Korean Text Handling Profile

## 1. Purpose

Define Korean-language handling controls for editor, Git paths, search, export, and evidence stability.

## 2. Baseline controls

- Korean/English mixed text shall be preserved in editor JSON, Markdown, preview, DOCX, HWPX/HWP, and export manifests.
- Unicode normalization policy shall be explicit for text fields, filenames, search indexes, and hashes.
- IME composition shall not trigger broken autosave, duplicate characters, or noisy checkpoint commits.
- Font fallback for DOCX/HWPX/HWP shall be recorded in export manifests when it affects layout.
- Markdown filenames in controlled project docs remain English; student-visible assignment titles may contain Korean.

## 3. Traceability

- Requirements: `EDUOPS-FR-051`
- Non-functional requirements: `EDUOPS-NFR-018`, `EDUOPS-NFR-022`
- V&V: `STD-051`

## 6. Markdown projection normalization

Korean/English mixed text shall be normalized to NFC before canonical hashing and Markdown projection. Projection output uses LF line endings even on Windows. IME composition events must not create partial operation journal entries that split Hangul syllable composition incorrectly.
