---
title: DEC-OS-001 Windows and Linux Desktop Target
document_id: EDUOPS-DEC-OS-001
version: 0.1.0
status: accepted
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  updates:
    - EDUOPS-NFR-001
    - EDUOPS-CON-001
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
---

# DEC-OS-001 Windows and Linux Desktop Target

## 1. Decision

EduOps shall target Windows and Linux desktop in the current product baseline.

The product remains desktop-only. Web application delivery, mobile application delivery, and LMS integration remain outside the current baseline.

## 2. Platform interpretation

Windows evidence shall record:

- Windows version;
- WebView2 runtime details;
- Rust toolchain;
- Node/npm or pnpm version;
- Tauri version when the runtime shell is present.

Linux evidence shall record:

- distribution and version;
- display/session type such as X11 or Wayland;
- Tauri-supported webview runtime details;
- Rust toolchain;
- Node/npm or pnpm version;
- Tauri version when the runtime shell is present.

## 3. M1A gate consequence

`GATE-UI-SHELL-DEMO-SLICE-A` may be closed by either a controlled Windows desktop capture or a controlled Linux desktop capture when all UI shell test cards pass and the evidence package records:

```text
live_external_action=false
external_call_made=false
github_mutation_made=false
remote.origin.url=<none>
desktop_capture_environment=<recorded>
platform_webview_runtime=<recorded>
reviewer_owner=<recorded>
ui_screenshot_or_recording=<linked>
```

Headless Linux command output alone is not sufficient. The gate still requires an observed desktop shell launch/capture.

## 4. Rationale

The development host and CI/dev workflows already exercise Linux-local fixture behavior. Making Linux a first-class desktop target reduces the need to block M1A on Windows-only capture while preserving evidence quality through platform-runtime capture requirements.

## 5. Superseded and revised decisions

- `EDUOPS-DEC-005` is revised by this decision. The former Windows-only target is superseded by the Windows/Linux desktop target.
- `EDUOPS-DEC-047` is revised by this decision for desktop shell and packaging scope. The beta stack remains Tauri 2/Rust/TypeScript/local-first, with Windows WebView2 evidence and Linux webview/runtime evidence.
- `EDUOPS-DEC-009` is closed for the initial OS target by this decision and remains open only for exact supported Windows versions and Linux distributions/session types.

## 6. Risk controls

- Cross-platform packaging increases the OS/runtime matrix and shall be tracked in the risk register.
- Platform-specific webview runtime differences shall be captured in the evidence package.
- The product remains desktop-only, so broad web/mobile scope expansion is not implied.
