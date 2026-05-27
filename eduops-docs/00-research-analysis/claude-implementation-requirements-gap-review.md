---
title: Claude Implementation Requirements Gap Review
document_id: SWENG-EDUTECH-CLAUDE-IMPL-REQ-GAP-REVIEW
version: 0.1.0
status: draft
created: 2026-05-14
updated: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  iso9001: ['7.5', '8.3', '8.5', '9.1']
  related: ['SWENG-EDUTECH-SRS', 'SWENG-EDUTECH-IMPL-REQ-GAP', 'SWENG-EDUTECH-IMPL-EXEC-PLAN']
---

# Claude Implementation Requirements Gap Review

## 1. Purpose

This document records a read-only Claude Code advisory analysis of implementation-needed requirements that remain missing, under-specified, misclassified, duplicated, or incorrectly prioritized in the EduOps controlled draft package.

## 2. Review scope

| Item | Scope |
|---|---|
| Reviewer | Claude Code read-only analysis, orchestrated by Hermes |
| Repository state | `83e2002 docs: identify eduops implementation requirement gaps` |
| Files emphasized | `01-requirements/implementation-requirements-gap-register.md`, `01-requirements/requirements-record.md`, `06-implementation/implementation-readiness-gap-analysis.md`, `06-implementation/implementation-executability-improvement-plan.md` |
| Boundary | No file edits by Claude; Hermes records the advisory analysis as controlled draft information. |

## 3. Overall verdict

Claude's verdict is **conditional fail for implementation readiness**: the gap register is useful, but the gap register itself contains gaps.

Main conclusions:

1. `requirements-record.md` already promotes the P0 implementation-contract bundle through `EDUOPS-FR-067`, `EDUOPS-FR-068`, and `EDUOPS-NFR-029`, while `implementation-requirements-gap-register.md` still lists the same P0 items as open candidate requirements. The register therefore needs a status/synchronization field such as `promoted to FR-067; document still required`.
2. The register defines `EDUOPS-CVR-*` for verification candidates but lists no CVR candidates, even though fixture gates, deterministic harnesses, accessibility checks, and performance checks are essential implementation requirements.
3. Several items are under-prioritized: state-machine transition tables and fixture gates are treated too late even though they are prerequisites for early vertical slices.
4. Additional implementation requirements are missing for conflict resolution, authoritative time, secret storage, notifications, search indexing, Korean IME behavior, audit taxonomy, error-code taxonomy, asset handling, backup/archive, app update, i18n/config, and test-data privacy.

## 4. Recommended candidate additions

### 4.1 P0 candidates

| Candidate ID | Candidate requirement | Why it matters |
|---|---|---|
| EDUOPS-CVR-001 | Define local fixture gates for SLICE-A/B/C, including pass criteria and required artifacts such as hashes, manifests, and logs. | Without verification gates, the no-live-action-before-fixtures rule cannot be enforced. |
| EDUOPS-CFR-007 | Promote state-machine transition tables for student lifecycle, submission, and assignment release/update into code-authoritative requirements. | Queued/pushed/confirmed and lifecycle gates are needed before early implementation. |
| EDUOPS-CFR-008 | Define deterministic conflict detection/resolution for `assignment/**`, `workspace/**`, and `knowledge/**`. | "Do not overwrite" is not enough to implement sync safely. |
| EDUOPS-CFR-009 | Define authoritative time/clock service rules for deadlines, commit timestamps, release windows, late status, and offline clock drift. | Dispute reconstruction depends on consistent timestamp semantics. |
| EDUOPS-CVR-002 | Define privacy-safe test data and fixture generation rules. | Fixtures must not contain real PII or leak student-private information. |

### 4.2 P1 candidates

