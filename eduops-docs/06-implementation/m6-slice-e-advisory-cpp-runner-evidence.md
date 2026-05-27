---
title: M6 SLICE-E Advisory C/C++ Runner Gate Evidence
document_id: EDUOPS-M6-SLICE-E-ADVISORY-CPP-RUNNER-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-EVAL-EXEC
    - SWENG-EDUTECH-EVAL-RUNNER-IO
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M6-RUNNER-IO-SPEC-BLOCKER
  tests:
    - eduops_runner::m6_runner_io_contract
    - eduops_runner::m6_runner_evidence_contract
    - eduops_runner::m6_runner_policy_contract
---

# M6 SLICE-E Advisory C/C++ Runner Gate Evidence

## 1. Gate result

M6 is accepted-constrained for fixture-local advisory C/C++ runner I/O, command-plan evidence, advisory compile/run result schema, evidence-manifest canonicalization, and negative sandbox policy boundary. Production host execution, real toolchain invocation, hosted runners, and official grading authority remain explicitly out of scope.

```text
gate=GATE-SLICE-E-ADVISORY-CPP-RUNNER
status=accepted-constrained
scope=RunnerInputPackage validation and canonical hashing; RunnerCommandPlan derivation (gcc/g++ with -std flag from c11/c17/cpp17/cpp20 profile, deterministic plan SHA-256); CompileResult/RunResult/AdvisoryDiagnostic schemas; in-process fake executor; RunnerEvidenceManifest canonical JSON with hardcoded advisory_only=true / official_grading_evidence=false / live_external_action=false / network_adapter_calls=0 / host_wide_sandbox_mutation=false non-claim literals plus manifest_sha256; SandboxProfileClaim / HostSandboxCapabilities / enforce_sandbox_policy with EDUOPS_RUNNER_POLICY_NETWORK_REJECTED and EDUOPS_RUNNER_POLICY_CONTROL_UNAVAILABLE rejects; timeout/memory_exceeded/run_failed/output-truncation-manual-review status pass-through
constraint=host process execution, real compiler invocation (gcc/clang/MSVC), live external action, hosted runners (GitHub Actions, self-hosted), official grading authority, raw credential lookup, host-wide sandbox mutation (seccomp/namespaces/cgroups/Job Object/AppContainer), production toolchain selection, real OS-level timeout/memory/network enforcement, evaluator integration, late-policy enforcement, instructor reopen workflow surface, and DEMO-1 export all out of scope
live_external_action=false
network_adapter_calls=0
host_process_executions=0
real_compiler_invocations=0
host_wide_sandbox_mutations=0
remote=none
```

M6 does not claim production runner adapter implementation, real compiler invocation, host process execution, hosted runner integration, OS-level sandbox configuration, official grading evidence, late-policy enforcement, evaluator integration, instructor reopen workflow, or DEMO-1 export.

## 2. Implemented acceptance scope

Accepted M6 behavior:

- `eduops_runner` defines `RUNNER_INPUT_SCHEMA_VERSION = "eduops.runner.input/0.1"`, `RunnerError`, `RunnerLanguage { C11, C17, Cpp17, Cpp20 }` with `RunnerLanguage::parse` returning `EDUOPS_RUNNER_LANGUAGE_UNSUPPORTED`, `RunnerSourceFile`, `RunnerStdinFixture`, `RunnerExpectedOutput`, `RunnerInputPackageDraft`, and `RunnerInputPackage::from_draft` validating required fields (`EDUOPS_RUNNER_INPUT_REQUIRED_FIELD_MISSING`), source-file non-empty (`EDUOPS_RUNNER_INPUT_SOURCE_FILES_EMPTY`), and source/stdin/expected-output relative paths (`EDUOPS_RUNNER_INPUT_PATH_ESCAPE` rejects absolute, `..`/`.`/empty segments, `~` prefix, backslash, `:`). Canonical JSON renders top-level keys alphabetically and `RunnerInputPackage::canonical_json_sha256` is deterministic.
- `eduops_runner` defines `RUNNER_COMMAND_PLAN_SCHEMA_VERSION`, `RUNNER_COMPILE_RESULT_SCHEMA_VERSION`, `RUNNER_RUN_RESULT_SCHEMA_VERSION`, `RUNNER_DIAGNOSTIC_SCHEMA_VERSION`, and `RUNNER_EVIDENCE_SCHEMA_VERSION` constants; `RunnerStage { Compile, Run }`; `RunnerStagePlan` with program/argv/cwd/env_allowlist/stdin; `RunnerCommandPlan::derive(&RunnerInputPackage)` selecting `gcc` for C profiles and `g++` for C++ profiles, with `-std=c11`/`-std=c17`/`-std=c++17`/`-std=c++20` plus `-O0 -Wall -Wextra -o work/main <primary>` and any non-primary source paths, the run stage wired to the declared stdin fixture, and a deterministic `plan_sha256` over the canonical-JSON bytes.
- `eduops_runner` defines `RunnerCompileStatus { Success, Failed }`, `RunnerRunStatus { Success, RunFailed, Timeout, MemoryExceeded, ManualReview, PathEscapeRejected, NetworkRejected, PolicyRejected }`, `RunnerDiagnosticSeverity { Error, Warning, Note }`, `AdvisoryDiagnostic`, `CompileResult`, `RunResult`, `RunnerEvidenceManifest`, and an in-process `FakeRunnerSeed` plus `execute_with_fake_runner(&pkg, &plan, seed)` that hashes seeded stdout/stderr bytes per stage, skips the run stage when compile fails, and renders a sorted `RunnerEvidenceManifest` canonical JSON with the fixed non-claim literals `advisory_only=true`, `official_grading_evidence=false`, `live_external_action=false`, `network_adapter_calls=0`, `host_wide_sandbox_mutation=false`, plus `manifest_sha256`.
- `eduops_runner` defines `SandboxProfileClaim`, `HostSandboxCapabilities`, `SandboxPolicyEvidence`, and `enforce_sandbox_policy(&claim, &host)` that rejects host network outbound calls under a `network=deny` claim with `EDUOPS_RUNNER_POLICY_NETWORK_REJECTED`, rejects any missing `required_for_fixture_pass` control with `EDUOPS_RUNNER_POLICY_CONTROL_UNAVAILABLE`, otherwise emits `audit_runner_policy_<profile_id>` evidence with `fail_before_exec=true` when `path_escape_policy == "fail-before-exec"`.

## 3. RED to GREEN evidence

### M6-T1 RunnerInputPackage validation and canonical hashing

```text
RED command:    cargo test -p eduops_runner --test m6_runner_io_contract -- --nocapture
RED result:     unresolved RunnerInputPackage / RunnerLanguage / RunnerSourceFile / RunnerStdinFixture / RunnerExpectedOutput / RunnerInputPackageDraft / RUNNER_INPUT_SCHEMA_VERSION / RunnerError imports
GREEN command:  cargo test -p eduops_runner --test m6_runner_io_contract -- --nocapture
GREEN result:   10 passed; 0 failed
Commit:         e59edb6
```

### M6-T2 advisory compile/run result, command plan, and evidence manifest

```text
RED command:    cargo test -p eduops_runner --test m6_runner_evidence_contract -- --nocapture
RED result:     unresolved command-plan/result/diagnostic/manifest imports
GREEN command:  cargo test -p eduops_runner --test m6_runner_evidence_contract -- --nocapture
GREEN result:   5 passed; 0 failed
Commit:         a352910
```

### M6-T3 advisory runner negative policy fixtures

```text
RED command:    cargo test -p eduops_runner --test m6_runner_policy_contract -- --nocapture
RED result:     unresolved SandboxProfileClaim / HostSandboxCapabilities / enforce_sandbox_policy imports
GREEN command:  cargo test -p eduops_runner --test m6_runner_policy_contract -- --nocapture
GREEN result:   9 passed; 0 failed
Commit:         97a6b35
```

### M6-RUNNER-IO-SPEC evaluation runner I/O contract

