---
title: EduOps Requirements Consistency Review
document_id: SWENG-EDUTECH-REQ-CONSISTENCY-REVIEW
version: 0.1.1
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  source_documents:
    - ../01-requirements/requirements-record.md
    - ../01-requirements/requirements-analysis.md
    - ../01-requirements/development-constraints.md
    - ../01-requirements/implementation-requirements-gap-register.md
    - ../02-design-planning/technology-stack-decision-record.md
    - ../02-design-planning/configuration-contract.md
    - ../02-design-planning/credential-storage-contract.md
    - ../03-verification-validation/software-test-description.md
    - ../03-verification-validation/verification-validation-plan.md
    - ../05-decisions/decision-log.md
  advisory_review: Claude read-only developer/requirements review, 2026-05-14
---

# EduOps Requirements Consistency Review

## 1. Purpose

This document records a read-only consistency review of the current HISYS EduOps requirements baseline. The review checks for product-level contradictions, stale open questions, ambiguous staged requirements, numbering/traceability defects, and requirements that could cause developer confusion before implementation.

## 2. Review method

The review used two evidence streams:

1. Automated local inspection over Markdown files excluding `build/`:
   - controlled Markdown count: 65 files;
   - identifier/reference scan for `EDUOPS-*`, `STD-*`, `CFG-FIX-*`, and scenario IDs;
   - keyword scan for likely conflict terms such as `desktop`, `Next.js`, `LMS`, `GitHub`, `official evaluation`, `queued`, `confirmed`, `raw credential`, and `live integration`;
   - frontmatter/link scan excluding generated `build/` outputs.
2. Claude read-only developer/requirements review over the requirements, decision, verification, implementation-gap, configuration, and credential documents.

The review did not modify source requirements. This document is a findings record for controlled follow-up.

## 3. Overall conclusion

No critical product-direction contradiction was found. The active baseline is internally coherent at the product level:

- Windows desktop-first/local-first delivery remains the baseline.
- Web/Next.js technology is allowed only as a packaged/controlled desktop or platform-specific UI substrate, not as standalone hosted web delivery.
- GitHub is the first repository backend, while fake/local adapters and no-live-action fixture gates control implementation staging.
- LMS and Google Classroom live integration remain excluded; Google Classroom and GitHub Classroom are benchmark/reference systems.
- C/C++ evaluation is a first evaluation profile; local beta execution is advisory until an approved sandbox/official runner exists.
- Configuration and credential handling now require controlled contracts before implementation.

The review found several **major stale/open-question and traceability issues** that should be corrected before treating the requirements package as implementation-stable. Most issues are not true business-rule conflicts; they are stale document-control states, incomplete cross-references after later decisions, numbering defects, or section-scope ambiguity.

## 4. Findings

