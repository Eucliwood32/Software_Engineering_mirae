---
title: HISYS EduOps Student Knowledge System and Export Profile
document_id: SWENG-EDUTECH-KNOWLEDGE-EXPORT
title_ko: 학생 지식체계 및 DOCX/HWP 내보내기 프로파일
version: 0.2.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Student Knowledge System and Export Profile

## 1. Differentiation conclusion

EduOps differentiates from GitHub Classroom and Google Classroom by making assignment execution itself a **Notion-style knowledge-work process** rather than a file-upload or repository-only workflow.

The student does not merely submit code or attachments. The student builds a personal, course-bounded knowledge system while solving assignments:

```text
Assignment brief
-> student planning notes
-> code/design decisions
-> experiments and evidence
-> reflection/learning notes
-> submission snapshot
-> DOCX/HWP/report export
-> reusable personal knowledge base
```

This profile is a product-baseline design input, not an LMS integration. It preserves the current Windows desktop, GitHub-first, no-LMS, role-separated, access-controlled baseline.

## 2. Product differentiation statement

| Reference product | Typical strength | EduOps differentiation |
|---|---|---|
| GitHub Classroom | Git repository distribution, code submission, autograding, PR feedback | Adds Notion-style task execution, structured learning notes, knowledge graph/history, DOCX/HWP report export, and student-owned knowledge reuse. |
| Google Classroom | Course/roster/coursework/submission/grade convenience | Adds Git-backed code/evidence traceability, local-first student workspace, structured assignment execution notebook, and reproducible report/evidence export. |
| Generic LMS | File submission and grade workflow | Adds knowledge-system creation as an assessed and reusable artifact, not only final answer upload. |

## 3. Student knowledge workspace model

A student workspace should contain both protected assignment content and student-owned knowledge artifacts:

```text
student-workspace/
├─ assignment/                 # read-only assignment original synced from instructor
├─ workspace/                  # student-editable code/work products
├─ knowledge/                  # student-owned assignment knowledge system
│  ├─ notes/                   # planning, concept notes, reflections
│  ├─ decisions/               # student design/implementation decision records
│  ├─ experiments/             # run logs, screenshots, test evidence, observations
│  ├─ references/              # allowed references/citations/source links
│  └─ index.md                 # generated/curated knowledge map
├─ reports/                    # generated DOCX/HWP/HWPX/PDF/Markdown report outputs
└─ metadata/                   # system-managed state and protected evidence
```

`knowledge/**` is student-editable but subject to export, citation, privacy, academic-integrity, and submission-snapshot rules. It must never be overwritten by assignment synchronization.

## 4. Notion-style assignment execution features

| Feature | Requirement intent | Evidence/control |
|---|---|---|
| Block-based assignment workspace | Students solve assignments through structured blocks: task, explanation, code excerpt, table, graph, image, checklist, decision, experiment, reflection. | Editor JSON plus canonical Markdown export and block validation. |
| Linked knowledge map | Notes, code files, decisions, tests, and references can be linked into a student knowledge map. | `knowledge/index.md`, backlinks, source hashes where applicable. |
| Assignment-to-knowledge promotion | Student can promote useful solution notes into reusable personal/course knowledge after submission. | Promotion record with scope, source assignment, timestamp, and privacy boundary. |
| Reflection and learning evidence | Assignment template can require hypothesis, method, result, error analysis, and learning reflection blocks. | Required-block validation and review rubric linkage. |
| Reusable report templates | Instructor can define report templates mapped from assignment/knowledge blocks. | Template version, field mapping, export profile, and validation result. |

## 5. DOCX and HWP export profile

DOCX/HWP export is a first-class product differentiator for Korean university/classroom contexts where report submission often requires Office or Hangul formats.

| Format | Baseline handling | Verification expectation |
|---|---|---|
| Markdown | Canonical inspectable source and Git evidence baseline | Round-trip with editor JSON and submission snapshot. |
| DOCX | Required export target for report-style submissions and feedback packets | Template-controlled output; tables/images/code blocks/citations preserved; export hash recorded. |
| HWP/HWPX | Required Korean institutional export target, preferably via HWPX when technically feasible and HWP through an approved converter/profile when required | HWPX/HWP fixture export validates headings, tables, images, code blocks, Korean text, metadata, and warning/fallback behavior. |
| PDF | Optional review/archive convenience output | Generated from the same controlled source; not a replacement for canonical Markdown/Git evidence. |

Important control: DOCX/HWP files are derived outputs. The authoritative evidence remains editor JSON, canonical Markdown, protected metadata, Git commit SHA, and export manifest.

## 6. Export manifest

Each generated report export should create an export manifest:

| Field | Purpose |
|---|---|
| `export_id` | Unique export event ID |
| `student_id` / `assignment_instance_id` | Trace to student and assignment |
| `source_commit_sha` | Git evidence for source content |
| `template_id` / `template_version` | Report template trace |
| `format` | markdown/docx/hwpx/hwp/pdf |
| `tool_profile` | Export engine/converter name and version |
| `content_hash` | Hash of generated output |
| `warnings` | Unsupported element, font, layout, missing asset, conversion warning |
| `redaction_profile` | Privacy/redaction setting used |
| `created_by` / `created_at` | Actor and timestamp |

## 7. V&V fixture set

Minimum export/knowledge fixtures:

1. simple Korean/English text report;
2. C/C++ code block with syntax/style preservation;
3. wide table and rubric table;
4. graph/diagram block with fallback image/source;
5. local image with caption/alt text;
6. missing image blocked or warning export;
7. student knowledge note linked to code/test evidence;
8. reflection block required by assignment template;
9. DOCX export hash/manifest;
10. HWPX/HWP export or controlled unsupported-profile warning;
11. submission snapshot includes generated report manifest;
12. privacy/redaction check before sharing/export.

## 8. Risks and controls

| Risk | Control |
|---|---|
| Export output diverges from canonical assignment evidence | Treat DOCX/HWP as derived outputs with manifests, hashes, and source commit links. |
| HWP support is technically fragile or proprietary | Prefer HWPX/open conversion profile first; require converter/version record and fallback warnings. |
| Student knowledge base leaks private/course-restricted information | Scope knowledge promotion, redaction, and export permissions; require privacy review for shared knowledge artifacts. |
| Knowledge-system features distract from assignment completion | Provide assignment-template-required blocks and lightweight defaults; keep student UI simple. |
| AI/automation or copy-paste pollutes student-owned knowledge | Preserve source/citation fields and instructor-visible evidence where required by policy. |

## 9. Open questions

1. Should HWPX be the primary controlled Korean format, with legacy HWP as a converter-dependent profile?
2. Should personal knowledge promotion be per-assignment opt-in, course-policy controlled, or always available locally to the student?
3. Should exported DOCX/HWP reports be instructor-required submission artifacts or optional student/reporting outputs?

## 10. Editing requirement dependency

The student knowledge/export profile depends on controlled editor requirements. The editor must preserve block identity, source payload, validation state, Git checkpoint evidence, and report/export mapping. See [Notion-style editing requirements profile](notion-style-editing-requirements-profile.md).

## 10. Gap-closure updates from Claude review

`knowledge/**` is now governed by [Knowledge topology and submission policy](knowledge-topology-submission-policy.md) and [Student knowledge policy](knowledge-policy.md). Export behavior is governed by [HWP and HWPX export strategy](hwp-export-strategy.md) and [Export fidelity acceptance criteria](export-fidelity-acceptance.md). The phrase round-trip means canonical-to-derived traceability with explicit loss/warning records, not mandatory reverse import from DOCX/HWP/HWPX.
