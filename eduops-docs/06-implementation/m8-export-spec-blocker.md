---
title: M8 Exporter Implementation Specification Gap Closure
document_id: EDUOPS-M8-EXPORT-SPEC-BLOCKER
version: 0.2.0
status: constrained-delegation-authorized
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - SWENG-EDUTECH-HWP-EXPORT
    - SWENG-EDUTECH-EXPORT-FIDELITY
    - SWENG-EDUTECH-BLOCK-SCHEMA
  gaps_recorded:
    - Exporter implementation specification (M8 row in implementation-milestones §6)
    - Constrained fixture-local exporter type contract authorized by user
---

# M8 Exporter Implementation Specification Gap Closure

## 1. Purpose

This document records the controlled gap-closure decision for the exporter implementation specification before the M8 SLICE-G export fixture and DEMO-1 evidence package gate is claimed. The "Exporter implementation specification" entry in the milestone-gated gap table of [Implementation milestones §6](implementation-milestones.md) is listed as `Required before M8` with the rationale that DOCX/HWPX output needs controlled writer behavior and fidelity thresholds before implementation.

[HWP and HWPX export strategy](../02-design-planning/hwp-export-strategy.md) defines an export baseline (HWPX preferred Korean interchange profile; legacy HWP as converter-dependent compatibility profile; canonical → HWPX generator, canonical → DOCX → HWPX/HWP converter, Hancom automation profile, LibreOffice/UNO profile, server-side converter routes; manifest fields covering source document IDs and commit SHA, block schema version, template ID/version, export tool route/version/OS/fonts/locale, output hash and timestamp, warnings/unsupported blocks/fallback artifacts, privacy/redaction profile, reviewer-visible canonical evidence link; initial fidelity fixtures for Korean title/paragraph, multi-level headings, wide table, C/C++ code block, local image with alt/hash/DPI), and [Export fidelity acceptance](../02-design-planning/export-fidelity-acceptance.md) defines acceptance criteria at the strategy/design level. They do not yet contain:

- a concrete `ExportRequest` / `ExportResult` / `ExportManifest` / `ExportArtifact` type contract for the `eduops_export::ExportAdapter` trait covering canonical-document input, route selection, target format, locale/font profile, redaction profile, and fallback policy;
- a controlled writer profile registry per route (`canonical-hwpx-generator`, `canonical-docx-then-hwpx-converter`, `hancom-automation`, `libreoffice-uno`, deferred `server-side-converter`) with tool/version/license/fidelity-profile bindings and a deterministic profile-selection rule;
- a controlled `ExportManifest` JSON schema with sorted canonical keys, SHA-256 over output artifacts, warning records, unsupported-block records, fallback-artifact records, privacy/redaction profile, and audit-event linkage;
- an enumerated `export_warning_code` set distinct from `EDUOPS_IO_*`, `EDUOPS_GATE_*`, `EDUOPS_RUNNER_*`, and `EDUOPS_VALIDATION_*` covering unsupported block types, font fallback, table-cell overflow, image DPI fallback, code-block monospace fallback, table-of-contents regeneration, citation rewrite, and converter-tool warnings;
- fidelity threshold definitions per writer profile (Korean title/paragraph round-trip, heading hierarchy preservation, table cell preservation, code block formatting preservation, image dimensions/DPI tolerance, citation/cross-reference preservation) with measurable accept/reject criteria;
- fallback artifact lifecycle rules (when a route fails, which fallback artifact is emitted; how the manifest records the failure; how the consolidated DEMO-1 harness reports partial-success vs full-failure);
- privacy/redaction profile types and binding rules for student PII, institutional identifiers, instructor notes, and review-private blocks;
- audit evidence requirements covering pre-export authorization, route selection record, tool invocation record, post-export evidence handoff, and the DEMO-1 consolidated harness contract;
- fail-closed offline rule consistent with AC-009 of the [access-control authorization model](../02-design-planning/access-control-authorization-model.md) for export routes that cannot prove tool availability or license status.

Authoring or commissioning an exporter implementation specification crosses a design/decision boundary that requires human review of converter licensing (Hancom automation, LibreOffice/UNO, server-side converter), DOCX/HWPX fidelity authority (acceptable fallback per block type, Korean locale handling, font substitution), privacy/redaction policy across student-visible vs reviewer-visible artifacts, host tool execution policy (LibreOffice/UNO and Hancom automation invoke host processes; server-side converter crosses live-external-action boundaries), and academic/operations approval for what counts as a "demonstration" claim under DEMO-1. The Ralph loop must not author or accept that specification directly under its non-delegable safety boundary because:

- license selection across HWPX/DOCX/Hancom/LibreOffice routes requires acquisition and legal review owned by a human authority;
- DOCX/HWPX fidelity acceptance thresholds are an academic/institutional decision that owns the "loss profile" definition;
- host tool execution (LibreOffice/UNO/Hancom automation) requires host-policy review and falls outside Ralph's fixture-only execution boundary;
- the DEMO-1 evidence package crosses a "live demo" boundary that requires explicit human approval before any consolidated demonstration claim is made;
- privacy/redaction policy for institutional artifacts crosses retention/legal review that Ralph does not hold.

## 2. Decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-M8-EXPORT-SPEC-DEFERRED` |
| Decision date | 2026-05-15 |
| Status | constrained delegation authorized; full exporter remains deferred |
| Authority required | human design owner with converter-license, fidelity, privacy/redaction, host-tool-execution, and DEMO-1 approval authority |
| Ralph delegation | authorized only for constrained fixture-local type contract and manifest-only export evidence |

The full exporter implementation specification remains deferred for real DOCX/HWPX generation, converter licensing, host-tool execution, privacy/legal approval, and DEMO-1 acceptance. The user has authorized Ralph to author and execute a constrained fixture-local type contract in [Exporter implementation specification — constrained fixture-local type contract](../02-design-planning/exporter-implementation-specification.md). M8 may produce executable `M8-T*` RED/GREEN rows only inside that constrained scope.

## 3. M8 status under this gap-closure decision

M8 status after constrained delegation:

- the `eduops_export` crate may define fixture-local `ExportRequest`, `ExportResult`, `ExportArtifact`, `ExportManifest`, warning-code, target-format, and writer-profile types;
- Ralph may queue RED/GREEN export-adapter tests for manifest-only fixture evidence;
- no host process is invoked for export (no LibreOffice/UNO/Hancom automation, no server-side converter);
- no live external action is performed by Ralph during M8 work;
- real DOCX/HWPX writer behavior, fidelity acceptance, privacy/legal policy, and DEMO-1 acceptance remain deferred to an authorized human owner.

This constrained closure does not claim, demonstrate, or imply real DOCX/HWPX exporter behavior or DEMO-1 evidence acceptance. It permits only fixture-local type contracts, manifest-only evidence, placeholder/fallback artifact records, deterministic hashes, and safety guards.

## 4. Required follow-up before claiming exporter implementation

The following work shall be completed by an authorized human owner before any milestone or gate claims DOCX/HWPX exporter behavior or DEMO-1 evidence:

1. author `docs/02-design-planning/exporter-implementation-specification.md` covering:
   - `ExportRequest` / `ExportResult` / `ExportArtifact` / `ExportManifest` type contract for the `eduops_export::ExportAdapter` trait with canonical-document input, route selection, target format, locale/font profile, redaction profile, fallback policy, and audit linkage;
   - controlled writer profile registry per route (`canonical-hwpx-generator`, `canonical-docx-then-hwpx-converter`, `hancom-automation`, `libreoffice-uno`, deferred `server-side-converter`) with tool/version/license/fidelity-profile bindings, deterministic profile-selection rule, and explicit fail-closed behavior when tool/license is unavailable;
   - `ExportManifest` canonical JSON schema with sorted keys, SHA-256 over output artifacts, warning records, unsupported-block records, fallback-artifact records, privacy/redaction profile, source-document/commit-SHA/block-schema-version linkage, template ID/version, and audit-event linkage;
   - enumerated `export_warning_code` set distinct from `EDUOPS_IO_*`, `EDUOPS_GATE_*`, `EDUOPS_RUNNER_*`, and `EDUOPS_VALIDATION_*`;
   - fidelity threshold definitions per writer profile covering Korean title/paragraph, heading hierarchy, table cell, code block, image dimensions/DPI tolerance, and citation/cross-reference preservation, with measurable accept/reject criteria;
   - fallback artifact lifecycle rules and the DEMO-1 consolidated harness contract (partial-success vs full-failure reporting);
   - privacy/redaction profile types and binding rules for student PII, institutional identifiers, instructor notes, and review-private blocks;
   - audit evidence requirements covering pre-export authorization, route selection record, tool invocation record, post-export evidence handoff, and DEMO-1 acceptance;
   - fail-closed offline rule consistent with AC-009 of the [access-control authorization model](../02-design-planning/access-control-authorization-model.md);
   - test requirements aligned with the M8 acceptance gates (Korean and English text/headings/code blocks/tables/images/citations preserved within declared loss profile; export manifest hash-linked to canonical source; DEMO-1 evidence remains local-only with `live_external_action=false`; prior slice gates pass together in consolidated demo run);
