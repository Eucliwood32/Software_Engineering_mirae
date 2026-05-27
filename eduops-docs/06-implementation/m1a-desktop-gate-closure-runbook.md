---
title: M1A Desktop Gate Closure Runbook
document_id: EDUOPS-M1A-DESKTOP-GATE-CLOSURE-RUNBOOK
version: 0.2.0
status: ready-for-user-execution
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
    - EDUOPS-M1A-LOCAL-UI-SHELL-PREREQUISITE-EVIDENCE
---

# M1A Desktop Gate Closure Runbook

## 1. Gate target

This runbook defines the user-executed evidence capture required to close:

```text
GATE-UI-SHELL-DEMO-SLICE-A
```

The product target is now Windows and Linux desktop. A controlled Windows capture or a controlled Linux desktop capture may close the gate when all test-card evidence fields pass.

## 2. Closure rule

The gate may be marked closed only when all required evidence below exists and is reviewed:

```text
TC-UI-SHELL-001=true
TC-UI-SHELL-002=true
TC-UI-SHELL-003=true
desktop_capture_environment=<recorded>
platform=<windows|linux>
platform_webview_runtime=<recorded>
reviewer_owner=<recorded>
live_external_action=false
external_call_made=false
github_mutation_made=false
remote.origin.url=<none>
ui_screenshot_or_recording=<linked>
run-summary.json=<validated>
```

Windows evidence shall record WebView2 runtime details. Linux evidence shall record distribution, display/session type, and the Tauri-supported webview runtime details.

## 3. User-executed capture procedure

Action requires user execution.

Reason: Ralph/Hermes may run local checks here, but a real desktop gate requires an observed desktop shell launch/capture in a named Windows or Linux desktop environment.

Risk: marking the gate closed without real desktop capture would falsely claim a demonstrable desktop UI.

### 3.1 Script-first capture command

Run from the EduOps repo root on the capture host. The script automates repository/toolchain metadata, validation commands, platform runtime records, static UI build, Firefox/desktop-browser launch, `run-summary.json`, and `manifest.sha256` generation. The only non-automated input is the human attestation that the captured visible desktop shell contains the required UI fields.

Linux example with automatic screenshot capture:

```bash
python3 scripts/m1a_desktop_gate_capture.py \
  --reviewer-owner "<name>" \
  --platform linux \
  --platform-webview-runtime "<webkitgtk-or-tauri-linux-webview-runtime>" \
  --attest-visible-ui-fields \
  --open-ui \
  --capture-delay-seconds 5 \
  --auto-capture
```

Windows PowerShell example with automatic screenshot capture:

```powershell
python scripts/m1a_desktop_gate_capture.py `
  --reviewer-owner "<name>" `
  --platform windows `
  --platform-webview-runtime "<WebView2 Runtime version>" `
  --attest-visible-ui-fields `
  --open-ui `
  --capture-delay-seconds 5 `
  --auto-capture
```

Manual capture fallback:

```bash
python3 scripts/m1a_desktop_gate_capture.py \
  --reviewer-owner "<name>" \
  --platform linux \
  --platform-webview-runtime "<webkitgtk-or-tauri-linux-webview-runtime>" \
  --attest-visible-ui-fields \
  --capture-file "<path-to-screenshot-or-recording>"
