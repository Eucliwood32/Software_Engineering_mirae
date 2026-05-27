---
title: Desktop Entrypoint Dependency Adoption Decision Specification
document_id: EDUOPS-DESKTOP-ENTRYPOINT-DEPENDENCY-ADOPTION-DECISION
version: 0.1.0
status: superseded
date: 2026-05-19
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
    - EDUOPS-DEC-OS-001
    - EDUOPS-FAST-NATIVE-DESKTOP-UI-BASELINE
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-MODULE-LAYOUT
  gaps_recorded:
    - Desktop entrypoint dependency adoption decision (superseded by authorized path B decision)
---

# Desktop Entrypoint Dependency Adoption Decision Specification

## 0. Supersession notice

This deferred decision specification is superseded by [Desktop Entrypoint Dependency Adoption Authorized Decision](desktop-entrypoint-dependency-adoption-authorized-decision.md), decision ID `EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-AUTHORIZED`, for the narrow path-B scope authorized on 2026-05-19. The path-A/path-B analysis in this document remains the rationale and boundary record, but its stop condition no longer blocks the first authorized Tauri 2 `query_session_capabilities` entrypoint increment.

## 1. Purpose

This document records the controlled deferred-decision posture for the desktop application entrypoint dependency adoption choice before any task beyond the desktop-app development plan §6 D1 (fixture-local Tauri configuration contract), §6 D4 (fixture-local smoke evidence template), or §6 D5 (fixture-local home screen render) is executed under Ralph automation.

The desktop-app development plan §3 candidate-A path is the selected first real desktop application path. Its full execution requires:

- Tauri 2 Cargo dependencies (`tauri`, `tauri-build`, `serde`, `serde_json`, and likely additional Tauri 2 ecosystem crates);
- a binary entrypoint at `apps/desktop/src/main.rs` that registers Tauri commands and opens a Tauri window;
- a desktop host runtime prerequisite (WebKitGTK on Linux, WebView2 on Windows);
- a Tauri CLI prerequisite (`cargo tauri` or `tauri` CLI) installed on the build/host machine;
- root `package.json` script entries that reference the Tauri CLI (`desktop:dev`, `desktop:build`);
- a user-observed launch capture step (desktop-app development plan §6 D6).

The current repository observes a deliberate zero-third-party-Cargo-dependency boundary outside the `eduops_*` workspace crates and standard library / dev-only build tooling. Adopting the Tauri 2 dependencies and committing to the host runtime prerequisite is a product-scope and operations-scope decision that requires explicit user authority. Until that authority is exercised, the Ralph loop shall remain inside the fixture-local D1/D4/D5 path and shall not execute D2/D3/D6.

## 2. Decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-DEFERRED` |
| Status | `superseded` |
| Date | 2026-05-19 |
| Authority required | user / product owner |
| Default until decision | path A — fixture-local D1/D4/D5 only |

The default-until-decision posture is path A: the desktop-app development plan §6 D1 fixture-local Tauri configuration contract (`apps/desktop/tauri.conf.json` and `apps/desktop/tests/desktop_tauri_config.rs`), §6 D4 fixture-local smoke evidence template (`apps/desktop-ui/scripts/desktop-smoke-template.mjs` and `apps/desktop-ui/tests/desktop-smoke-template.test.mjs`), and §6 D5 fixture-local home screen render (`apps/desktop-ui/src/desktopHomeRender.mjs` and `apps/desktop-ui/tests/desktop-home-render.test.mjs`) shall continue to be the only desktop-app increments executed under Ralph automation. The §6 D2 npm desktop scripts, §6 D3 Tauri IPC wiring beyond the existing `query_session_capabilities` M1A command, and §6 D6 user-observed launch gate shall not be executed under Ralph automation until this decision spec is superseded by an authorized commitment to path B.

## 3. Path A — Fixture-local D1/D4/D5 (current state)

### Inputs
- `apps/desktop/Cargo.toml` keeps only the existing path dependency on `eduops_api`;
- `apps/desktop/tauri.conf.json` is a controlled JSON file that is read by `apps/desktop/tests/desktop_tauri_config.rs` via `std::fs::read_to_string`; the file is not used by any binary entrypoint, by `cargo tauri`, or by any host runtime;
- `apps/desktop-ui/src/desktopHomeRender.mjs` exports a pure HTML-string render function that any Node test can import and assert against;
- `apps/desktop-ui/scripts/desktop-smoke-template.mjs` is a Node script that emits a deterministic `run-summary.json` shape under `--dry-run` and rejects all non-`--dry-run` invocations;
- root `package.json` contains only the existing `m0:*` script set; no `desktop:dev`, `desktop:build`, `desktop:prepare`, or `desktop:smoke` entries are present;
- `apps/desktop/src/main.rs` does not exist.

