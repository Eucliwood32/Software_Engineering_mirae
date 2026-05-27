---
title: Configuration Contract
document_id: SWENG-EDUTECH-CONFIG-CONTRACT
version: 0.1.1
status: draft
created: 2026-05-14
updated: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CFR-013', 'EDUOPS-CFR-014', 'EDUOPS-CFR-017', 'EDUOPS-CFR-018', 'EDUOPS-CFR-019', 'EDUOPS-CFR-020', 'EDUOPS-CFR-021', 'EDUOPS-CFR-022', 'EDUOPS-CNFR-008', 'EDUOPS-CIR-018', 'EDUOPS-CIR-020', 'EDUOPS-CVR-010']
  related: ['SWENG-EDUTECH-PROCESS-IPC', 'SWENG-EDUTECH-INTERNAL-API', 'SWENG-EDUTECH-DOMAIN-IDL', 'SWENG-EDUTECH-CONFIG-FIXTURE-PLAN']
  iso9001: ['7.5', '8.3.3', '8.3.4', '8.5.1', '9.1']
---

# Configuration Contract

## 1. Purpose

This document defines the beta configuration contract for EduOps. It converts developer-facing configuration questions into controlled requirements before SLICE-A source-code implementation. Configuration is treated as product behavior, not local implementation convenience.

## 2. Configuration scopes and precedence

EduOps shall resolve configuration in the following deterministic order. Later scopes may override earlier scopes only when the key is explicitly marked overrideable for the actor and mode.

| Precedence | Scope | Storage location seed | Typical owner | Override rule |
|---|---|---|---|---|
| 1 | `app_default` | packaged read-only defaults | product | never edited by users |
| 2 | `system` | machine-level controlled config | admin/operator | may set installation/workspace defaults |
| 3 | `user` | `%APPDATA%/EduOps/config.json` or equivalent | authenticated local user | may set locale, UI, notification, local paths |
| 4 | `course` | course root `.eduops/course.config.json` | instructor/admin | may set course policies, evaluation/export profiles |
| 5 | `repository` | repository `.eduops/repository.config.json` | system/instructor | may set repository-local topology and evidence rules |
| 6 | `runtime_override` | signed request/CLI dry-run argument | application core | limited to diagnostic or fixture mode; audited |

Unknown keys shall fail validation unless the schema version explicitly allows an `x_` extension namespace. The merged configuration shall be hashable and reproducible from the stored records.

## 3. Required configuration key families

| Candidate | Key family | Required baseline |
|---|---|---|
| `EDUOPS-CFR-013` | hierarchy and merge | deterministic merge, overrideable key registry, actor/mode authorization |
| `EDUOPS-CFR-014` | workspace root | CLI argument > `EDUOPS_HOME` > OS profile value > `%LOCALAPPDATA%/EduOps`; invalid roots fail safe |
| `EDUOPS-CFR-017` | evaluation profile | advisory Clang/LLVM fixture profile first; official runner profile requires later sandbox approval |
| `EDUOPS-CFR-018` | export profile | DOCX/HWPX/HWP converter path, template, warning policy, and fallback behavior |
| `EDUOPS-CFR-019` | rendering/profile | HTML/SVG/Canvas/WebGL profile, Korean font fallback, NFC normalization, and fallback snapshot behavior |
| `EDUOPS-CFR-020` | offline/sync | offline mode, queue limits, retry/backoff, and no-network fixture mode |
| `EDUOPS-CFR-021` | diagnostics/audit | log level, redaction profile, retention days, audit export boundary |
| `EDUOPS-CFR-022` | update channel | beta/stable channel, signed update check, rollback policy, update disable behavior |

## 4. Format and schema baseline

- Primary serialized format: JSON with canonical UTF-8, LF, sorted keys for evidence hashing.
- Schema path seed: `schemas/config/v1.json` in the future implementation repository.
- Every persisted config record includes `schema_version`, `scope`, `key`, `value_json`, `effective_hash`, `source_ref`, `created_at`, `updated_at`, and `updated_by`.
- Schema migration is explicit and auditable; incompatible schema versions boot read-only or quarantine the affected scope.
- Secret values are never stored in configuration records. Configuration stores only `CredentialRef` values defined in [Credential Storage Contract](credential-storage-contract.md).

## 5. Authorization and audit

Protected configuration changes shall use backend commands only. UI hiding is not authorization. Every accepted or denied `config.set` and every credential-reference binding emits an `AuditEvent` with before/after hashes and a redacted diff class. Student actors cannot read or mutate credential keys, update-channel keys, course policy keys, or repository backend keys unless a later accepted policy explicitly permits a narrow read-only view.

## 6. Acceptance gates

| Gate | Acceptance criterion | Verification link |
|---|---|---|
| `G-CFR-1` | `schemas/config/v1.json` and fixture records define all P0 key families before SLICE-A coding. | [Configuration Fixture Plan](../03-verification-validation/configuration-fixture-plan.md) |
| `G-CFR-2` | identical inputs produce byte-identical merged configuration and hash. | `EDUOPS-CVR-005` |
| `G-CFR-3` | clean first run succeeds with app defaults and no live external services. | `EDUOPS-CNFR-008` |
| `G-CFR-4` | invalid or unknown protected keys produce explicit errors and read-only safe boot where needed. | `EDUOPS-CVR-008` |
| `G-CFR-5` | offline fixture mode performs zero GitHub/network adapter calls. | `EDUOPS-CVR-009` |

## 7. Open review items

1. Confirm whether the implementation repository should keep JSON Schema files under `schemas/config/` or `crates/eduops-config/schemas/`.
2. Confirm whether the first public beta exposes a settings UI for all key families or only workspace, GitHub auth reference, evaluation profile, export profile, and diagnostics.
3. Confirm whether update-channel controls are included in the first beta or deferred to packaging hardening.
