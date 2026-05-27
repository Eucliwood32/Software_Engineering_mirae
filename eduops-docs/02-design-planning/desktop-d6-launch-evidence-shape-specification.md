---
title: Desktop D6 User-Observed Launch Evidence Shape Specification
document_id: EDUOPS-DESKTOP-D6-LAUNCH-EVIDENCE-SHAPE-SPECIFICATION
version: 0.3.0
status: accepted
date: 2026-05-20
owner: develop
quality_context: ISO 9001 draft documented information
traceability:
  upstream:
    - EDUOPS-DESKTOP-APP-DEVELOPMENT-PLAN
    - EDUOPS-DEC-OS-001
    - EDUOPS-DESKTOP-ENTRYPOINT-DEPENDENCY-AUTHORIZED-DECISION
    - EDUOPS-DESKTOP-ENTRYPOINT-DEPENDENCY-ADOPTION-DECISION
    - EDUOPS-M1A-DESKTOP-GATE-CLOSURE-RUNBOOK
    - EDUOPS-M1A-DESKTOP-GATE-CLOSURE-EVIDENCE
    - EDUOPS-UI-SHELL-DEMO-TEST-CARDS
    - SWENG-EDUTECH-PROCESS-IPC
  gaps_recorded:
    - Desktop-app development plan §6 D6 user-observed launch gate evidence schema
---

# Desktop D6 User-Observed Launch Evidence Shape Specification

## 0. Document scope

This specification defines **only** the controlled evidence shape — schema, attestation fields, evidence package layout, candidate vs. final status distinction, redaction rules, fail-closed non-claim language, and user-executed boundary — that the [Desktop App Development Plan](../06-implementation/desktop-app-development-plan.md) §6 D6 user-observed launch gate will produce when it is exercised.

This document does **not**:

- execute a desktop launch;
- capture screenshots or screen recordings;
- install WebKitGTK, WebView2, or the Tauri CLI;
- invoke `cargo tauri dev` or `cargo tauri build`;
- close the D6 user-observed launch gate;
- claim DEMO-1 readiness or acceptance;
- supersede or relax the non-claim boundary recorded in [Desktop Entrypoint Dependency Adoption Authorized Decision](desktop-entrypoint-dependency-adoption-authorized-decision.md) §7;
- authorize publication, installer release, network call, credential resolution, remote action, or repository administration.

Acceptance of this specification is acceptance of the **schema only**.

## 1. Purpose

The desktop-app development plan §6 D6 user-observed launch gate must produce reviewable, redaction-safe, fail-closed evidence that a real EduOps desktop window launched on a named host/runtime under the path-B Tauri 2 entrypoint authorized by `EDUOPS-DEC-DESKTOP-ENTRYPOINT-DEPENDENCY-AUTHORIZED`.

Until now, the only controlled record describing what such evidence shall contain has been:

- the desktop-app development plan §6 D6 acceptance bullet list (four lines);
- the existing `apps/desktop-ui/scripts/desktop-smoke-template.mjs` `--dry-run` template (an 11-key `run-summary.json` placeholder);
- the M1A precedent in [M1A Desktop Gate Closure Evidence](../06-implementation/m1a-desktop-gate-closure-evidence.md) and [M1A Desktop Gate Closure Runbook](../06-implementation/m1a-desktop-gate-closure-runbook.md), which used the static-browser preview rather than the path-B Tauri shell.

This specification consolidates those sources into a single controlled schema that future Ralph and user-executed runs can populate without inventing structure. Ralph may classify D6 candidates against this schema; it remains user-executed to produce the real launch capture.

## 2. Authorized vs. user-executed boundary

This boundary is load-bearing for every section below.

| Concern | Authorized for Ralph automation (docs/control only) | Reserved for user-executed gate |
|---|---|---|
| Author the schema in this document | Yes | — |
| Add or refine a future `run-summary.json` template under `docs/03-verification-validation/` | Yes, only when explicitly seeded and only for placeholder/skeleton content | — |
| Author a future `desktop-d6-launch-capture-runbook.md` analogous to M1A | Yes, when explicitly seeded as a later docs/control row | — |
| Install WebKitGTK / WebView2 / Tauri CLI | No | Yes |
| Run `npm run desktop:dev` or `npm run desktop:build` end-to-end with a real Tauri runtime | No | Yes |
| Open a real EduOps desktop window | No | Yes |
| Capture screenshot or screen recording | No | Yes |
| Author the reviewer attestation | No | Yes |
| Mark D6 gate **closed** | No | Yes (after Ralph verification of captured evidence per §9) |
| Claim DEMO-1 readiness | No | Out of scope of this document |

