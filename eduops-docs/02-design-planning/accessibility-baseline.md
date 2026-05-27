---
title: Accessibility Baseline
document_id: SWENG-EDUTECH-ACCESSIBILITY
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Accessibility Baseline

## 1. Purpose

Define the initial accessibility baseline for role-separated desktop UI and Notion-style editor behavior.

## 2. Baseline requirements

- Keyboard-only navigation for core student and instructor workflows.
- Visible focus order and no keyboard traps in block editor, dialogs, validation panels, and submission flow.
- Screen-reader labels for major controls, validation status, warnings, and submission state.
- Text alternatives for images/diagrams used as assignment evidence.
- Color shall not be the only indicator for validation, due dates, or submission state.
- Accessibility fixture tests shall be included before classroom pilot.

## 3. Traceability

- Non-functional requirements: `EDUOPS-NFR-024`
- V&V: `STD-052`

## 5. Storage-related accessibility controls

Projection/export warnings, tombstoned block notices, migration failures, and conflict states shall be keyboard reachable and screen-reader understandable. A student must be able to identify whether content is saved locally, checkpointed, submitted, or export-ready without relying only on color.
