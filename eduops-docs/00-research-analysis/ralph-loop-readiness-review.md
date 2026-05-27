---
title: Ralph Loop Readiness Review
document_id: SWENG-EDUTECH-RALPH-LOOP-READINESS-REVIEW
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  related: ['SWENG-EDUTECH-IMPL-EXEC-PLAN', 'SWENG-EDUTECH-RTM', 'SWENG-EDUTECH-STD', 'SWENG-EDUTECH-FIXTURE-HARNESS']
  evaluators: ['Claude Code read-only advisory', 'Codex read-only advisory']
---

# Ralph Loop Readiness Review

## 1. Purpose

This review evaluates whether the current EduOps controlled document package is sufficient to run a Ralph-style autonomous implementation loop that can produce a real result artifact using Codex/Claude-style agents without inventing missing requirements or violating fake/local/no-live-action gates.

## 2. Review scope

The review scope is the current local-only EduOps pre-development package on `main`. The evaluation focuses on whether an agent loop can select a bounded implementation slice, write RED tests, implement the minimal behavior, run GREEN validation, record evidence, and stop without hidden product decisions.

The review does not approve live GitHub, LMS, classroom, credential, official grading, or external side effects.

## 3. Evaluator results

| Evaluator | Result | Evidence note |
|---|---|---|
| Claude Code | `INSUFFICIENT_FOR_RALPH_LOOP` | Claude completed a read-only advisory evaluation after a max-turn continuation. It allowed only a single inert no-network skeleton target such as `GH-SLICE-0` or SLICE-A skeleton, and found P0 blockers for executable test cards, fixture CLI/artifacts, build/release baseline, and open decisions. |
| Codex | `INSUFFICIENT_FOR_RALPH_LOOP` | Codex first hit a read-only sandbox/bubblewrap failure, then was rerun with sandbox bypass under an explicitly read-only prompt. It found code implementation not approved yet; only a local documentation/test-card closure loop is approved before SLICE-A implementation. |

## 4. Consolidated decision

`DECISION: INSUFFICIENT_FOR_RESULT_PRODUCING_IMPLEMENTATION_RALPH_LOOP`

A Ralph loop should not yet write product source code intended to implement EduOps behavior. The package is strong enough to run a **controlled documentation/test-card closure loop** whose output is a result artifact such as a SLICE-A executable test-card package or GH-SLICE-0 fake-local test-card package. It is not yet sufficient for autonomous code implementation because exact executable test cards, fixture byte contents, harness command/schema, and build/dev command baselines are not fully fixed.

## 5. Minimum approved Ralph-loop target

The first approved Ralph loop target is:

```text
RALPH-DOC-LOOP-001: Produce executable SLICE-A/GH-SLICE-0 test-card and harness specification artifacts.
```

Required output artifact:

- exact requirement IDs;
- SDD/IDD anchors;
- STD anchors;
- fixture paths and file names;
- exact command or intended command signature;
- expected RED failure text;
- expected GREEN evidence paths;
- `run-summary.json` schema;
- no-live-action assertion with `live_external_action=false`;
- agent stop rule when a product decision remains open.

After that artifact is reviewed and committed, a separate Ralph implementation loop may attempt the smallest fake/local code slice.

## 6. Blockers before product-code Ralph loop

| Priority | Blocker | Affected docs |
|---|---|---|
| P0 | RTM/STD rows are still mostly grouped planning coverage; implementation needs slice-specific executable test cards with RED/GREEN evidence. | `01-requirements/requirements-traceability-matrix.md`, `03-verification-validation/software-test-description.md` |
| P0 | Fixture harness command, owning crate/tool, argument grammar, exit codes, `run-summary.json` schema, and fixture byte contents/hashes are not fixed enough for autonomous execution. | `03-verification-validation/fixture-corpus-and-harness-plan.md` |
| P0 | Build/dev/test baseline is missing as a controlled file; agents need pinned toolchain, package manager, commands, lockfile policy, and Windows/local validation command. | new `06-implementation/build-packaging-release-engineering.md` |
| P0 | Gap-register status ambiguity remains for configuration/credential rows marked `promoted-document-required` despite existing controlled docs. | `01-requirements/implementation-requirements-gap-register.md` |
| P1 | Minimal Git/local-storage adapter contracts are still needed before SLICE-A can complete fake/local checkpoint and empty-course persistence. | new or expanded adapter specs under `02-design-planning/` |
| P1 | Some open decisions can force mid-loop invention if not deferred out of scope. | `05-decisions/decision-log.md`, `02-design-planning/software-design-description.md`, `02-design-planning/github-adapter-software-design-description.md` |

## 7. Required agent guards

