---
title: Exporter Implementation Specification — Constrained Fixture-Local Type Contract
document_id: SWENG-EDUTECH-EXPORTER-IMPLEMENTATION-SPEC
version: 0.1.0
status: accepted-constrained-for-fixture-implementation
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-M8-EXPORT-SPEC-BLOCKER
    - SWENG-EDUTECH-HWP-EXPORT
    - SWENG-EDUTECH-EXPORT-FIDELITY
    - SWENG-EDUTECH-BLOCK-SCHEMA
  requirements:
    - EDUOPS-FR-044
    - EDUOPS-FR-045
    - EDUOPS-FR-046
    - EDUOPS-FR-055
    - EDUOPS-NFR-016
    - EDUOPS-NFR-019
    - EDUOPS-NFR-022
  verification:
    - STD-047
---

# Exporter Implementation Specification — Constrained Fixture-Local Type Contract

## 1. Purpose

This specification authorizes a constrained M8 implementation slice for the `eduops_export` crate. The slice defines fixture-local export request/result/artifact/manifest contracts and deterministic manifest-only evidence. It does not authorize real DOCX/HWPX generation, host converter execution, external converter services, official export fidelity acceptance, privacy/legal policy approval, or DEMO-1 acceptance.

The approved implementation profile is intentionally narrow:

```text
canonical block document fixture
→ ExportRequest
→ manifest-only export adapter
→ ExportManifest JSON + placeholder/fallback artifact records
→ deterministic hashes and warnings
```

## 2. Scope decision

| Field | Value |
|---|---|
| Decision ID | `EDUOPS-DEC-M8-CONSTRAINED-EXPORT-SPEC` |
| Authorized scope | Fixture-local type contract and manifest-only export evidence |
| Initial writer profile | `canonical-hwpx-generator` as a planned/stub fixture profile only |
| Target formats | `hwpx` and `docx` identifiers may be represented in requests/results; no real document writer is invoked |
| Runtime execution | Pure in-process data transformation only |
| External action | Not allowed |
| Host converter execution | Not allowed |
| DEMO-1 claim | Not allowed; only local candidate evidence may be assembled later |
| Fidelity authority | Not granted; existing seed thresholds remain design anchors, not final acceptance authority |
| Privacy/legal authority | Not granted; only profile identifiers and redaction records are modeled |

## 3. Non-claims

This specification does not approve or implement:

- real DOCX, HWPX, HWP, or PDF generation;
- Hancom automation, LibreOffice/UNO, server-side converters, or any host process execution;
- converter installation, license checks, or host environment mutation;
- live external action or network calls;
- official grading, filing, publication, submission, or institutional document acceptance;
- final visual fidelity thresholds beyond fixture-local evidence fields;
- privacy/legal retention policy approval;
- DEMO-1 acceptance or presenter-facing claim closure.

## 4. Data model

### 4.1 `ExportRequest`

`ExportRequest` shall contain the fields below. Implementations may model them as Rust structs/enums, but serialized evidence shall use canonical snake_case JSON keys sorted by the existing canonicalization helper selected by the crate.

| Field | Type | Required | Rule |
|---|---|---:|---|
| `request_id` | string | yes | Non-empty stable fixture identifier. |
| `source_document_id` | string | yes | Canonical document identifier. |
| `source_commit_sha` | string | yes | Git commit SHA or fixture SHA for the canonical source. |
| `block_schema_version` | string | yes | Canonical block schema version. |
| `canonical_document_hash` | hex string | yes | SHA-256 over canonical fixture payload. |
| `target_format` | enum | yes | `hwpx`, `docx`, or `manifest_only`. |
| `writer_profile` | enum | yes | Initially only `canonical_hwpx_generator_stub` is executable under Ralph. |
| `locale_profile` | string | yes | Example: `ko-KR`. |
| `font_profile` | string | yes | Fixture profile name only; no host font probing. |
| `redaction_profile` | enum | yes | `student_visible`, `reviewer_visible`, or `internal_review`. |
| `fallback_policy` | enum | yes | `manifest_only`, `warn_and_manifest`, or `fail_closed`. |
| `template_id` | string | yes | Template fixture identifier. |
| `template_version` | string | yes | Template fixture version. |
| `requested_by_role` | string | yes | Fixture role identifier; no live identity lookup. |
| `live_external_action` | bool | yes | Must be `false`. |
| `host_process_allowed` | bool | yes | Must be `false`. |

