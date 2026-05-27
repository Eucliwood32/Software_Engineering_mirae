---
title: Build, Packaging, and Release Engineering Baseline
document_id: SWENG-EDUTECH-BUILD-PACKAGING-RELEASE
version: 0.1.0
status: draft
created: 2026-05-14
updated: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CNFR-001']
  related: ['SWENG-EDUTECH-TECH-STACK', 'SWENG-EDUTECH-MODULE-LAYOUT', 'SWENG-EDUTECH-FIXTURE-HARNESS']
---

# Build, Packaging, and Release Engineering Baseline

## 1. Purpose

This baseline fixes the initial developer and agent command surface for the first fake/local implementation loops. It is not a final release engineering plan.

## 2. Initial toolchain baseline

| Item | Baseline |
|---|---|
| OS target | Windows and Linux desktop product. Windows evidence records WebView2; Linux evidence records distribution, display/session type, and Tauri-supported webview runtime. |
| Rust toolchain | Stable Rust `1.78` or later; first implementation shall add `rust-toolchain.toml` pin before code. |
| Desktop shell | Tauri 2.x family, exact minor pinned when desktop shell slice begins. |
| UI package manager | `pnpm` with checked-in lockfile when UI work begins. |
| Rust workspace | Cargo workspace rooted at implementation repo root. |
| Test runner | `cargo test` for first slice; `cargo nextest` may be added after lockfile/tooling baseline. |
| Git library | Fake/local adapter first; `git2` version pinned before libgit2-backed adapter. |
| Local DB | SQLite/SQLx only after local-storage adapter contract is accepted. |

## 3. Required commands for first loop

| Command purpose | Command signature |
|---|---|
| Format | `cargo fmt --all -- --check` |
| Static check | `cargo check --workspace` |
| Unit/contract test | `cargo test --workspace` |
| SLICE-A gate | `cargo run -p eduops_fixture -- run slice-a --mode local --fixture fixtures/slice-a --out build/evidence/slice-a/<run-id>` |
| Evidence validation | `cargo run -p eduops_fixture -- validate-evidence --gate GATE-SLICE-A-LOCAL-SKELETON --summary build/evidence/slice-a/<run-id>/run-summary.json --schema fixtures/schema/run-summary.schema.json` |
| UI shell typecheck/build | `pnpm --dir apps/desktop-ui install --frozen-lockfile && pnpm --dir apps/desktop-ui typecheck && pnpm --dir apps/desktop-ui build` |
| UI shell smoke tests | `cargo test -p eduops_desktop --test ui_shell_launch_health && cargo test -p eduops_desktop --test ui_slice_a_local_course && cargo test -p eduops_desktop --test ui_evidence_and_failure_display` |
| UI shell evidence validation | `cargo run -p eduops_fixture -- validate-evidence --gate GATE-UI-SHELL-DEMO-SLICE-A --summary build/evidence/ui-shell-slice-a/<run-id>/run-summary.json --schema fixtures/schema/run-summary.schema.json` |
| Fixture corpus validation | `cargo run -p eduops_fixture -- verify-corpus --fixture fixtures --hashes fixtures/shared/expected-hashes.json --denylist fixtures/shared/privacy-denylist.txt` |

Before source code exists, these commands are expected RED commands. The implementation loop must capture the failing output, then implement the minimum code required to make the targeted command pass.

## 4. Lockfile policy

- Rust implementation shall commit `Cargo.lock` for application/workspace builds.
- UI implementation shall commit `pnpm-lock.yaml` when UI packages are introduced.
- No dependency may be introduced only by an agent without updating this baseline or a package-specific decision if it affects runtime, credential handling, networking, or packaging.

## 5. Packaging boundary

The first Ralph implementation loop shall not build installers. Packaging work begins only after SLICE-A evidence exists and desktop shell slice is approved.

## 5.1 Windows/Linux UI evidence capture

`GATE-UI-SHELL-DEMO-SLICE-A` can be closed by either a controlled Windows desktop capture or a controlled Linux desktop capture. The gate requires an evidence-capture record containing:

- evidence capture environment name, OS version, platform webview runtime details, Rust toolchain, Node/npm or pnpm version, and Tauri version;
- reviewer/owner name or role;
- command log for frontend typecheck/build and `eduops_desktop` UI shell smoke tests;
- screenshot or screen-recording path under `build/evidence/ui-shell-slice-a/<run-id>/`;
- runtime assertion that `RequestEnvelope.live_external_action=false` is preserved into backend command handling and evidence output;
- no-live-action observation covering remote URLs, network calls, GitHub mutation, runner/exporter invocation, and raw credential lookup.

A headless host may record a prerequisite blocker or expected RED result, but that record is not sufficient to mark the UI shell gate complete. A Linux desktop host with the required webview/display capture evidence is sufficient.

## 6. Release evidence

Each implementation loop shall record:

- command line;
- exit code;
- selected requirement/test-card IDs;
- RED output;
- GREEN output;
- refactor/regression output;
- evidence directory path;
- local commit hash;
- confirmation that no remote/GitHub action occurred.
