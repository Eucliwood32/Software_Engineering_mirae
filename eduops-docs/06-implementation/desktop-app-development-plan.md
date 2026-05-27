---
title: Desktop App Development Plan
document_id: EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
version: 0.1.0
status: draft
created: 2026-05-19
owner: develop
quality_context: controlled implementation planning
traceability:
  upstream:
    - EDUOPS-IMPLEMENTATION-MILESTONES
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-MODULE-LAYOUT
    - SWENG-EDUTECH-INTERNAL-API
---

# Desktop App Development Plan

## 1. Goal

Create a real launchable EduOps desktop application from the current static desktop UI scaffold.

The first implementation target is a controlled Tauri 2 desktop shell that loads the existing `apps/desktop-ui` screen, performs a local backend health/session query through an explicit IPC boundary, displays the existing fake/local/no-live-action evidence fields, and can be launched by a repeatable local command. The plan does not authorize live GitHub, network, credential lookup, real Git mutation, deployment, installer publication, or production student data handling.

## 2. Current baseline

The repository already contains these relevant artifacts:

| Area | Current artifact | Current limitation |
|---|---|---|
| Rust desktop crate | `apps/desktop/src/lib.rs` | Provides shell capability metadata and `query_session_capabilities`; no binary app entrypoint or Tauri runtime wiring. |
| Rust test | `apps/desktop/tests/ui_shell_launch_health.rs` | Verifies no-live session capability envelope; does not launch a desktop window. |
| UI source | `apps/desktop-ui/src/main.ts` | Provides deterministic shell/evidence models; not bundled by Vite/Tauri. |
| UI build script | `apps/desktop-ui/scripts/build.mjs` | Writes a static `dist/index.html`; no dev server, no asset pipeline, no IPC bridge. |
| Root npm scripts | `package.json` | Provides `m0:*` checks only; no `desktop:dev`, `desktop:build`, or `desktop:smoke` command. |
| Controlled M1A milestone | `docs/06-implementation/implementation-milestones.md` §M1A | Requires Tauri/WebView2 shell launch, IPC smoke, UI evidence display, runtime evidence, and screenshot/screen-recording evidence. |

The current visible screen can be opened through a local static HTTP server. That is useful for inspection, but it is not yet a real desktop application launch path.

## 3. Candidate implementation approaches

| Candidate | Description | Advantages | Risks / tradeoffs | Decision |
|---|---|---|---|---|
| A. Minimal Tauri 2 shell around the existing static HTML | Add Tauri config, Rust binary entrypoint, a local command for session capabilities, and package scripts. Keep the UI mostly static for the first shell. | Smallest path to a real desktop window; preserves current evidence; lowest scope risk; supports TDD with launch/config smoke tests. | Requires Tauri/WebKitGTK/WebView2 platform prerequisites; UI remains simple. | Selected for first increment. |
| B. Browser-only dev server with richer UI | Add Vite/dev server and improve the HTML/TS UI without Tauri. | Fast iteration; fewer OS prerequisites. | Does not satisfy the user's goal of a real desktop app; repeats the current static-browser limitation. | Not selected as primary path. |
| C. Full product UI integration first | Wire course, roster, assignment, approval, local checkout, export, and runner screens before desktop packaging. | More visually complete. | Large scope; mixes many already-constrained M3..M8 behaviors; high risk of violating no-live/no-secret boundaries. | Deferred. |
| D. Native Rust GUI instead of Tauri | Replace web shell with egui/Slint/Iced-style native UI. | Could reduce web runtime dependencies. | Contradicts accepted Tauri/WebView2 baseline unless a design decision changes; more rework. | Not selected. |

## 4. Selected architecture

The first real desktop app path uses Candidate A.

```text
apps/desktop-ui/src/main.ts
  -> apps/desktop-ui/scripts/build.mjs
  -> apps/desktop-ui/dist/index.html
  -> apps/desktop/src/main.rs Tauri window
  -> apps/desktop/src/lib.rs session capability command
  -> eduops_api RequestEnvelope / ResultEnvelope
```

The UI continues to display only controlled fake/local fields:

- `ui_shell=tauri2-webview2-shell`;
- `adapter_modes=fake,local`;
- `live_external_action=false`;
- `direct_ui_filesystem_access=false`;
- `direct_ui_git_access=false`;
- `network_request_enabled=false`;
- SLICE-A course/evidence/fake-Git fields.

The Tauri command layer shall expose a read-only health/session command first. Mutating actions such as real course creation, real filesystem writes from UI, Git execution, GitHub operations, credential lookup, and network operations remain blocked until separate controlled gates authorize them.

## 5. Boundary record

Allowed in this plan:

- add local Tauri app configuration and source files;
- add local npm scripts for build/dev/smoke;
- add fixture/local tests for Tauri config, generated HTML, and command schema;
- run local build/typecheck/test commands;
- create local Git commits after validation.

Not allowed in this plan:

- pushing to a remote;
- creating GitHub repositories or changing remotes;
- resolving or storing real credentials;
- invoking live GitHub, network, LMS, notification, runner, exporter, or official grading services;
- packaging or publishing installers/releases;
- claiming DEMO-1 completion or production readiness;
- accepting desktop runtime evidence without a user-observed desktop launch/capture package.

