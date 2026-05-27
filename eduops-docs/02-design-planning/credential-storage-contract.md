---
title: Credential Storage Contract
document_id: SWENG-EDUTECH-CREDENTIAL-STORAGE
version: 0.1.0
status: draft
created: 2026-05-14
updated: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CFR-015', 'EDUOPS-CNFR-006', 'EDUOPS-CNFR-011', 'EDUOPS-CIR-019', 'EDUOPS-CIR-021', 'EDUOPS-CVR-006']
  related: ['SWENG-EDUTECH-CONFIG-CONTRACT', 'SWENG-EDUTECH-GITHUB-TOPOLOGY-TOKEN', 'SWENG-EDUTECH-ACCESS-CONTROL']
  iso9001: ['7.5', '8.3.3', '8.5.1', '9.1']
---

# Credential Storage Contract

## 1. Scope

This contract controls credential references used by EduOps configuration and adapters. It applies to GitHub App/PAT/session tokens, future self-hosted Git credentials, converter licenses, signing key references, and any future external connector credential.

## 2. Baseline decision

EduOps configuration shall never persist raw credentials. The first Windows beta shall use OS-protected credential storage such as Windows Credential Manager or DPAPI-backed storage through a controlled adapter. Product records store only `CredentialRef` values, hashes/fingerprints, provider labels, expiry metadata, and audit evidence.

## 3. Credential reference model

| Field | Meaning | Control |
|---|---|---|
| `credential_ref_id` | stable identifier used in config and adapter calls | non-secret |
| `provider` | `github`, `self_hosted_git`, `export_converter`, `update_signing`, or future approved provider | enum-controlled |
| `secret_locator` | OS credential-store locator | redacted from student views; not a raw token |
| `fingerprint_sha256` | hash/fingerprint for identity checks | safe for audit |
| `created_by`, `created_at`, `rotated_at`, `expires_at` | lifecycle metadata | audit-bound |
| `status` | `active`, `expired`, `revoked`, `rotation_required`, `quarantined` | state-machine controlled |
| `allowed_scopes` | permitted product scopes | default-deny |

## 4. Required behavior

- Credential registration validates provider, scope, expiry, and access through dry-run or fixture-safe calls before becoming active.
- Rotation creates a new credential reference and marks the old reference revoked or rotation-required; product logs must not include raw values.
- Revocation prevents future adapter use and emits an audit event.
- Diagnostic packages include credential reference IDs and fingerprints only when permitted by redaction profile.
- Student role has no credential read capability. Instructor/admin views show status and reference metadata, not raw secret material.

## 5. Interfaces

The implementation shall expose controlled API signatures for:

- `credential.registerReference(provider, proof, scope, dry_run)`
- `credential.rotateReference(credential_ref_id, proof, reason)`
- `credential.revokeReference(credential_ref_id, reason)`
- `credential.getStatus(credential_ref_id)`

These APIs are authoritative backend commands/queries and shall be represented in [Internal API Contract](internal-api-contract.md).

## 6. Verification gates

| Gate | Acceptance criterion |
|---|---|
| `G-CRED-1` | raw token/string fixture is absent from logs, exports, Git files, diagnostic bundles, and generated manifests |
| `G-CRED-2` | student actor receives default-deny for credential status/detail queries |
| `G-CRED-3` | expired/revoked credential reference cannot be used by GitHub adapter fixture |
| `G-CRED-4` | rotation produces before/after audit evidence without raw credential exposure |

## 7. Open review items

1. Select the Rust crate or platform API wrapper for Windows Credential Manager/DPAPI.
2. Decide whether the first beta supports GitHub App device/login flow, PAT registration, or both.
3. Decide whether converter licenses are handled by the same credential adapter or a separate license adapter.