Ralph shall never write a non-placeholder value into the user-executed columns of the schema in §3.

## 3. Evidence package shape

A D6 evidence package is a single directory under the build evidence tree. The directory itself is **not** Git-tracked. The controlled record committed to Git is a follow-up evidence summary document modeled on [M1A Desktop Gate Closure Evidence](../06-implementation/m1a-desktop-gate-closure-evidence.md) that cites the package's `evidence_root`, manifest hash, and `run-summary.json` content. This specification does not write either; it only defines their shape.

### 3.1 Directory layout

```text
build/evidence/desktop-d6-launch/desktop-local-<platform>-<YYYYMMDD-HHMMSS>/
├── run-summary.json
├── manifest.sha256
├── capture/
│   └── evidence.png        # or evidence.mp4 / evidence.webm
├── platform/
│   ├── platform-runtime.txt        # WebKitGTK or WebView2 runtime details per DEC-OS-001 §2
│   ├── toolchain-paths.txt         # cargo / node / npm / tauri CLI path inventory
│   └── desktop-environment.txt     # Linux session/display or Windows systeminfo
└── attestation/
    └── reviewer-attestation.txt    # human attestation text supplied by reviewer
```

Notes:

- `evidence_root` shall always live under an ignored build directory (e.g., `build/evidence/`).
- Exactly one capture artifact (image or short recording) is required per package.
- `manifest.sha256` shall record the SHA-256 of each file in the package other than `manifest.sha256` itself.
- No file in the package is permitted to contain any value from §6 (redaction rules).

### 3.2 `run-summary.json` schema

`run-summary.json` is the structured root of the package. Keys appear in alphabetical order with two-space indentation (matches the existing `desktop-smoke-template.mjs` style for byte-determinism on regeneration).

| Key | Type | Allowed values / format | Source |
|---|---|---|---|
| `adapter_modes` | string | `fake,local` (literal); no other token authorized at D6 | constant |
| `app_command_used` | string | `npm run desktop:dev` or `npm run desktop:build` (verbatim) | user-executed (or `<dry-run-inert>` in pre-launch placeholder) |
| `app_version` | string | semver string from `apps/desktop/Cargo.toml` `version` field | repo state |
| `arch` | string | `process.arch` value at capture time (`x64`, `aarch64`, etc.) | host capture |
| `audit_event_id` | string | `audit_desktop_d6_launch_<YYYYMMDD-HHMMSS>` | deterministic per package |
| `capture_artifact_kind` | string | one of `screenshot`, `screen-recording`, `screenshot-and-recording` | user-executed |
| `capture_artifact_path` | string | repo-relative path under `evidence_root` | user-executed |
| `capture_artifact_sha256` | string | hex SHA-256 of capture artifact file (or comma-separated pair for `screenshot-and-recording`) | user-executed |
| `desktop_capture_environment` | string | one of `linux-x11`, `linux-wayland`, `windows-desktop` | user-executed |
| `external_call_made` | boolean | always `false` (hardcoded literal) | constant |
| `git_branch` | string | `git rev-parse --abbrev-ref HEAD` output at capture time | host capture |
| `git_head` | string | `git rev-parse HEAD` output at capture time | host capture |
| `github_mutation_made` | boolean | always `false` (hardcoded literal) | constant |
| `host_runtime_pkgconfig_status` | string | one of `present`, `missing` (literal) | host capture |
| `human_attestation_visible_ui_fields` | boolean | `true` only after reviewer reviews `attestation/reviewer-attestation.txt`; otherwise `false` | user-executed |
| `ipc_health` | string | `ok` only when the running app reported the M1A `query_session_capabilities` success envelope; otherwise `degraded` or `unreachable` | user-executed |
| `live_external_action` | boolean | always `false` (hardcoded literal) | constant |
| `network_request_enabled` | boolean | always `false` (hardcoded literal) | constant |
| `node_version` | string | `process.version` value | host capture |
| `npm_version` | string | `npm --version` output | host capture |
| `os` | string | distribution + version string (Linux) or Windows version (Windows) | host capture |
| `os_platform` | string | `process.platform` value | host capture |
| `platform` | string | one of `linux`, `windows` (must match `os_platform` mapping) | user-executed |
| `platform_match` | boolean | `true` when `platform` matches `os_platform`'s OS family; `false` otherwise | derived |
| `platform_webview_runtime` | string | per DEC-OS-001 §2: WebView2 runtime version (Windows) or webview/WebKitGTK identifier and version (Linux); never `<placeholder>` for an accepted package | user-executed |
| `platform_webview_runtime_accepted` | boolean | `true` only when the reviewer attests the runtime string matches a supported version; otherwise `false` | user-executed |
| `remote_origin_url` | string | exactly `<none>` for the first D6 increment (no remote authorized) | repo state |
| `required_human_evidence_remaining` | array of strings | empty when status is `accepted`; otherwise lists missing items (`screenshot`, `attestation`, `platform_runtime`, `human_attestation_visible_ui_fields`, `ipc_health`) | derived |
| `reviewer_owner` | string | display name of the human reviewer who attested the capture; `<pending>` only for a `candidate-for-review` package | user-executed |
| `rust_toolchain` | string | `cargo --version` output | host capture |
| `schema_version` | string | this specification's `version` field at the time of capture (the current accepted version is `0.3.0`; earlier captures may retain `0.1.0` or `0.2.0` and remain valid because no §3.2 key has been removed and no `status="accepted"` predicate condition has been changed) | constant |
| `status` | string | one of `candidate-for-review`, `accepted`; never `closed` (Ralph closure is a separate document per §9) | derived |
| `tauri_cli_version` | string | `cargo tauri --version` output, or `<not-installed>` (literal) | host capture |
| `tauri_version` | string | resolved Tauri 2 version from `Cargo.lock` | repo state |
| `tc_ui_shell_001` | boolean | references [UI Shell Demonstration Test Cards](../03-verification-validation/ui-shell-demo-test-cards.md) `TC-UI-SHELL-001` outcome | derived |
| `tc_ui_shell_002` | boolean | references `TC-UI-SHELL-002` outcome | derived |
| `tc_ui_shell_003` | boolean | references `TC-UI-SHELL-003` outcome | derived |
| `xdg_session_type` | string | `x11`, `wayland`, or `unknown` (Linux only; `<not-applicable>` on Windows) | host capture |