| ID | Severity | Classification | Evidence | Finding | Recommended controlled-document fix |
|---|---|---|---|---|---|
| REQ-CON-001 | Major | Stale open question | `01-requirements/requirements-record.md` §8 lines 167-169; `05-decisions/decision-log.md` `EDUOPS-DEC-047`, `EDUOPS-DEC-048` | The SRS still lists UI framework/editor, C/C++ toolchain, and evaluation location as remaining questions even though beta stack and beta C/C++ execution baseline are accepted by decisions. | Move the closed items into resolved-question status or mark them `closed by EDUOPS-DEC-047/048`; leave only truly open supported-Windows-version scope if undecided. |
| REQ-CON-002 | Major | Stale open question | `01-requirements/requirements-analysis.md` §9 open-question rows and §12 closure text | Requirements analysis reportedly closes some open questions but still lists them as open. | Update the open-question table with `Closed`, `Partially closed`, or `Open` statuses and decision traces. |
| REQ-CON-003 | Major | Incorrect decision status | `05-decisions/decision-log.md` `EDUOPS-DEC-009`; `02-design-planning/technology-stack-decision-record.md` §4 | `EDUOPS-DEC-009` bundles supported platform boundary and exact UI/editor/rendering component. `EDUOPS-DEC-047` closes the stack choice, but not necessarily the exact supported Windows version. | Split `EDUOPS-DEC-009` or mark it `partially closed by EDUOPS-DEC-047`; keep Windows-version support as open until decided. |
| REQ-CON-004 | Major | Incomplete P0 gate trace | `01-requirements/requirements-record.md` `EDUOPS-FR-067`; `05-decisions/decision-log.md` `EDUOPS-DEC-052`; SRS §17 | `EDUOPS-FR-067` lists P0 implementation contracts but does not include the newly promoted configuration/credential contracts, even though `EDUOPS-DEC-052` makes configuration a pre-coding blocker. | Amend `EDUOPS-FR-067` to include configuration and credential-reference contracts or cross-reference `EDUOPS-FR-073..077`. |
| REQ-CON-005 | Major | Staged requirement requiring clarification | SRS evaluation requirements; `EDUOPS-DEC-048`; `evaluation-execution-profile.md` | Product-level automated evaluation requirements and beta advisory execution are compatible, but the distinction between advisory beta worker and official grading should remain explicit wherever evaluation requirements are cited. | Add a short cross-reference from evaluation requirements to `EDUOPS-DEC-048` and the evaluation execution profile to avoid implementers treating local advisory runs as official grading. |
| REQ-CON-006 | Minor | Acceptable staged requirement | SRS desktop baseline; rendering and technology-stack docs | Desktop-first delivery and conditional WebView/Next.js/web-technology use are not contradictory when interpreted as technology substrate versus delivery mode. Some terse document-map wording can still look contradictory to readers. | Preserve the distinction: standalone hosted web/mobile delivery is excluded; web UI technology packaged inside a controlled desktop shell is allowed after gates. |
| REQ-CON-007 | Minor | Acceptable staged requirement | SRS GitHub-first baseline; implementation plan no-live-action gates | GitHub-first repository backend and fake/local/no-live-action implementation gates are not contradictory. They define target backend sequence versus safe implementation staging. | Keep both; ensure every GitHub requirement references dry-run/local fixture gates before live connector use. |
| REQ-CON-008 | Minor | Acceptable staged requirement | SRS no-LMS baseline; classroom benchmark docs | Google Classroom and GitHub Classroom benchmark references do not conflict with no-LMS/no-live-integration baseline. They are reference systems, not integrations. | Keep benchmark docs clearly marked as reference-only and fixture-only until explicit promotion. |
| REQ-CON-009 | Minor | Potential duplicate scope | `01-requirements/requirements-record.md` `EDUOPS-FR-002`, `EDUOPS-FR-022` | Both requirements mention roster CSV/JSON import/export. Their intended scopes differ but the boundary is not fully explicit. | Clarify `EDUOPS-FR-022` as grade/evaluation export plus controlled roster snapshot exchange, with `EDUOPS-FR-002` owning primary roster import/versioning. |
| REQ-CON-010 | Minor | Section numbering/control defect | `01-requirements/requirements-record.md`, `01-requirements/requirements-analysis.md`, `03-verification-validation/verification-validation-plan.md`, `03-verification-validation/software-test-description.md`, `01-requirements/development-constraints.md` | Several documents have skipped or duplicated section numbers. This is not a semantic conflict but weakens controlled-document review. | Renumber sections or add explicit `Reserved` placeholders during the next cleanup revision. |
| REQ-CON-011 | Minor | Identifier order/control defect | `01-requirements/development-constraints.md`; `05-decisions/decision-log.md` | Some IDs are out of chronological/numeric order, for example late placement of `EDUOPS-DEC-013` and development-constraint insertions. | Preserve historical IDs but either reorder rows or add a note that IDs are historical and not sorted. |
| REQ-CON-012 | Minor | Frontmatter date staleness | README, INDEX, SRS, requirements analysis, development constraints, decision log | Some frontmatter dates remain `2026-05-12` while content includes 2026-05-13/14 decisions. | On the next content correction, bump version/date metadata for affected controlled documents. |
| REQ-CON-013 | Minor | Traceability gap | `02-design-planning/configuration-contract.md` gate `G-CFR-1` | Most configuration gates trace to `EDUOPS-CVR-*`, but `G-CFR-1` does not have the same explicit CVR binding. | Add a CVR trace or define a new CVR row for configuration schema presence/registration checks. |
| REQ-CON-014 | Minor | Section scope drift | `01-requirements/requirements-record.md` §4.4 | Section title `Repository backend and operating modes` now contains role UI, dashboards, document model, editor, rendering, knowledge, and export requirements. | Split §4.4 into topic sub-sections or rename it to cover backend, modes, document/editor, role UI, and export requirements. |

## 5. Recommended correction order

1. Correct stale open-question/status items: `REQ-CON-001`, `REQ-CON-002`, `REQ-CON-003`.
2. Update the P0 implementation gate trace: `REQ-CON-004`.
3. Add evaluation-staging clarification: `REQ-CON-005`.
4. Clean section numbering, section scope, frontmatter dates, and traceability polish: `REQ-CON-009..014`.

## 6. Review disposition

The requirements package can continue as a controlled draft, but it should not be described as fully consistency-clean until the major stale-status items are corrected. The current issues are suitable for a documentation cleanup commit; no production code should be started from the affected stale open-question rows without applying or explicitly waiving these corrections.


## 7. Cleanup disposition

A 2026-05-14 cleanup pass addressed the major document-control findings recorded above:

- `REQ-CON-001` and `REQ-CON-002`: beta stack, beta C/C++ toolchain, beta evaluation location, roster/identity, and GitHub topology questions were reclassified as closed or partially closed; exact supported Windows versions and manual override approvers remain open.
- `REQ-CON-003`: `EDUOPS-DEC-009` was changed from closed to partially closed by `EDUOPS-DEC-047`.
- `REQ-CON-004`: `EDUOPS-FR-067` now includes configuration and credential-reference/storage contracts in the P0 implementation gate.
- `REQ-CON-009`: roster import/export scope was clarified between `EDUOPS-FR-002` and `EDUOPS-FR-022`.
- `REQ-CON-010` and `REQ-CON-011`: major section-numbering issues were cleaned up, and development-constraint ID ordering was documented as historical.
- `REQ-CON-012`: affected document frontmatter dates/versions were bumped for this cleanup.
- `REQ-CON-013`: configuration schema gate trace now includes `EDUOPS-CVR-010`.
- `REQ-CON-014`: SRS §4.4 was renamed to reflect backend, modes, document model, and editor scope.

Remaining controlled decisions after cleanup are not contradictions: exact supported Windows versions, final official evaluation runner/sandbox approval, and allowed manual override approvers remain open baseline decisions.
