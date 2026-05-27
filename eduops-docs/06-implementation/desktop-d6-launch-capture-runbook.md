---
title: Desktop D6 User-Observed Launch Capture Runbook
document_id: EDUOPS-DESKTOP-D6-LAUNCH-CAPTURE-RUNBOOK
version: 0.1.0
status: ready-for-user-execution
date: 2026-05-20
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-DESKTOP-D6-LAUNCH-EVIDENCE-SHAPE-SPECIFICATION
    - EDUOPS-DESKTOP-ENTRYPOINT-DEPENDENCY-AUTHORIZED-DECISION
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
    - EDUOPS-DEC-OS-001
    - EDUOPS-M1A-DESKTOP-GATE-CLOSURE-RUNBOOK
    - EDUOPS-M1A-DESKTOP-GATE-CLOSURE-EVIDENCE
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
---

# Desktop D6 User-Observed Launch Capture Runbook

## 0. Document scope

This runbook documents the **user-executed** capture procedure required to produce a controlled D6 user-observed launch evidence package against the schema defined in [Desktop D6 User-Observed Launch Evidence Shape Specification](../02-design-planning/desktop-d6-launch-evidence-shape-specification.md).

This document does **not**:

- launch a desktop window;
- capture screenshots or screen recordings;
- install WebKitGTK, WebView2, or the Tauri CLI;
- invoke `cargo tauri dev` or `cargo tauri build`;
- close the D6 user-observed launch gate;
- claim DEMO-1 readiness or acceptance;
- supersede or relax any non-claim recorded in the D6 evidence-shape spec §7 or the [Desktop Entrypoint Dependency Adoption Authorized Decision](../02-design-planning/desktop-entrypoint-dependency-adoption-authorized-decision.md) §7.

The runbook authoring itself is a docs/control increment with no source-code change. Ralph does not run any of the commands listed below; the user runs them on a host that satisfies the prerequisites in §2.

## 1. Gate target

```text
GATE-MB-DESKTOP-D6-USER-OBSERVED-LAUNCH
```

The desktop-app development plan §6 D6 user-observed launch gate is closed only when a returned evidence package satisfies the §5 acceptance predicate in the D6 evidence-shape spec **and** Ralph completes the twelve verification steps in spec §9.

## 2. User-executed prerequisites

The capture host must satisfy:

- Linux: a Tauri-supported WebKitGTK runtime per [DEC-OS-001](../02-design-planning/dec-os-001-windows-linux-desktop-target.md) §2 (`libwebkit2gtk-4.1-0` or the documented successor) installed and visible in `ldconfig -p`.
- Windows: WebView2 Runtime per DEC-OS-001 §2 installed and reachable by `tauri`.
- Either host: a Tauri CLI install (system install via `cargo install tauri-cli`, package-manager install, or a pinned dev dependency) such that `cargo tauri --version` exits zero.
- A Rust toolchain compatible with the Tauri 2 minor version pinned in `Cargo.lock`.
- Node.js + npm versions matching the repository `package.json` engine expectations (see existing `desktop-smoke-template.mjs` output for the verified versions).
- A clean Git working tree on `main` (or a controlled topic branch) with `remote.origin.url=<none>` for the first D6 increment.

If any prerequisite is missing, **do not** force-launch with a workaround. Stop and record the missing prerequisite in the evidence package's `host_runtime_pkgconfig_status="missing"` field and request the runtime install per DEC-OS-001 §2 before proceeding.

## 3. Capture procedure

Action requires user execution. Ralph/Hermes may run local docs/control checks here, but the gate requires an observed desktop shell launch/capture in a named Windows or Linux desktop environment.

Risk: marking the gate closed without real desktop capture would falsely claim a demonstrable desktop UI launch.

### 3.1 Prepare the evidence root

