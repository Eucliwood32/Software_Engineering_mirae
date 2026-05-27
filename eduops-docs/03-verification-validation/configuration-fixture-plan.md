---
title: Configuration Fixture Plan
document_id: SWENG-EDUTECH-CONFIG-FIXTURE-PLAN
version: 0.1.0
status: draft
created: 2026-05-14
updated: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CVR-005', 'EDUOPS-CVR-006', 'EDUOPS-CVR-007', 'EDUOPS-CVR-008', 'EDUOPS-CVR-009']
  related: ['SWENG-EDUTECH-CONFIG-CONTRACT', 'SWENG-EDUTECH-CREDENTIAL-STORAGE', 'SWENG-EDUTECH-STD']
  iso9001: ['8.3.4', '8.3.5', '9.1']
---

# Configuration Fixture Plan

## 1. Purpose

This plan defines objective fixtures for configuration behavior before EduOps SLICE-A/B implementation. The plan keeps configuration requirements testable and prevents hidden defaults, secret leakage, and network side effects from entering early code.

## 2. Fixture set

| Fixture ID | Candidate | Scenario | Required evidence |
|---|---|---|---|
| `CFG-FIX-001` | `EDUOPS-CVR-005` | Merge app/default/user/course/repository/runtime fixture files twice. | identical `effective-config.json`, `effective-config.sha256`, merge trace |
| `CFG-FIX-002` | `EDUOPS-CVR-006` | Register a synthetic GitHub token fixture and generate logs/diagnostics. | zero raw-token matches; credential reference/fingerprint only |
| `CFG-FIX-003` | `EDUOPS-CVR-007` | Migrate config v1 to v2 and run compatibility read. | migration audit, before/after hash, no dropped required key |
| `CFG-FIX-004` | `EDUOPS-CVR-008` | Boot with unknown protected key and malformed value. | explicit error code, safe read-only boot or blocked boot |
| `CFG-FIX-005` | `EDUOPS-CVR-009` | Run offline fixture with network/GitHub disabled. | adapter-call log showing zero live GitHub/network calls |
| `CFG-FIX-006` | `EDUOPS-CNFR-008` | Clean user profile first run. | default workspace creation plan, no required external service |
| `CFG-FIX-007` | `EDUOPS-CNFR-011` | Student actor queries credential and protected course policy keys. | default-deny result and audit event |

## 3. Seed commands

The future implementation repository should provide equivalent commands:

```bash
eduops config validate --fixture fixtures/config/cfg-fix-001
eduops config merge --fixture fixtures/config/cfg-fix-001 --output build/config/effective-config.json
eduops config migrate --from fixtures/config/v1 --to-version v2 --dry-run
eduops boot --dry-run --offline --fixture fixtures/config/cfg-fix-005
eduops diagnostics scan-secrets build/config build/logs build/diagnostics
```

Before these commands exist, reviewers shall verify that the controlled contract defines inputs, outputs, pass/fail criteria, and traceability.

## 4. Acceptance criteria

- Configuration fixture outputs are deterministic and hashable.
- Raw credentials are absent from all generated files and logs.
- Invalid configuration cannot silently fall back to unsafe defaults.
- Offline mode prohibits live GitHub/network calls until an explicit sandbox/live gate is approved.
- Every accepted/denied protected configuration action produces an `AuditEvent`.