The §3.2 schema is **closed for required keys**: any key not listed above and not admitted as an optional key by §3.2.1 is invalid and shall be rejected by a future verification helper. The schema may be extended (additional required keys or additional optional keys) only by a controlled `version` bump in this specification.

### 3.2.1 Optional fields added in v0.3.0

The following keys are admitted as **optional** by v0.3.0. They MAY appear in `run-summary.json`; their absence does not violate the §3.2 closed-for-required-keys statement. When present, they shall obey the rules of this specification — in particular §6.2 rule 7.

| Key | Type | Allowed values / format | Source |
|---|---|---|---|
| `student_id_hash` | string | one of: the literal `<not-applicable>` (no student is associated with the capture); `fnv1a64:<16-hex>` (FNV-1a 64 hash of the student internal id, matching the [Professor CSV Intake Specification](professor-csv-intake-specification.md) `fnv1a64:<16hex>` redaction convention); `sha256:<64-hex>` (SHA-256 of the student internal id); or, in a placeholder package only, the literal `<placeholder>` | user-executed (or constant for `<not-applicable>` / `<placeholder>`) |

This field is intended for D6 captures where a student is the operator of the launched desktop (for example, a student reviewing their own per-student workspace under a future authorized increment). When the operator is staff or a professor, `student_id_hash` shall be absent or `<not-applicable>`.

The presence or absence of `student_id_hash` does **not** change the §5 `status="accepted"` predicate; it is recorded for audit traceability only. Adding this optional field does not relax any §7 non-claim.

The set of admitted optional keys (currently only `student_id_hash`) may be extended only by a controlled `version` bump in this specification. Any `student_*` key other than `student_id_hash` is unauthorized in v0.3.0 and shall be rejected.

### 3.3 `manifest.sha256` shape

Each line is `<hex-sha256>  <repo-relative-path-from-package-root>`. Order is the byte-sorted package-relative path. The `manifest.sha256` file itself is excluded from its own entries.

### 3.4 `attestation/reviewer-attestation.txt` shape

```text
reviewer_owner=<name>
attestation_date_utc=<YYYY-MM-DDTHH:MM:SSZ>
visible_ui_fields_attested=true
capture_artifact_kind=<screenshot|screen-recording|screenshot-and-recording>
capture_artifact_path=<repo-relative-path>
notes=<optional free text, redaction rules in §6 apply>
```