```

On Linux, `--open-ui` now runs the equivalent of:

```bash
npm --prefix apps/desktop-ui run build
firefox "$(pwd)/apps/desktop-ui/dist/index.html" &
```

If Firefox is unavailable, the script falls back to `xdg-open`. On Linux, `--auto-capture` uses the first available screenshot command from: `gnome-screenshot`, `grim`, `spectacle`, ImageMagick `import`, `scrot`, or `maim`. On Windows, it uses PowerShell with `System.Windows.Forms` and `System.Drawing`. Because `--auto-capture` captures the visible desktop, close or obscure unrelated sensitive windows before running it. Use `--open-ui --capture-delay-seconds 5` to open the static EduOps UI and give the browser time to come forward before capture; increase the delay if the screenshot still captures the terminal instead of the UI.

Optional helper: add `--open-ui` to build and open `apps/desktop-ui/dist/index.html` before automatic capture so the user can capture the visible UI surface.

The script exits with status `0` only when the evidence package is `candidate-for-review`. If automatic capture fails, screenshot/recording, explicit non-placeholder runtime detail, matching platform, or `--attest-visible-ui-fields` confirmation is missing, it either fails argument validation or writes a partial evidence package and exits non-zero instead of fabricating closure. `candidate-for-review` is not gate closure; Ralph still reviews the media, runtime, validation logs, and owner confirmation before closing the gate.

### 3.2 Manual fallback commands

If the script cannot run on the capture host, execute the equivalent commands manually and fill `docs/03-verification-validation/m1a-gate-closure-template.json`.

### 3.3 Linux desktop capture additions

On Linux, also record:

```bash
{
  echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE:-unknown}"
  echo "DESKTOP_SESSION=${DESKTOP_SESSION:-unknown}"
  echo "WAYLAND_DISPLAY=${WAYLAND_DISPLAY:-none}"
  echo "DISPLAY=${DISPLAY:-none}"
  lsb_release -a 2>/dev/null || cat /etc/os-release 2>/dev/null || true
  ldconfig -p 2>/dev/null | grep -Ei 'webkit2gtk|gtk|javascriptcore' || true
} > "$EVIDENCE_ROOT/linux-desktop-runtime.txt"
```

Launch the desktop shell or controlled smoke harness in the visible Linux desktop session. Capture a screenshot or short screen recording showing:

```text
EduOps Desktop
tauri2-webview2-shell or cross-platform Tauri shell identity
adapter_modes=fake,local
live_external_action=false
Create local course
course_id=course_eduops-m0_2026-spring
fake_git_status=clean
```

Save the capture under `$EVIDENCE_ROOT`.

### 3.4 Windows desktop capture additions

On Windows PowerShell, record:

```powershell
$EvidenceRoot = "build/evidence/ui-shell-slice-a/desktop-local-$(Get-Date -Format yyyyMMdd-HHmmss)"
New-Item -ItemType Directory -Force -Path $EvidenceRoot | Out-Null
systeminfo | Out-File "$EvidenceRoot/windows-systeminfo.txt" -Encoding utf8
Get-Command cargo,node,npm | Format-List | Out-File "$EvidenceRoot/toolchain-paths.txt" -Encoding utf8
```

Launch the desktop shell or controlled smoke harness in the visible Windows desktop session. Capture a screenshot or short screen recording showing the same UI fields listed in Section 3.3. Save the capture under `$EvidenceRoot`.

## 4. Gate summary template

After capture, write `run-summary.json` under the evidence root. Use `docs/03-verification-validation/m1a-gate-closure-template.json` as the template and replace all placeholder fields. The final summary shall set:

```text
status=candidate-for-review
platform=<windows|linux>
tc_ui_shell_001=true
tc_ui_shell_002=true
tc_ui_shell_003=true
live_external_action=false
external_call_made=false
github_mutation_made=false
remote_origin_url=<none>
```

## 5. Ralph closure action after user returns evidence

After the user provides the desktop capture evidence, Ralph shall:

1. prefer evidence generated by `scripts/m1a_desktop_gate_capture.py`;

1. verify the supplied `run-summary.json` fields;
2. verify that the linked screenshot or recording path exists or is attached;
3. verify that validation logs show pass results;
4. verify the platform runtime evidence: WebView2 for Windows, or Linux distribution/display/webview runtime details for Linux;
5. create a final `m1a-ui-shell-gate-evidence.md` document;
6. update `implementation-milestones.md` from local-prerequisite accepted to full M1A gate accepted;
7. update `ralph.md` to mark `GATE-UI-SHELL-DEMO-SLICE-A` closed and set next task to `M2-PREP`;
8. run repo validation and commit a focused `docs:` gate-closure commit.

## 6. Current gate status

```text
status=awaiting_desktop_capture
safe_next_action=user_run_windows_or_linux_desktop_capture
ralph_may_close_gate_without_capture=false
ralph_may_proceed_to_m2_without_user_override=false
```