```bash
cd /home/cbchoi/workspaces/develop/repos/eduops
EVIDENCE_ROOT="build/evidence/desktop-d6-launch/desktop-local-$(uname -s | tr '[:upper:]' '[:lower:]')-$(date -u +%Y%m%d-%H%M%S)"
mkdir -p "$EVIDENCE_ROOT/capture" "$EVIDENCE_ROOT/platform" "$EVIDENCE_ROOT/attestation"
echo "$EVIDENCE_ROOT"
```

The directory layout shall match D6 spec §3.1. The `build/evidence/` tree is not Git-tracked; the controlled record committed to Git is the follow-up `desktop-d6-launch-gate-evidence.md` document Ralph authors after verifying the returned package (§5 of this runbook).

Windows PowerShell equivalent:

```powershell
cd C:\path\to\eduops
$ts = (Get-Date -Format yyyyMMdd-HHmmss)
$EvidenceRoot = "build/evidence/desktop-d6-launch/desktop-local-windows-$ts"
New-Item -ItemType Directory -Force -Path "$EvidenceRoot/capture", "$EvidenceRoot/platform", "$EvidenceRoot/attestation" | Out-Null
$EvidenceRoot
```

### 3.2 Run the launch command

The authorized commands per the [Desktop Entrypoint Dependency Adoption Authorized Decision](../02-design-planning/desktop-entrypoint-dependency-adoption-authorized-decision.md) §6 are the two npm scripts:

```bash
npm run desktop:dev
```

or

```bash
npm run desktop:build
```

Both scripts route through the fail-closed preflight wrappers at `scripts/desktop-dev-preflight.mjs` and `scripts/desktop-build-preflight.mjs`. If the preflight fails closed with a `Tauri CLI not detected` / `DEC-OS-001` message, install the prerequisite per §2 of this runbook before retrying. Do **not** edit the wrappers to bypass the preflight.

The exact command string used shall be recorded verbatim in the `run-summary.json` `app_command_used` field (D6 spec §3.2). Do not concatenate or wrap the command; if you ran it inside a shell history, copy the literal string.

### 3.3 Capture the launched window

Once the EduOps desktop window is visible:

- **Screenshot only:** capture the active desktop region containing the EduOps window. Save as `$EVIDENCE_ROOT/capture/evidence.png` (or `.jpg`). Strip EXIF/metadata per D6 spec §6 rule 8 using `exiftool -all= "$EVIDENCE_ROOT/capture/evidence.png"` (Linux) or an equivalent tool on Windows.
- **Screen recording:** capture a short recording (≤30 seconds) showing the same visible UI fields. Save as `$EVIDENCE_ROOT/capture/evidence.mp4` or `.webm`. Strip embedded device metadata.
- **Screenshot + recording:** capture both; record `capture_artifact_kind="screenshot-and-recording"` and a comma-separated `capture_artifact_sha256` value pairing the two file hashes.

The capture image content shall display the visible UI fields listed in D6 spec §4 (the same list M1A used so D6 stays consistent with the M1A baseline and the desktop-app plan §6 D5 home render). Before saving, visually verify there is no unrelated sensitive on-screen content (chat windows, password managers, secrets, other repositories).

Compute the SHA-256 of the saved artifact:

```bash
sha256sum "$EVIDENCE_ROOT/capture/evidence.png"
```

Windows PowerShell:

```powershell
Get-FileHash "$EvidenceRoot/capture/evidence.png" -Algorithm SHA256
```

### 3.4 Record platform runtime metadata

Linux:

```bash
{
  echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-unknown}"
  echo "DESKTOP_SESSION=${DESKTOP_SESSION:-unknown}"
  echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-none}"
  echo "DISPLAY=${DISPLAY:-none}"
  lsb_release -a 2>/dev/null || cat /etc/os-release 2>/dev/null || true
  ldconfig -p 2>/dev/null | grep -Ei 'webkit2gtk|gtk|javascriptcore' || true
} > "$EVIDENCE_ROOT/platform/desktop-environment.txt"

{
  pkg-config --modversion webkit2gtk-4.1 2>/dev/null && echo "host_runtime_pkgconfig_status=present" \
    || echo "host_runtime_pkgconfig_status=missing"
} > "$EVIDENCE_ROOT/platform/platform-runtime.txt"

{
  cargo --version 2>&1 || true
  node --version 2>&1 || true
  npm --version 2>&1 || true
  cargo tauri --version 2>&1 || echo "cargo-tauri=<not-installed>"
} > "$EVIDENCE_ROOT/platform/toolchain-paths.txt"
```

