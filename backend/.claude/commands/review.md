---
description: "최근 변경사항을 리뷰합니다. spec 대비 정합성, 보안 규칙, 코딩 스타일을 검증합니다."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(git diff *)
  - Bash(git log *)
  - Bash(ruff *)
  - Bash(mypy *)
---

# /review — 코드 리뷰 워크플로우

## 워크플로우

### Step 1: 변경 범위 파악
```bash
!git diff --name-only HEAD~1
!git diff --stat HEAD~1
```

변경된 파일 목록과 변경량을 확인한다.

### Step 2: Spec 대비 정합성 검증
1. 변경된 `src/` 파일이 어떤 spec에 해당하는지 식별한다.
2. `specs/` 에서 해당 명세를 읽는다.
3. 수용 기준(Acceptance Criteria)과 실제 구현이 일치하는지 대조한다.

### Step 3: 보안 규칙 검증
다음 패턴이 소스코드에 존재하는지 검사한다:

```bash
!grep -rn "import requests\|import urllib\|import httpx\|import socket\|import pickle" src/
!grep -rn "open(.*'w'\|open(.*'a'" src/ | grep -v "cache_manager\|report"
```

### Step 4: 정적 분석 실행
```bash
!ruff check src/ --output-format=concise
!mypy src/ --ignore-missing-imports --no-error-summary 2>&1 | head -30
```

### Step 5: MVC 위반 검사
Model 계층에서 View를 직접 import하는지 확인:
```bash
!grep -rn "from.*frontend\|import.*frontend" src/backend/ src/business_logic/
```

### Step 6: 리뷰 결과 요약
각 검사 항목의 결과를 표로 정리하고 최종 PASS/FAIL 판정을 내린다.

## 판정 기준
- 🔴 **치명적 위반 1개 이상** → FAIL
- 🟡 **주요 경고만** → CONDITIONAL PASS (수정 권고)
- 🟢 **모두 통과** → PASS