1. Use fake/local adapters only.
2. Set and verify `live_external_action=false` for every loop artifact.
3. Reject any configured remote URL, live GitHub call, LMS call, credential lookup, external network call, or official grading claim.
4. Start from exact requirement ID, design anchor, interface anchor, fixture/test command, expected RED condition, expected GREEN evidence, and refactor/regression command.
5. Halt instead of inventing values when a required decision is open.
6. Keep implementation agents read/write only within declared slice targets.
7. Run Hermes review after the agent loop and before reporting completion.
8. Record evidence artifacts and local commit hash; do not use GitHub/remote promotion.

## 8. Recommended closure order

| Order | Closure item | Output |
|---|---|---|
| 1 | Add SLICE-A/GH-SLICE-0 executable test-card package. | `03-verification-validation/slice-a-executable-test-cards.md` or equivalent; update STD/RTM. |
| 2 | Make fixture harness concrete. | Update `fixture-corpus-and-harness-plan.md`; add `run-summary.json` schema and fixture content/hash registry. |
| 3 | Add build/package/release engineering baseline. | `06-implementation/build-packaging-release-engineering.md`. |
| 4 | Reconcile gap-register statuses. | Update promoted/configuration/credential rows so implementation gates are unambiguous. |
| 5 | Add minimal local storage and Git adapter contracts for SLICE-A. | Adapter specs or appendices sufficient for fake/local empty skeleton. |
| 6 | Re-run Claude and Codex. | Stop only if both approve `SUFFICIENT_FOR_RALPH_LOOP` for a clearly bounded fake/local implementation loop. |

## 9. Claude advisory output

