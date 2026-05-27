Error: Reached max turns (12)CLAUDE_DECISION: IMPROVE

## 1. 판정 근거 (요약)

베이스라인(Windows 데스크톱·로컬 우선, Git-backed Notion-style, no-LMS, GitHub-first later, fake/local 픽스처 게이트 선행)을 실제 베타 테스터가 사용 가능한 산출물로 도달시키기에 통제문서가 **충분하지 않음**. 핵심 근거:

- 통제문서 자체가 명시적으로 **"P0 HOW-level 계약이 작성되기 전 프로덕션 코드 시작 금지"**(`EDUOPS-DEC-040`, `06-implementation/implementation-readiness-gap-analysis.md` §5, `implementation-executability-improvement-plan.md` §6)라고 결정해 둠.
- 그러나 P0 5종 (`technology-stack-decision-record.md`, `process-topology-and-ipc-contract.md`, `module-and-package-layout.md`, `canonical-domain-idl.md`, `internal-api-contract.md`) 과 P1 7종(`git-adapter-specification.md` 외) **모두 리포지토리에 존재하지 않음** (find 결과 0건).
- `EDUOPS-FR-067/068/070/071/072`는 "promoted-document-required" 상태로, **약속만 있고 계약 본문 없음** → 베타 테스터용 Windows 설치본/실데이터 라운드트립을 코딩으로 진입할 수 없음.
- DEMO-1조차 "P0 구현 계약이 수용된 후"의 산출물로 미래형으로 기술됨(`working-demonstration-evidence-plan.md` §9). 즉 베타 테스터가 만질 vertical slice가 코드/픽스처 수준에서 아직 존재하지 않음.
- 결정 미정 항목(`EDUOPS-DEC-009` UI 프레임워크, `EDUOPS-DEC-010` C/C++ 툴체인/실행 위치, `EDUOPS-DEC-013` 학적 필드/오버라이드 권한)이 **Open** 상태로 남아 있어 베타 배포 결정점이 비어 있음.

베타 테스터 사용 가능성(설치-실행-과제수행-제출-회수-피드백) 관점에서, WHAT/WHY 통제는 강하지만 HOW 계약·실행 게이트·패키징 베이스라인이 비어 있어 지금 개발에 착수하면 코드 안에서 아키텍처 결정이 발생하며 ISO/통제 트레이서빌리티가 즉시 깨짐.

## 2. 개선 계획 (우선순위/파일/수용 게이트)

### P0 — 코딩 착수 차단 해제 (반드시 선행, 순서대로)

| # | 추가/갱신 파일 | 수용 게이트 |
|---|---|---|
| P0-1 | `02-design-planning/technology-stack-decision-record.md` 신규 | 데스크톱 셸·런타임·에디터 기반·로컬 DB·Git 라이브러리·익스포터 기반·패키저 각 1개씩 채택안+거부안 표 존재, `EDUOPS-DEC-009`/`010` Closed 처리 |
| P0-2 | `02-design-planning/canonical-domain-idl.md` 신규 (Course, Section, RosterEntry, StudentIdentityBinding, Assignment, BlockDocument, EditOperation, SubmissionSnapshot, EvaluationRun, ExportJob, AuditEvent, DiagnosticPackage) | JSON Schema/IDL로 머신체크 가능, 픽스처 1세트로 검증 가능 |
| P0-3 | `02-design-planning/process-topology-and-ipc-contract.md` 신규 | 셸/로컬 서비스/Git 워커/평가 러너/익스포트 워커 lifecycle·IPC envelope·크래시 복구 명시, "명시적 명령 없이는 외부 프로세스 미기동" 규칙 인코딩 |
| P0-4 | `02-design-planning/module-and-package-layout.md` 신규 | 도메인/앱/인프라/어댑터/픽스처/테스트 경로, 금지 의존 방향 표 존재 |
| P0-5 | `02-design-planning/internal-api-contract.md` 신규 | 모든 UI↔서비스 명령/쿼리의 입력·출력·오류코드·감사이벤트·idempotency 시그니처 명시 |
| P0-6 | `03-verification-validation/software-test-description.md` 갱신 + `fixture-corpus-and-harness-plan.md` 신규 (`EDUOPS-CVR-001`, `EDUOPS-CVR-002` 정식화) | SLICE-A/B/C 픽스처 게이트 ID·통과 조건·해시/매니페스트/로그 산출물 명세, PII 없음 규칙 |
| P0-7 | `02-design-planning/state-machine-canonical.md` 확장 (또는 `state-machine-implementation-tables.md` 신규로 `EDUOPS-CFR-007`/`008`/`009` 정식화) | 학생 lifecycle·submission·assignment release/update 전이 표(이벤트·가드·부작용·영속점·오류코드), sync 충돌 결정·차단 행위·롤백, 권위 시계/지연 정책 |

