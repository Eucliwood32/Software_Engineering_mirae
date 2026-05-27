---
title: Evaluation Runner I/O Contract
document_id: SWENG-EDUTECH-EVAL-RUNNER-IO
version: 0.1.0
status: accepted-for-fixture-implementation
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-EVAL-EXEC
    - SWENG-EDUTECH-PROCESS-IPC
    - SWENG-EDUTECH-DOMAIN-IDL
    - SWENG-EDUTECH-STD
  requirements:
    - EDUOPS-FR-017
    - EDUOPS-FR-018
    - EDUOPS-FR-056
    - EDUOPS-NFR-029
  milestone:
    - M6 SLICE-E advisory C/C++ runner
---

# Evaluation Runner I/O Contract

## 1. Purpose and scope

This contract defines the fixture-local I/O boundary for the EduOps advisory C/C++ evaluation runner. It closes the M6 entry criterion named "Evaluation runner I/O contract" for test-first fixture implementation. The contract defines request, result, diagnostic, and evidence manifest shapes before runner adapter code is authored.

The accepted scope is advisory C/C++ fixture execution only. This contract does not authorize official grading, live external execution, hosted runners, GitHub Actions, credential access, network access, host-wide sandbox mutation, or production deployment.

## 2. Controlled runner profile

| Field | Accepted value |
|---|---|
| Profile ID | `eduops.runner.advisory-cpp.fixture/0.1` |
| Language scope | Advisory C and C++ only |
| Execution authority | Fixture-local advisory evidence only |
| Official grading claim | Not allowed |
| Network access | Disabled; zero outbound calls expected |
| Host mutation | No host-wide sandbox, firewall, service, credential, or system configuration mutation |
| Filesystem scope | Per-run workspace directory plus declared read-only fixture inputs |
| Live external action | Prohibited |

Allowed language values are:

```text
c11
c17
cpp17
cpp20
```

Any other language/profile value is rejected before compile or run planning.

## 3. Runner input package schema

`RunnerInputPackage` is the canonical input to a runner adapter. It is serialized as deterministic JSON with sorted object keys. Paths are relative to the run workspace unless explicitly identified as fixture-root references.

```json
{
  "schema_version": "eduops.runner.input/0.1",
  "request_id": "run-20260515-000001",
  "course_id": "course-fixture-001",
  "assignment_id": "assignment-cpp-basics",
  "assignment_version": "v1",
  "submission_id": "submission-fixture-001",
  "submission_snapshot_sha": "sha256:...",
  "language": "cpp17",
  "toolchain_profile_id": "gcc-fixture-13-cpp17",
  "source_files": [
    {
      "path": "src/main.cpp",
      "sha256": "...",
      "role": "primary"
    }
  ],
  "stdin_fixture": {
    "path": "fixtures/stdin/sample-001.txt",
    "sha256": "..."
  },
  "expected_outputs": [
    {
      "path": "fixtures/expected/sample-001.stdout",
      "sha256": "...",
      "comparison": "exact-bytes"
    }
  ],
  "resource_limits_profile": "eduops.runner.limits.fixture-small/0.1",
  "sandbox_profile": "eduops.runner.sandbox.fixture-local-deny-network/0.1",
  "evidence_profile": "eduops.runner.evidence.fixture/0.1",
  "audit_event_id": "audit-run-request-001"
}
```

Required fields are `schema_version`, `request_id`, `course_id`, `assignment_id`, `assignment_version`, `submission_id`, `language`, `toolchain_profile_id`, `source_files`, `resource_limits_profile`, `sandbox_profile`, `evidence_profile`, and `audit_event_id`. Missing required fields fail before command planning.

The input package may reference fixture stdin and expected-output files. It shall not contain raw credentials, absolute host paths, network URLs for execution input, or user secrets.

## 4. Command invocation model

The runner adapter constructs a two-stage command plan from the input package:

1. compile stage;
2. run stage, if compilation succeeds.

A `RunnerCommandPlan` records the planned commands before process start:

```json
{
  "schema_version": "eduops.runner.command-plan/0.1",
  "compile": {
    "program": "g++",
    "argv": ["-std=c++17", "-O0", "-Wall", "-Wextra", "-o", "work/main", "src/main.cpp"],
    "cwd": "work",
    "env_allowlist": ["PATH", "TMPDIR"],
    "stdin": "empty"
  },
  "run": {
    "program": "work/main",
    "argv": [],
    "cwd": "work",
    "env_allowlist": ["TMPDIR"],
    "stdin": "fixtures/stdin/sample-001.txt"
  },
  "plan_sha256": "..."
}
```