The request is invalid if `live_external_action=true`, `host_process_allowed=true`, `writer_profile` names Hancom/LibreOffice/server-side converter execution, or a field contains a raw credential-like value.

### 4.2 `ExportResult`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `request_id` | string | yes | Mirrors `ExportRequest.request_id`. |
| `status` | enum | yes | `succeeded_with_warnings`, `failed_closed`, or `unsupported`. |
| `manifest` | object | yes | `ExportManifest`. |
| `artifacts` | array | yes | Zero or more `ExportArtifact` records. |
| `warnings` | array | yes | Zero or more `ExportWarning` records. |
| `diagnostics` | array | yes | Human-readable fixture diagnostics without secrets. |
| `external_call_made` | bool | yes | Must be `false`. |
| `host_process_invoked` | bool | yes | Must be `false`. |
| `demo_claim_made` | bool | yes | Must be `false`. |

The manifest-only adapter may return `succeeded_with_warnings` when it produces a complete manifest and explicit unsupported/fallback records. It shall return `failed_closed` when required canonical linkage, hashes, template metadata, or safety flags are missing.

### 4.3 `ExportArtifact`

| Field | Type | Required | Rule |
|---|---|---:|---|
| `artifact_id` | string | yes | Stable identifier. |
| `artifact_kind` | enum | yes | `manifest_json`, `placeholder_hwpx`, `placeholder_docx`, or `fallback_markdown`. |
| `target_format` | enum | yes | `manifest_only`, `hwpx`, `docx`, or `markdown`. |
| `path_hint` | string | yes | Relative path hint inside fixture evidence; no absolute path required. |
| `sha256` | hex string | yes | SHA-256 over artifact bytes or deterministic placeholder payload. |
| `byte_length` | integer | yes | Non-negative byte count. |
| `derived_from_block_ids` | array[string] | yes | Canonical block IDs represented by the artifact or placeholder. |
| `placeholder` | bool | yes | Must be `true` for non-manifest DOCX/HWPX records in this constrained slice. |

### 4.4 `ExportManifest`

`ExportManifest` is the primary M8 evidence object. It shall include:

| Field | Rule |
|---|---|
| `manifest_schema_version` | Fixed initial value `eduops.export.manifest.v1`. |
| `request_id` | Mirrors request. |
| `source_document_id` | Mirrors request. |
| `source_commit_sha` | Mirrors request. |
| `block_schema_version` | Mirrors request. |
| `canonical_document_hash` | Mirrors request. |
| `template_id` / `template_version` | Mirrors request. |
| `writer_profile` | Stub writer profile identifier. |
| `target_format` | Requested target format. |
| `locale_profile` / `font_profile` | Fixture profile identifiers. |
| `redaction_profile` | Request profile identifier. |
| `artifact_hashes` | Stable list of `artifact_id`, `sha256`, and `byte_length`. |
| `warnings` | Stable warning records. |
| `unsupported_blocks` | Stable unsupported block records. |
| `fallback_artifacts` | Stable fallback artifact records. |
| `audit_event_ids` | Fixture audit identifiers only. |
| `external_call_made` | Must be `false`. |
| `host_process_invoked` | Must be `false`. |
| `live_external_action` | Must be `false`. |
| `demo_claim_made` | Must be `false`. |
| `manifest_sha256` | SHA-256 over canonical manifest content excluding this field. |

## 5. Writer profile registry

The constrained registry contains one executable profile and several deferred profiles.

| Profile | Status | Rule |
|---|---|---|
| `canonical_hwpx_generator_stub` | executable fixture profile | Pure data/manifest path only; no real HWPX writer. |
| `canonical_docx_then_hwpx_converter` | deferred | Requires converter/tool/license decision; not executable by Ralph. |
| `hancom_automation` | deferred | Requires Hancom license and host automation policy; not executable by Ralph. |
| `libreoffice_uno` | deferred | Requires host process and fidelity policy approval; not executable by Ralph. |
| `server_side_converter` | prohibited in Ralph | Live external service boundary; not executable by Ralph. |

Profile selection shall be deterministic:

1. If `writer_profile=canonical_hwpx_generator_stub` and `host_process_allowed=false` and `live_external_action=false`, the manifest-only adapter may run.
2. If any deferred/prohibited profile is selected, the adapter shall fail closed before artifact generation and emit `EXPORT_PROFILE_DEFERRED` or `EXPORT_LIVE_EXTERNAL_BLOCKED`.
3. If target format is `hwpx` or `docx`, non-manifest artifacts must be placeholder records with `placeholder=true`.

## 6. Warning and failure codes

The M8 export code set is distinct from `EDUOPS_IO_*`, `EDUOPS_GATE_*`, `EDUOPS_RUNNER_*`, and `EDUOPS_VALIDATION_*`.

| Code | Meaning |
|---|---|
| `EXPORT_PROFILE_DEFERRED` | Requested profile is not executable in Ralph scope. |
| `EXPORT_LIVE_EXTERNAL_BLOCKED` | Request would require live external action. |
| `EXPORT_HOST_PROCESS_BLOCKED` | Request would require Hancom/LibreOffice/host process execution. |
| `EXPORT_UNSUPPORTED_BLOCK` | Canonical block type cannot be represented by the constrained fixture path. |
| `EXPORT_FONT_FALLBACK_DECLARED` | Font fallback is represented as a warning record. |
| `EXPORT_TABLE_OVERFLOW_WARNING` | Table width/page overflow is represented as a warning record. |
| `EXPORT_IMAGE_PLACEHOLDER_DECLARED` | Image is represented by hash/dimension metadata, not real embedded output. |
| `EXPORT_CODE_MONOSPACE_FALLBACK` | Code block formatting is represented by declared fallback. |
| `EXPORT_CITATION_REWRITE_DEFERRED` | Citation/cross-reference generation is deferred. |
| `EXPORT_DEMO_CLAIM_BLOCKED` | Request/result attempted to mark DEMO-1 acceptance. |
| `EXPORT_MANIFEST_HASH_MISMATCH` | Manifest hash verification failed. |
| `EXPORT_RAW_SECRET_REJECTED` | Credential-like or secret-like text was detected in evidence fields. |

## 7. Fixture-local acceptance rules

The constrained M8 tests shall verify:

1. a valid request creates an `ExportResult` with `external_call_made=false`, `host_process_invoked=false`, and `demo_claim_made=false`;
2. the manifest links source document ID, source commit SHA, canonical document hash, block schema version, template ID/version, writer profile, target format, and artifact hashes;
3. placeholder DOCX/HWPX artifact records are explicitly marked `placeholder=true` and hash-linked to deterministic placeholder payloads;
4. unsupported blocks produce `EXPORT_UNSUPPORTED_BLOCK` records rather than silent success;
5. deferred writer profiles fail closed before any artifact record is emitted;
6. live external action, host process execution, and DEMO-1 claim flags are rejected;
7. raw credential-like strings are rejected from request, manifest, artifact, warning, and diagnostic text;
8. canonical manifest serialization is deterministic across repeated construction.

## 8. Ralph task queue seed

After this specification is accepted, Ralph may create the following executable rows:

| Task | Purpose | First RED command |
|---|---|---|
| `M8-PREP-RERUN` | Re-evaluate M8 under constrained fixture-local scope and create RED/GREEN rows. | docs/control validation |
| `M8-T1` | Define `ExportRequest`, `ExportResult`, `ExportArtifact`, `ExportManifest`, writer profile, target format, status, and warning-code types. | `cargo test -p eduops_export --test m8_export_contract -- --nocapture` |
| `M8-T2` | Implement manifest-only fixture adapter with deterministic canonical manifest hashing. | `cargo test -p eduops_export --test m8_manifest_only_adapter -- --nocapture` |
| `M8-T3` | Add negative guards for deferred profiles, host process, live external action, DEMO-1 claim, unsupported blocks, and raw-secret leakage. | `cargo test -p eduops_export --test m8_export_safety_guards -- --nocapture` |
| `M8-GATE` | Record constrained M8 evidence and non-claims. | focused export tests plus repository validation |

## 9. Gate evidence non-claims

An accepted constrained M8 gate may claim only:

```text
fixture-local export type contracts
manifest-only export evidence
placeholder/fallback artifact records
deterministic manifest hashing
safety guards against live/host/demo/secret leakage
```

It shall not claim real DOCX/HWPX generation, visual fidelity, external converter availability, institutional document approval, DEMO-1 acceptance, or live export readiness.