## 6. Increment plan

### D0 — Desktop shell readiness checkpoint

**Objective.** Make the current desktop-app gap explicit and prepare a safe execution queue.

**Files.**

- Create: `docs/06-implementation/desktop-app-development-plan.md`
- Modify: `docs/INDEX.md`
- Modify: `docs/README.md`

**Validation.**

```bash
git diff --check
python3 - <<'PY'
from pathlib import Path
for path in [
    Path('docs/06-implementation/desktop-app-development-plan.md'),
    Path('docs/INDEX.md'),
    Path('docs/README.md'),
]:
    assert path.exists(), path
print('desktop_plan_docs=ok')
PY
```

**Acceptance.** The plan is committed as a documentation/control increment and no product code is changed.

### D1 — Add Tauri app metadata and launch entrypoint

**Objective.** Introduce a minimal launchable desktop shell without changing backend behavior.

**Files.**

- Create: `apps/desktop/src/main.rs`
- Create: `apps/desktop/tauri.conf.json` or `apps/desktop/src-tauri/tauri.conf.json` according to the selected Tauri 2 layout
- Modify: `apps/desktop/Cargo.toml`
- Modify: root `package.json`
- Test: `apps/desktop/tests/desktop_tauri_config.rs`

**Step 1: Write failing config test.**

The test should parse the Tauri config and assert:

- app product name contains `EduOps`;
- the frontend dist path points to `../desktop-ui/dist` or the equivalent committed location;
- the app does not define any updater, publish, or external URL requirement;
- the configured window title is `EduOps Desktop`.

**Step 2: Verify RED.**

```bash
cargo test -p eduops_desktop --test desktop_tauri_config -- --nocapture
```

Expected RED: config file or expected keys are missing.

**Step 3: Implement minimal config and entrypoint.**

Add only enough Tauri setup to load the static UI dist and expose no live external behavior.

**Step 4: Verify GREEN and repository checks.**

```bash
cargo test -p eduops_desktop --test desktop_tauri_config -- --nocapture
cargo test -p eduops_desktop -- --nocapture
npm run m0:ui-build
cargo check --workspace
```

**Commit.**

```bash
git add apps/desktop package.json
git commit -m "feat: add minimal desktop shell launch metadata"
```

### D2 — Add controlled desktop launch scripts

**Objective.** Give the user one obvious command for running and one command for smoke validation.

**Files.**

- Modify: root `package.json`
- Modify: `apps/desktop-ui/package.json` if a UI-specific helper is needed
- Create: `scripts/desktop-smoke.mjs` or `apps/desktop-ui/scripts/desktop-smoke.mjs`
- Test: `apps/desktop-ui/tests/desktop-launch-scripts.test.mjs`

**Commands to add.**

Recommended script names:

```json
{
  "desktop:prepare": "npm run m0:ui-build",
  "desktop:dev": "npm run desktop:prepare && cargo tauri dev --manifest-path apps/desktop/Cargo.toml",
  "desktop:build": "npm run desktop:prepare && cargo tauri build --manifest-path apps/desktop/Cargo.toml",
  "desktop:smoke": "node scripts/desktop-smoke.mjs"
}
```

If the installed Tauri CLI expects a different command shape, use the discovered CLI shape and record it in this document before coding.

**TDD.**

1. Write a Node test that reads root `package.json` and asserts the four scripts exist.
2. Verify RED before adding scripts.
3. Add scripts.
4. Verify GREEN.

**Validation.**

```bash
node apps/desktop-ui/tests/desktop-launch-scripts.test.mjs
npm run desktop:prepare
npm run desktop:smoke
```

**Commit.**

```bash
git add package.json scripts apps/desktop-ui/tests
git commit -m "feat: add desktop launch scripts"
```

### D3 — Wire backend health/session query through Tauri IPC

**Objective.** Make the desktop window prove that it can query the Rust backend through a controlled IPC command.

**Files.**

- Modify: `apps/desktop/src/lib.rs`
- Modify: `apps/desktop/src/main.rs`
- Modify: `apps/desktop-ui/src/main.ts`
- Modify: `apps/desktop-ui/scripts/build.mjs`
- Test: `apps/desktop/tests/ui_shell_launch_health.rs`
- Test: `apps/desktop-ui/tests/desktop-ipc-contract.test.mjs`

**Behavior.**

Expose one read-only command, for example `session_get_capabilities`, returning the existing `SessionCapabilities` record through a `ResultEnvelope`. The UI shall render the same controlled no-live fields and include a visible IPC status such as:

```text
ipc_session_health=ok
api_version=eduops.api/0.1
```

**RED.**

Add tests expecting the command symbol, generated HTML marker, and false no-live flags. Verify they fail before implementation.

**GREEN.**

Implement the minimal command wiring. The command must not read files, execute Git, open network sockets, resolve credentials, or mutate state.

**Validation.**