The command plan is evidence, not permission to execute outside the fixture boundary. The runner records the command plan and audit event before starting any compile or run process.

## 5. stdin, stdout, and stderr contract

| Stream | Contract |
|---|---|
| stdin | Empty by default or read from a declared fixture file in the input package. Interactive stdin is not supported. |
| stdout | Captured as bytes up to the configured output byte cap. Stored as an artifact reference with SHA-256. |
| stderr | Captured as bytes up to the configured output byte cap. Stored as an artifact reference with SHA-256. |
| combined logs | May be derived for diagnostics, but stdout and stderr hashes remain separate. |

Output truncation is represented as `output_truncated=true` in `RunResult` and `RunnerEvidence`. Truncated output is not a passing result unless the test case explicitly expects truncation.

## 6. Resource limits and sandbox boundary

`ResourceLimitsProfile` defines deterministic limits for fixture execution.

```json
{
  "schema_version": "eduops.runner.resource-limits/0.1",
  "profile_id": "eduops.runner.limits.fixture-small/0.1",
  "wall_timeout_ms": 3000,
  "cpu_timeout_ms": 2500,
  "peak_memory_bytes": 134217728,
  "process_count": 2,
  "file_descriptor_count": 64,
  "stdout_stderr_byte_cap": 1048576,
  "filesystem_write_allowlist": ["work/**", "evidence/**"],
  "filesystem_read_allowlist": ["src/**", "fixtures/**", "work/**"],
  "network": "disabled"
}
```

`SandboxProfile` defines boundary claims that the adapter must either enforce or report as unavailable before execution.

```json
{
  "schema_version": "eduops.runner.sandbox/0.1",
  "profile_id": "eduops.runner.sandbox.fixture-local-deny-network/0.1",
  "network": "deny",
  "path_escape_policy": "fail-before-exec",
  "linux_controls": ["rlimit", "working-directory-isolation"],
  "windows_controls": ["job-object", "working-directory-isolation"],
  "required_for_fixture_pass": ["working-directory-isolation", "path-escape-deny", "network-deny-evidence"]
}
```

The fixture implementation may initially use fake or simulated enforcement for tests, but the evidence must label enforcement mode precisely. A runner that cannot prove required fixture controls returns `policy_violation` before compile or run execution.

No code in M6 may mutate host-wide sandbox settings. The implementation may create per-run directories, fixture files, evidence files, and in-process/fake policy records only.

## 7. Compile result, run result, and advisory diagnostics schema

`CompileResult`:

```json
{
  "schema_version": "eduops.runner.compile-result/0.1",
  "stage": "compile",
  "status": "success",
  "exit_code": 0,
  "stdout_sha256": "...",
  "stderr_sha256": "...",
  "diagnostics": [],
  "started_at": "2026-05-15T00:00:00Z",
  "completed_at": "2026-05-15T00:00:01Z"
}
```

`RunResult`:

```json
{
  "schema_version": "eduops.runner.run-result/0.1",
  "stage": "run",
  "status": "success",
  "exit_code": 0,
  "stdout_sha256": "...",
  "stderr_sha256": "...",
  "output_truncated": false,
  "resource_usage": {
    "wall_time_ms": 14,
    "peak_memory_bytes": 1048576
  },
  "started_at": "2026-05-15T00:00:01Z",
  "completed_at": "2026-05-15T00:00:02Z"
}
```

`AdvisoryDiagnostic`:

```json
{
  "schema_version": "eduops.runner.diagnostic/0.1",
  "severity": "error",
  "code": "compile_error",
  "message": "compiler returned non-zero exit status",
  "source_ref": "src/main.cpp:12:3",
  "advisory_only": true
}
```

Allowed result statuses are `planned`, `policy_rejected`, `compile_failed`, `run_failed`, `timeout`, `memory_exceeded`, `path_escape_rejected`, `network_rejected`, `success`, and `manual_review`.

## 8. Evidence manifest schema

`RunnerEvidenceManifest` is the gate-facing evidence artifact.

