---
title: M0 Source Scaffold Evidence
document_id: EDUOPS-M0-SOURCE-SCAFFOLD-EVIDENCE
version: 0.1.0
status: implemented
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  milestone: M0 — Repository scaffold and toolchain bootstrap
  anchors:
    - EDUOPS-IMPLEMENTATION-MILESTONES
    - SWENG-EDUTECH-MODULE-LAYOUT
    - SWENG-EDUTECH-INTERNAL-API
---

# M0 Source Scaffold Evidence

## 1. Purpose

This record documents the first implementation increment for M0, repository scaffold and toolchain bootstrap. The increment creates a behavior-free source scaffold that can be checked by Rust, Node, and fixture commands before SLICE-A product behavior starts.

## 2. Scope implemented

The increment added these implementation boundaries:

```text
Cargo.toml
Cargo.lock
rust-toolchain.toml
package.json
package-lock.json
apps/desktop/
apps/desktop-ui/
crates/eduops_domain/
crates/eduops_api/
crates/eduops_core/
crates/eduops_storage/
crates/eduops_config/
crates/eduops_credentials/
crates/eduops_git/
crates/eduops_export/
crates/eduops_runner/
crates/eduops_workers/
crates/eduops_diagnostics/
crates/eduops_fixture/
fixtures/slice-a/empty-course.json
tests/contract/m0_scaffold/test_m0_scaffold.py
```

The source scaffold is intentionally minimal. It provides crate boundaries, a desktop shell metadata stub, a TypeScript UI scaffold, a fixture verification CLI, and a GitHub clone-only mode-gate stub. It does not implement SLICE-A course creation, storage persistence, desktop launch, Tauri runtime, GitHub network behavior, runner behavior, export behavior, credential lookup, or live external action.

## 3. Toolchain decisions

| Area | M0 decision |
|---|---|
| Rust | Cargo workspace, Rust `1.95.0`, edition `2024`, workspace resolver `3` |
| Desktop shell | `apps/desktop`, Cargo package `eduops_desktop`; Tauri runtime deferred to M1A |
| UI | `apps/desktop-ui`, npm-controlled TypeScript-like scaffold; no external package dependency |
| Package manager | `npm@10.9.7` recorded because `pnpm` is not installed in the current environment |
| Fixture command | `cargo run -p eduops_fixture -- verify-corpus fixtures/slice-a` |
| Live action boundary | `live_external_action=false` preserved in scaffold metadata and fixture corpus |

## 4. TDD evidence

RED was recorded before source scaffold implementation:

```text
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q
```

Expected RED result:

```text
5 failed
- Cargo.toml missing
- package.json missing
- required scaffold paths missing
- cargo check cannot find workspace
- fixture command cannot find workspace
```

GREEN was recorded after source scaffold implementation:

```text
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q
```

GREEN result:

```text
6 passed
```

## 5. M0 acceptance commands

The following commands passed after the scaffold was created:

```text
npm run m0:check
cargo test --workspace
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q
```

Observed command evidence:

```text
cargo check --workspace: OK
apps/desktop-ui typecheck: desktop-ui_typecheck=ok
apps/desktop-ui build: desktop-ui_build=ok
eduops_fixture verify-corpus fixtures/slice-a: fixture_corpus_status=ok
cargo test --workspace: OK; eduops_desktop no-live-action test OK; eduops_git clone-only mode-gate test OK
pytest M0 scaffold acceptance: 6 passed
```

## 6. Boundary assertions

The M0 scaffold preserves these boundaries:

1. No remote is configured in Git.
2. No network call is implemented or required by the M0 validation commands.
3. No GitHub push, repository creation, webhook, archive, or admin behavior is implemented.
4. `eduops_git::github::mode_gate_allows` permits `Clone` only and denies `Push`, `CreateRepository`, and `DeleteRepository`.
5. `eduops_desktop` records `LIVE_EXTERNAL_ACTION_DEFAULT=false`.
6. `fixtures/slice-a/empty-course.json` records `live_external_action=false`.
7. Tauri/WebView2 runtime launch remains deferred to M1A and is not claimed complete by M0.

## 7. Decision

M0 source scaffold is implemented enough to support the next controlled implementation increment.

```text
GO: M1 SLICE-A local skeleton planning and RED test creation
NO-GO: M1 behavior completion claim
NO-GO: M1A desktop UI demonstration claim
NO-GO: live external GitHub behavior
```