```bash
cargo test -p eduops_desktop --test ui_shell_launch_health -- --nocapture
node apps/desktop-ui/tests/desktop-ipc-contract.test.mjs
npm run m0:ui-build
cargo check --workspace
npm run m0:check
```

**Commit.**

```bash
git add apps/desktop apps/desktop-ui package.json
git commit -m "feat: wire desktop shell health IPC"
```

### D4 — Add visible desktop smoke evidence command

**Objective.** Produce a candidate evidence package whenever the app is launched for review.

**Files.**

- Create: `scripts/capture-desktop-smoke-evidence.mjs` or update the existing M1A capture script if one already exists
- Modify: `docs/06-implementation/m1a-desktop-gate-closure-runbook.md` only if the command name changes
- Test: `apps/desktop-ui/tests/desktop-smoke-evidence.test.mjs`

**Evidence fields.**

The generated package shall include:

- `run-summary.json`;
- app command used;
- Git HEAD and branch;
- OS/runtime metadata;
- `live_external_action=false`;
- `network_request_enabled=false`;
- screenshot path placeholder or captured media path;
- reviewer/owner attestation field;
- `candidate-for-review`, not final gate closure.

**Validation.**

```bash
node apps/desktop-ui/tests/desktop-smoke-evidence.test.mjs
node scripts/capture-desktop-smoke-evidence.mjs --dry-run
```

**Commit.**

```bash
git add scripts apps/desktop-ui/tests docs/06-implementation/m1a-desktop-gate-closure-runbook.md
git commit -m "feat: add desktop smoke evidence capture"
```

### D5 — Improve the first real desktop screen without broad product scope

**Objective.** Replace the plain diagnostic HTML with a small role-aware first screen while keeping behavior fixture-local.

**Files.**

- Modify: `apps/desktop-ui/src/main.ts`
- Modify: `apps/desktop-ui/scripts/build.mjs`
- Add or modify: `apps/desktop-ui/tests/*desktop-home*.test.mjs`

**Screen sections.**

1. Header: EduOps Desktop, fake/local indicator, no-live-action notice.
2. Instructor panel: create local course button, evidence preview, disabled live-GitHub controls with non-claim text.
3. Student panel: local workspace/read-only status placeholders.
4. Diagnostics panel: IPC health, app version, runtime boundary, evidence path.

**TDD.**

Add render tests asserting accessible headings, keyboard-focusable first action, no raw URL/credential display, and no-live flags before modifying the renderer.

**Validation.**

```bash
node apps/desktop-ui/tests/desktop-home-render.test.mjs
npm run m0:ui-build
npm run m0:check
```

**Commit.**

```bash
git add apps/desktop-ui
git commit -m "feat: render controlled desktop home screen"
```

### D6 — User-observed desktop launch gate

**Objective.** Confirm that the app launches as a real desktop app on a named host/runtime and preserve reviewable evidence.

This task requires user-observed execution when the host desktop/runtime matters. Ralph/Hermes may prepare scripts and candidate evidence but shall not mark final gate closure without human-observed screenshot/recording or explicit attestation.

**User command pattern.**

```bash
cd /home/cbchoi/workspaces/develop/repos/eduops
npm run desktop:dev
```

Then run the capture command prepared in D4, attach the screenshot/recording or output path, and request a gate-review commit.

**Acceptance.**

- The user sees an EduOps desktop window, not only a browser tab.
- The screen shows `live_external_action=false` and fake/local mode.
- IPC health is visible and reports `ok`.
- Evidence package is `candidate-for-review` until reviewed.

## 7. Recommended first execution queue

For the next Ralph or manual implementation loop, use this order:

```text
D1 -> D2 -> D3 -> D4 -> D5 -> D6
```

Stop after D3 if Tauri platform prerequisites are missing. In that case, record the prerequisite blocker and keep the static-browser screen as a fallback inspection mode. Do not skip directly to a visual redesign before D1-D3; the user need is launchability, not a prettier browser mockup.

## 8. Verification bundle for each code increment

Run focused tests first, then repository-level checks:

```bash
cargo test -p eduops_desktop -- --nocapture
npm --prefix apps/desktop-ui run typecheck
npm --prefix apps/desktop-ui run build
cargo check --workspace
npm run m0:check
```

For Tauri runtime-specific increments, add the relevant launch/build command after platform prerequisites are available:

```bash
npm run desktop:dev
# or
npm run desktop:build
```

## 9. Open questions before final desktop product claims

1. Which host will be used for the first official desktop capture: Linux desktop on this machine, Windows with WebView2, or both?
2. Is Tauri CLI already installed or should the project pin a local CLI dependency? Pinning is preferred for repeatability.
3. Should the first visible desktop screen remain a diagnostic shell or become an instructor-first course dashboard in D5?
4. Which evidence capture format is preferred for user review: screenshot only, short screen recording, or both?
5. When should real file picker, CSV upload UI, and local checkout reader screens be promoted from fixture-local model/render tests into an integrated desktop UI? These remain separate gates.

## 10. Next action

Start with D1. The first code increment should add a failing `desktop_tauri_config` test, observe RED, add the minimal Tauri metadata and entrypoint, then run the focused and repository-level validation commands before committing.