The attestation file shall be plain UTF-8 text. The reviewer must sign their own name in plaintext under `reviewer_owner=`. The file shall not contain any value rejected by §6.

## 4. Attestation fields

A D6 package's `human_attestation_visible_ui_fields=true` may be set only when **all** of the following items have been visually confirmed by the reviewer in the captured artifact (the same UI-fields list used by M1A is reused so D6 stays consistent with the M1A baseline and the desktop-app plan §6 D5 home render):

- `EduOps Desktop` heading visible (Tauri window title or H1, not browser tab text only);
- `ui_shell=tauri2-webview2-shell` or the cross-platform Tauri shell identity string visible;
- `adapter_modes=fake,local` visible;
- `live_external_action=false` visible;
- `direct_ui_filesystem_access=false` visible;
- `direct_ui_git_access=false` visible;
- `network_request_enabled=false` visible;
- `Create local course` action label visible (disabled state is acceptable and recommended; the action is fixture-local);
- `course_id=course_eduops-m0_2026-spring` placeholder text visible;
- `evidence_path=build/evidence/slice-a/local-skeleton` visible;
- `github_mutation_made=false` visible;
- `remote.origin.url=<none>` visible;
- absence of any unrelated sensitive content in the capture (per §6).

If any item is not visible in the capture, the attestation shall set `visible_ui_fields_attested=false` and the package shall remain `candidate-for-review`.

## 5. Candidate vs. final status distinction

`status` is the controlled state of the package. It is derived from explicit predicates so Ralph can deterministically classify a returned package without inventing intent.

```text
status = "accepted"  iff
    tc_ui_shell_001 == true
  and tc_ui_shell_002 == true
  and tc_ui_shell_003 == true
  and human_attestation_visible_ui_fields == true
  and platform_match == true
  and platform_webview_runtime_accepted == true
  and capture_artifact_path is present and non-placeholder
  and capture_artifact_sha256 is a 64-hex-character SHA-256 (or two such values for screenshot-and-recording)
  and ipc_health == "ok"
  and required_human_evidence_remaining == []
  and live_external_action == false
  and external_call_made == false
  and github_mutation_made == false
  and network_request_enabled == false
  and remote_origin_url == "<none>"

status = "candidate-for-review"  otherwise (any required field missing,
                                  any flag mismatched, attestation pending,
                                  or capture artifact missing)
```

The string `closed` is **not** a valid value for the `status` field on this package. Gate closure is recorded by a separate `desktop-d6-launch-gate-evidence.md` document that Ralph may produce only after verifying the returned `accepted` package per §9. This separation mirrors the existing M1A pattern where the package is `candidate-for-review` until reviewed and the gate closure is recorded in a different controlled document.

## 6. Redaction rules

Every text-bearing field on the package (`run-summary.json`, `manifest.sha256`, `platform/*.txt`, `attestation/*.txt`, and the on-disk capture metadata in EXIF/file path) is subject to the following redaction rules before the package is considered shippable for review:

1. No raw GitHub personal access token shape: the byte substrings `ghp_` and `github_pat_` (case-insensitive ASCII) are forbidden.
2. No URL credential form: the ASCII pattern `://<authority>:<secret>@<host>` is forbidden (matches the existing `scan_csv_bytes_for_raw_secrets` pattern in `eduops_domain`).
3. No raw HTTPS / HTTP / SSH repository URL pointing at a live host: `https://`, `http://`, `git@` substrings are forbidden in `run-summary.json` and `manifest.sha256`; in `attestation/notes` they shall be replaced by the FNV-1a 64 envelope (`fnv1a64:<16hex>`) as established by the professor CSV intake spec.
4. No SSH PEM blob: `-----BEGIN OPENSSH PRIVATE KEY-----`, `-----BEGIN RSA PRIVATE KEY-----`, `-----BEGIN EC PRIVATE KEY-----`, and `-----BEGIN PRIVATE KEY-----` are forbidden anywhere in the package.
5. No raw email substring: text matching `<local>@<host>.<tld>` is forbidden in `run-summary.json` and `manifest.sha256`; the reviewer name shall be a display name, not an email.
6. No raw long-digit sequence that could be an institutional or government identifier: 7+ contiguous digits in non-numeric semantic fields (anywhere except `git_head`, `capture_artifact_sha256`, port numbers in `desktop-environment.txt`, version strings, and timestamps) are forbidden.
7. No raw student identifier: see §6.2 for the rule 7 policy. The optional `student_id_hash` field (admitted in v0.3.0 §3.2.1) is the only authorized `student_*` key, and its value is restricted to a closed set of redacted forms (`<not-applicable>`, `<placeholder>` for placeholder packages, `fnv1a64:<16-hex>`, or `sha256:<64-hex>`); any raw student identifier is forbidden.
8. Capture artifact EXIF (PNG/JPEG/MP4 metadata) shall be inspected and any field carrying GPS, device serial, host machine name, or other PII shall be stripped before the artifact is committed to the evidence package.
9. The capture artifact image content itself shall not show unrelated sensitive on-screen content (chat windows, password managers, secrets, other repositories). The reviewer attests this in §4.

