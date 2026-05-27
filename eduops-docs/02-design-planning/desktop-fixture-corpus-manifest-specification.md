---
title: Desktop Fixture Corpus Manifest Specification
document_id: EDUOPS-DESKTOP-FIXTURE-CORPUS-MANIFEST-SPECIFICATION
version: 0.1.0
status: accepted
date: 2026-05-21
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-DESKTOP-IPC-EXPANSION-SPECIFICATION
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
    - SWENG-EDUTECH-FIXTURE-CORPUS-HARNESS-PLAN
    - EDUOPS-DEC-066
  gaps_recorded:
    - Precomputed manifest prerequisite for the `query_fixture_corpus_index` desktop IPC command
---

# Desktop Fixture Corpus Manifest Specification

## 0. Document scope

This specification defines only the controlled HOW-level manifest contract that a future fixture-local `query_fixture_corpus_index` desktop IPC handler may read. The manifest is a precomputed, committed, deterministic index of the controlled `fixtures/slice-a/**` corpus. It is the `Desktop IPC Expansion Specification` §6 source-data class "controlled precomputed manifest committed to the repo" for the `query_fixture_corpus_index` command.

This document does **not**:

- author `fixtures/slice-a/manifest.json`;
- implement the `query_fixture_corpus_index` Rust handler;
- wire any new Tauri command into `apps/desktop/src/main.rs`;
- read the live filesystem from a desktop IPC handler;
- perform a directory walk, glob, symlink resolution, or caller-controlled path read;
- invoke a real Tauri runtime, desktop window, Git command, credential lookup, network call, remote action, installer publication, or DEMO-1 evidence claim.

Acceptance of this specification is acceptance of the **manifest contract only**. Manifest data authoring, handler implementation, Tauri wiring, and STD/RTM addenda remain separately gated Ralph follow-ups.

## 1. Purpose

`Desktop IPC Expansion Specification` §3 authorizes `query_fixture_corpus_index` to return a read-only directory index of the controlled fixture corpus under `fixtures/slice-a/**`: file path, SHA-256 from a controlled precomputed manifest, and byte length. The same specification explicitly forbids a live filesystem scan from the handler.

This specification closes the prerequisite HOW-level gap by defining:

1. the closed fixture-root boundary;
2. the manifest schema and canonical JSON layout;
3. the currently observed closed entry list for `fixtures/slice-a/**`;
4. validation rules for future manifest authoring;
5. non-claim boundaries for the future handler.

## 2. Authorized source-data boundary

The only fixture root admitted by this manifest v0.1.0 is:

```text
fixtures/slice-a/
```

The closed file list observed for v0.1.0 is:

| Relative path | Byte length | SHA-256 |
|---|---:|---|
| `fixtures/slice-a/empty-course.json` | 288 | `7b02f473f2a792060f6d27c8bafa58fc0c0b476d8564dfebbaa2ca242cdc2f12` |

Rules:

1. Every manifest entry path shall be repo-relative and start with `fixtures/slice-a/`.
2. Every manifest entry path shall use `/` separators and shall not contain `..`, absolute-path syntax, drive prefixes, NUL bytes, or shell metacharacter semantics.
3. The manifest authoring step may inspect the repo working copy to compute byte length and SHA-256. The future IPC handler shall not repeat that inspection.
4. The future IPC handler shall read only the committed manifest asset selected by the follow-up implementation row. It shall not walk `fixtures/slice-a/`, glob, resolve symlinks, read fixture file contents, or accept a caller-supplied path.
5. Adding, removing, or renaming any `fixtures/slice-a/**` file requires a manifest-authoring checkpoint that updates the entry list and validation evidence.

## 3. Manifest JSON shape

The future manifest file shall be authored at:

```text
fixtures/slice-a/manifest.json
```

The top-level object shall contain these keys in alphabetical order when serialized as canonical JSON:

| Key | Type | Rule |
|---|---|---|
| `entries` | array | Sorted by `relative_path` ascending. |
| `fixture_root` | string | Literal `fixtures/slice-a`. |
| `generated_by` | string | Literal `ralph-precomputed-manifest`. |
| `live_filesystem_scan_permitted` | boolean | Literal `false`. |
| `manifest_schema_version` | string | Literal `0.1.0`. |
| `source_class` | string | Literal `controlled-precomputed-manifest-committed-to-repo`. |

Each `entries[]` object shall contain these keys in alphabetical order:

| Key | Type | Rule |
|---|---|---|
| `byte_length` | integer | Non-negative byte length of the file at manifest-authoring time. |
| `relative_path` | string | Repo-relative path under `fixtures/slice-a/`. |
| `sha256` | string | Lowercase 64-hex SHA-256 of the file bytes at manifest-authoring time. |

Canonical JSON layout:

```json
{
  "entries": [
    {
      "byte_length": 288,
      "relative_path": "fixtures/slice-a/empty-course.json",
      "sha256": "7b02f473f2a792060f6d27c8bafa58fc0c0b476d8564dfebbaa2ca242cdc2f12"
    }
  ],
  "fixture_root": "fixtures/slice-a",
  "generated_by": "ralph-precomputed-manifest",
  "live_filesystem_scan_permitted": false,
  "manifest_schema_version": "0.1.0",
  "source_class": "controlled-precomputed-manifest-committed-to-repo"
}
```

The future handler response type may project the manifest into a Rust `FixtureCorpusIndex` type, but it shall preserve the same semantic fields: schema version, fixture root, source class, and sorted entries with relative path, byte length, and SHA-256.

## 4. Validation rules for manifest authoring

A later manifest-authoring Ralph row shall validate the following before committing `fixtures/slice-a/manifest.json`:

1. `manifest_schema_version == "0.1.0"`.
2. `fixture_root == "fixtures/slice-a"`.
3. `source_class == "controlled-precomputed-manifest-committed-to-repo"`.
4. `live_filesystem_scan_permitted == false`.
5. `entries` is non-empty unless a controlled decision explicitly accepts an empty SLICE-A corpus.
6. `entries` is sorted by `relative_path` and contains no duplicates.
7. Every `relative_path` starts with `fixtures/slice-a/` and passes the path-safety rules in §2.
8. Every listed file exists at manifest-authoring time and is a regular file in the repo working copy.
9. Every `byte_length` equals the byte length read at manifest-authoring time.
10. Every `sha256` equals the lowercase SHA-256 of the file bytes read at manifest-authoring time.
11. The manifest file itself is not included as a fixture entry unless a future controlled version bump explicitly changes that rule.
12. The validation output does not echo raw credentials, raw repository URLs, email addresses, or any D6 redaction-rule violation.

## 5. Future `query_fixture_corpus_index` handler boundary

A future fixture-local handler implementation may be seeded after this specification is accepted. The handler shall:

- expose `query_fixture_corpus_index(RequestEnvelope<()>) -> ResultEnvelope<FixtureCorpusIndex>` in `eduops_desktop`;
- derive its result from the committed precomputed manifest, not from a live directory walk;
- emit a deterministic audit event id of the form `audit_query_fixture_corpus_index_<request_id>`;
- hardcode no-live posture fields consistent with the existing IPC handlers where applicable;
- fail closed with an allowed `Desktop IPC Expansion Specification` §5 denial code if the manifest is absent, malformed, too large, or inconsistent with this schema;
- keep response size at or below the §3 limit of 64 KiB.

The handler shall not:

- accept any caller-supplied path or fixture root;
- call `std::fs::read_dir`, glob, symlink-resolution logic, `git`, credential stores, network APIs, or host-process commands;
- mutate files, directories, Git state, credentials, remotes, or repository administration state;
- claim DEMO-1 readiness, desktop launch evidence, or real IPC execution from a desktop window.

## 6. Relationship to controlled documents

- [Desktop IPC Expansion Specification](desktop-ipc-expansion-specification.md) §3 authorizes the `query_fixture_corpus_index` command, and §6 defines the source-data class that this manifest specification instantiates.
- [Desktop App Development Plan](../06-implementation/desktop-app-development-plan.md) provides the MB-DESKTOP path-B context in which additional read-only fixture-local IPC commands are useful.
- [Fixture Corpus and Harness Plan](../03-verification-validation/fixture-corpus-and-harness-plan.md) is the parent fixture-corpus control for SLICE-A local fixture evidence.
- [Blocker Resolution Authority](../05-decisions/blocker-resolution-authority-2026-05-20.md) provides the local-safe authority for additional IPC and fixture-local blocker resolution while preserving user-executed/live boundaries.

## 7. Acceptance boundary

Acceptance of this specification means:

- `fixtures/slice-a/empty-course.json` is the only v0.1.0 fixture entry currently admitted for the precomputed manifest, with byte length `288` and SHA-256 `7b02f473f2a792060f6d27c8bafa58fc0c0b476d8564dfebbaa2ca242cdc2f12`;
- the manifest schema, canonical JSON layout, source-class label, and validation rules are the controlled baseline for a later `fixtures/slice-a/manifest.json` authoring row;
- the future `query_fixture_corpus_index` handler may be implemented only after a separate PREP/T/GATE cycle and shall use the committed manifest rather than a live filesystem scan;
- no handler implementation, Tauri wiring, Cargo dependency addition, live filesystem walk, caller-controlled path read, real IPC invocation, desktop launch, screenshot capture, installer publication, credential resolution, network call, remote action, repository administration, submission/provisioning state promotion, evaluation authority, DEMO-1 acceptance, or user-managed external-repo action is authorized or implied by this document.

## 8. Change log

- **v0.1.0 (2026-05-21):** initial manifest-contract acceptance for the `query_fixture_corpus_index` prerequisite. Defines the v0.1.0 closed `fixtures/slice-a/**` entry list, canonical manifest JSON layout, validation rules, future handler boundary, document relationships, and non-claims.
