---
title: M8 SLICE-G Export Fixture Gate Evidence
document_id: EDUOPS-M8-SLICE-G-EXPORT-FIXTURE-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-EXPORTER-IMPLEMENTATION-SPEC
    - SWENG-EDUTECH-HWP-EXPORT
    - SWENG-EDUTECH-EXPORT-FIDELITY
    - SWENG-EDUTECH-BLOCK-SCHEMA
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
    - EDUOPS-M8-EXPORT-SPEC-BLOCKER
  tests:
    - eduops_export::m8_export_contract
    - eduops_export::m8_manifest_only_adapter
    - eduops_export::m8_export_safety_guards
---

# M8 SLICE-G Export Fixture Gate Evidence

## 1. Gate result

M8 is accepted-constrained for the fixture-local export type contract, the manifest-only fixture adapter, placeholder/fallback artifact records, deterministic canonical manifest hashing, and fail-closed safety guards. Real DOCX/HWPX generation, host converter execution, live external action, fidelity authority, privacy/legal policy authority, and DEMO-1 acceptance remain explicitly out of scope.

```text
gate=GATE-SLICE-G-EXPORT-FIXTURE
status=accepted-constrained
scope=ExportRequest/ExportResult/ExportArtifact/ExportManifest type contract with ExportTargetFormat (manifest_only/hwpx/docx), ExportWriterProfile (canonical_hwpx_generator_stub executable; canonical_docx_then_hwpx_converter, hancom_automation, libreoffice_uno deferred; server_side_converter prohibited), ExportRedactionProfile, ExportFallbackPolicy, ExportResultStatus, ExportArtifactKind, ExportWarningCode (EXPORT_*); assemble_manifest_only(request, document) emits deterministic canonical manifest JSON with sorted keys and hardcoded non-mutation safety flags, placeholder hwpx/docx artifacts with placeholder=true, optional fallback markdown artifact under warn_and_manifest policy, typed warnings for code/image/table/citation blocks, ExportUnsupportedBlock records plus EXPORT_UNSUPPORTED_BLOCK warnings for unknown block kinds, and deterministic audit event ids; fail-closed guards reject deferred writer profiles with EXPORT_HOST_PROCESS_BLOCKED, the prohibited server-side converter with EXPORT_LIVE_EXTERNAL_BLOCKED, raw credential-shaped values (GitHub PAT prefix, URL credential form) and case-insensitive denylist substring with EXPORT_RAW_SECRET_REJECTED before any artifact construction
constraint=real DOCX/HWPX/HWP/PDF generation, Hancom/LibreOffice/UNO/server-side converter execution, any host process invocation, live external action, real network call, fidelity threshold authority, privacy/legal retention policy authority, DEMO-1 evidence acceptance, and presenter-facing demonstration claim are explicitly out of scope
live_external_action=false
host_process_invoked=false
external_call_made=false
demo_claim_made=false
network_adapter_calls=0
real_docx_or_hwpx_writes=0
host_converter_executions=0
remote=none
```

M8 does not claim a real DOCX/HWPX writer, a host converter invocation, a live external action, a network call, a fidelity threshold acceptance, a privacy/legal policy approval, or DEMO-1 evidence acceptance.

## 2. Implemented acceptance scope

Accepted M8 behavior, per `docs/02-design-planning/exporter-implementation-specification.md` §4 §5 §6 §7:

- `eduops_export` defines the type contract from §4: `ExportRequestDraft`/`ExportRequest`, `ExportResultDraft`/`ExportResult`, `ExportArtifactDraft`/`ExportArtifact`, `ExportArtifactHashEntry`, `ExportWarning`, `ExportUnsupportedBlock`, `ExportFallbackArtifact`, and `ExportManifest`. `ExportRequest::from_draft` and `ExportResult::from_draft` reject `live_external_action=true`, `host_process_allowed=true`, `external_call_made=true`, `host_process_invoked=true`, and `demo_claim_made=true` with `EXPORT_LIVE_EXTERNAL_BLOCKED`/`EXPORT_HOST_PROCESS_BLOCKED`/`EXPORT_DEMO_CLAIM_BLOCKED`. `ExportArtifact::from_draft` rejects non-manifest hwpx/docx artifacts that are not `placeholder=true` with `EXPORT_PLACEHOLDER_REQUIRED`. The constant `EXPORT_MANIFEST_SCHEMA_VERSION = "eduops.export.manifest.v1"`.
- `eduops_export` defines the enumerated namespaces from §4 and §6: `ExportTargetFormat { ManifestOnly, Hwpx, Docx }`; `ExportWriterProfile { CanonicalHwpxGeneratorStub, CanonicalDocxThenHwpxConverter, HancomAutomation, LibreofficeUno, ServerSideConverter }` with `is_executable_under_ralph`, `requires_host_process`, `requires_live_external_action` predicates; `ExportRedactionProfile { StudentVisible, ReviewerVisible, InternalReview }`; `ExportFallbackPolicy { ManifestOnly, WarnAndManifest, FailClosed }`; `ExportResultStatus { SucceededWithWarnings, FailedClosed, Unsupported }`; `ExportArtifactKind { ManifestJson, PlaceholderHwpx, PlaceholderDocx, FallbackMarkdown }`; `ExportWarningCode` covering `EXPORT_PROFILE_DEFERRED`, `EXPORT_LIVE_EXTERNAL_BLOCKED`, `EXPORT_HOST_PROCESS_BLOCKED`, `EXPORT_UNSUPPORTED_BLOCK`, `EXPORT_FONT_FALLBACK_DECLARED`, `EXPORT_TABLE_OVERFLOW_WARNING`, `EXPORT_IMAGE_PLACEHOLDER_DECLARED`, `EXPORT_CODE_MONOSPACE_FALLBACK`, `EXPORT_CITATION_REWRITE_DEFERRED`, `EXPORT_DEMO_CLAIM_BLOCKED`, `EXPORT_MANIFEST_HASH_MISMATCH`, and `EXPORT_RAW_SECRET_REJECTED`. The `EXPORT_*` namespace is intentionally distinct from `EDUOPS_IO_*`, `EDUOPS_GATE_*`, `EDUOPS_RUNNER_*`, and `EDUOPS_VALIDATION_*`.
- `eduops_export::assemble_manifest_only(request, document)` produces a deterministic `ExportResult` for the executable `canonical_hwpx_generator_stub` profile: emits a `manifest_json` artifact always, a `placeholder_hwpx` artifact for `Hwpx` target with `placeholder=true`, a `placeholder_docx` artifact for `Docx` target with `placeholder=true`, an optional `fallback_markdown` artifact under `WarnAndManifest` policy with a matching `ExportFallbackArtifact` record, typed warnings for code/image/table/citation supported blocks (`EXPORT_CODE_MONOSPACE_FALLBACK`/`EXPORT_IMAGE_PLACEHOLDER_DECLARED`/`EXPORT_TABLE_OVERFLOW_WARNING`/`EXPORT_CITATION_REWRITE_DEFERRED`), one `ExportUnsupportedBlock` record plus one `EXPORT_UNSUPPORTED_BLOCK` warning per unknown block kind, and deterministic audit event ids (`audit_export_manifest_<request_id>`, `audit_export_target_<format>_<request_id>`, plus per-block-warning audit ids). Each artifact carries a deterministic stable-input SHA-256 hash; `manifest_sha256` is SHA-256 over canonical JSON (the canonical JSON excludes `canonical_json` and `manifest_sha256` fields by construction). `external_call_made`, `host_process_invoked`, `live_external_action`, and `demo_claim_made` are hardcoded `false` literals in both the manifest and result.
- `eduops_export::scan_for_raw_export_secrets(text, denylist)` is a pure invariant scanner that rejects GitHub PAT prefix (`ghp_`, `github_pat_`), URL credential form `://user:token@host`, and case-insensitive denylist substring with `ExportSecretLeakage::CredentialShapedValue { reason }` or `ExportSecretLeakage::DenylistEntryObserved { reason }`. Rejection reasons never echo the raw matching substring. `assemble_manifest_only` runs `scan_for_raw_export_secrets` over `request_id`, `source_document_id`, `template_id`, `template_version`, `locale_profile`, `font_profile`, and `requested_by_role` and rejects any leakage with `EXPORT_RAW_SECRET_REJECTED` before any artifact is constructed.
- `eduops_export::assemble_manifest_only` enforces the §5 writer profile registry rule at entry: `CanonicalDocxThenHwpxConverter`/`HancomAutomation`/`LibreofficeUno` are rejected with `EXPORT_HOST_PROCESS_BLOCKED`; `ServerSideConverter` is rejected with `EXPORT_LIVE_EXTERNAL_BLOCKED`; any other non-executable profile is rejected with `EXPORT_PROFILE_DEFERRED`.

