---
title: M4 SLICE-C Roster, Identity, and Workspace Gate Evidence
document_id: EDUOPS-M4-SLICE-C-ROSTER-IDENTITY-WORKSPACE-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-ROSTER-SCHEMA
    - SWENG-EDUTECH-ACM
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
  tests:
    - eduops_domain::m4_roster_import_contract
    - eduops_domain::m4_identity_binding_contract
    - eduops_storage::m4_workspace_provisioning_contract
    - eduops_storage::m4_access_control_contract
---

# M4 SLICE-C Roster, Identity, and Workspace Gate Evidence

## 1. Gate result

M4 is accepted for the fixture-local roster, identity binding, workspace provisioning, and default-deny cross-student access-control boundary.

```text
gate=GATE-SLICE-C-ROSTER-IDENTITY-WORKSPACE
status=accepted-constrained
scope=deterministic roster import evidence with PII-safe redaction, identity binding state machine with duplicate detection and override evidence, fixture-local per-student workspace provisioning requiring an accepted binding, and default-deny cross-student access-control decision evidence
constraint=production identity provider, live GitHub identity verification, classroom LMS connector, section-aware policy engine, deletion/withdrawal, retention/archive workflows, and submission/grade state machine all out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
remote=none
```

M4 does not claim production OS-protected credential storage for identity material, live GitHub identity verification, email invitation send, classroom LMS connector, section-aware contextual policy beyond course-level eligibility, TA-write delegation through scoped tokens, retention/archive/withdrawal flows, submission/grade authorization, audit-log persistence, or instructor approval UI.

## 2. Implemented acceptance scope

Accepted M4 behavior:

- `eduops_domain` defines `ROSTER_SCHEMA_VERSION = "eduops.roster/0.1"`, `RosterRecordStatus`, `RosterRecordInput`, `RosterRecord`, `RosterRecordRejection`, `RosterImportRequest`, `RosterImportEvidence`, `RedactedRosterRecord`, `import_roster_records`, and `redact_roster_record`.
- `eduops_domain` enforces required-field validation, course-id consistency, PII denylist guard, duplicate-internal-id rejection, duplicate-github-username rejection, deterministic sorted canonical evidence JSON, SHA-256 file-content/evidence hashes, and SHA-256 fingerprints for redacted email and GitHub username.
- `eduops_domain` defines `IdentityBindingStatus`, `IdentityBindingOverride`, `IdentityBinding`, `IdentityBindingError`, and `IdentityBindingRegistry` with `invite`/`bind`/`bind_with_override`/`snapshot`. Re-invite of the same student with a different GitHub claim returns `EDUOPS_IDENTITY_DUPLICATE_INTERNAL_ID`; re-invite with the same claim returns `EDUOPS_IDENTITY_INVALID_TRANSITION`. `bind` requires a prior Invited state and rejects duplicate `approved_github_username` unless `bind_with_override` supplies complete `actor`/`reason`/`approval_ref` evidence.
- `eduops_storage` defines `ProvisionWorkspaceRequest`, `ProvisionWorkspaceEvidence`, and `LocalStorageAdapter::provision_workspace` that rejects non-local mode and live external action, requires `IdentityBindingStatus::Bound`, validates `course_id`/`student_internal_id` against path-escape, creates per-student `assignment`/`workspace`/`knowledge` directories, writes a deterministic `.provision-manifest.json` with SHA-256-fingerprinted GitHub username, and is idempotent.
- `eduops_storage` defines `AccessSubject`, `AccessSubjectRole`, `AccessResource`, `AccessAction`, `AccessDecision`, `AccessDecisionEvidence`, and `decide_access` with default-deny semantics, student self-resource allow, cross-student deny, instructor/admin allow within course scope, and TA read-only allow.

## 3. RED to GREEN evidence

### M4-T1/M4-T2 deterministic roster import and PII-safe redaction

```text
RED command:    cargo test -p eduops_domain --test m4_roster_import_contract -- --nocapture
RED result:     unresolved imports for roster types
GREEN command:  cargo test -p eduops_domain --test m4_roster_import_contract -- --nocapture
GREEN result:   6 passed; 0 failed
Commit:         0edb19f
```

### M4-T3 identity binding lifecycle with override evidence

