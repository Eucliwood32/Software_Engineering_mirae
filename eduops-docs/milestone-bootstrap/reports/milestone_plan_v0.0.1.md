---
title: EduOps Develop Milestone Bootstrap Plan
document_id: EDUOPS-MILESTONE-BOOTSTRAP-PLAN-V0-0-1
version: v0.0.1
status: draft
created: 2026-05-19
owner: develop
profile: develop
---

# EduOps Develop Milestone Bootstrap Plan v0.0.1

## 1. Target and profile

- Target working directory: `/home/cbchoi/workspaces/develop/repos/eduops`
- Detected profile: `develop`
- Selected profile: `develop`
- Git repository: yes, branch `main`
- Remote configured: yes, `origin`; no remote action authorized.

The workspace is already a local develop repository with controlled documents under `docs/`, Rust crates under `crates/`, desktop scaffolding under `apps/`, fixture/evidence conventions, and an existing Ralph control plan. No prior `docs/milestone-bootstrap/` package existed, so this is the initial bootstrap version.

## 2. Evidence inventory

| Evidence class | Observed source |
|---|---|
| Controlled docs | `docs/README.md`, `docs/INDEX.md`, requirements, RTM, design, STD, risk, decision, implementation evidence |
| Implementation plan | `docs/06-implementation/implementation-milestones.md`, `docs/06-implementation/desktop-app-development-plan.md` |
| Ralph handoff | `ralph.md`, existing active queue and reflection log preserved |
| Source code | Cargo workspace plus Rust crates and `apps/desktop`/`apps/desktop-ui` |
| Validation commands | `npm run m0:check`, `cargo test --workspace`, `cargo fmt --all --check`, `python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q`, docs JSON/link checks |

Inventory counts at bootstrap creation:

- Markdown files under `docs/`: 130
- Rust files: 61
- JSON files: 144
- Missing key bootstrap seed documents: 0

## 3. Readiness objective

Prepare the repository for the next local Ralph/TDD execution checkpoint while preserving current safety boundaries. The immediate handoff is not a live deployment or remote sync. It is a governed local-readiness package that records what is safe to execute next and which checks must pass.

## 4. Milestone readiness sequence

| ID | Milestone | Purpose | First executable checkpoint | Status |
|---|---|---|---|---|
| MB-D0 | Bootstrap package creation | Create profile, plan, tasks, testcases, gate, Hisys/local advisory record, validation log, and Ralph handoff link. | Documentation/control validation only. | current |
| MB-D1 | Existing Ralph queue continuation | Resume from `ralph.md` rather than chat context. | `M7-STUDENT-LOCAL-CHECKOUT-READER-READ-OUTSIDE-WORKSPACE-T1` if still current after Git reconstruction. | ready-subject-to-recheck |
| MB-D2 | Desktop app implementation path | Use `desktop-app-development-plan.md` to start D1 after user selects desktop-app execution scope. | Tauri config RED test before product code. | planned |
| MB-D3 | Queue refill governance | If Ralph queue exhausts, use §9.2 refill and this bootstrap package to select safe local fixture/docs work. | PREP/documentation-control task first. | planned |

## 5. Selected next-safe path

For ordinary Ralph continuation, the authoritative next task remains the existing `ralph.md` queue, not this bootstrap summary. At creation time, the latest readable checkpoint identifies `M7-STUDENT-LOCAL-CHECKOUT-READER-READ-OUTSIDE-WORKSPACE-T1` as the next safe local RED/GREEN task, with no live external action and no user-executed command required.

For the user's separate desktop-app goal, the safe entry is `desktop-app-development-plan.md` D1: first write a failing Tauri config/launch metadata test, then add the minimal Tauri app metadata and entrypoint. Do not mix that path with the existing M7 queue unless the user selects it as the next Ralph target.

## 6. Gaps and blockers

- Formal Hisys status may remain advisory/needs-more-evidence unless a current Hisys adapter accepts local codebase readiness evidence for this exact package.
- Real Tauri desktop runtime evidence still requires a controlled user-observed desktop launch/capture package.
- Remote push/publication/live GitHub/credential mutation remain outside authority.
- Existing `ralph.md` is large and already authoritative; this bootstrap adds a handoff reference rather than rewriting the queue.

## 7. Acceptance criteria for this bootstrap

- Required artifact set exists under `docs/milestone-bootstrap/`.
- `profile.yaml` records detected and selected profile.
- Task YAML and testcase YAML include develop profile gates.
- Quality gate distinguishes local validation from remote/live gates.
- Readiness decision separates formal Hisys result from local advisory result.
- `ralph.md` is merged by adding a bootstrap handoff section without overwriting active queue/reflection content.
- Markdown local links and JSON/YAML parsing pass.
