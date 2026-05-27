---
title: M1A Local UI Shell Prerequisite Evidence
document_id: EDUOPS-M1A-LOCAL-UI-SHELL-PREREQUISITE-EVIDENCE
version: 0.1.0
status: accepted-local-prerequisite
date: 2026-05-14
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-INTERNAL-API
    - EDUOPS-M1-SLICE-A-LOCAL-SKELETON-EVIDENCE
---

# M1A Local UI Shell Prerequisite Evidence

## 1. Decision

The Linux-local prerequisites for M1A were accepted as an intermediate checkpoint. The full `GATE-UI-SHELL-DEMO-SLICE-A` is now closed by controlled Linux desktop evidence recorded in [M1A desktop gate closure evidence](m1a-desktop-gate-closure-evidence.md).

```text
local_prerequisite_status=accepted
gate=GATE-UI-SHELL-DEMO-SLICE-A
full_gate_status=accepted_by_linux_desktop_capture
live_external_action=false
external_call_made=false
github_mutation_made=false
remote.origin.url=<none>
```

## 2. Accepted local evidence

### TC-UI-SHELL-001 local prerequisite

Implemented by:

```text
apps/desktop/tests/ui_shell_launch_health.rs
apps/desktop/src/lib.rs
```

Evidence:

```text
cargo test -p eduops_desktop --test ui_shell_launch_health -- --nocapture: PASS
```

Accepted local properties:

- backend health/capability query exists as `query_session_capabilities`;
- request and result use the controlled `RequestEnvelope` and `ResultEnvelope` types;
- response records `desktop_shell=true`;
- response records `api_version=eduops.api/0.1`;
- response records `ui_shell=tauri2-webview2-shell`;
- response records `adapter_modes=fake,local`;
- response records `live_actions_enabled=false`;
- response records no direct UI filesystem, Git, or network access.

### TC-UI-SHELL-002 local prerequisite

Implemented by:

```text
apps/desktop-ui/src/main.ts
apps/desktop-ui/scripts/build.mjs
tests/contract/m1a_ui_shell/test_m1a_ui_shell_static.py
```

Evidence:

```text
python3 -m pytest tests/contract/m1a_ui_shell/test_m1a_ui_shell_static.py -q: 2 passed
npm --prefix apps/desktop-ui run typecheck: PASS
npm --prefix apps/desktop-ui run build: PASS
```

Accepted local properties:

- static UI build renders product and shell identity;
- static UI build renders `adapter_modes=fake,local`;
- static UI build renders `live_external_action=false`;
- static UI build renders `direct_ui_filesystem_access=false`;
- static UI build renders `direct_ui_git_access=false`;
- static UI build renders `network_request_enabled=false`;
- static UI build renders the `Create local course` action label;
- static UI build renders the SLICE-A fixture course ID, audit event ID, evidence path, fake Git status/checkpoint, GitHub mutation flag, and absent remote origin.

## 3. Full gate closure

The full M1A gate evidence required by `docs/03-verification-validation/ui-shell-demo-test-cards.md` has been returned and reviewed. See [M1A desktop gate closure evidence](m1a-desktop-gate-closure-evidence.md).

```text
closure_status=accepted
platform=linux
evidence_root=build/evidence/ui-shell-slice-a/desktop-local-linux-20260515-012840
screenshot_sha256=ce99cd76824ad7c1060539338da195054be89a8d019525c905e4115e37eb1df0
reviewer_owner=Changbeom Choi
```

The earlier blocker is closed; this document remains the prerequisite checkpoint record.

## 4. Regression validation

The local gate was checked with:

```text
cargo fmt --all --check
npm run m0:check
cargo test --workspace
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py tests/contract/m1_slice_a/test_m1_slice_a_fixture_runner.py tests/contract/m1a_ui_shell/test_m1a_ui_shell_static.py -q
git diff --check
Markdown local links: PASS
JSON parse: PASS
```

## 5. Next action

Proceed to M2 Prepare after this closure record is committed. The next safe action is to re-read the M2 controlled anchors for configuration and credential-reference services before adding behavior.