```text
Specification:   docs/02-design-planning/evaluation-runner-io-contract.md
Acceptance:      accepted-for-fixture-implementation at f402f60
Decision record: docs/06-implementation/m6-runner-io-spec-blocker.md (closed-by-contract)
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> M6-T1 10 passed; M6-T2 5 passed; M6-T3 9 passed; plus existing M1..M5 totals (assignment-release 7, submission-state 7, repository-conflict 9, roster-import 6, identity-binding 8, workspace-provisioning 6, access-control 7, document-materialization 6, projection-fixture 1, operation-journal 1, block-document 1, configuration 1, credentials 1, safety 1, plus M0/M1 scaffold) all green
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
docs link/JSON sweep                                                       -> bad_local_links=0; bad_json_parse=0
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Advisory results cannot be promoted to official grading evidence | `m6_runner_evidence_contract::success_run_produces_distinct_stdout_stderr_hashes_and_manifest_non_claims`, `m6_runner_evidence_contract::compile_failure_records_diagnostic_and_skips_run_stage` (`advisory_only=true`, `official_grading_evidence=false`) | accepted |
| Timeout/memory/path-traversal negative fixtures pass | `m6_runner_policy_contract::timeout_seed_records_timeout_status_in_manifest`, `memory_exceeded_seed_records_status_in_manifest`, `path_escape_rejected_before_command_planning_records_no_command_plan` | accepted |
| Runner emits audit evidence before any external process start | `m6_runner_policy_contract::sandbox_policy_accepts_fixture_local_controls` (`audit_runner_policy_<profile_id>`), `m6_runner_evidence_contract::manifest_carries_command_plan_and_input_package_hashes` (`audit_event_id`) | accepted |
| Runner cannot touch host files outside the permitted workspace boundary | `m6_runner_io_contract::path_escape_in_source_file_is_rejected_before_command_planning`, `path_escape_in_fixture_paths_is_rejected`, `m6_runner_policy_contract::sandbox_policy_rejects_missing_required_control` | accepted |
| Manifest non-claims are hardcoded literals | `m6_runner_evidence_contract::manifest_canonical_json_top_level_keys_are_sorted_alphabetically` (sorted keys, `advisory_only` literal `true`) | accepted |
| Network attempts under deny policy are rejected | `m6_runner_policy_contract::sandbox_policy_rejects_network_call_attempt` (`EDUOPS_RUNNER_POLICY_NETWORK_REJECTED`) | accepted |
| Non-C/C++ profiles are rejected before command planning | `m6_runner_io_contract::non_c_or_cpp_language_profile_is_rejected`, `m6_runner_policy_contract::non_c_or_cpp_profile_rejected_before_command_planning_records_no_host_call` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- production runner adapter implementation (a `RunnerAdapter` host-process implementation);
- real compiler invocation, real C/C++ binary execution, or real toolchain selection (gcc/clang/MSVC and version policy);
- OS-level sandbox configuration (seccomp BPF, namespaces, cgroups, Job Objects, AppContainer);
- live external action, hosted runners (GitHub Actions, self-hosted), or any network call;
- official grading authority or any binding evaluation evidence;
- raw credential lookup, credential rotation, or credential persistence by the runner;
- host-wide sandbox mutation, firewall, service, kernel, or system configuration mutation;
- real wall-clock timeout, memory, file-descriptor, or process-count enforcement (the fake executor accepts seeded values);
- assignment-side conflict detection against released-version baselines (covered separately by M5 follow-up);
- late-policy enforcement, evaluator integration, instructor reopen workflow surface, or feedback release authority;
- observability/diagnostics ingestion beyond in-memory `audit_event_id` strings and structured diagnostic records;
- DEMO-1 export evidence (deferred to M8).

## 7. Follow-up

The following follow-up items are required before broader runner-related milestones may claim acceptance:

1. proceed to M7 GitHub clone-only adapter only at the selected safe integration point, preserving clone-only/fake/mock/dry-run boundaries and no live GitHub action;
2. proceed to M8 export fixture and DEMO-1 evidence only after the exporter implementation specification is authored and accepted;
3. before any host process execution, real compiler invocation, or hosted runner integration is added under Ralph, an authorized human owner must accept a host-runner adapter specification covering OS-level sandbox configuration, real toolchain selection policy, real timeout/memory/file-descriptor/process-count/network enforcement, host-process lifecycle, audit-log persistence, and academic-integrity boundary between advisory and official evaluation;
4. wire `enforce_sandbox_policy` evidence into the `RunnerEvidenceManifest` `policy_records` field when a host-runner adapter specification accepts that integration;
5. thread real `wall_time_ms` and `peak_memory_bytes` enforcement evidence against the active `ResourceLimitsProfile` (the fake executor accepts seeded values only).

## 8. Traceability

- [Evaluation execution profile](../02-design-planning/evaluation-execution-profile.md)
- [Evaluation runner I/O contract](../02-design-planning/evaluation-runner-io-contract.md)
- [Process topology and IPC contract](../02-design-planning/process-topology-and-ipc-contract.md)
- [M6 evaluation runner I/O contract specification gap closure](m6-runner-io-spec-blocker.md)
- [Implementation milestones](implementation-milestones.md)
- [M5 SLICE-D assignment publication, submission, and repository conflict gate evidence](m5-slice-d-assignment-submission-evidence.md)
- [M4 SLICE-C roster, identity, and workspace gate evidence](m4-slice-c-roster-identity-workspace-evidence.md)
- [M3 SLICE-B canonical document gate evidence](m3-slice-b-canonical-document-evidence.md)
- [M2 configuration and credential reference evidence](m2-configuration-credential-evidence.md)
