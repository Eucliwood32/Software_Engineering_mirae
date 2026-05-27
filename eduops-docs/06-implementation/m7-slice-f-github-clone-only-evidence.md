---
title: M7 SLICE-F GitHub Clone-Only Adapter Gate Evidence
document_id: EDUOPS-M7-SLICE-F-GITHUB-CLONE-ONLY-EVIDENCE
version: 0.1.0
status: accepted-constrained
date: 2026-05-15
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - SWENG-EDUTECH-GITHUB-ADAPTER-SPEC
    - SWENG-EDUTECH-GITHUB-ADAPTER-SDD
    - SWENG-EDUTECH-GITHUB-TOPOLOGY
    - SWENG-EDUTECH-IMPLEMENTATION-MILESTONES
  tests:
    - eduops_git::m7_github_mode_gate_contract
    - eduops_git::m7_github_privacy_naming_contract
    - eduops_git::m7_github_clone_evidence_contract
---

# M7 SLICE-F GitHub Clone-Only Adapter Gate Evidence

## 1. Gate result

M7 is accepted-constrained for fixture-local GitHub clone-only adapter mode-gate enumeration, privacy naming evaluation, and clone-evidence envelope assembly with credential-leakage scanning. Live mode, real network calls, clone-readonly approval mechanics, and submission-state promotion authority remain explicitly out of scope.

```text
gate=GATE-SLICE-F-GITHUB-CLONE-ONLY
status=accepted-constrained
scope=GitHubAdapterMode enumeration (FakeLocal / MockHttp / CloneReadonly) with evaluate_mode_gate returning Allowed/Blocked decisions and audit ids; deterministic GITHUB_NON_CLONE_OPERATION_BLOCKED for any non-clone operation in any mode; GITHUB_LIVE_ACTION_BLOCKED for CloneReadonly without explicit gate approval; PrivacyNamingScope (Repository/Branch/Team/Ref) with evaluate_privacy_naming rejecting empty/PAT-prefix/email-like/SSN-like/long-digit-run/denylist candidates with GITHUB_PRIVACY_POLICY_VIOLATION and redacted reasons; AssembleCloneEvidenceRequest / GitHubCloneEvidence with hardcoded operation_class='clone-only', external_call_made=false, external_side_effect_made=false, github_mutation_made=false, no_raw_secret_observed=true literals and FNV-1a 64 source_repo_url_hash; scan_for_raw_credentials rejecting GitHub PAT prefix, URL credential form ://user:token@host, and denylist substring hits
constraint=live GitHub action, real network call, clone-readonly mode approval mechanics, mock-http fixture parsing format, real retry/rate-limit/backoff policy, credential-rotation behavior, submission-state promotion, real source-URL SHA-256 audit hash, instructor approval surface, and any host-process invocation are explicitly out of scope
live_external_action=false
network_adapter_calls=0
github_adapter_calls=0
github_mutation_made=false
clone_readonly_executions=0
remote=none
```

M7 does not claim a live GitHub clone, mock-http fixture replay, real retry/rate-limit/backoff policy, credential rotation, submission-state promotion, instructor approval surface, or any real GitHub network round-trip.

## 2. Implemented acceptance scope

Accepted M7 behavior:

- `eduops_git::github::mode_gate` defines `GitHubAdapterMode { FakeLocal, MockHttp, CloneReadonly }` with `token()`, `GitHubModeDecision { Allowed { ... } | Blocked { code, audit_event_id } }`, and `evaluate_mode_gate(mode, operation, clone_readonly_gate_approved)`. Non-clone operations (`Push`/`CreateRepository`/`DeleteRepository`) are blocked in every mode with `GITHUB_NON_CLONE_OPERATION_BLOCKED`. `CloneReadonly` without `clone_readonly_gate_approved=true` is blocked with `GITHUB_LIVE_ACTION_BLOCKED`. The legacy `mode_gate_allows` API is preserved for the M0 baseline check.
- `eduops_git::github::privacy` defines `PrivacyNamingScope { Repository, Branch, Team, Ref }`, `PrivacyNamingRequest { candidate, denylist, scope }`, and `PrivacyNamingDecision { Accept { sanitized_name, audit_event_id } | Block { code, reason, audit_event_id } }`. `evaluate_privacy_naming` rejects empty candidates, GitHub PAT prefixes (`ghp_`, `github_pat_`), email-like substrings (`@` followed by `.`), SSN-like `xxx-xx-xxxx` patterns, denylist substring hits, and consecutive digit runs of 6 or more. Block reasons are redacted and never echo the raw matching substring. Accept emits a deterministic sanitized `[a-z0-9-_.]` name and a scope-tagged FNV-1a 64 audit id suffix.
- `eduops_git::github::clone_evidence` defines `AssembleCloneEvidenceRequest`, `GitHubCloneEvidence`, `GitHubCredentialLeakage { CredentialShapedValue | DenylistEntryObserved }`, `assemble_clone_evidence`, and `scan_for_raw_credentials`. The envelope hardcodes `operation_class="clone-only"`, `external_call_made=false`, `external_side_effect_made=false`, `github_mutation_made=false`, `no_raw_secret_observed=true`. The source URL is stored only as an FNV-1a 64 hash (`fnv1a64:...`); the raw URL is never stored. `assemble_clone_evidence` scans every input text field for raw credential leakage before constructing the envelope. `scan_for_raw_credentials(text, denylist)` rejects GitHub PAT prefix, URL credential form (`://...:...@`), and denylist substring hits.

## 3. RED to GREEN evidence

### M7-T1 GitHub adapter mode-gate enumeration

```text
RED command:    cargo test -p eduops_git --test m7_github_mode_gate_contract -- --nocapture
RED result:     unresolved GitHubAdapterMode / GitHubModeDecision / evaluate_mode_gate imports
GREEN command:  cargo test -p eduops_git --test m7_github_mode_gate_contract -- --nocapture
GREEN result:   6 passed; 0 failed
Commit:         29542a8
```

### M7-T2 GitHub privacy naming evaluator

```text
RED command:    cargo test -p eduops_git --test m7_github_privacy_naming_contract -- --nocapture
RED result:     unresolved PrivacyNamingDecision / PrivacyNamingRequest / PrivacyNamingScope / evaluate_privacy_naming imports
GREEN command:  cargo test -p eduops_git --test m7_github_privacy_naming_contract -- --nocapture
GREEN result:   9 passed; 0 failed
Commit:         3902dd0
```

### M7-T3 GitHub clone evidence envelope and credential leakage scan

```text
RED command:    cargo test -p eduops_git --test m7_github_clone_evidence_contract -- --nocapture
RED result:     unresolved AssembleCloneEvidenceRequest / GitHubCloneEvidence / GitHubCredentialLeakage / assemble_clone_evidence / scan_for_raw_credentials imports
GREEN command:  cargo test -p eduops_git --test m7_github_clone_evidence_contract -- --nocapture
GREEN result:   7 passed; 0 failed
Commit:         58c1724
```

## 4. Repository-level validation

```text
cargo fmt --all --check                                                    -> ok
npm run m0:check (rust-check, ui-typecheck, ui-build, fixture-check)       -> desktop-ui_typecheck=ok; desktop-ui_build=ok; fixture_corpus_status=ok
cargo test --workspace                                                     -> M7-T1 6 passed; M7-T2 9 passed; M7-T3 7 passed; M6-T1 10 passed; M6-T2 5 passed; M6-T3 9 passed; plus existing M1..M5 totals all green
python3 -m pytest tests/contract/m0_scaffold/test_m0_scaffold.py -q        -> 6 passed
git diff --check                                                           -> clean
docs link/JSON sweep                                                       -> bad_local_links=0; bad_json_parse=0
```

## 5. Evidence acceptance

