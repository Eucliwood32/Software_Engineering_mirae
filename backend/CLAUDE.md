# QCE 프로젝트 헌법 (Project Constitution)

> 이 문서는 모든 에이전트 세션 시작 시 자동 로드됩니다.
> 아래 규칙은 **불변(immutable)** 이며, 어떤 에이전트도 이를 위반하거나 재해석할 수 없습니다.

---

## 프로젝트 개요

**QCE (Quantitative Contribution Evaluator)** — 팀 프로젝트 기여도 정량 평가 도구.
Windows 전용 로컬 데스크톱 앱 (PyQt6 + Python 3.10+). 외부 네트워크 연결 완전 배제.

---

## 🔴 불변 규칙 (Immutable Rules)

### 규칙 1: Spec 우선 원칙
- `specs/` 디렉토리의 명세가 **코드보다 우선**한다.
- 코드가 spec과 불일치하면, 항상 **코드를 수정**한다.
- WHEN spec과 코드가 충돌 → DO NOT spec을 코드에 맞추지 마라 → DO 코드를 spec에 맞춰라.

### 규칙 2: 검증 없이 완료 선언 금지
- 다음 조건이 **모두** 충족되어야 작업 완료를 선언할 수 있다:
  1. `ruff check src/` — 에러 0개
  2. `mypy src/` — 에러 0개
  3. `pytest` — 전체 통과
  4. 커버리지 80% 이상 (Model 계층)
- WHEN 위 조건 중 하나라도 실패 → DO NOT "완료"라고 말하지 마라.

### 규칙 3: specs/ 변경 시 사용자 승인 필수
- `specs/` 디렉토리의 파일을 수정, 삭제, 이동하려면 **반드시 사용자에게 먼저 승인을 받아라**.
- WHEN spec 변경이 필요하다고 판단 → DO 변경 내용을 diff 형태로 제안 → DO NOT 직접 수정.

### 규칙 4: 네트워크 통신 완전 차단
- 소스코드에서 다음 모듈을 **절대 import하지 마라**:
  - `requests`, `urllib`, `httpx`, `socket`, `http.client`, `aiohttp`
- WHEN 외부 URL 열기가 필요 → DO `webbrowser.open()` 만 사용.

### 규칙 5: 읽기 전용 파일 접근
- 분석 대상 파일은 `open(path, 'r')` 또는 `open(path, 'rb')` 모드만 사용한다.
- WHEN 분석 대상 파일에 쓰기 모드 사용 → 즉시 코드 리뷰 Fail.

### 규칙 6: 직렬화 안전
- `pickle` 모듈을 **절대 import하지 마라**. `json` 만 사용한다.
- 캐시 파일(`.qce_cache`)은 반드시 원자적 쓰기(tmp → fsync → os.replace)로 저장한다.

### 규칙 7: MVC 단방향 의존성
- View → Controller → Model 방향만 허용한다.
- WHEN Model이 View를 직접 import → 즉시 코드 리뷰 Fail.
- Signal/Callback 패턴으로만 역방향 통신한다.

---

## 🟡 아키텍처 제약

### 기술 스택
- **언어:** Python 3.10+
- **UI:** PyQt6 (Worker Thread 분리 필수)
- **문서 파싱:** python-docx, python-pptx
- **NLP:** kiwipiepy 또는 soynlp (JRE 의존 금지)
- **테스트:** pytest
- **린터:** ruff
- **타입체커:** mypy
- **패키징:** PyInstaller --onefile

### 모듈 구조
```
src/
├── backend/           # 조원희 — 파일 파싱, Git 분석, 보안
│   ├── ooxml_parser.py
│   ├── git_parser.py
│   ├── messenger_parser.py
│   └── cache_manager.py
├── business_logic/    # 김휘중 — NLP, 점수 산출, 이상치 탐지
│   ├── normalizer.py
│   ├── scoring_engine.py
│   ├── alias_mapper.py
│   └── warning_engine.py
├── frontend/          # 이대한 — PyQt6 UI, 대시보드, 차트
│   ├── main_window.py
│   ├── dashboard_view.py
│   └── weight_panel.py
├── analyzer.py        # 오케스트레이터 (파이프라인 통합)
└── main.py            # 엔트리포인트
```

### 팀 역할
| 학번 | 이름 | 역할 | 담당 영역 |
|---|---|---|---|
| 20222047 | 조원희 | 백엔드 | 파일 파싱, Git 분석, 메신저 포맷 변환, 보안 |
| 20247142 | 이대한 | 프론트엔드 | PyQt6 UI, 대시보드, 차트, Drag & Drop |
| 20221985 | 김휘중 | 비즈니스 로직 | NLP 필터링, 점수 산출, 이상치 탐지, 신원 매핑 |

---

## 🟢 워크플로우 규칙

### 구현 순서
1. `specs/` 에서 해당 기능의 명세를 읽는다.
2. `plans/` 에 실행 계획을 작성한다.
3. `src/` 에 코드를 구현한다.
4. 단위 테스트를 작성한다.
5. `ruff` + `mypy` + `pytest` 를 실행한다.
6. 모두 통과하면 완료를 선언한다.

### 커밋 메시지 규칙
```
<type>(<scope>): <subject>

type: feat | fix | refactor | test | docs | chore
scope: backend | frontend | logic | spec | harness
```

### 코딩 컨벤션
- 모든 public 클래스/메서드에 docstring 필수
- 타입 힌트 필수 (함수 시그니처, 반환 타입)
- 변수명은 snake_case, 클래스명은 PascalCase
- 한 함수는 30줄 이내 권장 (초과 시 분리)

---

## 📁 핵심 경로

| 경로 | 용도 |
|---|---|
| `specs/` | 명세 파일 (SSOT) — 변경 시 사용자 승인 필수 |
| `plans/` | 실행 계획 — spec에서 파생 |
| `src/` | 소스코드 |
| `tests/` | 테스트 코드 |
| `.claude/agents/` | 서브 에이전트 정의 |
| `.claude/commands/` | 슬래시 커맨드 |

---

> ⚠️ 이 문서를 수정하려면 반드시 팀 전원의 합의가 필요합니다.
