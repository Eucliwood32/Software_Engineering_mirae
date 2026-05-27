---
title: Evaluation Execution Profile
document_id: SWENG-EDUTECH-EVAL-EXEC
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# Evaluation Execution Profile

## 1. Purpose

Resolve the open C/C++ evaluation execution gap by defining location, sandbox, resource, and evidence profiles before implementation.

## 2. Initial execution stance

EduOps shall use a controlled **local/lab runner profile** before live GitHub Actions or hosted runners. Student PC execution may support pre-checks, but official grading evidence requires an approved runner profile.

## 3. Execution profiles

| Profile | Use | Authority | Notes |
|---|---|---|---|
| Student local pre-check | Student feedback before submission | Advisory only | Cannot become official grade evidence without runner confirmation |
| Instructor/lab runner | Initial official evaluation | Authoritative after fixture pass | Preferred MVP official evidence path |
| GitHub Actions | Future extension | Conditional | Requires cost, privacy, rate-limit, token, and outage analysis |
| Self-hosted runner | Future extension | Conditional | Requires ops/runbook and isolation controls |

## 4. Windows sandbox controls

Official runner design shall evaluate Windows Job Object limits, AppContainer/low-integrity process options, filesystem allowlists, network blocking, timeout, memory/process limits, working-directory isolation, and log redaction. WSL/container options may be assessed but shall not be assumed available for all Windows clients.

## 5. Evaluation evidence schema seeds

Each evaluation record shall include:

- assignment version and submission commit SHA;
- compiler/toolchain profile;
- command line and environment profile hash;
- timeout, memory, process, filesystem, and network policies;
- stdout/stderr/log hashes;
- test result summary and raw result references;
- sandbox violations and manual review flags.

## 6. Traceability

- Requirements: `EDUOPS-FR-017`, `EDUOPS-FR-018`, `EDUOPS-FR-056`
- Constraints: `EDUOPS-CON-004`, `EDUOPS-CON-009`
- Decision: `EDUOPS-DEC-029`
- Risk: `EDUOPS-R-004`, `EDUOPS-R-033`