### Capabilities under path A
- Ralph can extend the fixture-local D5 home render with additional model variants;
- Ralph can extend the fixture-local D4 smoke evidence template with additional schema fields;
- Ralph can extend the fixture-local D1 Tauri configuration contract with additional structural property assertions;
- Ralph can author additional STD / RTM / README / INDEX / milestones traceability addenda for already-implemented executable test buckets;
- All existing M1A `apps/desktop/tests/ui_shell_launch_health.rs` session-capability behavior remains green and unchanged;
- All existing `m7-approval-ux-*` tests remain green and unchanged;
- `npm run m0:check` (`m0:rust-check` + `m0:ui-typecheck` + `m0:ui-build` + `m0:fixture-check`) remains green;
- `cargo check --workspace` remains green with the existing path-only dependency set.

### Limits under path A
- The current repository cannot launch a real desktop window;
- The current repository cannot exercise real Tauri IPC beyond the M1A session-capability command;
- The current repository cannot produce a real user-observed launch screenshot/recording;
- The desktop-app plan §6 D6 user-observed launch gate cannot be satisfied;
- DEMO-1 cannot be claimed from path A alone.

## 4. Path B — Tauri 2 adoption and binary entrypoint

### Required inputs
- Add Tauri 2 Cargo dependencies to `apps/desktop/Cargo.toml`:
  - `tauri` (workspace-default features, no live updater feature);
  - `tauri-build` as a build dependency;
  - `serde` with `derive` feature for command argument/return types;
  - `serde_json` for IPC payload serialization;
  - any Tauri 2 ecosystem crates required by the selected feature set (for example a plugin crate for filesystem or shell access — explicitly excluded by the desktop-app plan §5 boundary record);
- Add `apps/desktop/src/main.rs` that:
  - registers the existing `query_session_capabilities` command (and any new commands authorized at the same time) on the Tauri builder,
  - loads the `frontendDist=../desktop-ui/dist` HTML produced by `apps/desktop-ui/scripts/build.mjs`,
  - opens a single Tauri window with `title=EduOps Desktop`,
  - does not register any updater plugin, publish endpoint, filesystem plugin with write authority, or shell plugin;
- Add `tauri-build` invocation to `apps/desktop/build.rs` (if required by the Tauri 2 toolchain);
- Add npm scripts to root `package.json`:
  - `"desktop:prepare": "npm run m0:ui-build"`,
  - `"desktop:dev": "npm run desktop:prepare && cargo tauri dev --manifest-path apps/desktop/Cargo.toml"`,
  - `"desktop:build": "npm run desktop:prepare && cargo tauri build --manifest-path apps/desktop/Cargo.toml"`,
  - `"desktop:smoke": "node apps/desktop-ui/scripts/desktop-smoke-template.mjs --dry-run"` (or a successor script authorized at the same time);
- Confirm Tauri CLI presence on the host that will execute `desktop:dev` / `desktop:build`.

### Required host prerequisites
- Linux host: a Tauri-supported WebKit/WebKitGTK runtime per `EDUOPS-DEC-OS-001` §2;
- Windows host: WebView2 runtime per `EDUOPS-DEC-OS-001` §2;
- Either host: a Tauri CLI (`cargo install tauri-cli` or a pinned dev dependency adoption);
- A Rust toolchain compatible with the chosen Tauri 2 minor version.

### Trade-off summary

| Dimension | Path A | Path B |
|---|---|---|
| Cargo dependency surface | Path deps only | Path deps + Tauri 2 ecosystem crates |
| Host runtime prerequisite | None beyond stdlib | WebKitGTK (Linux) or WebView2 (Windows) |
| Tauri CLI prerequisite | Not required | Required |
| Real desktop window | No | Yes |
| Real IPC beyond M1A session-capability | No | Authorized one-at-a-time per spec |
| User-observed launch gate (`§6 D6`) | Cannot be satisfied | Can be satisfied with screenshot/recording |
| DEMO-1 acceptability | Not claimable | Becomes possible after fidelity gates |
| Maintenance overhead | Low (no third-party upgrade churn) | Moderate (Tauri 2 minor-version upgrade discipline required) |
| Security surface | Pure stdlib + path deps | Additional third-party crate review surface |

