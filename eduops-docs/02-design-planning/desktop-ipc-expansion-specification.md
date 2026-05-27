---
title: Desktop IPC Expansion Specification
document_id: EDUOPS-DESKTOP-IPC-EXPANSION-SPECIFICATION
version: 0.2.0
status: accepted
date: 2026-05-21
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-DEC-OS-001
    - EDUOPS-DESKTOP-ENTRYPOINT-DEPENDENCY-ADOPTION-AUTHORIZED-DECISION
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
    - EDUOPS-PROCESS-TOPOLOGY-AND-IPC-CONTRACT
    - EDUOPS-DEC-066
  gaps_recorded:
    - Authorized read-only / local-fixture-only IPC command surface beyond
      the existing `query_session_capabilities` M1A session-capability
      command.
---

# Desktop IPC Expansion Specification

## 0. Document scope

This specification defines **only** the controlled HOW-level contract for the
authorized desktop IPC command surface that the path-B Tauri 2 entrypoint
(authorized by `EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-AUTHORIZED`) may
expose **beyond** the existing `query_session_capabilities` M1A
session-capability command. It enumerates authorized command names,
request/response envelope shapes, fail-closed denial codes, fixture-data
sources, and explicit non-claims.

This document does **not**:

- modify any source file (no Rust crate edit, no TypeScript edit, no
  `package.json` change, no `Cargo.toml` change);
- adopt any new Cargo dependency or npm dependency;
- invoke `cargo tauri dev`, `cargo tauri build`, or any real desktop
  launch;
- open a real EduOps desktop window;
- perform any IPC invocation;
- claim any user-observed launch evidence or DEMO-1 readiness;
- authorize filesystem mutation, Git execution, credential lookup,
  network call, remote action, host runtime install, installer
  publication, or any live external action;
- supersede or relax any non-claim boundary recorded in
  [Desktop Entrypoint Dependency Adoption Authorized Decision](desktop-entrypoint-dependency-adoption-authorized-decision.md)
  §7 or
  [Desktop D6 User-Observed Launch Evidence Shape Specification](desktop-d6-launch-evidence-shape-specification.md)
  §7.

Acceptance of this specification is acceptance of the **contract only**.
Fixture-local handler implementation, IPC wiring of any specific command
into `apps/desktop/src/main.rs`, and any test or evidence work for
individual commands remain separately gated Ralph follow-ups.

## 1. Purpose

`EDUOPS-DEC-066` §2 authorizes Ralph/Hermes to resolve the "additional
IPC" blocker family through "a controlled IPC expansion specification for
read-only/local fixture commands before any source change", subject to
the boundary "No filesystem mutation, Git execution, credential lookup,
network call, or live external action."

The existing path-B Tauri 2 entrypoint at `apps/desktop/src/main.rs`
exposes exactly one Tauri command — `query_session_capabilities` — under
the opt-in `tauri-app` feature. The first path-B increment
intentionally restricted the IPC surface to this single
session-capability command per the authorized decision §2 boundary.

This specification expands that surface by enumerating which additional
commands are permitted under the same fail-closed boundary. It does so
HOW-level only: the spec defines the contract; a separate Ralph
follow-up authors any fixture-local handler implementation, and a
further follow-up performs any user-observed launch evidence work.

## 2. Authorized vs. user-executed boundary

This boundary is load-bearing for every section below.

| Concern | Authorized for Ralph automation (docs/control only) | Reserved for user-executed gate |
|---|---|---|
| Author this specification | Yes | — |
| Author a fixture-local Rust handler that returns deterministic test-fixture data for any command listed in §3 | Yes, only when explicitly seeded as a later Ralph row | — |
| Wire a §3 command into `apps/desktop/src/main.rs` `tauri::generate_handler!` macro | Yes, only when explicitly seeded as a later Ralph row and only under the opt-in `tauri-app` feature | — |
| Open a Tauri IPC channel to a real desktop window and invoke any §3 command | No | Yes |
| Install WebKitGTK / WebView2 / Tauri CLI | No | Yes |
| Run `cargo tauri dev` / `cargo tauri build` | No | Yes |
| Capture screenshots or screen recordings as evidence of a live IPC round-trip | No | Yes |
| Mutate the filesystem from inside any §3 command handler | Never (fail-closed) | Never (the §4 non-claim block forbids this) |
| Invoke `git` or call a credential store from inside any §3 command handler | Never (fail-closed) | Never |
| Make a network request from inside any §3 command handler | Never (fail-closed) | Never |