A future verification helper (rules 1–6 are already encoded in `apps/desktop-ui/scripts/desktop-d6-evidence-validate.mjs` per §6.1; rule 7 enforcement is scoped to the follow-up row `MB-DESKTOP-D6-EVIDENCE-VALIDATE-RULE-7-T1`) shall encode rules 1–7 as a byte-stream + structured-field scan analogous to the existing `scan_csv_bytes_for_raw_secrets` / `scan_local_checkout_evidence_for_raw_secrets` pattern. Rules 8 and 9 remain reviewer responsibility.

### 6.1 Rule 6 field whitelist (added in v0.2.0)

Rule 6 ("7+ contiguous digits in non-numeric semantic fields") would produce false positives if applied uniformly to every text-bearing field in the §3.2 schema, because several fields carry legitimate long-digit content (Git SHA, content SHA-256, timestamps embedded in audit ids, semantic version strings, OS version strings, port numbers in environment metadata). This section enumerates the controlled per-field policy so a verification helper can enforce rule 6 deterministically.

**Numeric-semantic-exempt fields (rule 6 is NOT applied).** These fields carry hex hashes, semantic versions, or timestamp prefixes whose digit content is part of the value's legitimate structure:

- `git_head` — Git SHA-1 (40 hex chars) or SHA-256 (64 hex chars).
- `capture_artifact_sha256` — single 64-hex value or two comma-separated 64-hex values.
- `audit_event_id` — `audit_desktop_d6_launch_<YYYYMMDD-HHMMSS>` carries a timestamp prefix; rule 6 may scan any trailing free text after the timestamp prefix but the timestamp itself is exempt.
- `app_version`, `node_version`, `npm_version`, `tauri_version`, `tauri_cli_version`, `rust_toolchain` — semantic version strings (e.g., `0.1.0`, `v22.22.2`, `cargo 1.95.0`); the digit groups inside dotted-version-number patterns are part of the value.
- `platform_webview_runtime` — version-bearing runtime identifier (e.g., `libwebkit2gtk-4.1-0 2.52.3-0ubuntu0.24.04.1`, `WebView2 Runtime 120.0.2210.91`).
- `os` — distribution + version string (e.g., `Ubuntu 24.04 LTS`, `Windows 11 Pro`).
- `schema_version` — semantic version of this specification.
- `student_id_hash` (v0.3.0 optional) — when present, the value is either the literal `<not-applicable>`, the literal `<placeholder>` (placeholder packages only), or a redacted hash form (`fnv1a64:<16-hex>` or `sha256:<64-hex>`); the hex characters in the hash forms are part of the value and are not a long-digit identifier.

**Rule 6 strict fields (long-digit substring of 7+ contiguous digits is rejected).** These fields shall not legitimately carry long-digit identifiers under the current schema:

- `reviewer_owner` — display name only; institutional/government identifiers are forbidden per D6 spec §6 rules 5 and 7.
- `app_command_used` — verbatim launch command string from a closed set (`npm run desktop:dev`, `npm run desktop:build`, or `<dry-run-inert>` in placeholder packages).
- `desktop_capture_environment` — closed enum (`linux-x11`, `linux-wayland`, `windows-desktop`).
- `platform` — closed enum (`linux`, `windows`).
- `os_platform` — closed enum (`linux`, `darwin`, `win32`, etc.) per Node.js `process.platform`.
- `arch` — closed enum (`x64`, `arm64`, `aarch64`, etc.) per Node.js `process.arch`.
- `host_runtime_pkgconfig_status` — closed enum (`present`, `missing`).
- `ipc_health` — closed enum (`ok`, `degraded`, `unreachable`).
- `capture_artifact_kind` — closed enum (`screenshot`, `screen-recording`, `screenshot-and-recording`).
- `xdg_session_type` — closed enum (`x11`, `wayland`, `unknown`, `<not-applicable>`).
- `status` — closed enum (`accepted`, `candidate-for-review`).
- `adapter_modes` — literal `fake,local` for D6 (closed set).
- `git_branch` — typically short alphanumeric/`/`/`-` token; long-digit sequences are unexpected.
- Every string element of the `required_human_evidence_remaining` array — closed enum of item names (`screenshot`, `attestation`, `platform_runtime`, `human_attestation_visible_ui_fields`, `ipc_health`).

