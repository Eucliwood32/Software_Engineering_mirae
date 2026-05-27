---
title: Canonical Domain IDL
document_id: SWENG-EDUTECH-DOMAIN-IDL
version: 0.2.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CFR-004', 'EDUOPS-CFR-013', 'EDUOPS-CFR-015']
  related: ['SWENG-EDUTECH-BLOCK-SCHEMA', 'SWENG-EDUTECH-STORAGE-ARCH']
---

# Canonical Domain IDL

## 1. Scope

This document defines schema-like domain records for early implementation. The IDL uses TypeScript-style shapes for readability; generated validators may use JSON Schema, Rust types, or equivalent.

## 2. Shared primitives

```ts
type Id<T extends string> = string; // `${prefix}_${ulid}` or deterministic fixture ID
type IsoTime = string; // RFC 3339 UTC, normalized by authoritative time service
type Sha256 = string;
type GitSha = string;
type PrivacyClass = 'course' | 'student_private' | 'submission_evidence' | 'course_review' | 'public_example_candidate';
type ActorRole = 'student' | 'instructor' | 'ta' | 'admin' | 'evaluator' | 'sync_worker' | 'system';
type LifecycleStatus = 'invited' | 'active' | 'locked' | 'withdrawn' | 'archived';
```

Every persisted record includes `schema_version`, `created_at`, `updated_at`, and optional `audit_ref`.

## 3. Course and roster records

```ts
interface Course {
  course_id: Id<'course'>;
  schema_version: 'eduops.course/0.1';
  code: string;
  title: string;
  term: string;
  locale: 'ko-KR' | 'en-US';
  timezone: string;
  repository_root: string;
  sections: Id<'section'>[];
  created_at: IsoTime;
  updated_at: IsoTime;
}

interface Section {
  section_id: Id<'section'>;
  course_id: Id<'course'>;
  label: string;
  instructor_ids: string[];
  ta_ids: string[];
  roster_source_ref?: string;
  status: 'draft' | 'active' | 'archived';
}

interface RosterEntry {
  roster_entry_id: Id<'roster'>;
  course_id: Id<'course'>;
  section_id: Id<'section'>;
  institutional_student_ref_hash: Sha256;
  display_name: string;
  email_hash?: Sha256;
  student_number_hash?: Sha256;
  lifecycle_status: LifecycleStatus;
  privacy_flags: string[];
  imported_from: { file_name: string; file_sha256: Sha256; row_number?: number };
}

interface StudentIdentityBinding {
  binding_id: Id<'binding'>;
  roster_entry_id: Id<'roster'>;
  provider: 'github' | 'local_fixture';
  provider_user_ref_hash: Sha256;
  display_handle?: string;
  state: 'unclaimed' | 'claimed' | 'approved' | 'rejected' | 'revoked';
  approved_by?: string;
  approved_at?: IsoTime;
  evidence_ref: string;
}
```

## 4. Assignment records

```ts
interface AssignmentBankItem {
  bank_item_id: Id<'bank_item'>;
  course_id: Id<'course'>;
  title: string;
  tags: string[];
  canonical_document_id: Id<'doc'>;
  source_repo_ref?: string;
  status: 'draft' | 'reviewed' | 'retired';
}

interface AssignmentVersion {
  assignment_version_id: Id<'assignment_version'>;
  bank_item_id: Id<'bank_item'>;
  version_label: string;
  canonical_document_hash: Sha256;
  git_ref: string;
  release_notes: string;
  created_by: string;
  created_at: IsoTime;
}

interface AssignmentInstance {
  assignment_instance_id: Id<'assignment_instance'>;
  assignment_version_id: Id<'assignment_version'>;
  course_id: Id<'course'>;
  section_ids: Id<'section'>[];
  release_at: IsoTime;
  due_at: IsoTime;
  late_policy_ref?: string;
  state: 'draft' | 'scheduled' | 'released' | 'update_available' | 'closed' | 'archived';
}

interface StudentWorkspace {
  workspace_id: Id<'workspace'>;
  roster_entry_id: Id<'roster'>;
  assignment_instance_id: Id<'assignment_instance'>;
  root_path: string;
  git_branch: string;
  assignment_version_id: Id<'assignment_version'>;
  lifecycle_state: 'not_provisioned' | 'provisioned' | 'active' | 'blocked' | 'archived';
  last_checkpoint_sha?: GitSha;
}
```

## 5. Document and operation records

