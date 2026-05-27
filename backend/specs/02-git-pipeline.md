# Spec 02: 로컬 Git 저장소 분석 파이프라인

> **대응 요구사항:** FR-2.1, FR-2.2
> **담당:** 백엔드(조원희) + 프론트엔드(이대한)

---

## FR-2.1 — git log 기반 커밋 데이터 추출

### 가치
조장이 코드 기여량을 자동으로 집계하여 커밋 수·추가/삭제 라인 수를 팀원별로 확인할 수 있다.

### 구현 기준 (How)

| 담당 | 구현 내용 |
|---|---|
| **백엔드** | `subprocess.run()`으로 `git log --numstat` 명령을 호출하고, stdout 문자열을 줄 단위로 읽어 커밋 해시·이메일·타임스탬프·추가/삭제 라인 수를 파싱하여 반환한다. |
| **프론트엔드** | 분석할 로컬 Git 저장소 경로를 선택하는 폴더 선택 다이얼로그를 제공한다. |
| **비즈니스 로직** | 파싱된 커밋 로그를 author_email 기준으로 집계하여 스키마로 구성하는 집계 함수를 구현한다. |

#### 세부 사항
- 호출 명령: `subprocess.run(["git", "log", "--numstat", "--format=%H|%ae|%ai"], cwd=repo_path, capture_output=True, text=True, timeout=30)`
- 결과 스키마: `{"author_email": {"commits": int, "additions": int, "deletions": int}}`
- 예외 처리: `subprocess.CalledProcessError` 및 `FileNotFoundError` → 빈 딕셔너리(`{}`) 반환, 예외 전파 금지
- 타임아웃: **30초** 고정

### 수용 기준 (Acceptance Criteria)

| # | 기준 | 판정 방법 |
|---|---|---|
| AC-1 | 커밋 3개(alice@test.com, +10줄/-5줄) → `{"alice@test.com": {"commits": 3, "additions": 10, "deletions": 5}}` | 딕셔너리 일치 |
| AC-2 | 유효하지 않은 경로(`C:\not_a_repo`) → 빈 딕셔너리(`{}`), 예외 미발생 | 정상 반환 |
| AC-3 | 대용량 저장소(커밋 10,000개) → git log 호출 **30초 이내** 완료 | 타임아웃 내 |

---

## FR-2.2 — 앱 시작 시 Git 설치 여부 헬스체크 및 안내 팝업

### 가치
Git 미설치 상태에서 앱이 조용히 실패하는 대신, 조장이 문제 원인을 즉시 파악하고 해결할 수 있다.

### 구현 기준 (How)

| 담당 | 구현 내용 |
|---|---|
| **백엔드** | 앱 시작 시 `subprocess.run(["git", "--version"])` 호출 결과를 확인하고, 실패 시 프론트엔드로 오류 Signal을 전달한다. |
| **프론트엔드** | Git 미설치 시 경고 문구·다운로드 링크·PATH 설정 안내를 포함한 모달 팝업을 표시하고, `[확인]` 클릭 시 Git 분석 관련 UI 버튼을 비활성화한다. |

#### 세부 사항
- 체크 시점: 메인 윈도우 표시 **전**
- 호출: `subprocess.run(["git", "--version"], capture_output=True, timeout=5)`
- 실패 조건: `FileNotFoundError` 또는 반환 코드 `!= 0`
- 팝업 내용:
  - 경고 문구: `"Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다."`
  - Git 공식 다운로드 링크: `https://git-scm.com/download/win` (클릭 시 기본 브라우저)
  - 환경변수 PATH 설정 안내 1줄 이상
  - `[확인]` 버튼 → 팝업 닫고 Git 분석 기능만 비활성화, 앱 계속 실행

### 수용 기준 (Acceptance Criteria)

| # | 기준 | 판정 방법 |
|---|---|---|
| AC-1 | Git 미설치 환경 → 메인 윈도우 전 팝업 표시 | 팝업 존재 확인 |
| AC-2 | `[확인]` 클릭 후 → 앱 미종료, 메인 윈도우 정상 표시 | 앱 상태 확인 |
| AC-3 | Git 정상 설치 → 팝업 미표시 | 팝업 부재 확인 |