Windows PowerShell:

```powershell
@(
  "WebView2_Runtime=" + (Get-ItemProperty -Path 'HKLM:\SOFTWARE\WOW6432Node\Microsoft\EdgeUpdate\Clients\{F3017226-FE2A-4295-8BDF-00C3A9A7E4C5}' -ErrorAction SilentlyContinue).pv,
  ("systeminfo " + (systeminfo | Out-String))
) | Out-File "$EvidenceRoot/platform/platform-runtime.txt" -Encoding utf8

(Get-Command cargo, node, npm, cargo-tauri -ErrorAction SilentlyContinue | Format-List) `
  | Out-File "$EvidenceRoot/platform/toolchain-paths.txt" -Encoding utf8

systeminfo | Out-File "$EvidenceRoot/platform/desktop-environment.txt" -Encoding utf8
```

### 3.5 Populate the placeholder template

Start from the controlled placeholder template at [`desktop-d6-launch-evidence-template.json`](../03-verification-validation/desktop-d6-launch-evidence-template.json):

```bash
cp docs/03-verification-validation/desktop-d6-launch-evidence-template.json \
   "$EVIDENCE_ROOT/run-summary.json"
```

Then replace every `<placeholder>` value in `$EVIDENCE_ROOT/run-summary.json` with the captured value. Keep the four hardcoded `false` literals (`external_call_made`, `github_mutation_made`, `live_external_action`, `network_request_enabled`) and the `<none>` literal for `remote_origin_url` unchanged. Set `status="accepted"` only when every condition in the D6 spec §5 predicate holds; otherwise keep `status="candidate-for-review"`.

Suggested field-by-field source mapping:

- `git_head` ← `git rev-parse HEAD`
- `git_branch` ← `git rev-parse --abbrev-ref HEAD`
- `os_platform` ← Linux `uname -s` lowercased / Windows `process.platform`
- `arch` ← `uname -m` / Windows `$env:PROCESSOR_ARCHITECTURE`
- `node_version` ← `node --version`
- `npm_version` ← `npm --version`
- `os` ← Linux `lsb_release -d -s` / Windows `(Get-CimInstance Win32_OperatingSystem).Caption`
- `xdg_session_type` ← Linux `$XDG_SESSION_TYPE` / Windows `<not-applicable>`
- `desktop_capture_environment` ← `linux-x11` / `linux-wayland` / `windows-desktop`
- `platform` ← `linux` / `windows`
- `platform_match` ← `true` only when `os_platform` matches `platform`'s OS family
- `platform_webview_runtime` ← non-placeholder string from `platform/platform-runtime.txt` per DEC-OS-001 §2
- `platform_webview_runtime_accepted` ← `true` only after reviewer attests the version is supported
- `host_runtime_pkgconfig_status` ← `present` / `missing` from `platform/platform-runtime.txt`
- `rust_toolchain` ← `cargo --version`
- `tauri_cli_version` ← `cargo tauri --version` or `<not-installed>` (literal)
- `tauri_version` ← resolved Tauri 2 entry from `Cargo.lock`
- `app_version` ← `apps/desktop/Cargo.toml` `version` field
- `app_command_used` ← `npm run desktop:dev` or `npm run desktop:build` (verbatim)
- `audit_event_id` ← `audit_desktop_d6_launch_<YYYYMMDD-HHMMSS>` matching the evidence-root timestamp
- `capture_artifact_kind` ← `screenshot` / `screen-recording` / `screenshot-and-recording`
- `capture_artifact_path` ← repo-relative path under `evidence_root`
- `capture_artifact_sha256` ← SHA-256 hex (or `<screenshot-sha256>,<recording-sha256>`)
- `tc_ui_shell_001..003` ← outcomes from [UI Shell Demonstration Test Cards](../03-verification-validation/ui-shell-demo-test-cards.md) under the same capture
- `ipc_health` ← `ok` only when the running app reported the M1A `query_session_capabilities` success envelope
- `human_attestation_visible_ui_fields` ← `true` only after reviewer review per §3.6
- `reviewer_owner` ← reviewer display name (never an email; D6 spec §6 rule 5)
- `required_human_evidence_remaining` ← empty array `[]` when `status="accepted"`; otherwise list of missing items

Apply the D6 spec §6 redaction rules to every text-bearing value before saving the file. Specifically: no raw GitHub PAT prefix (`ghp_` / `github_pat_`), no URL credential form (`://user:secret@host`), no raw `https://` / `http://` / `git@` URL in `run-summary.json`, no SSH PEM blob headers, no raw email substring, no raw long-digit identifier in non-numeric semantic fields, and no raw student identifier.