```ts
interface BlockDocument {
  document_id: Id<'doc'>;
  schema_version: 'eduops.block-document/0.1';
  owner_scope: 'assignment' | 'workspace' | 'knowledge' | 'feedback';
  privacy_class: PrivacyClass;
  root_block_ids: Id<'block'>[];
  blocks: Record<string, {
    block_id: Id<'block'>;
    type: 'heading' | 'paragraph' | 'code' | 'table' | 'graph' | 'image' | 'file' | 'reference' | 'experiment' | 'decision' | 'reflection' | 'report_placeholder';
    payload: unknown;
    lineage?: { cloned_from?: Id<'block'>; tombstoned_at?: IsoTime };
    validation_state: 'unchecked' | 'valid' | 'warning' | 'invalid';
  }>;
  markdown_projection_sha256?: Sha256;
  asset_refs: string[];
}

interface EditOperation {
  operation_id: Id<'op'>;
  document_id: Id<'doc'>;
  actor_id: string;
  actor_role: ActorRole;
  base_revision: string;
  operation_type: 'insert_block' | 'update_block' | 'move_block' | 'delete_block' | 'restore_block' | 'set_metadata';
  patch: unknown;
  idempotency_key: string;
  created_at: IsoTime;
}
```

## 6. Evidence records

```ts
interface SubmissionSnapshot {
  submission_snapshot_id: Id<'submission'>;
  workspace_id: Id<'workspace'>;
  assignment_version_id: Id<'assignment_version'>;
  submission_state: 'draft' | 'checkpointed' | 'queued' | 'pushed' | 'confirmed' | 'rejected' | 'reopened';
  git_commit_sha: GitSha;
  git_ref: string;
  document_hashes: Sha256[];
  included_knowledge_refs: string[];
  submitted_at: IsoTime;
  authoritative_received_at?: IsoTime;
}

interface EvaluationRun {
  evaluation_run_id: Id<'eval'>;
  submission_snapshot_id: Id<'submission'>;
  mode: 'advisory_local' | 'official_sandbox';
  runner_profile: string;
  toolchain_profile: string;
  state: 'queued' | 'running' | 'passed' | 'failed' | 'error' | 'timeout' | 'cancelled';
  result_json_sha256?: Sha256;
  log_sha256?: Sha256;
  started_at?: IsoTime;
  completed_at?: IsoTime;
}

interface ExportJob {
  export_job_id: Id<'export'>;
  source_ref: Id<'doc'> | Id<'submission'>;
  format: 'docx' | 'hwpx' | 'hwp';
  state: 'queued' | 'running' | 'completed' | 'completed_with_warnings' | 'failed';
  artifact_sha256?: Sha256;
  manifest_sha256?: Sha256;
  warning_codes: string[];
}

interface AuditEvent {
  audit_event_id: Id<'audit'>;
  actor_id: string;
  actor_role: ActorRole;
  action: string;
  object_type: string;
  object_id: string;
  result: 'allowed' | 'denied' | 'completed' | 'failed';
  correlation_id: string;
  idempotency_key?: string;
  before_hash?: Sha256;
  after_hash?: Sha256;
  occurred_at: IsoTime;
}

interface DiagnosticPackage {
  diagnostic_package_id: Id<'diag'>;
  scope: 'course' | 'workspace' | 'submission' | 'export' | 'evaluation';
  correlation_ids: string[];
  redaction_profile: 'student_safe' | 'instructor_safe' | 'operator_safe';
  artifact_manifest_sha256: Sha256;
  created_at: IsoTime;
}
```

## 7. Configuration and credential records

```ts
type ConfigScope = 'app_default' | 'system' | 'user' | 'course' | 'repository' | 'runtime_override';

interface ConfigRecord {
  config_record_id: Id<'config'>;
  schema_version: 'eduops.config/0.1';
  scope: ConfigScope;
  key: string;
  value_json: unknown;
  effective_hash: Sha256;
  source_ref: string;
  updated_by: string;
  created_at: IsoTime;
  updated_at: IsoTime;
}

interface CredentialRef {
  credential_ref_id: Id<'credential'>;
  schema_version: 'eduops.credential-ref/0.1';
  provider: 'github' | 'self_hosted_git' | 'export_converter' | 'update_signing';
  secret_locator: string; // OS credential-store locator, never a raw token
  fingerprint_sha256?: Sha256;
  allowed_scopes: string[];
  status: 'active' | 'expired' | 'revoked' | 'rotation_required' | 'quarantined';
  created_by: string;
  created_at: IsoTime;
  rotated_at?: IsoTime;
  expires_at?: IsoTime;
}
```

## 8. Validation rules

- IDs are stable and never reused.
- Fixture IDs may be deterministic; production IDs shall be collision-resistant.
- Hash fields are computed over normalized canonical bytes.
- Student PII fields are stored as hashes unless a later privacy contract explicitly permits local cleartext.
- `AuditEvent` is required for protected commands, state transitions, export generation, submission, and evaluation.
