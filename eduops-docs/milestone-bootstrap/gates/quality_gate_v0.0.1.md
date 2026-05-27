---
title: EduOps Milestone Bootstrap Quality Gate
version: v0.0.1
status: draft
profile: develop
---

# Quality Gate v0.0.1

## Local checks

| Check | Command / method | Required result |
|---|---|---|
| Git state | `git status --short --branch` | Dirty state classified; no unrelated dirty files before execution |
| Diff whitespace | `git diff --check` | Pass |
| Bootstrap artifact parse | Python parse of JSON/YAML under `docs/milestone-bootstrap/` | Pass |
| Markdown local links | Python local-link checker over bootstrap docs | Pass |
| Existing repo M0 gate | `npm run m0:check` | Recommended before code/Ralph execution; not required for docs-only bootstrap if time-bounded |
| Rust workspace | `cargo test --workspace` | Required for behavior tasks |
| Focused TDD | Task-specific focused RED/GREEN command | Required before behavior commit |
| Secret boundary | No credential lookup, no raw token storage, no live connector | Pass |

## Human-gated actions

The following are blocked unless a separate explicit human gate is given: `git push`, PR/release/publication, live GitHub/network actions, credential/keychain mutation, destructive Git/history operations, installer publication, production/student data mutation.

## Gate verdict for v0.0.1

Local advisory verdict: `develop_bootstrap_ready_for_local_ralph_handoff` if artifact parse/link validation passes and `ralph.md` handoff is merged. Formal Hisys verdict is recorded separately in `hisys/result_v0.0.1.md`.
