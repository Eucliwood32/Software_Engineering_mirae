---
title: SLICE-A and GH-SLICE-0 Executable Test Cards
document_id: SWENG-EDUTECH-SLICE-A-TEST-CARDS
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  requirements: ['EDUOPS-FR-067', 'EDUOPS-FR-068', 'EDUOPS-FR-078', 'EDUOPS-FR-079', 'EDUOPS-FR-080', 'EDUOPS-NFR-032', 'EDUOPS-NFR-033', 'EDUOPS-NFR-034']
  tests: ['STD-071', 'STD-072', 'STD-073', 'STD-084', 'STD-085', 'STD-086']
---

# SLICE-A and GH-SLICE-0 Executable Test Cards

## 1. Purpose

This document closes `RALPH-DOC-LOOP-001` for the first fake/local Ralph implementation loop. It converts grouped planning anchors into exact executable test cards. The commands are authoritative command signatures for the first implementation loop; before the harness exists, the expected RED result is command-not-found or missing-gate failure.

## 2. Global guards

- `adapter_mode=local` or `adapter_mode=fake-local` only.
- `live_external_action=false` in every request, evidence file, and `run-summary.json`.
- No Git remote URL may exist under fixture repositories.
- No raw credential or token string may appear in input, log, result, audit, manifest, or diagnostic output.
- Any socket/network attempt fails the gate.
- Any missing expected artifact fails the gate.

## 3. Test cards

| Card ID | Trace | Design / interface anchors | Exact command | Fixture inputs | Expected RED failure | Expected GREEN evidence | No-live-action assertion |
|---|---|---|---|---|---|---|---|
| `TC-SLICE-A-001` | `EDUOPS-FR-067`, `STD-071`, `STD-085` | SDD §14, IDD §9, process topology, module layout | `cargo run -p eduops_fixture -- run slice-a --mode local --fixture fixtures/slice-a --out build/evidence/slice-a/local-skeleton` | `fixtures/slice-a/course-empty.json`, `fixtures/slice-a/workspace-policy.json`, `fixtures/shared/seed-manifest.json` | `error: package 'eduops_fixture' not found` or `GATE-SLICE-A-LOCAL-SKELETON missing implementation` | `build/evidence/slice-a/local-skeleton/run-summary.json`, `command-log.txt`, `course.json`, `audit.jsonl`, `git-status.txt`, `manifest.sha256` | `run-summary.json.live_external_action == false`; `git-status.txt` contains no `remote.origin.url`. |
| `TC-SLICE-A-002` | `EDUOPS-FR-078`, `EDUOPS-FR-079`, `STD-084`, `STD-085` | RTM §4, STD §18 | `cargo run -p eduops_fixture -- validate-evidence --gate GATE-SLICE-A-LOCAL-SKELETON --summary build/evidence/slice-a/local-skeleton/run-summary.json --schema fixtures/schema/run-summary.schema.json` | `fixtures/schema/run-summary.schema.json`, output from `TC-SLICE-A-001` | `run-summary.json not found` or schema validation failure | validator exits `0`, emits `evidence-valid=true`, and records schema/hash checks | Summary schema requires `live_external_action=false`. |
| `TC-SLICE-A-003` | `EDUOPS-CVR-001`, `EDUOPS-CVR-002`, `STD-072`, `STD-073` | Fixture harness plan §7 | `cargo run -p eduops_fixture -- verify-corpus --fixture fixtures --hashes fixtures/shared/expected-hashes.json --denylist fixtures/shared/privacy-denylist.txt` | all checked-in `fixtures/**` files | hash registry missing or privacy denylist scanner missing | `build/evidence/fixture-corpus/verification.json` with all hashes matched and zero denylist hits | Validator fails if any fixture implies network, credential lookup, or remote URL. |
| `TC-GH-000` | `EDUOPS-FR-080`, `EDUOPS-FR-081`, `EDUOPS-FR-084`, `EDUOPS-NFR-034`, `STD-086` | GitHub Adapter SDD §4, §12; GitHub adapter spec | `cargo test -p eduops_git --test gh_fix_001_fake_local_no_network -- --nocapture` | `fixtures/github/fake-local-no-network/request.json`, `expected-result.json` | test file or `eduops_git::github::fake_local` module missing | test passes and writes `build/evidence/github/gh-fix-001/run-summary.json` | `operation_class=clone-only`, `external_call_made=false`, `external_side_effect_made=false`, `github_mutation_made=false`, `live_external_action=false`. |

## 4. Implementation-loop entry rule

A product-code Ralph loop may start only if the loop prompt cites one or more cards from §3 and commits RED evidence before changing implementation files. If the first RED condition is different from the expected RED text, the loop must stop for human/Hermes review.

## 5. Evidence acceptance checklist

- Requirement ID is present.
- SDD and IDD anchors are present.
- Exact command is present.
- Expected RED output is recorded before implementation.
- GREEN command output and evidence paths are recorded after implementation.
- `manifest.sha256` covers every output artifact.
- `live_external_action=false` appears in `run-summary.json`.
- Hermes reviews the evidence package before completion is reported.