### 3.6 Write the reviewer attestation

Open `$EVIDENCE_ROOT/attestation/reviewer-attestation.txt` and fill it per D6 spec §3.4:

```text
reviewer_owner=<your name>
attestation_date_utc=<YYYY-MM-DDTHH:MM:SSZ>
visible_ui_fields_attested=true
capture_artifact_kind=<screenshot|screen-recording|screenshot-and-recording>
capture_artifact_path=<repo-relative-path>
notes=

[non-claim footer — copy D6 spec §7 block verbatim]
This D6 launch evidence does NOT claim:

- installer publication or distribution readiness;
- DEMO-1 acceptance or DEMO-1 readiness;
- end-to-end interactive accessibility audit with a real screen-reader;
- keyboard navigation simulation across the full app surface;
- live external action, network call, credential resolution, token refresh,
  rotation, or storage modification;
- live GitHub action, real `git clone`/`fetch`/`push`/`ls-remote`;
- remote repository administration, submission/provisioning state promotion,
  or evaluation-result authority;
- additional IPC commands beyond the existing `query_session_capabilities`
  M1A session-capability command (no new IPC surface is opened by D6);
- repository administration, real CSV upload UI, real desktop file-picker UI,
  real reviewer attestation workflow beyond the plain-text attestation file;
- user-managed external-repo boundary actions per `EDUOPS-DEC-064` and
  `EDUOPS-DEC-065`.
```

Set `visible_ui_fields_attested=true` only when every UI field listed in D6 spec §4 is visible in the captured artifact **and** the capture image contains no unrelated sensitive content. If either condition fails, set `visible_ui_fields_attested=false` and the package remains `candidate-for-review`.

### 3.7 Write the manifest

Compute `manifest.sha256` covering every file in the package other than itself:

```bash
( cd "$EVIDENCE_ROOT" && find . -type f ! -name manifest.sha256 -print0 \
  | sort -z \
  | xargs -0 sha256sum \
  > manifest.sha256
)
```

Windows PowerShell:

```powershell
Get-ChildItem -Path $EvidenceRoot -Recurse -File `
  | Where-Object { $_.Name -ne 'manifest.sha256' } `
  | Sort-Object FullName `
  | ForEach-Object { "$((Get-FileHash $_.FullName -Algorithm SHA256).Hash.ToLower())  $($_.FullName.Replace($EvidenceRoot, '').TrimStart('\','/'))" } `
  | Out-File "$EvidenceRoot/manifest.sha256" -Encoding utf8
```

Each manifest line shall be `<hex-sha256>  <repo-relative-path-from-package-root>` per D6 spec §3.3. Order is the byte-sorted package-relative path.

### 3.8 Self-check before handing back to Ralph