```text
DECISION: INSUFFICIENT_FOR_RALPH_LOOP

SCOPE: A Ralph-style autonomous loop is approved only for a single inert, no-network skeleton slice (GH-SLICE-0 fake-local adapter or SLICE-A directory/IPC skeleton); it is not approved for any FR-by-FR implementation, real Git/GitHub, runner, exporter, or editor work.

BLOCKERS:
- P0 — `06-implementation/implementation-executability-improvement-plan.md` §6 explicitly states "Do not start production code until the P0 architecture, state-machine, configuration, credential, fixture-gate, RTM, and TDD evidence controls are accepted"; multiple controls are still `promoted-document-required`.
- P0 — `01-requirements/implementation-requirements-gap-register.md` §3: `EDUOPS-CFR-013/014/015`, `EDUOPS-CIR-018`, `EDUOPS-CVR-005` remain `promoted-document-required`, which by §2 status rules means "Implementation remains blocked until document gate closes."
- P0 — `01-requirements/requirements-traceability-matrix.md` §4 + `03-verification-validation/software-test-description.md` §17/§18: every RTM/STD row is grouped coverage only; no per-FR executable test card exists, so the agent cannot drive RED→GREEN TDD per requirement.
- P0 — `03-verification-validation/fixture-corpus-and-harness-plan.md` §3: gate commands reference an `eduops-fixture` CLI whose crate location, argument schema, exit codes, and `run-summary.json` schema are undefined; fixture file contents (`fake-git-template/`, `block-document-*.eduops.json`, `roster-valid.csv`, `seed-manifest.json`, `expected-hashes.json`) are named but not provided.
- P0 — `02-design-planning/technology-stack-decision-record.md` + missing `build-packaging-release-engineering.md` (gap `EDUOPS-CNFR-001`, P1-7): no pinned crate/npm versions, no Rust toolchain pin, no Tauri 2.x minor, no test runner choice, no Cargo workspace or `package.json` skeleton, no lockfile policy.
- P1 — `02-design-planning/internal-api-contract.md` and `module-and-package-layout.md`: API signatures are TypeScript-shaped; Rust trait signatures for `GitAdapter`, `StorageAdapter`, `CredentialAdapter`, `ExportAdapter`, `RunnerAdapter` are not declared, and per-crate module file enumeration (outside the GitHub subtree) is absent.
- P1 — `02-design-planning/canonical-domain-idl.md` §1: schemas are TS examples; no canonical JSON Schema files committed at `schemas/config/v1.json` or domain equivalents — schema location is itself listed as open in `configuration-contract.md` §7.
- P1 — `05-decisions/decision-log.md` `EDUOPS-DEC-013` (Open: student registry fields, override authority, mode UI labels), `software-design-description.md` §9 (5 open implementation decisions), `github-adapter-software-design-description.md` §14 (auth, mock server, backoff constants, sandbox owner) — each forces a product decision mid-loop.

MINIMUM_RALPH_LOOP_TARGET: `GH-SLICE-0` — `crates/eduops_git/src/github/{mod.rs, mode_gate.rs, fake_local.rs}` plus `tests/contract/github_adapter/gh_fix_001.rs` and `fixtures/github/fake-local-no-network/`, producing a `GitHubAdapterResult` with `adapter_mode='fake-local'`, `external_call_made=false`, `external_side_effect_made=false`, `no_raw_secret_observed=true`, zero socket syscalls, and a `run-summary.json` reporting `live_external_action=false`, gated by `STD-086`/`GH-FIX-001`.

REQUIRED_AGENT_GUARDS:
- Hard-pin `adapter_mode='fake-local'` and `live_external_action=false` in every request envelope; fail any test that opens a socket (`sandbox→live` is "Always denied in current baseline" per GitHub SDD §4).
- No remote URLs in any Git fixture; configured remote fails the slice gate (`fixture-corpus-and-harness-plan.md` §6).
- Credential adapter must return references only; raw token/secret strings in payload, log, or audit are auto-fail (`credential-storage-contract.md` §2/§5).
- TDD evidence required per behavior: RED commit → GREEN commit → refactor/regression note (STD §18, plan §3 P0-12); no implementation commit without a paired failing-then-passing test artifact.
- No new product decisions: if a needed value is "Open" in SDD §9, DEC-013, config §7, credential §7, or GH SDD §14, the agent halts and requests a controlled-document update instead of inventing one.
- Read-only outside the slice's declared file targets; no edits to docs, RTM, STD, or decision log from inside the loop.
- Human review gate before promoting any slice beyond GH-SLICE-0 / SLICE-A skeleton; GH-SLICE-1+ and SLICE-B+ require separate approval per GitHub SDD §12 and roadmap §5.

DOC_FIXES_RECOMMENDED:
- `06-implementation/build-packaging-release-engineering.md` (new): pin Rust toolchain, Tauri 2.x minor, `git2`/SQLx/Tiptap versions, `cargo`/`nextest` test runner, lockfile policy, Windows packaging commands — closes `EDUOPS-CNFR-001`/P1-7.
- `03-verification-validation/fixture-corpus-and-harness-plan.md` §3–§5: specify the `eduops-fixture` CLI (owning crate, argument grammar, exit codes, `run-summary.json` JSON Schema) and commit the byte contents and expected SHA-256 of `seed-manifest.json`, `expected-hashes.json`, `fake-git-template/`, `block-document-basic.eduops.json`, `roster-valid.csv`, `roster-invalid.csv`, `identity-claims.json`.
- `01-requirements/requirements-traceability-matrix.md` §4 + `03-verification-validation/software-test-description.md` §17: replace grouped coverage with one executable test card per FR/NFR (fixture command, RED artifact, GREEN artifact, evidence path) — closes the STD-085 per-requirement evidence rule.
- `02-design-planning/internal-api-contract.md` and `module-and-package-layout.md`: add a Rust-trait appendix declaring `GitAdapter`, `StorageAdapter`, `CredentialAdapter`, `ExportAdapter`, `RunnerAdapter`, and `GitHubAdapter` signatures plus the per-crate module file list outside `crates/eduops_git/src/github/`.
- `02-design-planning/canonical-domain-idl.md` §1 + `02-design-planning/configuration-contract.md` §7: commit the JSON Schema files (`schemas/config/v1.json` and domain schemas) at a single fixed path, with version pin.
- `02-design-planning/credential-storage-contract.md` §7: name the exact Rust DPAPI crate and pin GitHub auth choice (App vs PAT) for the first beta — required before any non-fake-local credential code.
- `05-decisions/decision-log.md` `EDUOPS-DEC-013` + `software-design-description.md` §9: resolve open items (mandatory student registry fields, override authority, UI mode labels, UI framework selection) or explicitly defer them out of the first loop's scope.
- `02-design-planning/github-adapter-software-design-description.md` §14: defer or close auth/mock-server/backoff/sandbox-owner items so the agent does not encounter "Open" rows inside GH-SLICE-0/1 work.

CONFIDENCE: High — the controlled package itself states implementation is gated, multiple P0 candidates remain in `promoted-document-required` status, no per-requirement executable test cards exist, and the harness CLI plus fixture byte contents are unspecified; these conditions independently each block a Ralph loop beyond the single inert skeleton slice identified.
```

## 10. Codex advisory output