## 5. Why the decision is deferred

The path-B commitment crosses the following boundaries that the Ralph loop does not unilaterally authorize:

- **Third-party Cargo dependency adoption.** The repository currently holds a deliberate zero-third-party-Cargo-dependency baseline outside the `eduops_*` workspace crates. Adopting `tauri`, `tauri-build`, `serde`, `serde_json`, and any Tauri 2 ecosystem crates is a product-scope decision that the Ralph automation cannot enact without user authority. The first such adoption sets the supply-chain trust posture for subsequent decisions.
- **Host operating-environment prerequisite.** Path B commits the project to a WebKitGTK (Linux) or WebView2 (Windows) host runtime that must be installed on every build/launch host. This is an operations-scope commitment that the Ralph automation cannot make.
- **Tauri CLI installation prerequisite.** Path B's `desktop:dev` and `desktop:build` npm scripts reference `cargo tauri dev` / `cargo tauri build`. Without the Tauri CLI installed, the scripts would fail by default and create a broken-by-default user experience that contradicts the desktop-app plan §6 D2 acceptance criteria.
- **Tauri 2 minor-version upgrade discipline.** Path B introduces a third-party-crate upgrade cadence that the project does not yet have governance for. The fixture-local path A does not introduce that cadence.
- **Security review surface.** Each Tauri 2 ecosystem crate adopted expands the dependency-review surface (license, advisory, transitive-dep) that the project must continuously monitor.
- **DEMO-1 readiness coupling.** Path B is a prerequisite for the user-observed launch gate per desktop-app plan §6 D6; D6 is in turn a prerequisite for the DEMO-1 demonstration claim. The DEMO-1 claim crosses an institutional/operations approval boundary that Ralph automation cannot enact (analogous to the M8 export DEMO-1 deferral in `m8-export-spec-blocker.md`).

The Ralph loop cannot decide these points unilaterally because they fall outside the non-delegable safety boundary in `ralph.md` §2 (no live external action, no destructive/dependency-graph-altering action, no commitment to a host runtime, no DEMO-1 claim).

## 6. Conditions under which path B may proceed

The path-B commitment may proceed only when all of the following are explicitly authorized by the user / product owner:

1. The Tauri 2 dependency adoption is approved in writing, including the specific minor version and the feature set (no updater, no publish, no shell-write, no filesystem-write features).
2. The host runtime prerequisite is selected and confirmed for the first target host (Linux WebKitGTK or Windows WebView2 per `EDUOPS-DEC-OS-001`).
3. The Tauri CLI installation path is selected and recorded (system install vs. pinned dev dependency vs. `cargo install tauri-cli`).
4. A controlled "first authorized commit" is named for path B (which file is added first, which test is added first, what RED/GREEN evidence is acceptable).
5. The desktop-app plan §6 D2 npm script entries are authorized for inclusion (script names, command shapes, ordering).
6. The desktop-app plan §6 D3 IPC wiring scope is limited explicitly to the first authorized command beyond `query_session_capabilities` (or explicitly to "no new commands" for the first path-B increment).
7. The user-observed launch gate evidence shape (screenshot only, short screen recording, or both) is selected per the desktop-app plan §9 question 4.
8. The non-claim list for the first path-B increment is recorded (still no DEMO-1 claim, still no installer publication, still no remote action, still no credential resolution, still no live external action beyond the IPC boundary).

When all eight conditions hold, this decision spec shall be superseded by a `desktop-entrypoint-dependency-adoption-authorized-decision` record, this row's `status` shall change from `deferred` to `superseded`, and the Ralph loop may execute the desktop-app plan §6 D2 / D3 sequence under the new authority record. Until then, the Ralph loop shall remain in path A.

## 7. Default behavior until decision

While `status` remains `deferred`:

