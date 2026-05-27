---
title: M6 Evaluation Runner I/O Contract Specification Gap Closure
document_id: EDUOPS-M6-RUNNER-IO-SPEC-BLOCKER
version: 0.1.0
status: closed-by-contract
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - SWENG-EDUTECH-EVAL-EXEC
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-DOMAIN-IDL
  gaps_recorded:
    - Evaluation runner I/O contract (M6 row in implementation-milestones §6)
---

# M6 Evaluation Runner I/O Contract Specification Gap Closure

## 1. Purpose

This document records the controlled gap-closure decision for the evaluation runner I/O contract specification before the M6 SLICE-E advisory C/C++ runner gate is claimed. The "Evaluation runner I/O contract" entry in the milestone-gated gap table of [Implementation milestones §6](implementation-milestones.md) is listed as `Required before M6` with the rationale that the runner must define command layout, resource limits, sandbox boundary, and evidence schema before code.

[Evaluation execution profile](../02-design-planning/evaluation-execution-profile.md) defines execution profiles (student local pre-check, instructor/lab runner, GitHub Actions, self-hosted runner), Windows sandbox control candidates (Job Object limits, AppContainer/low-integrity process options, filesystem allowlists, network blocking, timeout, memory/process limits, working-directory isolation, log redaction), and evaluation-evidence schema seeds (assignment version, submission commit SHA, compiler/toolchain profile, command line and environment profile hash, timeout/memory/process/filesystem/network policies, stdout/stderr/log hashes, test result summary and raw result references, sandbox violations and manual review flags) at a design-level draft. It does not yet contain:

- a concrete `RunRequest` / `RunResult` / `RunnerEvidence` type contract for the `eduops_runner::RunnerAdapter` trait covering command layout, argv, stdin/stdout/stderr handling, environment variable allowlist, working-directory isolation, and toolchain profile selection;
- a controlled `ResourceLimitsProfile` schema for timeout (wall + CPU), peak memory, process count, file descriptor count, output byte cap, and filesystem allowlist with deterministic canonical JSON;
- a controlled `SandboxProfile` specification for Linux (rlimit/seccomp filter list/namespace allowlist/cgroup limits/network-deny) and Windows (Job Object limits, AppContainer/low-integrity profile, network blocking, filesystem allowlist), with explicit fail-closed behavior on configuration mismatch;
- a controlled `EvaluationEvidence` JSON manifest schema with sorted canonical keys, SHA-256 over stdout/stderr/log artifacts, sandbox-violation records, manual-review flags, and audit-event linkage;
- error/timeout/OOM/sandbox-violation classification with deterministic `runner_error_code` enumeration distinct from `EDUOPS_IO_*` and `EDUOPS_GATE_*`;
- audit evidence requirements covering pre-execution authorization, command-line/environment hash recording, and post-execution evidence handoff per the [process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md) request/response envelope;
- a fail-closed offline rule consistent with AC-009 of the [access-control authorization model](../02-design-planning/access-control-authorization-model.md) for runner adapters that cannot prove sandbox configuration.

Authoring or commissioning the evaluation runner I/O contract crosses a design/decision boundary that requires human review of policy authority, OS sandboxing strategy, toolchain selection (gcc/clang/MSVC), resource-limit policy across Windows/Linux/macOS hosts, evaluation-evidence retention/redaction policy, and academic integrity safeguards (advisory vs official-evaluation separation). The Ralph loop must not author or accept that specification directly under its non-delegable safety boundary because:

- system-level sandboxing (seccomp BPF, namespace unshare, cgroup limits, Windows Job Objects, AppContainer manifests) requires careful host-policy review and falls outside Ralph's local fixture-only execution boundary;
- compiler invocation, real C/C++ host execution, and external toolchain binding require build-host/policy authority;
- unsafe C/C++ execution is identified as a primary risk in `implementation-milestones.md` §M6 and `EDUOPS-R-004`/`EDUOPS-R-033`;
- official/advisory evaluation-evidence separation is an academic policy boundary owned by a human authority.

## 2. Decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-M6-RUNNER-IO-SPEC-DEFERRED` |
| Decision date | 2026-05-15 |
| Status | closed by [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md); M6-PREP may create fixture-local advisory runner RED/GREEN tasks |
| Authority required | human design owner with sandbox policy, toolchain selection, and academic integrity authority |
| Ralph delegation | not authorized to author the specification or implement runner behavior |

The evaluation runner I/O contract specification has been authored and accepted for fixture-local advisory implementation in [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md). The previous blocker is closed for M6-PREP. M6 remains constrained to fixture-local advisory C/C++ runner behavior and shall not claim official grading, live external execution, hosted runners, or host-wide sandbox mutation.

## 3. M6 status under this gap-closure decision

M6 status after contract closure:

- [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md) defines `RunnerInputPackage`, command plan, result, diagnostic, resource-limit, sandbox, and evidence-manifest schemas;
- M6-PREP may create executable RED/GREEN tasks for fixture-local advisory runner behavior;
- initial implementation may use fake/local deterministic adapters and shall not perform live external action, official grading, hosted execution, raw credential lookup, or host-wide sandbox mutation;
- the M6 row in the active task queue may move from `pending-after-M6-RUNNER-IO-SPEC-and-human-authored-spec` to a fixture-local `M6-PREP` queue.

This gap closure still does not claim, demonstrate, or imply implemented C/C++ advisory runner behavior. It closes only the specification entry criterion so Ralph can create M6 fixture-local RED/GREEN tasks.

## 4. Closed follow-up before claiming runner adapter implementation

The required specification follow-up is now satisfied by [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md). The implementation follow-up remains constrained as follows before any milestone or gate claims advisory C/C++ runner behavior:

1. use [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md), which covers:
   - `RunRequest` / `RunResult` / `RunnerEvidence` type contract for the `RunnerAdapter` trait, including command/argv/env, stdin/stdout/stderr handling, working-directory isolation, and toolchain profile selection (gcc/clang/MSVC and version policy);
   - `ResourceLimitsProfile` canonical JSON schema (wall/CPU timeout, peak memory, process count, file descriptor count, output byte cap, filesystem allowlist) consistent with `evaluation-execution-profile.md` §4–§5;
   - `SandboxProfile` specification for Linux (rlimit/seccomp/namespace/cgroup) and Windows (Job Object limits/AppContainer/network blocking/filesystem allowlist) with fail-closed semantics on configuration mismatch;
   - `EvaluationEvidence` JSON manifest schema with sorted canonical keys, SHA-256 over stdout/stderr/log artifacts, sandbox-violation records, manual-review flags, and audit-event linkage;
   - `runner_error_code` enumeration distinct from `EDUOPS_IO_*` and `EDUOPS_GATE_*`, including timeout/OOM/sandbox-violation/path-escape classifications;
   - audit evidence requirements covering pre-execution authorization and post-execution evidence handoff;
   - fail-closed offline rule consistent with AC-009 of the [access-control authorization model](../02-design-planning/access-control-authorization-model.md);
   - test requirements aligned with the M6 acceptance gates (advisory results cannot be promoted to official grading evidence; timeout/memory/path-traversal negative fixtures pass; runner emits audit evidence before external process start; runner cannot touch host files outside the permitted workspace boundary);
2. author an explicit acceptance/decision record updating the milestone-gated gap table entry from open to closed;
3. update the affected RTM and STD rows to reference the new specification as the runner I/O contract acceptance source;
4. coordinate with the [process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md) for runner-worker boundary and envelope expectations, and with the [canonical domain IDL](../02-design-planning/canonical-domain-idl.md) for evidence-type identity.

After this contract closure, Ralph may create executable M6 fixture-local tasks (`M6-T*`). M6 evidence may claim only fixture-local advisory runner I/O/evidence behavior until later host-runner and official-grading gates are accepted.

## 5. Why this remains constrained after closure

The Ralph safety boundary prohibits live external action, destructive change, system-level sandbox configuration, and any work that requires authority Ralph does not hold. Authoring the evaluation runner I/O contract specification is a design decision pass that requires:

- sandbox policy authority spanning Linux and Windows host configurations;
- toolchain selection authority (gcc/clang/MSVC and version policy);
- academic integrity authority for advisory vs official-evaluation separation;
- design owner sign-off through the [decision log](../05-decisions/decision-log.md);
- coordination with the [evaluation execution profile](../02-design-planning/evaluation-execution-profile.md), [process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md), [canonical domain IDL](../02-design-planning/canonical-domain-idl.md), and the [risk register](../04-risk-management/risk-register.md) entries for unsafe C/C++ execution.

Closing the specification gap preserves traceability without overclaiming host execution, official grading, or production sandbox acceptance outside Ralph's safety boundary.

## 6. Traceability

| Reference | Source |
|---|---|
| Milestone-gated gap table row | [Implementation milestones §6](implementation-milestones.md) — "Evaluation runner I/O contract" row |
| Evaluation profile baseline | [Evaluation execution profile](../02-design-planning/evaluation-execution-profile.md) |
| Worker boundary / IPC | [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md) |
| Domain evidence types | [Canonical domain IDL](../02-design-planning/canonical-domain-idl.md) |
| Risk register | [Risk register](../04-risk-management/risk-register.md) — `EDUOPS-R-004`, `EDUOPS-R-033` |
| Prior gap-closure precedent | [M3 editor adapter bridge specification gap closure](m3-bridge-spec-blocker.md), [M5 scoped submission and review authorization specification gap closure](m5-auth-spec-blocker.md) |

## 7. Non-claims

This document does not implement runner adapter behavior, invoke a compiler, execute host C/C++ binaries, approve official grading, approve hosted runners, mutate host-wide sandbox configuration, or claim production evaluation evidence. The linked contract closes the M6 specification entry criterion for fixture-local advisory implementation only.