## 3. RED to GREEN evidence

### M8-T1 export type contract

```text
RED command:    cargo test -p eduops_export --test m8_export_contract -- --nocapture
RED result:     unresolved EXPORT_MANIFEST_SCHEMA_VERSION / ExportArtifact / ExportArtifactDraft / ExportArtifactKind / ExportError / ExportFallbackPolicy / ExportManifest / ExportRedactionProfile / ExportRequest / ExportRequestDraft / ExportResult / ExportResultDraft / ExportResultStatus / ExportTargetFormat / ExportWarning / ExportWarningCode / ExportWriterProfile imports
GREEN command:  cargo test -p eduops_export --test m8_export_contract -- --nocapture
GREEN result:   20 passed; 0 failed
Commit:         fdede30
```

### M8-T2 manifest-only fixture adapter

```text
RED command:    cargo test -p eduops_export --test m8_manifest_only_adapter -- --nocapture
RED result:     unresolved ExportFixtureBlock / ExportFixtureDocument / assemble_manifest_only imports
GREEN command:  cargo test -p eduops_export --test m8_manifest_only_adapter -- --nocapture
GREEN result:   13 passed; 0 failed
Commit:         50ef8ea
```

### M8-T3 fail-closed safety guards

```text
RED command:    cargo test -p eduops_export --test m8_export_safety_guards -- --nocapture
RED result:     unresolved ExportSecretLeakage / scan_for_raw_export_secrets imports
GREEN command:  cargo test -p eduops_export --test m8_export_safety_guards -- --nocapture
GREEN result:   13 passed; 0 failed
Commit:         01a35bd
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> M8-T1 20 passed; M8-T2 13 passed; M8-T3 13 passed; M7-T1 6 passed; M7-T2 9 passed; M7-T3 7 passed; M6-T1 10 passed; M6-T2 5 passed; M6-T3 9 passed; plus existing M1..M5 totals all green
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
docs link/JSON sweep                                                       -> bad_local_links=0; bad_json_parse=0
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Valid request creates `ExportResult` with `external_call_made=false`, `host_process_invoked=false`, `demo_claim_made=false` | `m8_manifest_only_adapter::manifest_only_adapter_emits_succeeded_with_safety_flags_false`, `m8_export_contract::export_result_constructs_with_required_safety_flags` | accepted |
| Manifest links source document ID, source commit SHA, canonical document hash, block schema version, template ID/version, writer profile, target format, and artifact hashes | `m8_manifest_only_adapter::manifest_links_request_and_canonical_source`, `manifest_records_artifact_hashes_for_each_artifact` | accepted |
| Placeholder DOCX/HWPX artifact records are explicitly marked `placeholder=true` and hash-linked to deterministic placeholder payloads | `m8_manifest_only_adapter::hwpx_target_emits_placeholder_hwpx_artifact_alongside_manifest`, `docx_target_emits_placeholder_docx_artifact_alongside_manifest`, `m8_export_contract::export_artifact_constructs_with_placeholder_flag_for_hwpx_docx`, `export_artifact_rejects_non_manifest_hwpx_or_docx_without_placeholder` | accepted |
| Unsupported blocks produce `EXPORT_UNSUPPORTED_BLOCK` records rather than silent success | `m8_manifest_only_adapter::manifest_emits_unsupported_block_record_for_unknown_kind`, `m8_export_safety_guards::unsupported_blocks_each_produce_one_record_and_warning` | accepted |
| Deferred writer profiles fail closed before any artifact record is emitted | `m8_export_safety_guards::deferred_canonical_docx_then_hwpx_converter_fails_closed_with_host_block`, `deferred_hancom_automation_fails_closed_with_host_block`, `deferred_libreoffice_uno_fails_closed_with_host_block`, `prohibited_server_side_converter_fails_closed_with_live_external_block` | accepted |
| Live external action, host process execution, and DEMO-1 claim flags are rejected | `m8_export_contract::export_request_rejects_live_external_action_true`, `export_request_rejects_host_process_allowed_true`, `export_result_rejects_live_or_host_or_demo_true` | accepted |
| Raw credential-like strings are rejected from request, manifest, artifact, warning, and diagnostic text | `m8_export_safety_guards::adapter_rejects_pat_prefix_in_request_field`, `adapter_rejects_url_credential_in_request_field`, `scan_rejects_github_pat_prefix`, `scan_rejects_github_pat_long_prefix`, `scan_rejects_url_credential_form`, `scan_rejects_denylist_substring_case_insensitive` | accepted |
| Canonical manifest serialization is deterministic across repeated construction | `m8_manifest_only_adapter::manifest_canonical_json_is_deterministic_across_repeated_assembly`, `manifest_sha256_is_sha256_over_canonical_json`, `manifest_canonical_json_excludes_self_hash_and_self_canonical_json_fields` | accepted |
| Audit event ids encode scope/format deterministically | `m8_manifest_only_adapter::manifest_records_deterministic_audit_event_ids` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- real DOCX, HWPX, HWP, or PDF generation;
- Hancom automation, LibreOffice/UNO, server-side converter, or any host process execution;
- converter installation, license checks, or host environment mutation;
- live external action, real network call, or remote publication;
- official grading, filing, publication, submission, or institutional document acceptance;
- final visual fidelity thresholds beyond fixture-local evidence fields;
- privacy/redaction profile authority beyond fixture profile identifiers (`student_visible`/`reviewer_visible`/`internal_review`);
- DEMO-1 acceptance, presenter-facing claim closure, or working-demonstration evidence approval;
- a cryptographic source URL hash beyond the artifact's deterministic stable-input SHA-256;
- the placeholder HWPX/DOCX artifact representing real `.hwpx`/`.docx` bytes (each carries `placeholder=true` and a deterministic stable-input hash, not a real binary writer output);
- a complete font/locale/template/audit registry beyond fixture identifiers.

## 7. Follow-up

The following follow-up items are required before broader export milestones may claim acceptance:

1. an authorized human owner must accept (or extend) the exporter implementation specification to cover real writer profile execution (`canonical_hwpx_generator` non-stub, `canonical_docx_then_hwpx_converter`, `hancom_automation`, `libreoffice_uno`, or any `server_side_converter` route) before any executable real-writer row is queued under Ralph;
2. author final fidelity thresholds per writer profile covering Korean title/paragraph, heading hierarchy, table cell preservation, code block formatting, image dimensions/DPI tolerance, and citation/cross-reference preservation, with measurable accept/reject criteria;
3. author the privacy/redaction policy authority binding rules for student PII, institutional identifiers, instructor notes, and review-private blocks;
4. author the DEMO-1 acceptance criteria and the consolidated demonstration harness contract before DEMO-1 evidence may be claimed;
5. integrate the `assemble_manifest_only` adapter into a `ExportAdapter` trait implementation that the desktop UI and submission state machine can invoke deterministically;
6. extend the manifest-only adapter to additional supported block kinds when new canonical block schema versions are accepted.

## 8. Traceability

- [Exporter implementation specification — constrained fixture-local type contract](../02-design-planning/exporter-implementation-specification.md)
- [M8 exporter implementation specification gap closure](m8-export-spec-blocker.md)
- [HWP and HWPX export strategy](../02-design-planning/hwp-export-strategy.md)
- [Export fidelity acceptance](../02-design-planning/export-fidelity-acceptance.md)
- [Working demonstration and evidence plan](../03-verification-validation/working-demonstration-evidence-plan.md)
- [Software test description](../03-verification-validation/software-test-description.md) — STD-047
- [Implementation milestones](implementation-milestones.md)
- [M7 SLICE-F GitHub clone-only adapter gate evidence](m7-slice-f-github-clone-only-evidence.md)
- [M6 SLICE-E advisory C/C++ runner gate evidence](m6-slice-e-advisory-cpp-runner-evidence.md)
- [M3 SLICE-B canonical document gate evidence](m3-slice-b-canonical-document-evidence.md)