| Acceptance gate | Source | Result |
|---|---|---|
| Non-clone operation returns `GITHUB_NON_CLONE_OPERATION_BLOCKED` before external request | `m7_github_mode_gate_contract::non_clone_operations_blocked_in_every_mode`, `clone_readonly_requires_gate_approval_before_allowed` | accepted |
| Privacy naming rejects PII before any network plan | `m7_github_privacy_naming_contract::reject_raw_student_internal_id_from_denylist`, `reject_email_like_candidate`, `reject_github_pat_shaped_string`, `reject_ssn_like_pattern`, `reject_long_consecutive_digit_run_as_potential_institutional_id` | accepted |
| Adapter evidence cannot promote submission state by itself | `m7_github_clone_evidence_contract::assemble_clone_evidence_returns_envelope_with_hardcoded_non_mutation_literals` (`operation_class="clone-only"`, `external_side_effect_made=false`, `github_mutation_made=false`) | accepted |
| Raw credentials do not appear in evidence text | `m7_github_clone_evidence_contract::assemble_clone_evidence_rejects_raw_credential_in_input_text`, `assemble_clone_evidence_rejects_raw_url_credential_segment`, `scan_for_raw_credentials_blocks_pat_prefix`, `scan_for_raw_credentials_blocks_denylist_entry` | accepted |
| Source URL is stored only as a hash | `m7_github_clone_evidence_contract::assemble_clone_evidence_returns_envelope_with_hardcoded_non_mutation_literals` (`!source_repo_url_hash.contains(raw URL)`), `source_repo_url_hash_is_deterministic_across_calls` | accepted |
| Audit event ids encode scope/mode/operation deterministically | `m7_github_mode_gate_contract::mode_decision_audit_event_id_encodes_mode_and_operation`, `m7_github_privacy_naming_contract::audit_event_id_encodes_scope_for_each_decision` | accepted |

## 6. Non-claims

This evidence summary does not claim:

- a live GitHub clone, real network round-trip, or real authentication handshake;
- mock-http fixture replay format, fixture parser, retry policy, or rate-limit/backoff behavior (deferred to a later task that author-aligns the mock-http fixture format with the GitHub adapter specification §9);
- clone-readonly mode approval mechanics (the gate that flips `clone-readonly` from blocked to allowed) — this remains a human-authored integration-point decision and the `clone_readonly_gate_approved` boolean is a *test input*, not a Ralph-authored approval;
- credential rotation, credential persistence, or credential lifecycle beyond `credential_ref_id` and `credential_fingerprint_hint` references;
- submission-state promotion authority (clone evidence cannot itself queue/push/confirm a submission);
- a cryptographic SHA-256 source-URL hash (current FNV-1a 64 hash is a small stable identifier for fixture-only audit);
- repository creation, collaborator invitation, branch protection, webhook/check-run, or any GitHub state mutation;
- instructor approval surface, evaluator integration, or observability ingestion;
- live external action of any kind.

## 7. Follow-up

The following follow-up items are required before broader GitHub-related milestones may claim acceptance:

1. an authorized human owner must accept a clone-readonly integration-point specification covering allowlist policy, approval workflow, credential-reference acquisition, scope-grant lifecycle, and audit linkage before any executable real-network row is queued under Ralph;
2. author the mock-http fixture format specification (`GH-FIX-002` and STD-087) so an executable mock-http fixture replay row can be queued under Ralph;
3. add real retry/rate-limit/backoff policy and `GitHub_RATE_LIMITED` / `GITHUB_OUTAGE_OR_TIMEOUT` evidence shape when the mock-http fixture format is accepted;
4. upgrade `source_repo_url_hash` from FNV-1a 64 to SHA-256 once a cryptographic audit hash is required by an accepted controlled-evidence policy;
5. integrate the privacy naming evaluator into the clone planner so that no clone plan is constructed without a passing privacy-naming decision;
6. proceed to M8 export fixture and DEMO-1 evidence only after the exporter implementation specification is authored and accepted (per `EDUOPS-M8-EXPORT-SPEC-BLOCKER`).

## 8. Traceability

- [GitHub adapter specification](../02-design-planning/github-adapter-specification.md)
- [GitHub adapter software design description](../02-design-planning/github-adapter-software-design-description.md)
- [GitHub topology and token model](../02-design-planning/github-topology-and-token-model.md)
- [Software test description](../03-verification-validation/software-test-description.md) — STD-086 through STD-091
- [Implementation milestones](implementation-milestones.md)
- [M6 SLICE-E advisory C/C++ runner gate evidence](m6-slice-e-advisory-cpp-runner-evidence.md)
- [M5 SLICE-D assignment publication, submission, and repository conflict gate evidence](m5-slice-d-assignment-submission-evidence.md)
- [M2 configuration and credential reference evidence](m2-configuration-credential-evidence.md)