A verification helper shall apply rule 6 to the strict fields only and skip the exempt fields. If a future schema extension adds a new field, this section shall be amended to classify it before the helper is updated.

### 6.2 Rule 7 policy (enabled in v0.3.0)

Rule 7 ("raw student identifier") is now enabled by the optional `student_id_hash` field admitted in §3.2.1.

**Field-level enforcement.** When any `student_*` key is present in `run-summary.json`:

1. The key shall be `student_id_hash` (no other `student_*` key is authorized in v0.3.0; any other `student_*` key is rejected as an unauthorized schema extension).
2. The value shall be exactly one of:
   - the literal `<not-applicable>`;
   - the literal `<placeholder>` (permitted only in a placeholder package per §8);
   - `fnv1a64:<16-hex>` where `<16-hex>` matches the regex `^[0-9a-f]{16}$` (case-insensitive);
   - `sha256:<64-hex>` where `<64-hex>` matches the regex `^[0-9a-f]{64}$` (case-insensitive).
3. The value shall NOT be a raw student identifier. The following forms are explicitly rejected:
   - a bare digit sequence (e.g., `12345678`) — rejected because such a sequence may be an institutional or government identifier;
   - an email-form substring (e.g., `student@example.com`) — already covered by rule 5 but explicitly recapped here;
   - any plain-text personal name, username, or institutional id substring outside the four allowed value forms above.
4. The `student_id_hash` field is exempt from rule 6 (long-digit identifier) because the hex characters in the hash forms are part of the value's legitimate structure (see §6.1).

**Cross-field enforcement.** No `student_*` raw identifier may appear anywhere else in `run-summary.json` (for example, embedded in `notes` of `attestation/reviewer-attestation.txt`, in `reviewer_owner`, or in `audit_event_id`). A future verification helper shall encode this as a byte-stream scan over every text-bearing field analogous to the existing `scan_csv_bytes_for_raw_secrets` / `scan_local_checkout_evidence_for_raw_secrets` pattern. Rule 6's long-digit-substring scan already catches bare 7+ digit sequences in `reviewer_owner` and other §6.1 strict fields; rule 7 extends that posture by binding the dedicated `student_id_hash` field to a closed set of redacted forms.

**Placeholder package interaction.** A placeholder package per §8 may carry `student_id_hash=<placeholder>` or `student_id_hash=<not-applicable>`. The placeholder literal `<placeholder>` is permitted only for placeholder packages and shall be rejected by the §5 acceptance predicate path (placeholder packages can never be `accepted`).

**Verification helper status.** Encoding rule 7 in `apps/desktop-ui/scripts/desktop-d6-evidence-validate.mjs` is the scope of the follow-up Ralph row `MB-DESKTOP-D6-EVIDENCE-VALIDATE-RULE-7-T1`. This specification's acceptance enables that follow-up; it does not by itself modify the validator.

## 7. Fail-closed non-claim language

The accompanying `desktop-d6-launch-gate-evidence.md` document, once authored by Ralph after a returned `accepted` package (per §9), shall include the following non-claim block verbatim. This list is the controlled non-claim baseline; Ralph may not omit, weaken, or relax any item:

```text
This D6 launch evidence does NOT claim:

- installer publication or distribution readiness;
- DEMO-1 acceptance or DEMO-1 readiness;
- end-to-end interactive accessibility audit with a real screen-reader;
- keyboard navigation simulation across the full app surface;
- live external action, network call, credential resolution, token refresh,
  rotation, or storage modification;
- live GitHub action, real `git clone`/`fetch`/`push`/`ls-remote`;
- remote repository administration, submission/provisioning state promotion,
  or evaluation-result authority;
- additional IPC commands beyond the existing `query_session_capabilities`
  M1A session-capability command (no new IPC surface is opened by D6);
- repository administration, real CSV upload UI, real desktop file-picker UI,
  real reviewer attestation workflow beyond the plain-text attestation file;
- user-managed external-repo boundary actions per `EDUOPS-DEC-064` and
  `EDUOPS-DEC-065`.
```

