---
title: Desktop SLICE-A Evidence Summary Source Specification
document_id: EDUOPS-DESKTOP-SLICE-A-EVIDENCE-SUMMARY-SOURCE-SPECIFICATION
version: 0.1.0
status: accepted
date: 2026-05-21
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-DESKTOP-IPC-EXPANSION-SPECIFICATION
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
    - SWENG-EDUTECH-SLICE-A-TEST-CARDS
    - SWENG-EDUTECH-FIXTURE-CORPUS-HARNESS-PLAN
    - EDUOPS-DEC-066
  gaps_recorded:
    - Source-contract prerequisite for the `query_slice_a_evidence_summary` desktop IPC command, including absence semantics for the gitignored `/build/` directory
---

# Desktop SLICE-A Evidence Summary Source Specification

## 0. Document scope

This specification defines only the controlled HOW-level source-data contract that a future fixture-local `query_slice_a_evidence_summary` desktop IPC handler may read. The handler returns a read-only projection of the SLICE-A local-skeleton run-summary record at a single fixed repo working-copy path. The source data is **not** committed to Git — the repo `.gitignore:17` rule `/build/` excludes the directory from version control — so the handler must define deterministic absence semantics for the common case where the file is not present in the working copy.

This is the [Desktop IPC Expansion Specification](desktop-ipc-expansion-specification.md) §6 source-data class "repo working-copy single fixed-path read" for the `query_slice_a_evidence_summary` command.

This document does **not**:

- implement the `query_slice_a_evidence_summary` Rust handler;
- wire any new Tauri command into `apps/desktop/src/main.rs`;
- modify `.gitignore` to track `/build/`;
- author or modify any artifact under `build/evidence/slice-a/local-skeleton/`;
- perform a directory walk, glob, symlink resolution, or caller-controlled path read;
- invoke a real Tauri runtime, desktop window, Git command, credential lookup, network call, remote action, installer publication, or DEMO-1 evidence claim.

Acceptance of this specification is acceptance of the **source-data contract only**. Handler implementation, Tauri wiring, STD/RTM addenda, and any change to the build-artifact directory's Git policy remain separately gated Ralph follow-ups.

## 1. Purpose

[Desktop IPC Expansion Specification](desktop-ipc-expansion-specification.md) §3 row 5 authorizes `query_slice_a_evidence_summary` to "Return read-only SLICE-A `run-summary.json` content from `build/evidence/slice-a/local-skeleton/run-summary.json` when present in the repo working copy. Returns `<not-found>` if absent." The same specification explicitly restricts the handler to "repo file read via `std::fs::read_to_string` constrained to the literal path; rejects anything else."

This specification closes the prerequisite HOW-level gap by defining:

1. the closed fixed-path read boundary;
2. the absence-handling semantics under the `.gitignore:17` `/build/` rule;
3. the closed allowed-key set sourced from the observed working-copy artifact shape;
4. the deterministic `<not-found>` response shape;
5. validation rules for the future handler implementation;
6. non-claim boundaries for the future handler.

## 2. Authorized source-data boundary

The only repo working-copy path admitted by the future handler is the literal:

```text
build/evidence/slice-a/local-skeleton/run-summary.json
```

Rules:

1. The handler shall accept no caller-supplied path, fragment, prefix, suffix, query, or environment-variable override that could redirect the read.
2. The handler shall reject anything other than this exact literal repo-relative path. Reads using absolute paths, `..` segments, alternate separators, symlinks, drive prefixes, NUL bytes, or shell metacharacter semantics are forbidden.
3. The handler shall not enumerate, glob, walk, or otherwise scan `build/`, `build/evidence/`, `build/evidence/slice-a/`, or `build/evidence/slice-a/local-skeleton/`.
4. The handler shall perform exactly one `std::fs::read_to_string` invocation against the canonical literal path per request. It shall not retry, follow symlinks, watch the filesystem, or open any related handle.
5. The handler shall not write to, mutate, delete, or rename any file or directory.

## 3. Absence semantics under `.gitignore:17`

The repo `.gitignore` line 17 contains:

```text
/build/
```

This rule excludes the entire `/build/` tree from Git version control. As a consequence:

1. The `build/evidence/slice-a/local-skeleton/run-summary.json` artifact is **not committed** to Git and is therefore **not guaranteed** to be present in a freshly cloned working copy.
2. The artifact is **conventionally produced** by the `eduops_fixture` SLICE-A run (`cargo run -p eduops_fixture -- run-slice-a` or equivalent harness command). The produced file is the in-scope source for this handler.
3. The handler shall treat absence as a non-error, observable, deterministic outcome. Specifically: a read that fails with `std::io::ErrorKind::NotFound` shall map to the `<not-found>` response form defined in §5.
4. The handler shall **not** attempt to create, generate, scaffold, or fetch the missing artifact in any way. Production of the artifact is exclusively the responsibility of the user-run SLICE-A fixture harness.
5. The handler shall **not** request, suggest, or imply a change to the `.gitignore` `/build/` rule. The artifact remains a build product, not source.

## 4. Closed allowed-key set

The observed v0.1.0 shape of `build/evidence/slice-a/local-skeleton/run-summary.json` produced by the current SLICE-A fixture harness contains exactly the following top-level keys in their canonical order:

| Key | Type | Rule |
|---|---|---|
| `gate` | string | The SLICE-A gate identifier the run aimed to evidence. The v0.1.0 expected literal is `GATE-SLICE-A-LOCAL-SKELETON`. |
| `live_external_action` | boolean | Whether the run executed any live external action. The v0.1.0 expected literal is `false`. |
| `external_call_made` | boolean | Whether any external call was made during the run. The v0.1.0 expected literal is `false`. |
| `github_mutation_made` | boolean | Whether any GitHub mutation was attempted or completed. The v0.1.0 expected literal is `false`. |
| `course_id` | string | The course identifier the run was scoped to. |
| `artifacts` | array of strings | The list of artifact relative-path basenames the run produced under the same local-skeleton directory. |

Rules:

1. The handler shall deserialize the file as JSON via `serde_json::from_str` with the response struct declared `#[serde(deny_unknown_fields)]` against the closed allowed-key set above.
2. A document containing any key outside the closed set shall fail closed with the §6 `DESKTOP_IPC_INTERNAL_ERROR` denial code rather than silently passing.
3. A document missing any of the six required keys shall fail closed with the same denial code.
4. A document whose `live_external_action`, `external_call_made`, or `github_mutation_made` is not the literal `false` shall fail closed; the SLICE-A local-skeleton harness must never produce a `true` value for these fields, and a non-false value indicates a corrupted or tampered artifact.
5. A document whose `gate` is not `GATE-SLICE-A-LOCAL-SKELETON` shall fail closed; this handler's v0.1.0 scope is the local-skeleton gate only.
6. A document whose `artifacts` contains entries with `..`, absolute-path syntax, alternate separators, NUL bytes, or shell metacharacter semantics shall fail closed.

A future version bump of this specification may widen the allowed-key set or admit additional gate identifiers. v0.1.0 is intentionally narrow.

## 5. Deterministic `<not-found>` response shape

When the read fails with `std::io::ErrorKind::NotFound`, the handler shall produce a `ResultEnvelope<SliceAEvidenceSummary>` whose `data` carries the deterministic literal:

| Field | Literal |
|---|---|
| `availability` | `"<not-found>"` |
| `gate` | `null` (the handler shall use `Option<String>`, `None`) |
| `live_external_action` | `false` |
| `external_call_made` | `false` |
| `github_mutation_made` | `false` |
| `course_id` | `null` |
| `artifacts` | `[]` (empty list) |

Rules:

1. The `<not-found>` response shall not include any inferred or invented gate identifier, course identifier, or artifact list.
2. The `<not-found>` response shall hardcode the three no-live boolean literals at `false` so that downstream consumers cannot misinterpret an absent record as a positive live-action signal.
3. The `<not-found>` response shall set `availability` to the literal string `<not-found>` so that the present/absent distinction is observable without inspecting nullable fields.
4. When the read succeeds and the document validates, the handler shall set `availability` to the literal string `<present>` and populate all other fields from the parsed document.

## 6. Fail-closed denial codes

Per [Desktop IPC Expansion Specification](desktop-ipc-expansion-specification.md) §5 the handler shall map source-data failures to the closed denial-code set:

| Trigger | Denial code |
|---|---|
| Parse failure (invalid JSON, schema-violation, unknown key, missing required key, illegal value, illegal `artifacts` entry) | `DESKTOP_IPC_INTERNAL_ERROR` |
| Response would exceed 64 KiB after canonical projection | `DESKTOP_IPC_RESPONSE_TOO_LARGE` |
| Anything other than `std::io::ErrorKind::NotFound` returned from the read (for example a permission error or an I/O hardware error) | `DESKTOP_IPC_INTERNAL_ERROR` |

The `<not-found>` response is not a denial — it is a deterministic positive observation that the file is absent.

The handler shall not introduce new denial codes outside the §5 closed set.

## 7. Future `query_slice_a_evidence_summary` handler boundary

A future fixture-local handler implementation may be seeded after this specification is accepted. The handler shall:

- expose `query_slice_a_evidence_summary(RequestEnvelope<()>) -> ResultEnvelope<SliceAEvidenceSummary>` in `eduops_desktop`;
- derive its result from the single fixed-path read defined in §2 and the absence semantics defined in §3 and §5;
- emit a deterministic audit event id of the form `audit_query_slice_a_evidence_summary_<request_id>`;
- hardcode no-live posture fields consistent with the existing IPC handlers;
- fail closed with an allowed §5 denial code if the file is present but invalid;
- keep response size at or below the 64 KiB limit.

The handler shall not:

- accept any caller-supplied path, fragment, prefix, suffix, or query argument;
- call `std::fs::read_dir`, `std::fs::metadata`, `std::fs::canonicalize`, glob, symlink-resolution logic, `git`, credential stores, network APIs, host-process commands, or watch the filesystem;
- mutate files, directories, Git state, credentials, remotes, or repository administration state;
- claim DEMO-1 readiness, desktop launch evidence, real IPC execution from a desktop window, screenshot capture, screen-recording, or installer publication;
- alter the `.gitignore` `/build/` rule;
- generate, scaffold, fetch, or otherwise produce the source artifact when it is absent.

## 8. Relationship to controlled documents

- [Desktop IPC Expansion Specification](desktop-ipc-expansion-specification.md) §3 row 5 and §6 authorize the `query_slice_a_evidence_summary` command and the source-data class that this specification instantiates.
- [Desktop App Development Plan](../06-implementation/desktop-app-development-plan.md) provides the MB-DESKTOP path-B context in which additional read-only fixture-local IPC commands are useful.
- [SLICE-A Executable Test Cards](../03-verification-validation/slice-a-executable-test-cards.md) define the SLICE-A behaviors whose fixture run produces the source artifact this handler reads.
- [Fixture Corpus and Harness Plan](../03-verification-validation/fixture-corpus-and-harness-plan.md) is the parent fixture-corpus control under which the SLICE-A run-summary record is produced.
- [Blocker Resolution Authority](../05-decisions/blocker-resolution-authority-2026-05-20.md) provides the local-safe authority for additional IPC and fixture-local blocker resolution while preserving user-executed/live boundaries.

## 9. Acceptance boundary

Acceptance of this specification means:

- the literal path `build/evidence/slice-a/local-skeleton/run-summary.json` is the only source admitted for the future `query_slice_a_evidence_summary` handler;
- the `.gitignore:17` `/build/` rule is preserved; the handler treats `NotFound` as a deterministic `<not-found>` observation rather than an error;
- the closed six-key allowed set and the `GATE-SLICE-A-LOCAL-SKELETON` gate literal are the controlled baseline for a later handler implementation row;
- the future `query_slice_a_evidence_summary` handler may be implemented only after a separate PREP/T/GATE cycle and shall obey the boundary above;
- no handler implementation, Tauri wiring, Cargo dependency addition, `.gitignore` change, live filesystem walk, caller-controlled path read, real IPC invocation, desktop launch, screenshot capture, installer publication, credential resolution, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, DEMO-1 acceptance, or user-managed external-repo action is authorized or implied by this document.

## 10. Change log

- **v0.1.0 (2026-05-21):** initial source-contract acceptance for the `query_slice_a_evidence_summary` prerequisite. Defines the closed single fixed-path read boundary, the `.gitignore:17` `/build/` absence semantics, the closed six-key allowed set sourced from the observed working-copy artifact (`gate`, `live_external_action`, `external_call_made`, `github_mutation_made`, `course_id`, `artifacts`), the deterministic `<not-found>` response shape, the §5 denial-code mapping, the future handler boundary, document relationships, and non-claims.
