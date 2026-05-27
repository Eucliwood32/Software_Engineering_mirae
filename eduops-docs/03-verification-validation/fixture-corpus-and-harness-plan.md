---
title: Fixture Corpus and Harness Plan
document_id: SWENG-EDUTECH-FIXTURE-HARNESS
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CVR-001', 'EDUOPS-CVR-002', 'EDUOPS-CFR-006']
  tests: ['STD-072', 'STD-073']
---

# Fixture Corpus and Harness Plan

## 1. Purpose

This plan defines deterministic, privacy-safe fixtures and local harness gates for SLICE-A/B/C. The gates are required before live GitHub, live classroom, or official evaluation actions.

## 2. Fixture rules

- Fixtures contain no real student names, emails, student numbers, GitHub handles, tokens, repository names, or institutional IDs.
- Human-readable fixture names use synthetic labels such as `Student Alpha` and deterministic hashes.
- Fixture clocks use pinned UTC timestamps and declared timezone cases.
- Fixture randomness uses a checked-in seed manifest.
- Fixture Git repositories use local paths only and must not include remotes.
- Fixture evidence sets report `live_external_action=false`.

## 3. Gate table

| Gate ID | Slice | Required local command | Pass criteria | Required artifacts |
|---|---|---|---|---|
| `GATE-SLICE-A-LOCAL-SKELETON` | SLICE-A | `eduops-fixture run slice-a --mode local` | Backend boots, IPC ping succeeds, empty course persists, fake Git checkpoint created, no remote configured. | `run-summary.json`, `command-log.txt`, `course.json`, `audit.jsonl`, `git-status.txt`, `manifest.sha256` |
| `GATE-SLICE-B-DOCUMENT-PATH` | SLICE-B | `eduops-fixture run slice-b --mode local` | Block document saves, Markdown projection is deterministic, operation journal replays, checkpoint hash is stable. | `document.eduops.json`, `document.md`, `document.manifest.json`, `operation-journal.jsonl`, `projection-hash.txt`, `audit.jsonl` |
| `GATE-SLICE-C-ROSTER-IDENTITY` | SLICE-C | `eduops-fixture run slice-c --mode local` | Roster import accepts/rejects expected rows, local identity binding approval works, workspace is provisioned without PII leakage. | `roster-import-report.json`, `identity-bindings.json`, `workspace-manifest.json`, `privacy-scan.json`, `audit.jsonl` |

## 4. Corpus layout

```text
fixtures/
  shared/
    seed-manifest.json
    privacy-denylist.txt
    expected-hashes.json
  slice-a/
    course-empty.json
    fake-git-template/
  slice-b/
    block-document-basic.eduops.json
    block-document-korean-code-table.eduops.json
    expected-projection.md
  slice-c/
    roster-valid.csv
    roster-invalid.csv
    identity-claims.json
```

## 5. Harness outputs

Every gate run writes:

- `run-summary.json` with gate ID, command, timestamp, adapter mode, `live_external_action=false`, pass/fail, and artifact manifest hash.
- `audit.jsonl` with normalized `AuditEvent` records.
- `privacy-scan.json` showing denylist scan results and token/remote checks.
- `manifest.sha256` listing artifact paths and SHA-256 hashes.
- `known-gaps.md` only when a gate is allowed to pass with explicitly accepted limitations.

## 6. Blocking rules

- A missing artifact fails the gate.
- A configured remote URL fails SLICE-A/B/C gates.
- Any privacy denylist hit fails unless the hit is in a documented synthetic fixture allowlist.
- Any live network command, credential lookup, or official grading action fails the gate.


## 7. Concrete harness command contract for `RALPH-DOC-LOOP-001`

The fixture harness is owned by future crate `crates/eduops_fixture` and executable package `eduops_fixture`. Until code exists, the command signatures below are expected RED commands.

| Command | Purpose | Exit codes |
|---|---|---|
| `cargo run -p eduops_fixture -- run slice-a --mode local --fixture fixtures/slice-a --out build/evidence/slice-a/local-skeleton` | Execute `GATE-SLICE-A-LOCAL-SKELETON`. | `0` pass, `10` missing fixture, `11` schema/hash mismatch, `12` live-action violation, `13` remote URL found, `14` privacy hit, `20` implementation missing. |
| `cargo run -p eduops_fixture -- validate-evidence --gate GATE-SLICE-A-LOCAL-SKELETON --summary build/evidence/slice-a/local-skeleton/run-summary.json --schema fixtures/schema/run-summary.schema.json` | Validate evidence against schema and gate invariants. | Same as above; `15` evidence schema failure. |
| `cargo run -p eduops_fixture -- verify-corpus --fixture fixtures --hashes fixtures/shared/expected-hashes.json --denylist fixtures/shared/privacy-denylist.txt` | Validate checked-in fixture corpus before a loop starts. | Same as above. |

## 8. Checked-in fixture registry

| Path | Purpose | Gate |
|---|---|---|
| `fixtures/shared/seed-manifest.json` | deterministic clock, timezone, and seed | all gates |
| `fixtures/shared/privacy-denylist.txt` | synthetic denylist and credential-prefix denylist | all gates |
| `fixtures/shared/expected-hashes.json` | authoritative SHA-256 registry for fixture inputs | all gates |
| `fixtures/schema/run-summary.schema.json` | JSON Schema for evidence summary | `TC-SLICE-A-002` |
| `fixtures/slice-a/course-empty.json` | empty course input | `TC-SLICE-A-001` |
| `fixtures/slice-a/workspace-policy.json` | local-only workspace policy | `TC-SLICE-A-001` |
| `fixtures/slice-a/fake-git-template/HEAD` | fake/local Git template head | `TC-SLICE-A-001` |
| `fixtures/slice-a/fake-git-template/config` | fake/local Git config with no remote URL | `TC-SLICE-A-001` |
| `fixtures/github/fake-local-no-network/request.json` | GH-SLICE-0 fake-local request | `TC-GH-000` |
| `fixtures/github/fake-local-no-network/expected-result.json` | GH-SLICE-0 expected result | `TC-GH-000` |

## 9. `run-summary.json` schema binding

The authoritative schema is `fixtures/schema/run-summary.schema.json`. The minimal invariant is:

```json
{
  "gate_id": "GATE-SLICE-A-LOCAL-SKELETON",
  "command": "cargo run -p eduops_fixture -- run slice-a --mode local --fixture fixtures/slice-a --out build/evidence/slice-a/local-skeleton",
  "status": "green_pass",
  "timestamp_utc": "2026-05-14T00:00:00Z",
  "adapter_mode": "local",
  "live_external_action": false,
  "artifacts": [{"path": "course.json", "sha256": "..."}],
  "checks": {"remote_url_count": 0, "network_call_count": 0, "privacy_denylist_hits": 0}
}
```

Any missing field, `live_external_action=true`, remote URL, network call, or privacy hit fails the gate.
