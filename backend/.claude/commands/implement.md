---
description: "Spec에서 코드를 구현합니다. 사용법: /implement <spec-id> (예: /implement 01-ooxml-pipeline)"
allowed-tools:
  - Read
  - Write
  - Edit
  - Glob
  - Grep
  - Bash(ruff *)
  - Bash(mypy *)
  - Bash(pytest *)
  - Bash(python *)
argument-hint: "<spec-id>"
---

# /implement — Spec → Code 구현 워크플로우

**입력:** $ARGUMENTS (예: `01-ooxml-pipeline`)

## 워크플로우

### Step 1: 명세 로드
1. `specs/$ARGUMENTS.md` 파일을 읽는다.
2. 해당 spec의 모든 구현 기준(How)과 수용 기준(Acceptance Criteria)을 파악한다.
3. 담당 역할(백엔드/프론트엔드/비즈니스 로직)별로 작업을 분류한다.

### Step 2: 실행 계획 수립
1. `plans/$ARGUMENTS-plan.md` 에 다음을 작성한다:
   - 구현할 모듈 목록
   - 각 모듈의 클래스/함수 시그니처
   - 의존성 관계
   - 예상 테스트 케이스
2. 계획을 사용자에게 보여주고 승인을 받는다.

### Step 3: 코드 구현
1. `src/` 하위에 해당 모듈을 생성한다.
2. CLAUDE.md의 코딩 컨벤션을 준수한다:
   - 타입 힌트 필수
   - docstring 필수
   - 함수 30줄 이내
3. 구현 중 spec과 불일치가 발생하면 즉시 중단하고 보고한다.

### Step 4: 테스트 작성
1. `tests/` 하위에 테스트 파일을 생성한다.
2. 수용 기준(Acceptance Criteria)의 각 항목을 테스트 케이스로 변환한다.
3. 경계값, 예외 케이스를 추가로 작성한다.

### Step 5: 검증
1. 다음을 순서대로 실행한다:
   ```bash
   ruff check src/ --fix
   mypy src/ --ignore-missing-imports
   pytest tests/ -v --tb=long
   ```
2. 모두 통과하면 완료를 선언한다.
3. 실패하면 수정 후 재실행한다.

### Step 6: 리뷰 요청
- code-reviewer 에이전트에게 리뷰를 위임한다.

## 주의사항
- spec에 없는 기능을 추가하지 마라.
- spec의 수용 기준을 변경하지 마라.
- 네트워크/pickle/쓰기모드 사용 금지.