### P1 — SLICE-A/B/C 진입 차단 해제 (P0 통과 후 즉시)

| # | 파일 | 수용 게이트 |
|---|---|---|
| P1-1 | `02-design-planning/git-adapter-specification.md` | fake/local과 GitHub-backed가 동일 계약으로 테스트됨 |
| P1-2 | `02-design-planning/local-storage-adapter-specification.md` | SQLite DDL, 잠금, 마이그레이션, 인덱스 리빌드 라운드트립 픽스처 가능 |
| P1-3 | `02-design-planning/editor-adapter-bridge-specification.md` + `korean-text-handling-profile.md` 보강 (Korean IME 합성/오토세이브 억제/언두 그룹) | 에디터 후보가 동일 계약으로 채점 가능, IME 회귀 픽스처 통과 기준 명시 |
| P1-4 | `02-design-planning/secret-storage-adapter-specification.md` (DPAPI) | 토큰 저장/회전/소거 시그니처, GitHub 어댑터 내부 토큰 은닉 금지 |
| P1-5 | `02-design-planning/asset-binary-adapter-specification.md` | 이미지·DOCX/HWPX 해시·LFS 적격성·정리 신호 |
| P1-6 | `06-implementation/build-packaging-release-engineering.md` (`EDUOPS-CNFR-001`) | 새 개발자가 문서만으로 Windows 부트스트랩 가능, 락파일/린트/타입/테스트 명령·MSI/Installer·서명·자동업데이트 룰 (베타 배포 전제) |

### P2 — DEMO-1 실행→베타 테스터 도달 (P1 후)

| # | 파일/작업 | 수용 게이트 |
|---|---|---|
| P2-1 | `03-verification-validation/working-demonstration-evidence-plan.md`에 첨부할 `demo-fixture-corpus-and-script.md`, `demo-run-evidence-schema.md` | DEMO-1 12-step 스크립트의 픽스처 경로·`run-summary.json` 스키마 확정 |
| P2-2 | `02-design-planning/evaluation-runner-io-contract.md` (`EDUOPS-CIR-005`) | C++ 1개 advisory 픽스처가 결정론적 result JSON 생성, Windows 샌드박스 경계 정의 |
| P2-3 | `02-design-planning/github-adapter-specification.md` (드라이런/모의서버) | 자격증명 없이 모의서버 통과, live는 명시 게이트 후에만 |
| P2-4 | `02-design-planning/exporter-implementation-specification.md` (`EDUOPS-CFR-005`+`CIR-010` 병합) | 골든 픽스처와 손실/경고 매니페스트 일치 |
| P2-5 | `02-design-planning/authorization-implementation-specification.md`, `observability-and-diagnostics-specification.md`, `roster-schema-and-identity-policy.md` 확장 (Open `EDUOPS-DEC-013` 폐쇄) | PDP/PEP 요청·결정 JSON, 상관 ID, 로스터 필드/오버라이드 권한 확정 |

### 횡단 — 미결 결정 폐쇄

- `EDUOPS-DEC-009/010/013`를 Accepted로 전환하는 결정 레코드를 `05-decisions/decision-log.md`에 추가. (UI 스택, C/C++ 툴체인·실행 위치, 학적 필드/오버라이드)
- `01-requirements/implementation-requirements-gap-register.md`에서 P0/P1 행이 새 문서로 닫힐 때마다 `promoted-document-required` → `promoted`로 상태 갱신.

## 3. 다음 평가 중단 기준 (Stop criteria — 모두 충족 시 재평가 가능)

1. P0-1~P0-7 7개 문서가 리포지토리에 존재하고 INDEX/Roadmap에서 참조됨, `EDUOPS-FR-067/070/071`의 수용기준 모두 충족.
2. `EDUOPS-DEC-009/010/013` 모두 Accepted 상태로 갱신.
3. SLICE-A 픽스처 게이트(빈 vertical 스켈레톤)의 통과 조건이 STD에 등록되고 `EDUOPS-CVR-001`이 `promoted` 상태.
4. `build-packaging-release-engineering.md`가 Windows 부트스트랩·서명·MSI/Installer·자동업데이트·롤백을 포함(베타 배포 사전 조건).
5. `working-demonstration-evidence-plan.md`의 DEMO-1 스크립트가 실제 실행 가능한 픽스처/하니스 경로로 인스턴스화되어 있고, `live_external_action=false` 증거 패키지 레이아웃이 정의됨.

위 5개가 모두 충족되면 베타 테스터 도달 가능한 개발 착수에 대한 재승인 평가 의미가 있음. 그 전에는 다시 IMPROVE 판정이 유지됨.