The same non-claim block shall be repeated in the `attestation/reviewer-attestation.txt` `notes` field as a footer when the reviewer attests visible UI fields, so the package itself carries the non-claim posture forward independent of the gate evidence document.

## 8. Fixture-local / pre-launch placeholder package

Ralph may not produce a real D6 capture. Ralph **may**, when later seeded as a separate row, produce a controlled placeholder package whose only purpose is to exercise schema validation. A placeholder package shall:

- live under `build/evidence/desktop-d6-launch/placeholder-<YYYYMMDD-HHMMSS>/`;
- record `status=candidate-for-review`;
- record `app_command_used=<dry-run-inert>`;
- record `capture_artifact_kind=<not_captured>`, `capture_artifact_path=<not_captured>`, `capture_artifact_sha256=<not_captured>`;
- record `human_attestation_visible_ui_fields=false`, `platform_webview_runtime=<placeholder>`, `platform_webview_runtime_accepted=false`, `reviewer_owner=<pending>`, `ipc_health=<not_observed>`, `tc_ui_shell_001=false`, `tc_ui_shell_002=false`, `tc_ui_shell_003=false`;
- record `required_human_evidence_remaining=["screenshot","attestation","platform_runtime","human_attestation_visible_ui_fields","ipc_health"]`;
- never appear in the controlled evidence summary document as anything other than an explicit dry-run example.

A placeholder package is **never** sufficient to close the D6 gate. The schema-validation utility, if later authored, shall accept placeholder packages only when every placeholder-required literal above is present verbatim.

## 9. Ralph closure action after user returns evidence

This section mirrors [M1A Desktop Gate Closure Runbook](../06-implementation/m1a-desktop-gate-closure-runbook.md) §5 with the path-B Tauri 2 entrypoint adaptations.

After the user provides a returned package, Ralph shall:

1. verify the supplied `run-summary.json` parses and contains every key listed in §3.2;
2. verify the `status="accepted"` predicate in §5 holds over the parsed values;
3. verify the linked `capture_artifact_path` exists at the package root and its SHA-256 matches `capture_artifact_sha256`;
4. verify `manifest.sha256` covers every file in the package other than itself and each recorded hash matches;
5. verify the redaction rules in §6 1–7 against `run-summary.json` and the `*.txt` files (text scan); rules 8–9 remain reviewer-attested;
6. verify the platform runtime evidence per DEC-OS-001 §2 (WebView2 runtime details for Windows; distribution / display / session type / webview runtime for Linux);
7. verify `live_external_action=false`, `external_call_made=false`, `github_mutation_made=false`, `network_request_enabled=false`, and `remote_origin_url=<none>` are all present verbatim;
8. verify `app_command_used` is one of the authorized launch commands per §3.2;
9. create a `docs/06-implementation/desktop-d6-launch-gate-evidence.md` document modeled on [M1A Desktop Gate Closure Evidence](../06-implementation/m1a-desktop-gate-closure-evidence.md);
10. include the §7 non-claim block verbatim;
11. update `ralph.md` to mark the desktop-app plan §6 D6 gate accepted and continue with the next controlled row;
12. run repository validation (`npm run m0:check` and `git diff --check`) and commit a focused `docs:` gate-closure commit.

Ralph shall not perform any of the above steps before the user returns a real captured package. If any step fails, Ralph shall stop and report a user-run command block per `ralph.md` §2.

## 10. Future controlled rows authorized by this acceptance

Accepting this specification authorizes the following controlled docs/control rows that the Ralph queue-refill checkpoint may later seed under continuous-run authorization without further user confirmation:

- A `docs/03-verification-validation/desktop-d6-launch-evidence-template.json` placeholder template populated from §3.2 keys with `<placeholder>` values; this is analogous to the existing `m1a-gate-closure-template.json` referenced by the M1A runbook §3.2.
- A `docs/06-implementation/desktop-d6-launch-capture-runbook.md` controlled runbook modeled on the M1A runbook with the path-B Tauri 2 commands; the runbook shall not invoke the commands itself; it shall only document them for user-executed evidence capture.
- A fixture-local schema-validation helper (e.g., `apps/desktop-ui/scripts/desktop-d6-evidence-validate.mjs`) that walks a returned package, parses `run-summary.json`, evaluates the §5 predicate, runs the §6 redaction rules 1–7, and reports `accepted` / `candidate-for-review` without writing any data.

Each of those rows shall be a separate Ralph PREP/T/GATE cycle. None of them may execute a real desktop launch, install host runtime software, invoke `cargo tauri dev`/`build`, capture screenshots, or close the D6 gate.