| Candidate ID | Candidate requirement | Why it matters |
|---|---|---|
| EDUOPS-CIR-011 | Define asset/binary adapter for images, diagrams, DOCX/HWPX/HWP derived artifacts, hashes, LFS candidates, and cleanup signals. | Asset handling crosses editor, export, Git, storage, and privacy boundaries. |
| EDUOPS-CIR-012 | Define secret/credential storage adapter using Windows DPAPI or equivalent OS-backed protection, including rotate/wipe behavior. | Token handling should not be hidden inside the GitHub adapter. |
| EDUOPS-CIR-013 | Define notification adapter for Windows toast and in-app notifications. | Assignment-update notifications are already product requirements but lack implementation contract. |
| EDUOPS-CIR-014 | Define rebuildable search-index adapter build/query/invalidate contract. | Search caches must respect privacy and rebuild from canonical artifacts. |
| EDUOPS-CIR-015 | Define Korean IME/editor composition contract. | Korean IME support cannot be left as a generic editor-quality claim. |
| EDUOPS-CFR-010 | Define schema-migration runner contract, quarantine path, downgrade rejection, warning manifest, and migration API. | Schema migration rules need executable signatures. |
| EDUOPS-CFR-011 | Define audit-event taxonomy and versioned schema. | Audit records need stable code values and required field semantics. |
| EDUOPS-CFR-012 | Define error-code taxonomy and retry/terminal/UI-display classification. | Cross-adapter failures need consistent machine-readable errors. |

### 4.3 P2 candidates

| Candidate ID | Candidate requirement | Why it matters |
|---|---|---|
| EDUOPS-CIR-016 | Define backup/archive operation contract. | Archive, withdrawal cleanup, and retention require implementation operations. |
| EDUOPS-CIR-017 | Define app update/installer signing/rollback contract. | Windows desktop delivery needs update governance. |
| EDUOPS-CVR-003 | Define accessibility verification harness. | Accessibility baseline needs executable checks. |
| EDUOPS-CVR-004 | Define performance benchmark harness with hardware profile, deterministic seed, and commands. | P50/P95 targets need reproducible measurement. |
| EDUOPS-CNFR-004 | Define i18n/locale contract for ko-KR/en-US, NFC normalization, date/number formatting, and sorting. | Korean/English course operations need deterministic locale behavior. |
| EDUOPS-CNFR-005 | Define system/user configuration contract, storage location, migration, defaults, and precedence. | Configuration otherwise becomes scattered across modules. |

## 5. Current register defects to fix

| Defect | Recommended fix |
|---|---|
| P0 candidates duplicate already-promoted SRS items. | Add a status column and mark `EDUOPS-CFR-001..005` as `promoted via EDUOPS-FR-067 / document still required`. |
| `EDUOPS-CVR-*` class is defined but unused. | Add CVR candidates for fixture gates, privacy-safe test data, accessibility harness, and performance harness. |
| Fixture corpus is classified as `CFR` and P1 only. | Reclassify the gate aspect as P0 `CVR`; keep fixture corpus content as P1 document detail if needed. |
| State-machine transition tables are P2. | Promote to P0/P1 because they are needed for early submission/lifecycle implementation. |
| Export pipeline and warning emitter are split awkwardly. | Merge warning/loss emitter into exporter implementation specification or define a clear subordinate interface. |
| Partial-coverage rows lack candidate-ID mapping. | Add explicit candidate IDs to each refinement in the register's partial-coverage table. |

## 6. Recommended promotion order

1. Patch the register status model: distinguish `candidate`, `promoted`, `document-required`, `superseded`, and `merged`.
2. Split `EDUOPS-FR-067` into traceable P0 subrequirements or map `EDUOPS-CFR-001..005` to it as promoted subitems.
3. Promote local fixture gates and state-machine transition tables before SLICE-A/B implementation.
4. Promote conflict-resolution, clock service, and privacy-safe fixtures before student/assignment sync work.
5. Promote adapter contracts in this order: Git, local storage, asset/binary, editor bridge, Korean IME, secret store, GitHub, runner, notification, search.
6. Promote audit taxonomy and error-code taxonomy before multi-worker integration.
7. Promote backup/update/accessibility/performance/i18n/config candidates during later integration hardening.

## 7. Risk if not addressed

- Developers or agents may treat already-promoted P0 items as still open candidates and encode temporary architecture decisions directly in code.
- Live-action gates may become subjective because CVR-level fixture and harness requirements are missing.
- Korean IME and HWPX/DOCX differentiation may fail late if editor/asset/export contracts are not promoted early.
- Deadline, late status, and audit disputes may be unreproducible without authoritative time and audit taxonomy requirements.
- Token/notification/search concerns may leak into unrelated adapters, making privacy and secret-handling verification weak.

## 8. Hermes interpretation

The next controlled-document action should be to revise `implementation-requirements-gap-register.md` rather than immediately writing source code. The revision should add status fields, add CVR candidates, re-prioritize state machine and fixture gate work, and record the new P0/P1/P2 candidates above. After that, promote selected P0 items into the SRS/DDP/STD and only then draft the P0 implementation-contract documents.
