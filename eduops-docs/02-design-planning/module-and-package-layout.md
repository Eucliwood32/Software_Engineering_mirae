---
title: Module and Package Layout
document_id: SWENG-EDUTECH-MODULE-LAYOUT
version: 0.5.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CFR-003', 'EDUOPS-CFR-013', 'EDUOPS-CFR-015']
  related: ['SWENG-EDUTECH-PROCESS-IPC', 'SWENG-EDUTECH-DOMAIN-IDL']
---

# Module and Package Layout

## 1. Source tree

```text
apps/
  desktop/                  # Tauri app shell, WebView config, desktop assets; Cargo package name: eduops_desktop
  desktop-ui/               # TypeScript UI, editor integration, view models
crates/
  eduops_domain/            # Canonical IDs, domain types, state tables
  eduops_api/               # Command/query envelopes, signatures, error model
  eduops_core/              # Use cases, authorization calls, orchestration
  eduops_storage/           # SQLite, file layout, canonical document persistence
  eduops_config/            # Configuration schema, merge, validation, migration
  eduops_credentials/       # OS-protected credential reference adapter
  eduops_git/               # Git adapter trait, fake/local/libgit2/GitHub implementations
  eduops_export/            # Export adapter trait and DOCX/HWPX fixture implementation
  eduops_runner/            # Advisory C/C++ runner adapter and manifests
  eduops_workers/           # Job queue, progress events, worker lifecycle
  eduops_diagnostics/       # Diagnostic package builder and redaction
fixtures/
  slice-a/
  slice-b/
  slice-c/
  config/                   # Configuration merge, migration, invalid-config, offline fixtures
  shared/
docs/
  generated/                # Generated schema/API docs, not hand-authored source
tests/
  contract/
  integration/
  golden/
```

If the repository remains documentation-only during pre-development, this layout is a contract for the future source tree and not a request to create source files now.

## 2. Dependency direction

Allowed dependency direction:

```text
desktop-ui -> api types only
desktop shell -> api + core command host
core -> domain + api + config + credential refs + storage + adapter traits + workers
workers -> domain + api + adapter traits
adapters -> domain + api + adapter-specific libraries
storage -> domain
diagnostics -> domain + api + storage read interfaces
```

## 3. Forbidden dependencies

| From | Must not depend on | Reason |
|---|---|---|
| `apps/desktop-ui` | `eduops_storage`, `eduops_git`, `eduops_runner`, `eduops_export`, OS filesystem APIs | UI cannot bypass command authorization or audit. |
| `eduops_domain` | Any adapter, UI, DB, filesystem, network, or Tauri crate | Domain types and state tables must remain portable and testable. |
| `eduops_storage` | UI, GitHub, runner, exporter UI state | Storage cannot own product workflow or external side effects. |
| `eduops_config` | raw credential values, UI-only state, live network clients | Configuration owns validated records and references, not secrets or side effects. |
| `eduops_credentials` | UI/editor modules or course workflow policy | Credential adapter exposes references and status only through core-authorized APIs. |
| `eduops_git` | UI/editor modules | Git behavior must be mediated by core use cases and state gates. |
| `eduops_runner` | GitHub/live remote connectors | Advisory runner cannot imply official grading or remote side effects. |
| Any module | Direct live GitHub or LMS connector calls during SLICE-A/B/C | Fake/local gates must pass first. |

## 4. Test and fixture ownership

- `tests/contract` verifies API envelopes, state tables, and adapter trait behavior.
- `tests/integration` verifies vertical slices using fake/local adapters.
- `tests/golden` verifies deterministic projections, export manifests, and fixture hashes.
- `tests/contract/config` verifies configuration merge, schema, migration, redaction, and offline isolation.
- `fixtures/slice-a` through `fixtures/slice-c` are privacy-safe deterministic inputs required before code is considered beta-directed.
- `fixtures/config` verifies configuration and credential behavior before live adapter settings are enabled.

## 5. Generated artifacts

