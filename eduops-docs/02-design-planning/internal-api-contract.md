---
title: Internal API Contract
document_id: SWENG-EDUTECH-INTERNAL-API
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CIR-001', 'EDUOPS-CIR-018', 'EDUOPS-CIR-019']
  related: ['SWENG-EDUTECH-DOMAIN-IDL', 'SWENG-EDUTECH-PROCESS-IPC']
---

# Internal API Contract

## 1. Scope

This document defines first-beta command/query signatures across the UI shell, application core, and workers. Payloads use the canonical domain IDL. All protected commands require authorization, idempotency, audit, and fixture/live-action gate checks.

## 2. Result envelope and error model

All APIs return the `ResultEnvelope<T>` from the process topology contract. Error codes use:

| Prefix | Domain |
|---|---|
| `EDUOPS_AUTH_*` | Authorization and scope failures |
| `EDUOPS_VALIDATION_*` | Payload, roster, document, export, or runner validation |
| `EDUOPS_STATE_*` | Illegal lifecycle, assignment, submission, or conflict transition |
| `EDUOPS_IO_*` | File, DB, Git, export, runner, or diagnostics I/O |
| `EDUOPS_GATE_*` | Fixture/live-action gate denial |
| `EDUOPS_CONFLICT_*` | Sync or concurrent edit conflict |
| `EDUOPS_CONFIG_*` | Configuration schema, merge, authorization, or migration failure |
| `EDUOPS_CREDENTIAL_*` | Credential reference, rotation, revocation, or secret-store failure |

Errors include `retriable`, `user_visible`, and optional `diagnostic_ref`. User-visible messages are resolved by UI message code, not raw exception text.

## 3. Audit and idempotency fields

Commands include `idempotency_key`, `correlation_id`, `actor`, `dry_run`, and `live_external_action=false` unless a later accepted gate explicitly enables a live action. Successful protected commands emit at least one `AuditEvent`. Replayed idempotent commands return the prior result envelope when the payload hash matches.

## 4. First beta command signatures

| Command | Input | Output | Required audit action |
|---|---|---|---|
| `course.createLocalCourse` | `{code,title,term,locale,timezone}` | `Course` | `course.create` |
| `roster.importFixtureRoster` | `{course_id,section_id,file_ref,file_sha256}` | `{accepted:RosterEntry[], rejected:ValidationIssue[]}` | `roster.import` |
| `identity.recordLocalClaim` | `{roster_entry_id,provider_user_ref_hash,display_handle}` | `StudentIdentityBinding` | `identity.claim` |
| `identity.approveBinding` | `{binding_id,decision,reason}` | `StudentIdentityBinding` | `identity.approve` |
| `workspace.provisionLocal` | `{assignment_instance_id,roster_entry_id}` | `StudentWorkspace` | `workspace.provision` |
| `assignment.createBankItem` | `{course_id,title,document_id,tags}` | `AssignmentBankItem` | `assignment.bank.create` |
| `assignment.publishVersion` | `{bank_item_id,version_label,release_notes}` | `AssignmentVersion` | `assignment.version.publish` |
| `assignment.releaseInstance` | `{assignment_version_id,section_ids,release_at,due_at}` | `AssignmentInstance` | `assignment.instance.release` |
| `document.saveOperation` | `{document_id,base_revision,operation}` | `{document_id,revision,hashes}` | `document.edit` |
| `document.materializeProjection` | `{document_id,profile}` | `{json_sha256,markdown_sha256,manifest_sha256}` | `document.materialize` |
| `workspace.checkpoint` | `{workspace_id,message}` | `{git_commit_sha,manifest_sha256}` | `workspace.checkpoint` |
| `submission.queueLocal` | `{workspace_id,checkpoint_sha}` | `SubmissionSnapshot` | `submission.queue` |
| `submission.confirmLocalFixture` | `{submission_snapshot_id,fake_remote_ref}` | `SubmissionSnapshot` | `submission.confirm.fixture` |
| `evaluation.runAdvisoryFixture` | `{submission_snapshot_id,runner_profile}` | `{job_id}` | `evaluation.advisory.start` |
| `export.generateFixture` | `{source_ref,format,template_ref}` | `{job_id}` | `export.start` |
| `diagnostics.createPackage` | `{scope,object_id,redaction_profile}` | `DiagnosticPackage` | `diagnostics.package` |
| `config.set` | `{scope,key,value_json,expected_before_hash?,reason}` | `ConfigRecord` | `config.set` |
| `config.validate` | `{scope?,candidate_records}` | `{valid:boolean,issues:ValidationIssue[],effective_hash?}` | `config.validate` |
| `config.migrate` | `{scope,from_version,to_version,dry_run}` | `{migration_id,before_hash,after_hash,warnings}` | `config.migrate` |
| `credential.registerReference` | `{provider,proof,scope,dry_run}` | `CredentialRef` | `credential.register` |
| `credential.rotateReference` | `{credential_ref_id,proof,reason}` | `CredentialRef` | `credential.rotate` |
| `credential.revokeReference` | `{credential_ref_id,reason}` | `CredentialRef` | `credential.revoke` |

## 5. First beta query signatures

| Query | Input | Output |
|---|---|---|
| `session.getCapabilities` | `{}` | `{desktop_shell,api_version,adapter_modes,live_actions_enabled:false}` |
| `course.listLocal` | `{}` | `Course[]` |
| `course.getDashboard` | `{course_id}` | `{sections,roster_counts,assignment_counts,pending_jobs}` |
| `roster.listEntries` | `{course_id,section_id?}` | `RosterEntry[]` |
| `assignment.listInstances` | `{course_id,section_id?}` | `AssignmentInstance[]` |
| `workspace.getStatus` | `{workspace_id}` | `{workspace,git_status,document_status,submission_status}` |
| `document.load` | `{document_id,revision?}` | `BlockDocument` |
| `job.getStatus` | `{job_id}` | `{state,phase,progress,artifact_refs,error?}` |
| `audit.search` | `{scope,object_id,limit}` | `AuditEvent[]` |
| `config.getEffective` | `{scope?,redaction_profile}` | `{records:ConfigRecord[],effective_hash,merge_trace_ref}` |
| `config.listKeys` | `{scope?,include_protected:false}` | `{key,scope,overrideable,redacted_value_hint?}[]` |
| `credential.getStatus` | `{credential_ref_id}` | `{credential_ref_id,provider,status,fingerprint_sha256?,expires_at?}` |

## 6. Worker result binding

Workers never mutate course state directly. They return job results to the application core, which validates state guards, persists artifacts, and records final audit events.


## 10. Ralph-loop Rust trait appendix

The first fake/local implementation loop shall use these trait names as stable implementation anchors:

| Trait | Owning crate | Required before |
|---|---|---|
| `StorageAdapter` | `crates/eduops_storage` | `TC-SLICE-A-001` |
| `GitAdapter` | `crates/eduops_git` | `TC-SLICE-A-001` |
| `CredentialAdapter` | `crates/eduops_credentials` | credential status only; no lookup in SLICE-A |
| `GitHubAdapter` | `crates/eduops_git::github` | `TC-GH-000` |
| `RunnerAdapter` | `crates/eduops_runner` | deferred out of SLICE-A |
| `ExportAdapter` | `crates/eduops_export` | deferred out of SLICE-A |

The SLICE-A loop may implement only `StorageAdapter`, `GitAdapter`, and inert `GitHubAdapter` mode-gate behavior required by the cited test cards. Other traits remain stubs or out-of-scope.