```json
{
  "schema_version": "eduops.runner.evidence/0.1",
  "run_id": "runner-evidence-001",
  "request_id": "run-20260515-000001",
  "profile_id": "eduops.runner.advisory-cpp.fixture/0.1",
  "advisory_only": true,
  "official_grading_evidence": false,
  "live_external_action": false,
  "network_adapter_calls": 0,
  "host_wide_sandbox_mutation": false,
  "input_package_sha256": "...",
  "command_plan_sha256": "...",
  "compile_result": "evidence/compile-result.json",
  "run_result": "evidence/run-result.json",
  "stdout_artifact": {
    "path": "evidence/stdout.bin",
    "sha256": "..."
  },
  "stderr_artifact": {
    "path": "evidence/stderr.bin",
    "sha256": "..."
  },
  "diagnostics": ["evidence/diagnostics.json"],
  "policy_records": ["evidence/policy-records.json"],
  "audit_event_id": "audit-run-request-001",
  "manual_review_required": false
}
```

The manifest is canonicalized with sorted keys before hashing. The manifest hash is stored in the M6 gate evidence summary.

## 9. Failure modes

| Failure mode | Required result | Evidence requirement |
|---|---|---|
| Compile error | `compile_failed` | Compiler stderr hash, diagnostic with `compile_error`, no run stage |
| Timeout | `timeout` | Timeout limit, observed elapsed value, killed-stage indicator |
| Memory limit exceeded | `memory_exceeded` | Limit profile, observed or simulated memory evidence |
| Path traversal / path escape | `path_escape_rejected` | Rejected path, policy id, no process start |
| Network attempt | `network_rejected` or `policy_rejected` | Network-deny policy record, zero successful network calls |
| Output cap exceeded | `manual_review` or `run_failed` | Truncation flag and byte cap evidence |
| Sandbox/control unavailable | `policy_rejected` | Missing control id and fail-before-exec record |
| Non-C/C++ profile | `policy_rejected` | Rejected language/profile value |
| Runtime non-zero exit | `run_failed` | Exit code, stdout/stderr hashes, advisory diagnostic |

All failure modes are advisory. None may become official grade, penalty, or release evidence without a later official-evaluation policy and gate.

## 10. Fixture-only execution boundary

M6 implementation shall start with fixture tests and fake/local adapters. The allowed execution boundary is:

- deterministic local fixture directories under test-controlled temporary roots;
- no live GitHub, LMS, hosted runner, or external network service;
- no raw credential lookup;
- no system package installation;
- no firewall, service manager, kernel, cgroup, AppContainer, or Job Object host-wide configuration change by Ralph;
- no deletion or mutation of user data outside test temp directories;
- no official grading claim.

The first runnable implementation may use a fake executor that returns deterministic compile/run results from fixture files. A later host process executor may be added only after tests prove the same I/O and evidence contract and after the host boundary is reviewed.

## 11. Test anchors

The M6 RED/GREEN queue shall derive tests from this contract. Initial test anchors are:

| Test ID | Purpose | Expected command |
|---|---|---|
| `M6-T1` | Runner input package validation and canonical hashing | `cargo test -p eduops_runner --test m6_runner_io_contract -- --nocapture` |
| `M6-T2` | Advisory compile/run result schema and evidence manifest | `cargo test -p eduops_runner --test m6_runner_evidence_contract -- --nocapture` |
| `M6-T3` | Negative policy fixtures for timeout, path escape, network disabled, and non-C/C++ profile | `cargo test -p eduops_runner --test m6_runner_policy_contract -- --nocapture` |
| `M6-GATE` | Constrained SLICE-E evidence summary | repository validation plus focused M6 tests |

## 12. Traceability

| Anchor | Link |
|---|---|
| Evaluation execution profile | [Evaluation execution profile](evaluation-execution-profile.md) |
| Process boundary | [Process topology and IPC contract](process-topology-and-ipc-contract.md) |
| Domain evidence types | [Canonical domain IDL](canonical-domain-idl.md) |
| STD coverage | [Software test description](../03-verification-validation/software-test-description.md) — `STD-014`, `STD-015`, `STD-016`, `STD-048`, `STD-M6-001..STD-M6-006` |
| Implementation milestone | [Implementation milestones](../06-implementation/implementation-milestones.md) — M6 |
| Previous blocker | [M6 runner I/O spec blocker](../06-implementation/m6-runner-io-spec-blocker.md) |

## 13. Non-claims

This contract does not implement a runner, invoke a compiler, run C/C++ binaries, approve official grading, select a production sandbox, approve hosted runners, perform live external actions, mutate host-wide sandbox configuration, or create production evaluation evidence. It defines the fixture-local I/O and evidence contract needed for M6 RED/GREEN implementation under Ralph.
