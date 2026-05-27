---
title: GitHub Topology and Token Model
document_id: SWENG-EDUTECH-GITHUB-TOPOLOGY
version: 0.1.0
status: draft
date: 2026-05-13
owner: pre-develop
quality_context: ISO 9001 draft documented information
---

# GitHub Topology and Token Model

## 1. Purpose

Define the controlled GitHub topology and credential model needed for GitHub-first repository backend operation.

## 2. Topology candidates

| Candidate | Strength | Risk | Initial stance |
|---|---|---|---|
| Organization per institution/course group | Clear admin boundary and team model | Requires org ownership/permissions | Preferred production topology |
| Repository per assignment instance with submission branches | Centralized review and branch protection | Large branch count, naming privacy | Current concept baseline |
| Repository per student workspace | Strong isolation | Repository explosion and provisioning cost | Evaluate for privacy-sensitive courses |
| Self-hosted Git later | More control | Operational burden | Future extension only |

## 3. Naming and privacy rules

Branch/repository names should avoid raw student numbers where other students or external collaborators can see them. Use internal pseudonymous IDs and map them through controlled roster/identity records.

## 4. Token model

| Token type | Use | Control |
|---|---|---|
| GitHub App installation token | Preferred automation for org/repo operations | Short-lived, scoped, auditable |
| OAuth user token | User-authorized actions | Least scope; avoid background admin automation where possible |
| PAT | Development/admin fallback only | Not preferred for production; never stored raw |
| SSH deploy key | Repo-specific Git operation | Scoped per repo; rotate/revoke policy required |

Raw tokens shall not be stored in project docs, logs, exports, or student workspaces. Store references/fingerprints only.

## 4.1 Professor-provisioned repository authority assumption

For the first live `clone-readonly` integration target, EduOps assumes that the professor or authorized course owner has already created the target GitHub repository and holds all access authority required to grant read-only clone/fetch access. This assumption is controlled by `EDUOPS-DEC-064`.

The assumption authorizes product design and fixture/runbook preparation for a professor-owned repository, but it does not authorize EduOps automation to create repositories, add collaborators, change branch protection, rotate credentials, push commits, create webhooks/check-runs, or mutate GitHub state. The first live operation remains clone-only and must be captured through a user-executed runbook with:

- repository owner/course owner identity recorded as a role label, not a raw credential;
- repository URL handled through a redacted/hash envelope in docs and evidence;
- credential-reference id and fingerprint hint only, never a raw token;
- approval evidence from `course_admin` or `platform_admin`;
- explicit `git clone`/`git fetch` command evidence supplied by the human operator when live execution is authorized;
- `github_mutation_made=false` and no repository administration side effects.

## 4.2 User-managed live GitHub boundary and clone input modes

`EDUOPS-DEC-065` excludes live GitHub account administration, raw credential handling, remote setup, and externally consequential Git execution from EduOps automation. Those responsibilities remain with the professor, student, or other authorized human operator.

EduOps consumes only bounded inputs after that human-managed boundary:

| Mode | Human/operator responsibility | EduOps responsibility | Boundary |
|---|---|---|---|
| Professor/course-owner operation | The professor or authorized course owner prepares repository access, credentials/remotes if needed, and a CSV containing roster rows plus GitHub repository URL fields. | Parse the approved CSV, validate/redact repository URL fields, map rows to pseudonymous roster/workspace records, and run clone-only processing for the listed repositories under the controlled adapter boundary. | No repo creation, collaborator administration, credential lookup, push, webhook/check-run, branch protection, or remote mutation by EduOps. |
| Student local operation | The student clones their own repository into a local checkout before starting EduOps. | Run EduOps from the provided local repository path and inspect/use that checkout according to local fixture/product rules. | EduOps does not log in as the student, configure the student's remote, or clone on behalf of the student in this mode. |

CSV inputs must be treated as controlled operational input, not as credential storage. Raw repository URLs may be accepted at the runtime boundary for clone planning/execution, but persistent docs/evidence should store redacted forms, hashes, or controlled references unless a user-executed runbook explicitly attaches a sanitized evidence excerpt.

## 5. Traceability

- Requirements: `EDUOPS-FR-023`, `EDUOPS-FR-059`
- Constraints: `EDUOPS-CON-007`, `EDUOPS-CON-010`
- Decision: `EDUOPS-DEC-032`, `EDUOPS-DEC-064`, `EDUOPS-DEC-065`
- Risk: `EDUOPS-R-035`
