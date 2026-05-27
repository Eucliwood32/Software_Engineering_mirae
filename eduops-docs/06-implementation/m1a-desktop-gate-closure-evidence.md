---
title: M1A Desktop Gate Closure Evidence
document_id: EDUOPS-M1A-DESKTOP-GATE-CLOSURE-EVIDENCE
version: 0.1.0
status: accepted
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
    - EDUOPS-M1A-LOCAL-UI-SHELL-PREREQUISITE-EVIDENCE
    - EDUOPS-M1A-DESKTOP-GATE-CLOSURE-RUNBOOK
---

# M1A Desktop Gate Closure Evidence

## 1. Decision

`GATE-UI-SHELL-DEMO-SLICE-A` is accepted for the Linux desktop evidence package below.

```text
gate=GATE-UI-SHELL-DEMO-SLICE-A
status=accepted
platform=linux
detected_host_platform=linux
platform_match=true
reviewer_owner=Changbeom Choi
live_external_action=false
external_call_made=false
github_mutation_made=false
remote.origin.url=<none>
headless_linux_command_output_alone_is_sufficient=false
```

The accepted package is a `candidate-for-review` package whose runtime media was visually inspected. The gate closure decision relies on both script validation and visual review of the supplied desktop screenshot.

## 2. Evidence package

Runtime evidence is generated under the ignored build evidence tree and is not committed as source-controlled content. The controlled record is this document.

```text
evidence_root=build/evidence/ui-shell-slice-a/desktop-local-linux-20260515-012840
run_summary=build/evidence/ui-shell-slice-a/desktop-local-linux-20260515-012840/run-summary.json
manifest=build/evidence/ui-shell-slice-a/desktop-local-linux-20260515-012840/manifest.sha256
ui_screenshot_or_recording=build/evidence/ui-shell-slice-a/desktop-local-linux-20260515-012840/capture/evidence.png
screenshot_sha256=ce99cd76824ad7c1060539338da195054be89a8d019525c905e4115e37eb1df0
screenshot_bytes=78652
source_upload=build/evidence/ui-shell-slice-a/evidence.png
source_upload_sha256=ce99cd76824ad7c1060539338da195054be89a8d019525c905e4115e37eb1df0
```

`run-summary.json` records:

```text
status=candidate-for-review
tc_ui_shell_001=true
tc_ui_shell_002=true
tc_ui_shell_003=true
platform_webview_runtime=libwebkit2gtk-4.1-0 2.52.3-0ubuntu0.24.04.1
platform_webview_runtime_accepted=true
human_attestation_visible_ui_fields=true
required_human_evidence_remaining=[]
```

## 3. Desktop capture environment

The evidence package recorded the capture host and desktop runtime metadata.

```text
python_platform=Linux-6.17.0-1017-oem-x86_64-with-glibc2.39
machine=x86_64
git_head=e34b517
git_status=## main
remote_origin_url=<none>
cargo_version=cargo 1.95.0 (f2d3ce0bd 2026-03-21)
node_version=v22.22.2
npm_version=10.9.7
xdg_session_type=x11
desktop_session=ubuntu
display=:10.0
wayland_display=none
os=Ubuntu 24.04.4 LTS
webkit_runtime_probe=libwebkit2gtk-4.1.so.0 present; libwebkitgtk-6.0.so.4 present
```

The human-provided runtime string used for gate review is:

```text
libwebkit2gtk-4.1-0 2.52.3-0ubuntu0.24.04.1
```

## 4. Visual review result

Visual inspection of `evidence.png` confirmed that the screenshot displays the EduOps desktop UI shell and the required fields:

```text
EduOps Desktop
ui_shell=tauri2-webview2-shell
adapter_modes=fake,local
live_external_action=false
direct_ui_filesystem_access=false
direct_ui_git_access=false
network_request_enabled=false
Create local course
course_id=course_eduops-m0_2026-spring
audit_event_id=audit_course_create_req-ui-slice-a-001
evidence_path=build/evidence/slice-a/local-skeleton
fake_git_status=clean
fake_git_checkpoint=local_checkpoint
github_mutation_made=false
remote.origin.url=<none>
```

Visual inspection also found no unrelated sensitive content in the accepted screenshot.

## 5. Validation evidence

The package validation commands passed:

```text
cargo fmt --all --check: PASS
npm run m0:check: PASS
cargo test --workspace: PASS
python -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py tests/contract/m1_slice_a/test_m1_slice_a_fixture_runner.py tests/contract/m1a_ui_shell/test_m1a_ui_shell_static.py -q: 9 passed
npm --prefix apps/desktop-ui run build: PASS
```

The local repository state recorded by the evidence package was:

```text
git_head=e34b517
remote_origin_url=<none>
```

## 6. Blocker review after closure

No M1A gate blocker remains for starting the next milestone. `GATE-UI-SHELL-DEMO-SLICE-A` has controlled Linux desktop evidence and may be treated as closed for Ralph milestone sequencing.

The next milestone is M2 configuration and credential-reference services. No M1A blocker remains for `M2-PREP`, but M2 implementation is not yet broadly unblocked. The first M2 checkpoint must select or narrow the credential implementation approach enough for a local fixture implementation. Known M2 risks are not M1A blockers, but they should be handled before or during M2 implementation:

1. Credential implementation must remain reference-only; raw secrets must not be persisted in config, logs, manifests, diagnostics, or Git-tracked outputs.
2. Configuration precedence and effective-hash behavior must be fixture-tested before broad feature work.
3. Offline/local mode must continue to produce zero network adapter calls.
4. Repository remains local-only with `remote.origin.url=<none>`; no push, GitHub repository mutation, deployment, or live external action is authorized.
5. M2 should begin with a Prepare checkpoint that re-reads `configuration-contract.md`, `credential-storage-contract.md`, `configuration-fixture-plan.md`, `internal-api-contract.md`, and `ralph.md` before adding behavior.

## 7. Closure statement

`GATE-UI-SHELL-DEMO-SLICE-A` is closed for the Linux desktop evidence package above. Ralph may proceed to M2 after this closure record is committed and the working tree is clean.