```text
DECISION: INSUFFICIENT_FOR_RALPH_LOOP

SCOPE: Code implementation is not approved yet; only a local documentation/test-card closure loop is approved before SLICE-A implementation.

BLOCKERS:
- P0 - `01-requirements/requirements-traceability-matrix.md` §5-§6 and `03-verification-validation/software-test-description.md` §17.1-§18: SLICE-A requirements are still grouped planning coverage, not executable test cards with requirement-specific RED output, GREEN evidence paths, and no-live-action assertions.
- P0 - `03-verification-validation/fixture-corpus-and-harness-plan.md` §3-§5: SLICE-A defines a future command and artifact list, but not an executable harness/test-card package sufficient for an autonomous TDD loop to run without inventing validation behavior.
- P1 - `01-requirements/implementation-requirements-gap-register.md` §4 and `06-implementation/implementation-executability-improvement-plan.md` §4: Git adapter, local storage adapter, and build/package/dev-command baselines remain candidate/P1 items, yet SLICE-A requires local persistence, fake Git checkpoint evidence, and repeatable local validation.
- P1 - `01-requirements/implementation-requirements-gap-register.md` §3: configuration/credential rows still show `promoted-document-required` even though controlled docs now exist, creating gate-state ambiguity for whether P0 is closed.

MINIMUM_RALPH_LOOP_TARGET: First run should produce a controlled SLICE-A test-card/evidence-harness artifact, then implement only `GATE-SLICE-A-LOCAL-SKELETON`: local desktop/core skeleton, IPC ping, empty course persistence, empty document save/load, fake/local Git checkpoint, `run-summary.json`, audit log, manifest hash, and `live_external_action=false`.

REQUIRED_AGENT_GUARDS:
- No live GitHub, LMS, classroom, network, credential lookup, or official grading side effects.
- Start from exact requirement ID, design/interface anchor, fixture command, expected RED failure, expected GREEN evidence, and refactor/regression command.
- Use fake/local adapters only; no remotes configured in fixture Git repositories.
- Preserve RED-GREEN-REFACTOR evidence in the produced package.
- Fail closed on missing artifacts, privacy denylist hits, raw secrets, configured remotes, or live-action flags.
- Treat P1 adapter/spec gaps as blockers before completing affected slice behavior.

DOC_FIXES_RECOMMENDED:
- Add `SLICE-A executable test cards` to `requirements-traceability-matrix.md` and `software-test-description.md`, including exact requirement IDs, command, fixture paths, expected RED output, GREEN artifacts, and no-live-action assertion.
- Expand `fixture-corpus-and-harness-plan.md` with concrete SLICE-A fixture files, expected hashes, artifact schema, and pass/fail validator behavior.
- Add or promote a minimal `build-packaging-release-engineering.md` covering package manager, bootstrap, lint/type/test commands, lockfiles, and local evidence commands.
- Add minimal Git/local-storage adapter contracts needed for SLICE-A fake/local checkpoint and empty-course persistence.
- Reconcile `implementation-requirements-gap-register.md` statuses for configuration and credential rows from `promoted-document-required` to the correct current state.

CONFIDENCE: High - the package is strong directionally, but its own RTM/STD gates explicitly require exact executable test cards before coding, and those are not yet present for SLICE-A.
```

## 11. Hermes self-review against requested objective

| Objective | Review result |
|---|---|
| Use Claude and Codex for review. | Met. Claude and Codex were both run as read-only advisory evaluators. Codex required a sandbox-bypass retry due to local bubblewrap failure, and git status was checked afterward. |
| Decide whether the package is sufficient for a Ralph loop that produces a result. | Met. The answer is insufficient for product-code loop, sufficient only for documentation/test-card closure loop. |
| Identify what must be supplemented. | Met. P0/P1 blockers and closure order are listed. |
| Preserve no-live-action boundary. | Met. Review explicitly excludes live GitHub/LMS/classroom/credential/official grading side effects. |
| Provide controlled evidence. | Met. This document records evaluator outputs and consolidated decision. |

## 12. Conclusion

The next Ralph loop should not be an implementation loop. It should be a controlled document/test-card closure loop that produces executable SLICE-A/GH-SLICE-0 test cards, concrete fixture/harness schema, and build/dev command baseline. After that result is reviewed and committed, Claude and Codex should re-evaluate implementation-loop readiness.


## 13. Supplementation addendum

The following closure artifacts were added after the initial insufficient decision:

- [SLICE-A and GH-SLICE-0 Executable Test Cards](../03-verification-validation/slice-a-executable-test-cards.md);
- concrete fixture files under `fixtures/shared/`, `fixtures/slice-a/`, `fixtures/github/fake-local-no-network/`, and `fixtures/schema/run-summary.schema.json`;
- [Build, Packaging, and Release Engineering Baseline](../06-implementation/build-packaging-release-engineering.md);
- [Git Adapter Specification](../02-design-planning/git-adapter-specification.md);
- [Local Storage Adapter Specification](../02-design-planning/local-storage-adapter-specification.md);
- gap-register status reconciliation for configuration/credential/Git/storage/build rows.

Hermes self-review: the supplementation addresses the documented blockers for a bounded fake/local loop candidate, but it does not itself substitute for a fresh Claude/Codex approval. The next safe step is re-review of the updated package before product-code Ralph execution.