Ralph shall never author a §3 command handler that performs any of the
"Never" actions.

## 3. Authorized command surface

The following table enumerates the **closed** set of additional IPC
commands authorized by this specification beyond the existing
`query_session_capabilities` M1A command. Any IPC command name not
listed here and not equal to `query_session_capabilities` is
unauthorized in v0.1.0 and shall be rejected at design review.

The §3 set may be extended only by a controlled `version` bump of this
specification.

| Command name | Purpose | Request payload | Response payload | Source data | Fixture-local handler authorized? |
|---|---|---|---|---|---|
| `query_session_capabilities` | (existing M1A command — out of scope of this expansion; listed here for completeness) | `RequestEnvelope<()>` | `ResultEnvelope<SessionCapabilities>` | `default_session_capabilities()` | already implemented in `apps/desktop/src/lib.rs` |
| `query_app_metadata` | Return read-only app/build identity (name, semver, build feature flags, no-live posture). | `RequestEnvelope<()>` | `ResultEnvelope<AppMetadata>` | static const strings + compile-time `env!("CARGO_PKG_VERSION")` | Yes, deterministic in-process computation |
| `query_runtime_environment` | Return read-only runtime environment descriptor (`os`, `arch`, `node_version` via the UI shell's own `process` if needed, `webview_runtime_identifier_hint`). | `RequestEnvelope<()>` | `ResultEnvelope<RuntimeEnvironment>` | `std::env::consts::OS` / `std::env::consts::ARCH` / static constants | Yes, no FS read beyond `std::env::consts` |
| `query_fixture_corpus_index` | Return read-only directory index of the controlled fixture corpus under `fixtures/slice-a/**` (file path, sha256 from a controlled precomputed manifest, byte length). Never reads file contents. | `RequestEnvelope<()>` | `ResultEnvelope<FixtureCorpusIndex>` | precomputed JSON manifest committed to the repo (no live FS scan) | Yes, the manifest is a static asset; no live FS scan |
| `query_slice_a_evidence_summary` | Return read-only SLICE-A `run-summary.json` content from `build/evidence/slice-a/local-skeleton/run-summary.json` when present in the repo working copy. Returns `<not-found>` if absent. | `RequestEnvelope<()>` | `ResultEnvelope<SliceAEvidenceSummary>` | repo file read via `std::fs::read_to_string` constrained to the literal path; rejects anything else | Yes, read-only single fixed path |
| `query_d6_evidence_template_shape` | Return the D6 evidence-shape spec §3.2.1 required-key list and the §6.2 rule 7 allowed-form set as a structured descriptor. Never returns a real D6 evidence package. | `RequestEnvelope<()>` | `ResultEnvelope<D6EvidenceShapeDescriptor>` | static const list derived from `desktop-d6-launch-evidence-shape-specification.md` v0.3.0 | Yes, static descriptor |

Notes:

- Every authorized command is **read-only** at the handler boundary.
  No handler may write, append, create, delete, rename, chmod, or
  symlink any path on the host filesystem.
- Every authorized command shall return a `ResultEnvelope<...>` that
  carries a deterministic `audit_event_id` of the shape
  `audit_<command_name_snake>_<request_id>` (matching the existing
  `query_session_capabilities` convention at
  `apps/desktop/src/lib.rs:49`).
- The total response size shall be bounded (≤ 64 KiB per response). A
  handler that would produce a larger response shall fail closed with
  `DESKTOP_IPC_RESPONSE_TOO_LARGE`.

## 4. Request / response envelope shapes

Every authorized command shall use the existing
`eduops_api::RequestEnvelope<P>` / `eduops_api::ResultEnvelope<P>`
shapes already used by `query_session_capabilities`. No new envelope
type is introduced by this specification.

The handler signature pattern is:

```rust
#[must_use]
pub fn query_<command>(request: RequestEnvelope<RequestPayload>)
    -> ResultEnvelope<ResponsePayload>;
```

Where:

- `RequestPayload` is `()` for all §3 v0.1.0 commands (no input is
  required because every authorized command is read-only and bounded
  to a fixed input set).
- `ResponsePayload` is the specific descriptor type declared in §3.

Tauri wiring (when a §3 command is later promoted by a separate Ralph
row) uses the same `#[tauri::command]` + `tauri::generate_handler!`
pattern as `apps/desktop/src/main.rs:49` and shall preserve the opt-in
`tauri-app` feature gating (no default Cargo build compiles the Tauri
runtime crate).

## 5. Fail-closed denial codes

A §3 command handler shall return `ResultEnvelope::err(...)` (or the
analogous error variant on the existing envelope) with one of the
following codes when the listed condition is observed. The codes form
a **closed** set; any other rejection code is unauthorized and shall
be rejected at design review.

| Code | Triggering condition |
|---|---|
| `DESKTOP_IPC_COMMAND_NOT_AUTHORIZED` | The Tauri runtime receives an invocation for a command name not equal to `query_session_capabilities` and not listed in §3. |
| `DESKTOP_IPC_REQUEST_ENVELOPE_INVALID` | The request envelope fails the existing `eduops_api::RequestEnvelope` validation (e.g., missing `request_id`, malformed `api_version`). |
| `DESKTOP_IPC_FIXTURE_NOT_FOUND` | A §3 command that reads a fixture path observes that the fixture is absent. Returned with an audit event recording the missing path label (hash only, not the raw path). |
| `DESKTOP_IPC_RESPONSE_TOO_LARGE` | A handler would produce a response larger than 64 KiB. |
| `DESKTOP_IPC_INTERNAL_ERROR` | A handler observes an unexpected condition that is not classified by the codes above. The error message shall not echo any raw filesystem path, credential, repository URL, raw email, or any value that would violate the D6 spec §6 redaction rules. |

A handler shall **never** return a code that indicates a live external
action attempt (no `DESKTOP_IPC_NETWORK_FAILED`, no
`DESKTOP_IPC_GIT_FAILED`, no `DESKTOP_IPC_CREDENTIAL_RESOLUTION_FAILED`)
because none of those actions is authorized in v0.1.0 — such an
attempted action would itself be a specification violation, not a
runtime error.

## 6. Fixture data sources

Each authorized command derives its response from one of the following
**closed** classes of source data. No other source class is permitted
in v0.1.0.

| Class | Description | Example |
|---|---|---|
| Compile-time constant | A value baked into the binary at build time. | `env!("CARGO_PKG_VERSION")`, `std::env::consts::OS` |
| Static const list | A value declared as a `const` or `static` in `apps/desktop/src/lib.rs` or an adjacent module. | `DESKTOP_SHELL_NAME`, the §3 D6 schema descriptor |
| Controlled precomputed manifest committed to the repo | A JSON file under `docs/`, `fixtures/`, or `build/evidence/` that is part of the repo working copy and that Ralph has authority to author. | `fixtures/slice-a/manifest.json` (if/when authored) |
| Repo working-copy single fixed-path read | A `std::fs::read_to_string` of a single literal path declared in §3, with no caller-controlled path component. | `build/evidence/slice-a/local-skeleton/run-summary.json` |

A handler shall **never** read a caller-supplied path, perform a
directory walk, glob, or resolve symlinks. The fixed-path read in the
last class above is permitted only because the path is hard-coded in
the handler source and is not influenced by the IPC caller.

## 7. Explicit non-claims

Accepting this specification does NOT claim:

- a real Tauri IPC round-trip from a real desktop window;
- a real `cargo tauri dev` / `cargo tauri build` execution;
- WebKitGTK or WebView2 runtime installation;
- installer publication or distribution readiness;
- DEMO-1 acceptance or DEMO-1 readiness;
- end-to-end interactive accessibility audit with a real screen
  reader;
- keyboard navigation simulation on a real desktop window;
- credential resolution, token refresh, rotation, or storage
  modification;
- live GitHub action, real `git clone` / `fetch` / `push` /
  `ls-remote`;
- repository administration, submission / provisioning state
  promotion, or evaluation-result authority;
- network call of any kind;
- D6 user-observed launch gate closure;
- the desktop-app development plan §6 D6 user-observed launch gate
  evidence content;
- user-managed external-repo boundary actions per `EDUOPS-DEC-064`
  and `EDUOPS-DEC-065`.

Each downstream Ralph follow-up that promotes a §3 command into a
fixture-local handler implementation shall preserve this non-claim
list verbatim.

## 8. Authorized future controlled rows

Accepting this specification authorizes the following classes of
follow-up rows that a later Ralph queue-refill checkpoint may seed
without further user confirmation, each as a separate
PREP/T/GATE cycle:

1. A fixture-local handler implementation for ONE selected §3 command
   (e.g., `query_app_metadata`), authored under the existing
   `eduops_desktop` crate with deterministic in-process computation
   and a focused RED/GREEN test bucket analogous to
   `apps/desktop/tests/ui_shell_launch_health.rs`. The handler shall
   not yet be wired into the Tauri `generate_handler!` macro.
2. Tauri wiring for ONE accepted fixture-local handler under the
   opt-in `tauri-app` feature, analogous to the existing
   `query_session_capabilities_command` wrapper at
   `apps/desktop/src/main.rs:49`. The wiring shall not perform any
   real IPC invocation.
3. STD / RTM addenda crediting any accepted §3 handler and its
   Tauri wiring, analogous to the existing M1A and MB-DESKTOP D6
   STD/RTM addenda.
4. Future controlled `version` bumps to this specification adding new
   §3 commands within the §2 / §4 / §5 / §6 / §7 boundary.

None of those rows may execute a real desktop launch, install host
runtime software, invoke `cargo tauri dev` / `cargo tauri build`,
capture screenshots, claim DEMO-1, or perform any user-managed
external-repo action.

## 9. Relationship to other specifications

- [Desktop App Development Plan](../06-implementation/desktop-app-development-plan.md)
  §6 is the source of the path-B Tauri 2 entrypoint adoption and the
  D6 user-observed launch gate.
- [Desktop Entrypoint Dependency Adoption Authorized Decision](desktop-entrypoint-dependency-adoption-authorized-decision.md)
  §2 / §6 / §7 is the source of the "first increment exposes only
  `query_session_capabilities`" boundary that this specification
  expands within the bounded `EDUOPS-DEC-066` §2 authority.
- [DEC-OS-001 Windows and Linux Desktop Target](dec-os-001-windows-linux-desktop-target.md)
  §2 is the source of the host platform / runtime constraints that
  every authorized handler shall honor.
- [Process Topology and IPC Contract](process-topology-and-ipc-contract.md)
  is the parent contract for the IPC envelope and the no-live posture
  that every authorized handler shall preserve.
- [Desktop D6 User-Observed Launch Evidence Shape Specification](desktop-d6-launch-evidence-shape-specification.md)
  §3.2.1 / §6.2 is the source of the D6 evidence-shape descriptor that
  `query_d6_evidence_template_shape` exposes.
- [EduOps Blocker Resolution Authority](../05-decisions/blocker-resolution-authority-2026-05-20.md)
  `EDUOPS-DEC-066` §2 "Additional IPC" row is the authorization for
  this specification.

## 10. Acceptance boundary

Acceptance of this specification means:

- the authorized command surface in §3, the envelope contract in §4,
  the fail-closed denial codes in §5, the closed source-data classes
  in §6, the non-claim block in §7, the authorized future rows in
  §8, and the cross-references in §9 are the controlled baseline for
  any subsequent IPC handler authoring;
- Ralph may seed §8 follow-up rows under continuous-run authorization
  without further user confirmation, each as a separate PREP/T/GATE
  cycle;
- no Cargo dependency is added, no source file is modified, no
  `apps/desktop/src/main.rs` change is performed, no Tauri wiring
  change is performed, no host runtime install, no Tauri CLI install,
  no live external action, no credential resolution, no network
  call, no remote action, no installer publication, no DEMO-1 claim,
  no user-observed launch gate closure is authorized or implied by
  this acceptance.

## 11. Change log

- **v0.1.0 (2026-05-20):** initial contract-only acceptance under
  `EDUOPS-DEC-066` §2 additional IPC authority. §0 document scope,
  §1 purpose, §2 authorized-vs.-user-executed boundary, §3 closed
  authorized command surface (`query_app_metadata`,
  `query_runtime_environment`, `query_fixture_corpus_index`,
  `query_slice_a_evidence_summary`, `query_d6_evidence_template_shape`
  plus the existing `query_session_capabilities` for completeness),
  §4 envelope contract, §5 five-code closed denial-code set, §6
  four-class closed source-data set, §7 non-claim block, §8
  authorized future rows, §9 cross-references, §10 acceptance
  boundary.
- **v0.2.0 (2026-05-21):** controlled `version` bump per §8 row 4
  documenting completion of §8 row 1 (fixture-local handler
  implementation), row 2 (Tauri wiring), and row 3 (STD/RTM addenda)
  for all five §3 commands. `query_app_metadata` library handler at
  `ef9fe0f` plus Tauri wiring at `3770706`; `query_runtime_environment`
  library handler at `1dc9999` plus Tauri wiring at `6f5b17c`;
  `query_d6_evidence_template_shape` library handler at `3cba516` plus
  Tauri wiring at `a910439`; `query_fixture_corpus_index` library
  handler at `722f15f` plus Tauri wiring at `23fd157` (sourced from
  the controlled precomputed manifest at `de537ab` per the Desktop
  Fixture Corpus Manifest Specification v0.1.0 at `ebf9df1`);
  `query_slice_a_evidence_summary` library handler at `1bea58b` plus
  Tauri wiring at `5d1032a` (sourced from the working-copy single
  fixed-path read per the Desktop SLICE-A Evidence Summary Source
  Specification v0.1.0 at `e531721`). STD addendum rows
  `STD-MB-DESKTOP-IPC-QUERY-APP-METADATA-001`,
  `STD-MB-DESKTOP-IPC-QUERY-RUNTIME-ENVIRONMENT-001`,
  `STD-MB-DESKTOP-IPC-QUERY-D6-EVIDENCE-TEMPLATE-SHAPE-001`,
  `STD-MB-DESKTOP-IPC-QUERY-FIXTURE-CORPUS-INDEX-001`, and
  `STD-MB-DESKTOP-IPC-QUERY-SLICE-A-EVIDENCE-SUMMARY-001` plus the
  corresponding MB-DESKTOP RTM addendum paragraphs trace every command
  pair to `EDUOPS-FR-002` / `EDUOPS-NFR-004` / `EDUOPS-NFR-013` /
  `EDUOPS-NFR-035`. The §3 closed surface, §4 envelope contract, §5
  fail-closed denial-code set, §6 closed source-data set, and §7
  non-claim block remain unchanged from v0.1.0; no source file
  modified by this version bump; no Cargo dependency added; no host
  runtime install authorized; no real Tauri runtime invocation; no
  real desktop launch; no installer publication; no DEMO-1 claim.
