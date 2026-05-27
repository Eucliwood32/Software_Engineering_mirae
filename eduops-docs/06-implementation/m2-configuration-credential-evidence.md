---
title: M2 Configuration and Credential Reference Evidence
document_id: EDUOPS-M2-CONFIG-CREDENTIAL-EVIDENCE
version: 0.1.0
status: accepted
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-CONFIG-CONTRACT
    - SWENG-EDUTECH-CREDENTIAL-STORAGE
    - SWENG-EDUTECH-CONFIG-FIXTURE-PLAN
  tests:
    - CFG-FIX-001
    - CFG-FIX-002
    - CFG-FIX-004
    - CFG-FIX-005
---

# M2 Configuration and Credential Reference Evidence

## 1. Gate result

M2 is accepted for the local fixture configuration and credential-reference scope.

```text
gate=M2-CONFIG-CREDENTIAL-REFERENCE
status=accepted
scope=deterministic configuration merge, effective hash, fixture-local credential references, invalid-config fail-safe evidence, offline zero-call evidence
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
raw_secret_persistence=false
remote=none
```

M2 does not claim production OS credential backend selection, GitHub live authentication, GitHub clone execution, settings UI completeness, migration beyond the current fixture scope, or production schema-file generation.

## 2. Implemented acceptance scope

Accepted M2 behavior:

- `eduops_config` defines `ConfigScope`, `ConfigRecord`, deterministic scope/key/source ordering, sorted canonical effective JSON, merge trace, and SHA-256 effective hash.
- `eduops_config` rejects unknown protected keys and raw-secret-like values with safe read-only error evidence.
- `eduops_config` records offline fixture isolation evidence with zero network and GitHub adapter calls.
- `eduops_credentials` defines fixture-local credential references with provider/status enums, register/status/rotate/revoke lifecycle, reference IDs, SHA-256 fingerprints, and redacted records.
- Credential fixture behavior keeps raw token strings out of redacted records and audit evidence.

## 3. RED to GREEN evidence

### M2-T1/M2-T2 deterministic configuration merge

RED command:

```bash
cargo test -p eduops_config --test m2_config_merge_contract -- --nocapture
```

Observed RED result:

```text
unresolved imports `merge_effective_config`, `ConfigRecord`, `ConfigScope`
```

GREEN command:

```bash
cargo test -p eduops_config --test m2_config_merge_contract -- --nocapture
```

Observed GREEN result:

```text
test deterministic_merge_applies_scope_precedence_and_effective_hash ... ok
```

### M2-T3 credential-reference lifecycle

RED command:

```bash
cargo test -p eduops_credentials --test m2_credential_reference_contract -- --nocapture
```

Observed RED result:

```text
unresolved imports `CredentialProvider`, `CredentialReferenceStore`, `CredentialStatus`, `RegisterCredentialReferenceRequest`, `RotateCredentialReferenceRequest`
```

GREEN command:

```bash
cargo test -p eduops_credentials --test m2_credential_reference_contract -- --nocapture
```

Observed GREEN result:

```text
test credential_reference_lifecycle_never_persists_raw_secret_material ... ok
```

### M2-T4 config safety and offline isolation

RED command:

```bash
cargo test -p eduops_config --test m2_config_safety_contract -- --nocapture
```

Observed RED result:

```text
unresolved imports `validate_config_records`, `assert_offline_fixture_isolated`, `OfflineFixtureRun`
```

GREEN command:

```bash
cargo test -p eduops_config --test m2_config_safety_contract -- --nocapture
```

Observed GREEN result:

```text
test unknown_protected_key_fails_safe_with_read_only_evidence ... ok
test offline_fixture_records_zero_network_or_github_calls ... ok
```

## 4. Gate validation commands

The following validation commands passed before this evidence record was prepared:

```bash
cargo fmt --all --check
npm run m0:check
cargo test --workspace
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q
git diff --check
```

Focused M2 tests included in `cargo test --workspace`:

```text
crates/eduops_config/tests/m2_config_merge_contract.rs: 1 passed
crates/eduops_config/tests/m2_config_safety_contract.rs: 2 passed
crates/eduops_credentials/tests/m2_credential_reference_contract.rs: 1 passed
```

## 5. Acceptance boundary and next milestone impact

M2 closes the local fixture gate for deterministic configuration and credential-reference behavior. It unblocks later clone-only GitHub adapter work only at the reference/config boundary; live GitHub authentication and mutation remain disabled until a later explicit gate.

Deferred items:

- production OS credential storage adapter selection and implementation;
- schema-file generation or external JSON Schema validation;
- broader settings UI behavior;
- student default-deny credential access beyond the fixture-local reference lifecycle;
- live GitHub clone-only adapter execution.

## 6. Closure statement

`M2-CONFIG-CREDENTIAL-REFERENCE` is accepted for the local fixture scope above. Ralph should stop at this clean milestone boundary unless the next milestone task queue is explicitly prepared in `ralph.md`.