```text
RED command:    cargo test -p eduops_domain --test m4_identity_binding_contract -- --nocapture
RED result:     unresolved identity-binding type imports
GREEN command:  cargo test -p eduops_domain --test m4_identity_binding_contract -- --nocapture
GREEN result:   8 passed; 0 failed
Commit:         a6dd318
```

### M4-T4 local workspace provisioning with bound-binding gate

```text
RED command:    cargo test -p eduops_storage --test m4_workspace_provisioning_contract -- --nocapture
RED result:     missing ProvisionWorkspaceRequest and provision_workspace method
GREEN command:  cargo test -p eduops_storage --test m4_workspace_provisioning_contract -- --nocapture
GREEN result:   6 passed; 0 failed
Commit:         5a7d29c
```

### M4-T5 cross-student access-control decision evidence

```text
RED command:    cargo test -p eduops_storage --test m4_access_control_contract -- --nocapture
RED result:     unresolved access-control type imports
GREEN command:  cargo test -p eduops_storage --test m4_access_control_contract -- --nocapture
GREEN result:   7 passed; 0 failed
Commit:         18d1057
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> passed=65 failed=0 ignored=0
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
docs link/JSON sweep                                                       -> markdown_files=100; json_files=9; bad_local_links=0; bad_json_parse=0
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Cleartext student PII is absent from generated evidence except where explicitly allowed by schema | `m4_roster_import_contract::redacted_record_omits_raw_email_and_raw_github_username`, `m4_roster_import_contract::deterministic_import_produces_stable_evidence_hash` (canonical evidence uses redacted records) | accepted |
| Duplicate identity binding is rejected unless override evidence exists | `m4_identity_binding_contract::duplicate_institutional_id_binding_is_rejected_without_override`, `duplicate_github_username_binding_is_rejected_without_override`, `override_allows_duplicate_github_username_when_evidence_present` | accepted |
| Privacy denylist scan passes for in-test PII patterns | `m4_roster_import_contract::pii_denylist_pattern_in_display_name_is_rejected` | accepted within in-test denylist scope (production denylist remains future work) |
| Student actor cannot read another student's protected binding or workspace state | `m4_access_control_contract::student_cannot_read_other_student_workspace`, `student_cannot_read_other_student_binding`, `student_cannot_write_other_student_workspace`, `missing_subject_actor_is_denied_by_default`, `missing_resource_identifiers_are_denied_by_default` | accepted |
| Workspace provisioning requires accepted binding and is path-safe | `m4_workspace_provisioning_contract::provision_creates_per_student_workspace_for_bound_binding`, `provision_rejects_invited_binding`, `provision_rejects_path_escape_in_identifiers`, `provision_rejects_live_external_action`, `provision_rejects_non_local_adapter_mode`, `provision_is_idempotent_for_existing_workspace` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- production OS-protected identity material storage;
- live GitHub identity verification or invitation;
- email invitation send or notification delivery;
- classroom LMS connector or roster sync;
- section-aware contextual policy engine;
- TA-write delegation through scoped tokens;
- retention/archive/withdrawal workflows or PII rotation evidence;
- submission/grade authorization (M5);
- audit-log persistence beyond in-memory `audit_event_id`;
- instructor approval UI or workflow surface;
- production PII denylist artifact and review record.

## 7. Follow-up

The following follow-up items are required before broader identity-related milestones may claim acceptance:

1. author a controlled PII denylist artifact and approval record;
2. add explicit `Imported` and `Rejected`/`Withdrawn` lifecycle states to `IdentityBindingStatus` when their tests exist;
3. add section-aware and time-aware contextual policy fields to `AccessDecisionEvidence` when M5 submission/feedback flows require them;
4. add scoped TA write delegation through `IdentityBindingOverride` or a TA-scope record;
5. add audit-log persistence and replay tests when an audit sink exists;
6. proceed to M5 assignment publication, sync, and submission state machine once the state-machine implementation tables entry criterion is met.

## 8. Traceability

- [Roster schema and identity policy](../02-design-planning/roster-schema-and-identity-policy.md)
- [Access control and authorization model](../02-design-planning/access-control-authorization-model.md)
- [Implementation milestones](implementation-milestones.md)
- [M3 SLICE-B canonical document gate evidence](m3-slice-b-canonical-document-evidence.md)
- [M2 configuration and credential reference evidence](m2-configuration-credential-evidence.md)
