---
title: M1 SLICE-A Local Skeleton Evidence
document_id: EDUOPS-M1-SLICE-A-LOCAL-SKELETON-EVIDENCE
version: 0.1.0
status: accepted
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  requirements: ['EDUOPS-FR-067', 'EDUOPS-FR-068', 'EDUOPS-FR-078', 'EDUOPS-FR-079', 'EDUOPS-FR-080', 'EDUOPS-NFR-032', 'EDUOPS-NFR-033', 'EDUOPS-NFR-034']
  tests: ['TC-SLICE-A-001', 'GATE-SLICE-A-LOCAL-SKELETON']
---

# M1 SLICE-A Local Skeleton Evidence

## 1. Gate result

M1 is accepted for the local skeleton scope.

```text
gate: GATE-SLICE-A-LOCAL-SKELETON
result: PASS
scope: local fixture course creation, local persistence, fake-local Git evidence
live_external_action: false
external_call_made: false
github_mutation_made: false
remote: none
```

M1 does not claim desktop UI demonstration, Windows WebView2 evidence, live GitHub behavior, final storage schema, credential lookup, assignment state machine, or runner/export behavior.

## 2. Gate command

```bash
cargo run -p eduops_fixture -- run slice-a \
  --mode local \
  --fixture fixtures/slice-a \
  --out build/evidence/slice-a/local-skeleton
```

Observed result:

```text
slice_a_status=ok evidence_dir=build/evidence/slice-a/local-skeleton
m1_gate_evidence_valid=true
course_id=course_eduops-m0_2026-spring
artifacts=run-summary.json,command-log.txt,course.json,audit.jsonl,git-status.txt,manifest.sha256
```

## 3. Evidence package

Runtime evidence was generated at:

```text
build/evidence/slice-a/local-skeleton/
```

The repository-level `build/` directory is ignored as transient runtime output. This document records the controlled gate result and selected evidence values for source control.

Generated artifacts:

```text
run-summary.json
command-log.txt
course.json
audit.jsonl
git-status.txt
manifest.sha256
```

`run-summary.json` values:

```json
{
  "gate": "GATE-SLICE-A-LOCAL-SKELETON",
  "live_external_action": false,
  "external_call_made": false,
  "github_mutation_made": false,
  "course_id": "course_eduops-m0_2026-spring"
}
```

`git-status.txt` values:

```text
remote.origin.url=<none>
remote_urls=0
status_digest=cb856ea7c11e2ed16e49fdbb7e72b05661a1dc8d64c6af3c2b53ee222bdf3c62
checkpoint_id=checkpoint_2cbd94ad9541
```

`manifest.sha256` values:

```text
ed0a73047b7b3b2a24eb04f12a1c3c894470fb00dff9bf956c6d511a93b2fec7  course.json
2cbd94ad95419d33db73499594824e6f07133571e9443134926745ec729ac92f  git-status.txt
cb856ea7c11e2ed16e49fdbb7e72b05661a1dc8d64c6af3c2b53ee222bdf3c62  run-summary.json
```

## 4. Validation commands

```bash
cargo fmt --all --check
npm run m0:check
cargo test --workspace
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py tests/contract/m1_slice_a/test_m1_slice_a_fixture_runner.py -q
git diff --check
```

Document validation:

```text
markdown_files: 94
json_files: 8
bad_local_links: 0
```

## 5. M1 acceptance boundary

Accepted M1 capabilities:

- `RequestEnvelope` and `ResultEnvelope` preserve request/correlation identifiers.
- `course.createLocalCourse` creates a deterministic empty-course fixture result.
- Local storage adapter persists and reloads the course snapshot without live action.
- Fake-local Git adapter records status/checkpoint evidence with zero remotes.
- Fixture runner emits the SLICE-A local evidence package.

Deferred to later milestones:

- M1A: desktop shell and WebView2 UI evidence.
- M2: configuration and credential-reference services.
- M3+: canonical document and workflow behavior.
- M7: GitHub clone-only adapter implementation beyond fake-local evidence.