2. author an explicit acceptance/decision record updating the milestone-gated gap table entry from open to closed;
3. update the affected RTM and STD rows to reference the new specification as the exporter implementation acceptance source;
4. coordinate with the [block schema](../02-design-planning/block-schema.md) for export-aware block fields, with the [notion-style document storage architecture](../02-design-planning/notion-style-document-storage-architecture.md) for canonical-source linkage, and with the [working demonstration and evidence plan](../03-verification-validation/working-demonstration-evidence-plan.md) for the DEMO-1 harness contract.

After this work, a later Ralph or implementation pass may create executable `M8-T*` fixture-local tasks restricted to a single writer profile (initially likely `canonical-hwpx-generator`) and shall not invoke host tools, real LibreOffice/UNO/Hancom processes, or server-side converters under Ralph.

## 4A. Constrained delegation accepted on 2026-05-15

The user explicitly authorized Ralph to proceed with the recommended constrained scope:

```text
Ralph may author the M8 constrained fixture-local exporter type contract.
Allowed: ExportRequest/ExportResult/ExportArtifact/ExportManifest, warning codes,
manifest-only fixture export, deterministic evidence hash.
Excluded: real DOCX/HWPX generation, Hancom/LibreOffice/UNO/server-side converter,
host process execution, live external action, fidelity/privacy/DEMO-1 acceptance claim.
```

The accepted constrained specification is [Exporter implementation specification — constrained fixture-local type contract](../02-design-planning/exporter-implementation-specification.md). The follow-up checklist in §4 remains authoritative for any future full exporter, but it is no longer a blocker for the constrained `M8-T1` through `M8-GATE` Ralph queue.

## 5. Why this is a recorded blocker rather than a closed gap

The Ralph safety boundary prohibits live external action, destructive change, host process execution, and any work that requires authority Ralph does not hold. Authoring the exporter implementation specification is a design decision pass that requires:

- converter license authority across HWPX/DOCX/Hancom/LibreOffice routes;
- fidelity threshold authority owned by the academic/operations function;
- privacy/redaction policy authority crossing retention/legal review;
- host-tool execution authority for LibreOffice/UNO/Hancom automation;
- live external action authority for any deferred server-side converter route;
- DEMO-1 evidence acceptance authority crossing demonstration approval;
- design owner sign-off through the [decision log](../05-decisions/decision-log.md);
- coordination with the [HWP and HWPX export strategy](../02-design-planning/hwp-export-strategy.md), [Export fidelity acceptance](../02-design-planning/export-fidelity-acceptance.md), and [Working demonstration and evidence plan](../03-verification-validation/working-demonstration-evidence-plan.md).

Recording the gap as a controlled blocker (mirroring [`EDUOPS-M3-BRIDGE-SPEC-BLOCKER`](m3-bridge-spec-blocker.md), [`EDUOPS-M5-AUTH-SPEC-BLOCKER`](m5-auth-spec-blocker.md), and the initial [`EDUOPS-M6-RUNNER-IO-SPEC-BLOCKER`](m6-runner-io-spec-blocker.md) pattern) preserves traceability without overclaiming exporter acceptance or inventing implementation work outside Ralph's safety boundary.

## 6. Traceability

| Reference | Source |
|---|---|
| Milestone-gated gap table row | [Implementation milestones §6](implementation-milestones.md) — "Exporter implementation specification" row |
| Export strategy baseline | [HWP and HWPX export strategy](../02-design-planning/hwp-export-strategy.md) |
| Export fidelity baseline | [Export fidelity acceptance](../02-design-planning/export-fidelity-acceptance.md) |
| Knowledge export profile | [Student knowledge export profile](../02-design-planning/student-knowledge-export-profile.md) |
| Demonstration plan | [Working demonstration and evidence plan](../03-verification-validation/working-demonstration-evidence-plan.md) |
| Risk register | [Risk register](../04-risk-management/risk-register.md) — DOCX/HWPX fidelity, converter licensing, demo overclaim |
| Prior gap-closure precedent | [M3 editor adapter bridge specification gap closure](m3-bridge-spec-blocker.md), [M5 scoped submission and review authorization specification gap closure](m5-auth-spec-blocker.md), [M6 evaluation runner I/O contract specification gap closure](m6-runner-io-spec-blocker.md) |

## 7. Non-claims

This document does not implement an exporter adapter, invoke any DOCX/HWPX writer or converter (LibreOffice/UNO, Hancom automation, server-side converter), produce real output artifacts, accept any fidelity threshold, approve any writer profile or license, or claim DEMO-1 evidence acceptance. It records constrained delegation for fixture-local manifest-only M8 work while preserving the full-export deferral.
