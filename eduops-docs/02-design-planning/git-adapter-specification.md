---
title: Git Adapter Specification
document_id: SWENG-EDUTECH-GIT-ADAPTER-SPEC
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CIR-002']
  related: ['SWENG-EDUTECH-MODULE-LAYOUT', 'SWENG-EDUTECH-SLICE-A-TEST-CARDS']
---

# Git Adapter Specification

## 1. Scope

This specification defines the minimum fake/local Git adapter contract required for SLICE-A. It does not approve live GitHub or remote Git operations.

## 2. Rust trait baseline

```rust
pub trait GitAdapter {
    fn init_local_workspace(&self, request: InitLocalWorkspaceRequest) -> Result<GitWorkspaceEvidence, GitAdapterError>;
    fn status(&self, request: GitStatusRequest) -> Result<GitStatusEvidence, GitAdapterError>;
    fn checkpoint(&self, request: CheckpointRequest) -> Result<CheckpointEvidence, GitAdapterError>;
    fn assert_no_remote(&self, request: GitStatusRequest) -> Result<NoRemoteEvidence, GitAdapterError>;
}
```

## 3. Required request/result fields

| Contract | Required fields |
|---|---|
| `InitLocalWorkspaceRequest` | `workspace_path`, `fixture_template_path`, `adapter_mode='fake-local'`, `live_external_action=false` |
| `GitWorkspaceEvidence` | `workspace_path`, `head_ref`, `remote_count`, `external_side_effect_made=false`, `audit_event_id` |
| `GitStatusEvidence` | `changed_paths`, `untracked_paths`, `remote_urls=[]`, `status_digest` |
| `CheckpointRequest` | `workspace_path`, `message`, `included_paths`, `require_no_remote=true` |
| `CheckpointEvidence` | `checkpoint_id`, `tree_digest`, `included_paths`, `manifest_sha256`, `audit_event_id` |

## 4. SLICE-A acceptance

`TC-SLICE-A-001` passes only when the adapter can initialize a local workspace from `fixtures/slice-a/fake-git-template/`, produce status evidence, create a fake/local checkpoint evidence record, and prove no remote URL exists.
