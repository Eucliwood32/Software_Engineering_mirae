# Spec 06: 비기능적 요구사항 (Non-Functional Requirements)

> **대응 요구사항:** NFR-1, NFR-1.2, NFR-2.1, NFR-2.2, NFR-2.3, NFR-2.4, NFR-3.1, NFR-3.2
> **담당:** 전원

---

## NFR-1 — UI 비동기 처리 (UI Thread Safety)

### 가치
대용량 파일 분석 중에도 UI가 응답 가능한 상태를 유지하여 사용자 경험을 보호한다.

### 구현 기준

| 담당 | 구현 내용 |
|---|---|
| **백엔드** | 파싱·분석 연산을 Worker Thread 내에서 실행, 완료·오류 시 Signal로 결과를 메인 스레드에 전달 |
| **프론트엔드** | Worker Thread 시작 시 Progress Bar 표시, 완료·오류 Signal 수신 시 결과/오류 메시지 업데이트 |

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | 10만 줄 `.txt` 분석 중 메인 윈도우 드래그 → 창 이동 가능 (프리징 없음) |
| AC-2 | 분석 시작 후 1초 이내 Progress Bar 출현 |
| AC-3 | 분석 완료/오류 시 Progress Bar 사라지고 결과/오류 메시지 표시 |

---

## NFR-1.2 — 분석 중복 실행 방지 (Race Condition Guard)

### 가치
`[분석 시작]` 연속 클릭 시 Worker Thread 중복 실행 방지, 데이터 오염 방지.

### 구현 기준

| 담당 | 구현 내용 |
|---|---|
| **백엔드** | Worker Thread 시작·종료 Signal 발행, `try/finally`로 종료 Signal 보장 |
| **프론트엔드** | `is_analyzing` 플래그, `[분석 시작]` 버튼 `setEnabled()` 제어 |

#### 세부 사항
- `is_analyzing: bool = False` 전역 플래그
- 버튼 클릭 시 `is_analyzing == True` → 즉시 return
- Worker 시작 전: `is_analyzing = True`, 버튼 비활성화
- Worker 종료 시: `is_analyzing = False`, 버튼 활성화 (메인 스레드 Signal/Callback)

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | 분석 시작 후 0.5초 이내 버튼 비활성화(disabled) |
| AC-2 | 실행 중 5회 연속 클릭 → Worker Thread 1개만 실행 |
| AC-3 | 동일 입력 재분석 시 → 첫 실행과 동일 점수 (중복 누적 없음) |
| AC-4 | Worker `RuntimeError` 비정상 종료 → 버튼 다시 활성화 |

---

## NFR-2.1 — 읽기 전용 파일 접근

### 구현 기준
- 분석 대상 파일: `open(path, 'r')` 또는 `open(path, 'rb')` 모드만 사용
- 리포트 저장: 사용자 지정 **새 경로**에만 쓰기

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | 분석 후 입력 파일의 `os.path.getmtime` 변화 없음 |
| AC-2 | 코드 리뷰 시 분석 대상 경로에 `open(path, 'w')` 존재 → Fail |

---

## NFR-2.2 — 네트워크 통신 완전 차단

### 구현 기준
- 금지 import: `requests`, `urllib`, `httpx`, `socket`, `http.client`
- URL 열기: `webbrowser.open()` 만 허용

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | 앱 실행 중 외부 IP 송신 패킷 0개 (방화벽/Wireshark 검증) |
| AC-2 | 소스 트리에 네트워크 라이브러리 import 존재 → Fail |

---

## NFR-2.3 — 익명화 통계 캐시 파일 저장 (원자적 쓰기)

### 구현 기준

| 담당 | 구현 내용 |
|---|---|
| **백엔드** | `.qce_cache.tmp` → `fsync()` → `os.replace()` 원자 교체 |
| **프론트엔드** | 캐시 손상 시 모달 다이얼로그 표시 |
| **비즈니스 로직** | 캐시 스키마 정의, 원본 텍스트 포함 여부 검증 |

#### 세부 사항
- 직렬화: `json.dumps()` **만** 사용, `pickle` 금지
- 저장 가능 데이터: 팀원 식별자, 정규화 수치 점수, 타임스탬프, 가중치 설정
- 저장 금지 데이터: 원본 메시지 텍스트, 소스코드 내용
- 원자적 쓰기 3단계:
  1. `.qce_cache.tmp` 에 JSON 완전히 쓰기
  2. `tmp_file.flush()` + `os.fsync(tmp_file.fileno())`
  3. `os.replace('.qce_cache.tmp', '.qce_cache')`
- 손상 캐시 복구: `json.JSONDecodeError`/`KeyError` → 삭제 → 모달 다이얼로그 → 빈 초기 상태

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | `.qce_cache` → `json.loads()` 정상 복원 |
| AC-2 | 역직렬화 객체에 원본 메시지 문자열 포함 → Fail |
| AC-3 | `import pickle` 존재 → Fail |
| AC-4 | 쓰기 중 강제 종료 → 재시작 시 모달 다이얼로그 + 초기 화면 |
| AC-5 | 정상 쓰기 후 `.qce_cache.tmp` 미잔존 |

---

## NFR-2.4 — 원본 파일 없이 캐시만으로 대시보드 로드

### 구현 기준
- 앱 시작 시 `.qce_cache` 존재 → 원본 파일 존재 여부 검사 않고 즉시 역직렬화
- 상태바: `"캐시 파일에서 이전 분석 결과를 불러왔습니다. (분석 일시: YYYY-MM-DD HH:MM)"`

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | 원본 파일 모두 삭제 후 재시작 → 이전 결과 정상 표시 |
| AC-2 | 상태바에 `"캐시 파일에서 이전 분석 결과를 불러왔습니다."` 표시 |

---

## NFR-3.1 — 파일 인코딩 자동 감지 및 방어적 예외 처리

### 구현 기준
- 인코딩 시도 순서: UTF-8 → CP949
- 두 번 모두 실패: `{"error": "encoding_failed", "path": path}` 반환, 앱 계속 실행

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | UTF-8 파일 → 1회 시도 정상 파싱 |
| AC-2 | CP949 파일 → UTF-8 실패 후 CP949 재시도 성공, 한글 무결 |
| AC-3 | Shift-JIS 파일 → 앱 미종료, `error` 키 딕셔너리 반환 |

---

## NFR-3.2 — 메신저 모듈 결합도 완화 검증 (격리 테스트)

### 구현 기준
- `messenger_parser`, `git_parser`, `ooxml_parser` 독립 모듈 분리
- 상위 오케스트레이터(`analyzer.py`)가 결과 통합
- 공통 인터페이스: `Dict[str, int]`

### 수용 기준

| # | 기준 |
|---|---|
| AC-1 | `messenger_parser.py` 삭제 → `git_parser`/`ooxml_parser` 단위 테스트 `ImportError` 없이 통과 |
| AC-2 | `messenger_parser` Mocking `RuntimeError` → Git/OOXML 결과 정상 포함 |
| AC-3 | 위 통합 테스트 `pytest` 종료 코드 `0` |