## 11. Relationship to other specifications

- [Desktop App Development Plan](../06-implementation/desktop-app-development-plan.md) §6 D6 is the source of the gate target and acceptance bullets that this document expands into a closed schema.
- [DEC-OS-001 Windows and Linux Desktop Target](dec-os-001-windows-linux-desktop-target.md) §2 is the source of the `platform_webview_runtime` evidence requirement.
- [Desktop Entrypoint Dependency Adoption Authorized Decision](desktop-entrypoint-dependency-adoption-authorized-decision.md) §3, §6, §7 are the source of the non-claim list and the authorized command set referenced by §3.2's `app_command_used` allowed values and by §7's non-claim block.
- [M1A Desktop Gate Closure Runbook](../06-implementation/m1a-desktop-gate-closure-runbook.md) §3 and [M1A Desktop Gate Closure Evidence](../06-implementation/m1a-desktop-gate-closure-evidence.md) §2 are the precedent for the package layout, the run-summary fields, and the candidate-for-review-vs.-accepted-vs.-closed separation.
- [UI Shell Demonstration Test Cards](../03-verification-validation/ui-shell-demo-test-cards.md) is the source of `TC-UI-SHELL-001..003` referenced by §3.2.
- The existing `apps/desktop-ui/scripts/desktop-smoke-template.mjs` `--dry-run` template's 11-key shape is the seed for §3.2's broader set; the same key names are reused where applicable to preserve byte-determinism on regeneration.

## 12. Acceptance boundary

Acceptance of this specification means:

- the schema in §3, attestation fields in §4, candidate-vs.-final logic in §5, redaction rules in §6, non-claim block in §7, placeholder-package shape in §8, Ralph closure procedure in §9, and authorized future rows in §10 are the controlled baseline for D6 evidence;
- Ralph may classify D6 candidates against this schema and seed safe docs/control follow-ups in §10 without further user confirmation;
- the D6 gate itself is **not** opened, advanced, executed, or closed by this acceptance;
- no Cargo dependency, no `apps/desktop/src/main.rs` change, no `apps/desktop/Cargo.toml` change, no `apps/desktop/build.rs` change, no `package.json` script change, no host runtime install, no Tauri CLI install, no live external action, no credential resolution, no remote action, no installer publication, no DEMO-1 claim is authorized or implied by this acceptance.

## 13. Change log

- **v0.3.0 (2026-05-20):** admitted the optional redacted `student_id_hash` field in new §3.2.1 with a closed set of allowed value forms (`<not-applicable>`, placeholder-only `<placeholder>`, `fnv1a64:<16-hex>`, `sha256:<64-hex>`); enabled the rule 7 policy in §6.2 (field-level enforcement of the closed value set plus cross-field rejection of any raw student identifier elsewhere); refined §6 rule 7 intro line to reference §6.2; added `student_id_hash` to the §6.1 numeric-semantic-exempt list so the hex characters in the hash forms are not flagged by rule 6; refined the §3.2 `schema_version` row to describe semver compatibility across version bumps; noted that the rule 7 validator implementation is scoped to a follow-up row. No §3.2 required-key change; no §5 predicate change; no §7 non-claim relaxation; no Cargo dependency change; no source code change; no real launch, screenshot, credential, network, remote, or DEMO-1 action authorized.
- **v0.2.0 (2026-05-20):** added §6.1 enumerating the rule 6 field whitelist (numeric-semantic-exempt and rule-6-strict fields) so a verification helper can apply rule 6 deterministically; added §6.2 recording that rule 7 (raw student id) remained N/A under the v0.2.0 38-key schema and would be enabled by a future schema extension that adds a `student_*` field (now enabled in v0.3.0). No §3.2 schema change; no §5 predicate change; no non-claim relaxation.
- **v0.1.0 (2026-05-20):** initial schema-only acceptance with §0 document scope, §1 purpose, §2 authorized-vs.-user-executed boundary, §3 evidence package shape (38-key closed `run-summary.json` schema, `manifest.sha256` byte-sorted layout, attestation file shape), §4 attestation visible-UI-fields list, §5 candidate-vs.-accepted-vs.-closed status predicate, §6 redaction rules 1–9, §7 controlled non-claim block, §8 fixture-local placeholder package shape, §9 Ralph closure procedure mirroring the M1A runbook §5, §10 authorized future controlled rows, §11 relationship to other specs, §12 acceptance boundary.
