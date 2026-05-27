---
title: Local Storage Adapter Specification
document_id: SWENG-EDUTECH-LOCAL-STORAGE-ADAPTER-SPEC
version: 0.1.0
status: draft
date: 2026-05-14
owner: pre-develop
quality_context: ISO 9001 draft documented information
traceability:
  candidates: ['EDUOPS-CIR-003']
  related: ['SWENG-EDUTECH-DOMAIN-IDL', 'SWENG-EDUTECH-SLICE-A-TEST-CARDS']
---

# Local Storage Adapter Specification

## 1. Scope

This specification defines the minimum local storage contract for SLICE-A empty course persistence and document save/load. It does not define the final SQLite schema.

## 2. Rust trait baseline

```rust
pub trait StorageAdapter {
    fn open_workspace(&self, request: OpenWorkspaceRequest) -> Result<WorkspaceEvidence, StorageError>;
    fn save_course(&self, request: SaveCourseRequest) -> Result<PersistenceEvidence, StorageError>;
    fn load_course(&self, request: LoadCourseRequest) -> Result<CourseSnapshot, StorageError>;
    fn save_empty_document(&self, request: SaveEmptyDocumentRequest) -> Result<PersistenceEvidence, StorageError>;
}
```

## 3. Required request/result fields

| Contract | Required fields |
|---|---|
| `OpenWorkspaceRequest` | `workspace_root`, `schema_version`, `adapter_mode='local'`, `live_external_action=false` |
| `WorkspaceEvidence` | `workspace_root`, `created`, `schema_version`, `manifest_path`, `audit_event_id` |
| `SaveCourseRequest` | `course_id`, `course_json`, `expected_schema_version` |
| `PersistenceEvidence` | `path`, `sha256`, `bytes_written`, `audit_event_id` |
| `CourseSnapshot` | `course_id`, `schema_version`, `sha256`, `loaded_at_utc` |

## 4. SLICE-A acceptance

`TC-SLICE-A-001` passes only when `fixtures/slice-a/course-empty.json` can be saved, loaded, hashed, and included in `manifest.sha256` without external services.
