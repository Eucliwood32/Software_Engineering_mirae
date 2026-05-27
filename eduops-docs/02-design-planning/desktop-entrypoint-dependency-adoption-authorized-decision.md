---
title: Desktop Entrypoint Dependency Adoption Authorized Decision
document_id: EDUOPS-DESKTOP-ENTRYPOINT-DEPENDENCY-AUTHORIZED-DECISION
version: 0.1.0
status: authorized
date: 2026-05-19
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  supersedes:
    - EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-DEFERRED
  upstream:
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
    - EDUOPS-DESKTOP-ENTRYPOINT-DEPENDENCY-ADOPTION-DECISION
    - EDUOPS-DEC-OS-001
    - EDUOPS-FAST-NATIVE-DESKTOP-UI-BASELINE
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-MODULE-LAYOUT
  authorizes:
    - MB-DESKTOP-PATH-B-AUTH-PREP
    - MB-DESKTOP-D3-ENTRYPOINT-T1
---

# Desktop Entrypoint Dependency Adoption Authorized Decision

## 1. Purpose

This document records user / product-owner authorization for path B in the desktop entrypoint dependency adoption decision. It supersedes the deferred posture recorded in [Desktop Entrypoint Dependency Adoption Decision Specification](desktop-entrypoint-dependency-adoption-decision-specification.md) and gives Ralph a controlled authority record for the first Tauri 2 desktop entrypoint increment.

This record authorizes a narrow first path-B increment only. It does not authorize publication, installer release, live external actions, credential resolution, remote repository mutation, updater/publish features, shell-write, filesystem-write, or a DEMO-1 claim. In short, the first increment preserves no updater, no filesystem-write, and no DEMO-1 boundaries.

## 2. Decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-AUTHORIZED` |
| Supersedes | `EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-DEFERRED` |
| Status | `authorized` |
| Date | 2026-05-19 |
| Authority | user / product owner |
| Source approval | Discord develop EduOps thread user instruction: "go for B" followed by "Path B authorized decision record 작성하고 queue에 seeding해." |
| First authorized path | Path B — Tauri 2 dependency adoption and binary entrypoint, constrained to the first session-capability IPC increment |

The product owner authorizes Tauri 2 dependency adoption for a minimal launchable desktop entrypoint path. The first implementation increment shall remain test-first and shall be limited to registering or preserving the existing `query_session_capabilities` capability boundary. No additional IPC command is authorized in the first increment.

## 3. Authorized dependency and feature boundary

The following dependency adoption is authorized for the first path-B increment:

- `tauri` 2.x, pinned by Cargo resolution in `Cargo.lock` once added;
- `tauri-build` 2.x as a build dependency if required by the selected Tauri 2 toolchain;
- `serde` with `derive` feature;
- `serde_json` for IPC payload serialization when required by the Tauri command boundary.

The first increment shall use the minimal Tauri feature set required to compile and register the existing session-capability command. The following are explicitly not authorized:

- updater plugin or update endpoint;
- publish or installer publication configuration;
- shell plugin or shell-write authority;
- filesystem-write authority or broad filesystem plugin access;
- credential lookup, token refresh, keychain mutation, or secret persistence;
- live network request, live GitHub call, real `git clone` / `fetch` / `push` / `ls-remote`;
- remote repository administration;
- DEMO-1 readiness or acceptance claim.

## 4. Host runtime and CLI boundary

Path B commits the product architecture to the Tauri 2 host-runtime family described by [DEC-OS-001 Windows and Linux Desktop Target](dec-os-001-windows-linux-desktop-target.md): Linux WebKitGTK or Windows WebView2.

This document authorizes repository source changes that prepare a Tauri entrypoint. It does not assert that the current host has the WebKitGTK/WebView2 runtime or the Tauri CLI installed. Ralph may add scripts that are fail-closed or preparation-only, but actual user-observed desktop launch evidence remains a separate user-executed gate.

## 5. First authorized commit shape

The first Ralph-executable implementation row seeded from this authorization shall be:

- Task ID: `MB-DESKTOP-D3-ENTRYPOINT-T1`
- Primary files:
  - create or update `apps/desktop/src/main.rs`;
  - update `apps/desktop/Cargo.toml` for the minimal authorized Tauri 2 dependency set;
  - create or update `apps/desktop/build.rs` only if required by Tauri 2;
  - preserve existing `apps/desktop/tests/ui_shell_launch_health.rs` and `apps/desktop/tests/desktop_tauri_config.rs` expectations.
- RED / validation-first command:
  - first add a focused test or compile gate that fails for the missing binary entrypoint or missing Tauri wiring;
  - then run the focused Rust desktop tests and `cargo check -p eduops_desktop` or the closest project-supported equivalent.
- GREEN boundary:
  - `query_session_capabilities` remains the only authorized IPC command;
  - the entrypoint compiles or reaches the documented fail-closed host-runtime boundary;
  - no updater, publish, shell-write, filesystem-write, credential, remote, network, installer, or DEMO-1 behavior is introduced.

## 6. Npm script authorization boundary

The following script intent is authorized for a later D2 row after the binary entrypoint row is prepared or explicitly selected by Ralph:

- `desktop:prepare`: run the existing desktop UI build preparation command;
- `desktop:smoke`: run the existing dry-run smoke template or its authorized successor;
- `desktop:dev` / `desktop:build`: may be added only with clear Tauri CLI prerequisite wording and fail-closed behavior if the CLI or host runtime is absent.

Ralph shall not run a real desktop launch as proof of user-observed evidence. Real launch, screenshot, screen recording, and interactive accessibility evidence remain user-executed gate actions.

## 7. Non-claim list

This authorization does not claim or authorize:

- real user-observed desktop launch evidence;
- screenshot or screen-recording capture;
- end-to-end interactive accessibility audit on a real desktop window;
- installer publication or distribution readiness;
- DEMO-1 acceptance;
- live external action, network call, credential resolution, remote action, repository administration, submission/provisioning state promotion, or evaluation-result authority.

Any evidence generated by the first path-B increment shall be labeled as local build / compile / fixture evidence unless a later user-executed gate supplies real desktop evidence.

## 8. Ralph resume rule

When this authorization record is present and linked from `ralph.md`, Ralph may supersede the stop condition `EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-DEFERRED` and seed path-B rows under the following order:

1. `MB-DESKTOP-PATH-B-AUTH-PREP` — re-read this authorization record, the deferred decision specification, desktop-app development plan, DEC-OS-001, process topology and IPC contract, module/package layout, current `apps/desktop` files, and Git state; confirm the working tree is clean and no live/external boundary is crossed.
2. `MB-DESKTOP-D3-ENTRYPOINT-T1` — add the minimal test-first Tauri 2 binary entrypoint and `query_session_capabilities` command wiring under the scope in §5.
3. `MB-DESKTOP-D3-ENTRYPOINT-GATE` — record constrained evidence for the first path-B entrypoint increment.
4. `QUEUE-REFILL-PREP-POST-MB-DESKTOP-D3-ENTRYPOINT` — classify D2 scripts, D6 user-observed launch gate, and any additional IPC commands under the same non-claim boundary.

Ralph shall stop rather than proceed if satisfying the next row would require live external action, credential use, remote mutation, installer publication, destructive Git, host package installation, or a DEMO-1 claim.

## 9. Relationship to superseded deferred decision

The deferred specification remains useful as the rationale and trade-off analysis for path A vs. path B. Its default behavior no longer blocks the first path-B increment because this authorization record satisfies the user / product-owner authority condition. The deferred document is superseded only for the narrow scope recorded here; any broader desktop capability remains gated by its own controlled record or user-executed evidence gate.
