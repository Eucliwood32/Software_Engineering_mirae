---
title: Rendering Engine Cost and Reuse Analysis
document_id: SWENG-EDUTECH-RENDER-COST
version: 0.1.0
status: draft
date: 2026-05-12
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Rendering Engine Cost and Reuse Analysis

## 1. Analysis conclusion

Owning a reusable rendering capability can be strategically valuable across EduOps and other SysAI Lab projects, but the recommended investment is **not a full custom rendering engine first**. The best first investment is a reusable **rendering contract + adapter SDK + fixture suite + evidence snapshot pipeline**.

This creates reusable value without taking on the cost of a browser/text-layout/table-layout/GPU engine.

## 2. Effort estimate

| Option | Scope | Team assumption | Calendar estimate | Person-month estimate | Recommendation |
|---|---|---:|---:|---:|---|
| A. Rendering adapter MVP | Canonical blocks, graph/table/image fixtures, HTML5/SVG rendering, image validation, export snapshot, role-view proof | 2 people | 2-4 months | 4-8 PM | Best first step |
| B. Reusable rendering core | Project-agnostic package/API, plugin renderer registry, Canvas/WebGL profile, snapshot hashing, cross-project docs | 3 people | 4-8 months | 12-24 PM | Strong strategic target |
| C. Full custom renderer | Own document layout, table layout, graph rendering, image pipeline, export, editor integration | 5 people | 12-24 months | 60-120 PM | Too large for current stage |
| D. Production full engine | Cross-platform custom engine with accessibility, IME, GPU fallback, packaging, long-term maintenance | 6 people | 18-36 months | 108-216 PM | Only if rendering becomes a standalone product line |

PM = person-months. Estimates assume experienced developers and normal QA/documentation. They exclude opportunity cost from EduOps product features delayed by renderer work.

## 3. Reuse value across projects

A reusable renderer is valuable if it is framed as a controlled rendering subsystem rather than as a monolithic engine.

Reusable assets:

- canonical document/block model;
- graph/table/image block schemas;
- renderer adapter API;
- HTML5/SVG/Canvas/WebGL renderer profiles;
- local asset validation and hashing;
- fallback/error evidence model;
- snapshot/export package format;
- fixture suite for rendering regression tests;
- role/profile-specific view filtering;
- audit metadata for renderer version, input hash, output hash, and failure reason.

Likely reusable project classes:

| Project type | Reuse fit |
|---|---|
| EduOps assignment documents | High |
| Lapidary Markdown/graph/image workspace rendering | High |
| Hisys evidence/report rendering | High |
| Royul generated configuration/report previews | Medium-high |
| Solis simulation graph/trace visualization | Medium, especially graph profiles |
| General web/mobile UI | Medium, if the contract remains portable |

## 4. Cost drivers

The major cost is not drawing pixels. The cost is correctness, evidence, compatibility, and maintenance:

1. Korean IME/editor behavior;
2. table layout edge cases;
3. graph layout determinism;
4. image path/security validation;
5. export/snapshot consistency;
6. accessibility and keyboard navigation;
7. platform packaging and GPU fallback;
8. renderer sandboxing;
9. regression fixtures;
10. long-term API compatibility.

## 5. Recommended staged plan

### Stage 0: Rendering contract and fixtures, 2-4 weeks

Outputs:

- block schema draft;
- graph/table/image fixture corpus;
- evidence snapshot schema;
- renderer profile metadata;
- pass/fail harness.

### Stage 1: Adapter MVP, 2-4 months, 4-8 PM

Outputs:

- HTML5/CSS/SVG renderer path;
- image validation and hashing;
- Markdown/export snapshot;
- student/instructor view proof;
- initial Next.js or desktop-shell prototype candidate.

### Stage 2: Reusable core, 4-8 months, 12-24 PM

Outputs:

- project-agnostic rendering package;
- adapter plugin API;
- Canvas/WebGL optional profile;
- cross-project fixtures;
- versioned rendering evidence format.

### Stage 3: Full custom engine, only if justified, 12-24+ months

Entry criteria:

- mature engines fail documented fixtures;
- rendering becomes a product capability shared by multiple revenue/project lines;
- team can fund long-term maintenance;
- accessibility/IME/export/security requirements are resourced.

## 6. Decision gate

Before building a new renderer, require this evidence:

| Gate | Required evidence |
|---|---|
| Fixture failure | Existing HTML5/SVG/Canvas/WebGL stack fails important fixtures |
| Business reuse | At least three projects commit to using the renderer contract |
| Maintenance owner | A team/owner accepts versioning, QA, security, and compatibility obligations |
| Export evidence | Custom path can generate reproducible snapshots better than existing substrates |
| Opportunity-cost approval | EduOps feature delay is explicitly accepted |

## 7. Recommended decision

Adopt **Option B as the strategic target**, but start with **Option A**.

Do not start with Option C/D. The first milestone should prove that an EduOps/SysAI reusable rendering core can control graph/table/image/evidence behavior while delegating low-level layout and GPU work to mature engines.

## 8. Traceability

| Decision / requirement | Cost-analysis implication |
|---|---|
| EDUOPS-DEC-017 | Rendering quality is a first-class product requirement |
| EDUOPS-DEC-019 | Mature rendering substrates are preferred before a new engine |
| EDUOPS-DEC-020 | Reusable rendering core is a strategic option, but full custom engine is gated |
| EDUOPS-FR-033 | Graph/table/image fixtures are required |
| EDUOPS-NFR-012 | Rendering performance/fallback evidence is required |
