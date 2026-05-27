---
description: "전체 프로젝트 검증 파이프라인을 실행합니다. 린터, 타입체커, 테스트, 커버리지를 순차 실행합니다."
allowed-tools:
  - Read
  - Glob
  - Grep
  - Bash(ruff *)
  - Bash(mypy *)
  - Bash(pytest *)
  - Bash(python *)
---

# /validate — 전체 검증 파이프라인

## 워크플로우

### Gate 1: 린터 (ruff)
```bash
!ruff check src/ --output-format=concise 2>&1
```

**통과 조건:** 에러 0개
**실패 시:** 자동 수정 가능한 항목은 `ruff check --fix`로 수정 후 재실행

### Gate 2: 타입 체커 (mypy)
```bash
!mypy src/ --ignore-missing-imports 2>&1
```

**통과 조건:** 에러 0개
**실패 시:** 타입 에러 위치와 수정 방향을 제시

### Gate 3: 단위 테스트 (pytest)
```bash
!python -m pytest tests/ -v --tb=long 2>&1
```

**통과 조건:** 0 failures, 0 errors
**실패 시:** 실패 테스트별 원인 분석

### Gate 4: 커버리지
```bash
!python -m coverage run -m pytest tests/ -q 2>&1
!python -m coverage report --show-missing 2>&1
```

**통과 조건:** backend/ + business_logic/ 커버리지 ≥ 80%
**실패 시:** 커버리지가 부족한 모듈과 미커버 라인 목록 출력

### Gate 5: 보안 스캔
```bash
!grep -rn "import requests\|import urllib\|import httpx\|import socket\|import pickle" src/ 2>&1 || echo "✅ 금지 import 없음"
!grep -rn "open(.*'w'\|open(.*'a'" src/ 2>&1 | grep -v "cache_manager\|report_writer" || echo "✅ 비인가 쓰기 모드 없음"
```

**통과 조건:** 금지 패턴 0건
**실패 시:** 즉시 FAIL — 해당 라인 제거 필요

## 최종 결과 요약

```markdown
## 검증 결과 요약

| Gate | 항목 | 결과 | 세부 |
|---|---|---|---|
| 1 | ruff (린터) | ✅/❌ | N errors |
| 2 | mypy (타입) | ✅/❌ | N errors |
| 3 | pytest (테스트) | ✅/❌ | N passed, N failed |
| 4 | coverage (커버리지) | ✅/❌ | XX% |
| 5 | security (보안) | ✅/❌ | N violations |

### 최종 판정: ✅ ALL GATES PASSED / ❌ BLOCKED AT GATE N
```

## 규칙
- 모든 Gate를 순서대로 실행한다 (하나라도 실패하면 이후 Gate는 SKIP하지 않고 계속 실행).
- 최종 판정은 모든 Gate가 통과해야만 PASS이다.
- Gate 실패 시 "나중에 고치면 된다"는 판단을 하지 마라. 지금 고쳐라.
