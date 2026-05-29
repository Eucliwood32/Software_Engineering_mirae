# QCE 문서 인덱스 (Documentation Index)

본 디렉토리는 QCE(부탁해 꼬마선장) 프로젝트의 연구, 요구사항 명세, 설계, 테스트 및 의사결정 내역을 관리하는 공간입니다. **???** 표준을 기반으로 작성되었습니다.

## 디렉토리 구조 및 내용

### `00-research-analysis/` (연구 및 분석)
- `problem-statement.md`: 문제 정의 및 프로젝트 추진 배경
- `concept-of-operations.md`: 시스템 운용 개념 및 유스케이스 시나리오

### `01-requirements/` (요구사항 명세)
- `requirements-record.md`: 기능적 요구사항 (FR) 상세 목록
- `development-constraints.md`: 비기능적 요구사항 (NFR) 및 제약사항 (C)
- `requirements-traceability-matrix.md`: **RTM (요구사항 추적 매트릭스)** - 기능 구현 상태 추적

### `02-design-planning/` (설계 및 기획)
- `architecture-overview.md`: 시스템 아키텍처 및 DFD (데이터 흐름도)
- `model-parser-design.md`: 데이터 파서 설계
- `model-business-logic-design.md`: 정규화·Capping·이상 신호·집계·캐시·리포트 등 BusinessLogic 레이어 상세 설계
- `view-design.md`: PyQt6 UI 계층 및 캔버스 시각화 설계
- `controller-design.md`: 모델-뷰 중재 로직 설계

### `03-verification-validation/` (테스트 및 검증)
- `test-plan.md`: 단위 테스트(Model 우선) 및 통합/수동 테스트 계획
- `test-cases.md`: 주요 기능(FR) 및 제약사항(NFR) 합격 기준표

### `04-risk-management/` (위험 관리)
- `risk-register.md`: 프로젝트 진행 간 발생 가능한 리스크 및 완화 계획

### `05-decisions/` (아키텍처 의사결정 기록 - ADR)
- `ADR-0001-MVC-Pattern.md`: 엄격한 MVC 단방향 아키텍처 채택
- `ADR-0002-PyQt6-Selection.md`: 프론트엔드 프레임워크로 PyQt6 선정
- `ADR-0003-IsolationForest.md`: 어뷰징 탐지 알고리즘 선정
- `ADR-template.md`: (신규 의사결정 시 사용할 템플릿)

### `06-implementation/` (구현 및 배포 가이드)
- `coding-conventions.md`: 네이밍 규칙, 브랜치 전략, 커밋 메시지 규약
- `build-and-package.md`: PyInstaller/Nuitka를 활용한 `.exe` / `.app` 빌드 가이드

---

## 기여자 가이드 (Contributor Guidelines)

문서화 및 코드 작성 시 아래의 원칙을 반드시 준수해야 합니다.

1. **FR-ID 명시 원칙:**
   - 코드 주석: `# FR-1.2` 형태로 기능 ID를 명시합니다.
   - 커밋 메시지: `[FR-1.2] feat: core.xml에서 OS 계정명 추출` 포맷을 사용합니다.
2. **브랜치 전략:**
   - `main` ← `develop` ← `feature/FR-X-설명` 형태로 PR을 생성합니다.
3. **요구사항 추적 (RTM):**
   - 구현이 완료되거나 테스트가 진행 중인 경우, 반드시 `01-requirements/requirements-traceability-matrix.md`의 상태(TODO/WIP/Done)를 갱신합니다.