Generated code or schema files must identify their source document/schema and generation command. Generated docs belong under `docs/generated/` and are not edited manually.


## 6. GitHub adapter package refinement

[GitHub Adapter Software Design Description](github-adapter-software-design-description.md) refines `crates/eduops_git/` into these future modules: `github/mod.rs`, `github/mode_gate.rs`, `github/clone_planner.rs`, `github/privacy_naming.rs`, `github/fake_local.rs`, `github/mock_http.rs`, `github/retry.rs`, and `github/evidence.rs`. Contract fixtures belong under `tests/contract/github_adapter/`, and privacy-safe fixture data belongs under `fixtures/github/`.


## 7. Editor adapter bridge package refinement

[Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) v0.1.0 closes its §4 forward reference to this layout document by adopting `crates/eduops_domain/` as the home for a future fixture-local `editor_bridge` sub-module. The placement is the natural fit because `eduops_domain` already owns the canonical `BlockDocument`, `EditorBlock`, operation journal, deterministic projection, and Korean text handling types that the bridge translates between an editor runtime document and EduOps-owned canonical structures.

The bridge module shall be reachable from the desktop UI shell but shall not depend on a specific editor runtime crate or any external editor package. The expected future internal layout is `crates/eduops_domain/src/editor_bridge/mod.rs` plus sub-modules for canonical-block ⇄ editor-node mapping, journal entry derivation, Korean IME composition handling, validation hooks, and error/rollback behavior; the exact sub-module split is determined per-PREP by the corresponding `STD-M3-EDITOR-BRIDGE-001..006` test bucket. Contract fixtures for the bridge belong under `tests/contract/editor_adapter_bridge/` (analogous to the existing `tests/contract/github_adapter/` precedent for the GitHub adapter), and fixture editor-state JSON data belongs under `fixtures/editor_adapter_bridge/`.

This placement note preserves every bridge specification §2.2 non-claim and the existing §2 / §3 dependency direction rules in this layout document: the `eduops_domain` crate does not depend on any UI / editor / IPC / Tauri / desktop crate, no editor runtime crate (Tiptap, ProseMirror, Lexical, Markdown-first, Monaco, or custom) is adopted by this note, no source file is modified, no Cargo dependency is added, and no `eduops_domain` API surface change is authorized. The future `editor_bridge` sub-module is a fixture-local target for later PREP/T/GATE cycles; each future cycle that adds the sub-module must preserve every bridge specification §2.2 non-claim.

Cross-references: [Editor Adapter Bridge Specification](editor-adapter-bridge-specification.md) at `e8d8235`; M3 editor adapter bridge STD addendum at `3a41653` introducing `STD-M3-EDITOR-BRIDGE-001..006`; M3 editor adapter bridge RTM addendum at `8fe258b`; [M3 editor bridge local-safe specification authority](../05-decisions/m3-editor-bridge-local-safe-spec-authority-2026-05-21.md) (`EDUOPS-DEC-067`) at `6f855ac`.


## 8. SLICE-A file enumeration

The first product-code Ralph loop may create only these implementation paths unless Hermes approves a scope change:

```text
Cargo.toml
rust-toolchain.toml
package.json
pnpm-lock.yaml or equivalent package-manager lock file
apps/desktop/
apps/desktop-ui/
crates/eduops_domain/src/lib.rs
crates/eduops_api/src/lib.rs
crates/eduops_storage/src/lib.rs
crates/eduops_git/src/lib.rs
crates/eduops_git/src/fake_local.rs
crates/eduops_git/src/github/mod.rs
crates/eduops_git/src/github/mode_gate.rs
crates/eduops_git/src/github/fake_local.rs
crates/eduops_fixture/src/main.rs
crates/eduops_fixture/src/run_summary.rs
crates/eduops_fixture/src/verify_corpus.rs
tests/contract/github_adapter/gh_fix_001_fake_local_no_network.rs
tests/ui_shell/
```

The loop may also write evidence under `build/evidence/`, which remains generated evidence and is excluded from controlled frontmatter checks.