- `apps/desktop/Cargo.toml` shall not adopt any new Cargo dependency;
- `apps/desktop/src/main.rs` shall not be created;
- `apps/desktop/build.rs` shall not be created;
- root `package.json` shall not add `desktop:dev`, `desktop:build`, `desktop:prepare`, or `desktop:smoke` script entries that depend on the Tauri CLI;
- the desktop-app plan §6 D2 / D3 / D6 increments shall not be executed under Ralph automation;
- the existing M1A `apps/desktop/tests/ui_shell_launch_health.rs` session-capability test shall remain green and unchanged;
- the existing D1 / D5 / D4 fixture-local test buckets shall remain green and unchanged;
- traceability addenda authored from path A evidence shall continue to preserve explicit non-claims for path-B-only behavior (real Tauri runtime adoption, real desktop launch, real Tauri IPC invocation, real desktop window, real screenshot/recording capture, installer publication, DEMO-1 acceptance, real reviewer attestation workflow, real credential resolution, network call, remote action, repository administration, submission/provisioning state promotion, and evaluation-result authority);
- user-managed external-repo boundary actions remain user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.

## 8. Acceptance boundary

This decision spec records a **deferred** posture and the trade-off analysis between path A and path B. Acceptance of this spec by the Ralph loop's controlled docs/control gate is acceptance of the deferral posture only. Acceptance of this spec does not:

- adopt any Tauri 2 Cargo dependency;
- create `apps/desktop/src/main.rs`;
- create `apps/desktop/build.rs`;
- add `desktop:dev`, `desktop:build`, `desktop:prepare`, or `desktop:smoke` scripts to root `package.json`;
- commit the project to a WebKitGTK / WebView2 host runtime prerequisite;
- commit the project to a Tauri CLI installation;
- authorize any user-observed launch capture step;
- claim DEMO-1 readiness or any portion of it;
- claim installer publication readiness;
- authorize any network call, credential resolution, remote action, repository administration, submission/provisioning state promotion, or evaluation-result authority.

It records only that the path-A vs. path-B trade-off is understood, that the deferred posture is in effect, and that the conditions in §6 are required before path B may proceed.

## 9. Relationship to other specifications

- [Desktop App Development Plan](../06-implementation/desktop-app-development-plan.md) §3 candidate table is the source of the path-A vs. path-B definitions; §5 boundary record is the source of the non-claims; §6 D1 / D4 / D5 increments are already implemented under path A; §6 D2 / D3 / D6 increments are blocked by this deferral.
- [DEC-OS-001 Windows and Linux Desktop Target](dec-os-001-windows-linux-desktop-target.md) is the source of the host runtime / Tauri version evidence fields that path B must record.
- [Fast native desktop UI baseline](fast-native-desktop-ui-baseline.md) is the source of the Tauri 2 + WebKitGTK / WebView2 architectural baseline.
- [Process topology and IPC contract](process-topology-and-ipc-contract.md) is the source of the IPC scope that path B's §6 D3 increments must respect.
- [Module and package layout](module-and-package-layout.md) is the source of the `apps/desktop` / `apps/desktop-ui` placement that path B must preserve.
- The existing M3-BRIDGE-SPEC-BLOCKER, M5-AUTH-SPEC-BLOCKER, M6-RUNNER-IO-SPEC-BLOCKER, and M8-EXPORT-SPEC-BLOCKER documents under `docs/06-implementation/` are the precedent docs/control deferral pattern that this spec follows.
- The MB-DESKTOP STD addendum in [Software test description](../03-verification-validation/software-test-description.md) and the MB-DESKTOP RTM addendum in [Requirements traceability matrix](../01-requirements/requirements-traceability-matrix.md) record the path-A V&V trace; this spec records the path-B authorization gap.

## 10. Resume rule for Ralph automation

When the Ralph loop reaches a queue-end refill checkpoint with this decision spec still in `deferred` status, the loop shall:

1. classify desktop-app plan §6 D2 / D3 / D6 as non-executable until this spec is superseded;
2. continue to author safe class-(1) / (3) / (4) docs/control increments inside path A that do not adopt any new Cargo dependency, do not create `apps/desktop/src/main.rs`, do not add Tauri-CLI-dependent npm scripts, and do not invoke any host runtime;
3. report a controlled queue-end stop only when no safe path-A class-(1) / (3) / (4) candidate remains and the only remaining candidate is path-B activation, in which case the stop reason shall name "EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-DEFERRED";
4. preserve all non-claims listed in §7 in any subsequent refill checkpoint.

When this spec is superseded by an authorized commitment to path B, the resume rule shall be updated to reference the new authorization record and the §6 D2 / D3 / D6 increments shall become executable under the new authority's RED/GREEN/gate protocol.
