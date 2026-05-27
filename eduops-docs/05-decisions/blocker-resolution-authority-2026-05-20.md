---
title: EduOps Blocker Resolution Authority
id: EDUOPS-DEC-066
version: 0.1.0
status: accepted
created: 2026-05-20
owner: develop
quality_context: controlled decision packet
traceability:
  upstream:
    - EDUOPS-DEC-DESKTOP-D6-RULE-6-TRACE-COMPLETE
    - EDUOPS-DESKTOP-D6-LAUNCH-EVIDENCE-SHAPE-SPEC
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
  downstream:
    - ralph.md
---

# EduOps Blocker Resolution Authority

## 1. Request context

The user requested blocker resolution after the Ralph queue reached the controlled stop `EDUOPS-DEC-DESKTOP-D6-RULE-6-TRACE-COMPLETE`.

The stop condition recorded that the prepared queue had no `next` or `pending` rows and that further safe work required explicit additional authority for at least one blocked family:

1. D6 rule 7 schema extension;
2. additional desktop IPC commands beyond `query_session_capabilities`;
3. cross-cutting product-scope expansion of MB-DESKTOP into controlled milestone/design/API documents;
4. D6 user-observed launch gate execution;
5. live GitHub / credential / remote / installer / host-runtime actions;
6. M3 editor adapter bridge specification;
7. M5 scoped submission/review authorization specification;
8. M8 real exporter / DEMO-1 evidence acceptance.

## 2. Decision

`EDUOPS-DEC-066` authorizes Ralph/Hermes to resolve blockers only through local-safe documentation/control and fixture-local implementation increments derived from existing controlled anchors.

This decision authorizes the following safe classes without additional user decisions:

| Class | Authorized resolution path | Boundary |
|---|---|---|
| D6 rule 7 | Author a controlled D6 evidence-schema extension specification that introduces a redacted `student_*` evidence field, then implement fixture-local validator/template/test updates after the specification gate is accepted. | No real student identifier may be stored. The field must carry a hash/envelope only. |
| Additional IPC | Author a controlled IPC expansion specification for read-only/local fixture commands before any source change. | No filesystem mutation, Git execution, credential lookup, network call, or live external action. |
| MB-DESKTOP cross-cutting trace | Update controlled docs only after a specific local-safe scope is selected in Ralph. | No relaxation of D6 launch, installer, or DEMO-1 non-claims. |
| M3 bridge | Author a HOW-level editor adapter bridge specification from existing block/document/storage anchors. | No editor-vendor runtime adoption or live UI claim until gated separately. |
| M5 authorization | Author a scoped submission/review authorization implementation specification from existing RBAC/state-machine anchors. | No live user account, repository, or course data mutation. |

This decision does not authorize the following non-delegable or user-managed actions:

- running a real desktop launch as evidence;
- capturing screenshots or screen recordings as final evidence;
- installing WebKitGTK, WebView2, Tauri CLI, system packages, or host runtimes;
- invoking `cargo tauri dev` or `cargo tauri build` as proof of D6 closure;
- publishing installers, releases, packages, or external artifacts;
- looking up, changing, storing, or rotating credentials;
- adding/changing remotes, pushing, creating GitHub repositories, or calling live GitHub APIs;
- running real `git clone`, `git fetch`, `git push`, or `git ls-remote` for live evidence;
- claiming DEMO-1 acceptance;
- executing real DOCX/HWPX writer, Hancom, LibreOffice/UNO, or server-side converter profiles.

## 3. First selected unblock path

The first safe unblock path is D6 rule 7 because it is already named in the D6 evidence-shape specification as the remaining redaction-rule gap and can be resolved through a controlled schema extension plus fixture-local validator tests.

Ralph shall seed this next queue:

1. `MB-DESKTOP-D6-RULE-7-SCHEMA-SPEC-PREP` — update the D6 evidence-shape specification to v0.3.0 with an explicit optional redacted `student_*` field and rule 7 policy.
2. `MB-DESKTOP-D6-RULE-7-SCHEMA-SPEC-GATE` — accept the docs/control schema extension gate.
3. `MB-DESKTOP-D6-EVIDENCE-VALIDATE-RULE-7-T1` — update the placeholder template and fixture-local validator/tests so raw student identifiers fail closed while redacted/hash fields pass.
4. `MB-DESKTOP-D6-EVIDENCE-VALIDATE-RULE-7-GATE` — accept the fixture-local rule 7 helper gate.
5. `QUEUE-REFILL-PREP-POST-MB-DESKTOP-D6-RULE-7` — classify the next blocker family.

## 4. Acceptance criteria

A blocker-resolution increment is accepted only when:

- the task is represented in `ralph.md` with a controlled anchor, validation-first command, acceptance boundary, and status;
- changed docs are linked from `docs/README.md` and `docs/INDEX.md` when a new document is created;
- Markdown local links resolve;
- JSON files parse;
- `git diff --check` passes;
- `npm run m0:check` passes unless the task is explicitly scoped to docs-only and the command is unchanged from a known green baseline;
- `ralph.md` records the Reflection result, success likelihood, and next selected task or stop reason;
- no non-delegable action is executed by Ralph/Hermes.

## 5. Non-claims

This decision resolves the queue-end authority blocker for local-safe blocker resolution. It does not close any product gate by itself and does not provide runtime evidence. Each downstream task must still pass its own gate.