Before requesting Ralph closure, the user shall confirm:

- the four hardcoded `false` literals are present verbatim in `run-summary.json`;
- `remote_origin_url` is exactly the literal `<none>`;
- every `<placeholder>` substring has been replaced (search the file for the literal `<placeholder>`);
- the capture artifact path exists, its SHA-256 matches, and EXIF/metadata has been stripped per D6 spec §6 rule 8;
- the attestation file lists `visible_ui_fields_attested=true` (or `false` for a candidate-for-review package);
- the manifest covers every package file other than itself;
- no raw secret, URL credential, repository URL, SSH PEM blob, email, or long-digit identifier appears anywhere in the package per D6 spec §6 rules 1–7.

If any check fails, fix the package before invoking the Ralph closure step in §5.

## 4. Status state machine

The package transitions through three states. Only `accepted` may be handed to Ralph for the §5 closure check; `closed` is recorded only by the follow-up `desktop-d6-launch-gate-evidence.md` document.

```text
candidate-for-review  → accepted  → closed
        (most fields  (predicate  (Ralph-only,
         user-filled,  in D6      after §5
         attestation   spec §5    verification
         pending)      holds)     passes)
```

A package may regress from `accepted` back to `candidate-for-review` if review surfaces a field that needs correction; in that case the timestamped evidence root shall be replaced rather than amended.

## 5. Ralph closure action after user returns evidence

When the user returns a package whose `run-summary.json` is in `status="accepted"`, Ralph shall (per D6 spec §9):

1. verify `run-summary.json` parses and contains every key listed in D6 spec §3.2;
2. verify the `status="accepted"` predicate in D6 spec §5 holds over the parsed values;
3. verify the linked `capture_artifact_path` exists at the package root and its SHA-256 matches `capture_artifact_sha256`;
4. verify `manifest.sha256` covers every file in the package other than itself and each recorded hash matches;
5. verify the redaction rules in D6 spec §6 1–7 against `run-summary.json` and the `*.txt` files;
6. verify the platform runtime evidence per DEC-OS-001 §2;
7. verify the hardcoded no-live booleans and `remote_origin_url=<none>` are present verbatim;
8. verify `app_command_used` is one of the authorized launch commands per D6 spec §3.2;
9. create a `docs/06-implementation/desktop-d6-launch-gate-evidence.md` document modeled on [M1A Desktop Gate Closure Evidence](m1a-desktop-gate-closure-evidence.md);
10. include the D6 spec §7 non-claim block verbatim in the new gate-evidence document;
11. update `ralph.md` to mark the desktop-app development plan §6 D6 gate accepted and continue with the next controlled row;
12. run repository validation (`npm run m0:check` and `git diff --check`) and commit a focused `docs:` gate-closure commit.

Ralph shall not perform any of these steps before the user returns a real captured package. If any step fails, Ralph shall stop and report a user-run command block per `ralph.md` §2 rather than fabricating closure.

## 6. Current gate status

```text
status=awaiting_user_executed_desktop_capture
safe_next_action=user_run_path_b_npm_desktop_dev_or_build_with_capture
ralph_may_close_gate_without_capture=false
ralph_may_proceed_to_demo_1_without_user_override=false
```

## 7. Non-claim summary

This runbook describes only the **shape** of the user-executed flow. Authoring this runbook does not:

- execute a desktop launch;
- capture screenshots or screen recordings;
- install WebKitGTK, WebView2, or the Tauri CLI;
- invoke `cargo tauri dev` / `cargo tauri build`;
- open or close the D6 gate;
- claim DEMO-1 readiness;
- adopt any Cargo dependency or modify any source file;
- authorize publication, installer release, network call, credential resolution, remote action, repository administration, submission-state promotion, or evaluation-result authority;
- authorize any IPC command beyond the existing `query_session_capabilities` boundary.

User-managed external-repo boundary actions remain user-managed per `EDUOPS-DEC-064` and `EDUOPS-DEC-065`.
