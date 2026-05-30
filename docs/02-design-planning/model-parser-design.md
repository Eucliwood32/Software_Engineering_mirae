# Model Parsing 설계 (Model Parsing Layer Design)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.0 |
| 작성일 | 2026-05-30 |
| 상위 문서 | Architecture Overview v1.1, Requirements Record v1.3, Development Constraints v2.0 |
| 관련 Spec | `backend/specs/01-ooxml-pipeline.md`, `02-git-pipeline.md`, `03-messenger-pipeline.md` |
| 관련 ADR | ADR-0003 (kiwipiepy > KoNLPy, NLP 엔진 선정) |
| 작성 주체 | QCE 개발팀 (조원희) |

---

## 1. 개요

### 1.1 목적
본 문서는 QCE 시스템의 **Model · Parsing 레이어**에 속하는 6개 컴포넌트의 상세 설계를 기술한다. 각 컴포넌트의 책임, 인터페이스 시그니처, 핵심 알고리즘, 예외·방어 처리 전략, 그리고 해당 컴포넌트가 실현하는 요구사항과 구속받는 제약사항을 명시한다.

파서 레이어는 이질적 외부 입력(OOXML/HWPX 문서, 로컬 Git 저장소, 카카오톡 `.txt`)을 **순수 데이터 구조로 변환**하는 시스템의 최외곽 경계이다. 입력의 손상·오염·인코딩 불일치가 빈번히 발생하는 영역이므로, 본 레이어의 설계 핵심은 **예외를 상위로 전파하지 않는 방어적 파싱**(NFR-3.1, NFR-3.2)이다.

### 1.2 범위
Architecture Overview §5.2에서 정의된 레이어 경계 시그니처 위에서, 내부 알고리즘과 필드 단위 상세를 다룬다. 정규화·집계·이상 신호 등 BusinessLogic 레이어는 `model-business-logic-design.md`에서, Worker Thread 오케스트레이션은 `controller-design.md`에서 다룬다.

본 문서가 다루는 6개 컴포넌트(Architecture Overview §4.2):

| 컴포넌트 | 추적 FR/NFR | 입력 | 출력 |
| :--- | :--- | :--- | :--- |
| DocumentParser | FR-1.1, FR-1.2 | `.docx`/`.pptx`/`.hwpx` 경로 | `dict[str, int]` |
| GitAnalyzer | FR-2.1 | 로컬 저장소 경로 | `dict[str, CommitStats]` |
| GitHealthChecker | FR-2.2 | (없음) | `bool` |
| MessengerParser | FR-3.1, FR-3.2 | 카카오톡 `.txt` 경로 | `ParseResult` |
| StopwordFilter | FR-3.3 | `list[MessengerRecord]` | `dict[str, int]` |
| EncodingHandler | NFR-3.1 | 텍스트 파일 경로 | `str \| dict[str, str]` |

### 1.3 설계 불변식
- **PyQt6 import 금지.** Parsing 레이어의 어떤 모듈도 `PyQt6` 심볼을 import하지 않는다. 이로써 파서는 UI 프레임워크와 독립적으로 pytest 단위 테스트가 가능하다 (Architecture Overview §3.2, NFR-3.2 검증 전제, 정적 게이트 `tests/static/test_mvc_layering.py`).
- **파서 상호 import 금지.** 3개 입력 파서(Document/Git/Messenger)는 서로를 직접 import하지 않는다. 모든 통합은 Controller의 `AnalysisOrchestrator`가 수행한다 (NFR-3.2, C-4). 따라서 임의의 1~2개 소스만 가용한 상황에서도 나머지 파서가 ImportError 없이 동작한다.
- **예외 비전파 (방어적 파싱).** 손상 파일·잘못된 경로·인코딩 실패·외부 명령 실패는 예외를 상위로 던지지 않고, **빈 결과 또는 에러 마커 dict**로 흡수한다. 파서 한 개의 실패가 전체 분석 프로세스를 중단시키지 않는다 (NFR-3.2, FR-1.1·FR-2.1·FR-3.2 수용기준).
- **읽기 전용 입력 접근.** 모든 입력 파일은 `'r'`/`'rb'` 모드로만 열린다. 분석 대상 경로에 쓰기·이동·삭제를 수행하지 않는다 (NFR-2.1, C-3, 정적 게이트 `tests/static/test_readonly_input.py`).
- **결정론 보장.** 동일 입력에 대해 동일 파싱 결과(특히 FR-3.3 불용어 분류)가 산출된다 (NFR-1.3).
- **네트워크 부재.** 파서는 `requests`/`urllib`/`socket` 등 네트워크 I/O를 import하지 않는다. Git 데이터는 로컬 `git` CLI(subprocess)로만 수집한다 (NFR-2.2, C-1·C-2, 정적 게이트 `tests/static/test_forbidden_imports.py`).

### 1.4 참조 데이터 타입
본 레이어는 Architecture Overview §5.1에 정의된 공용 데이터 타입을 사용한다.

```python
from dataclasses import dataclass

@dataclass
class CommitStats:                      # FR-2.1 — GitAnalyzer 출력 단위
    commits: int
    additions: int
    deletions: int

@dataclass
class MessengerRecord:                  # FR-3.1 — 단일 발화 레코드
    author: str
    timestamp: str
    message: str

@dataclass
class ParseResult:                      # FR-3.2 — MessengerParser 출력
    records: list[MessengerRecord]
    skipped_lines: int
```

### 1.5 설계 결정 요약
본 문서 작성에 앞서 확정된 6개 설계 결정사항을 기록한다. 추적성과 향후 정합성 감사를 위함이다.

| # | 결정 항목 | 확정 내용 | 근거 |
| :--- | :--- | :--- | :--- |
| D-1 | 카카오톡 발화 정규식 정본 | **Spec 포맷 `r"^(.+?)\s:\s(.+)$"`** (`작성자 : 메시지`)를 정본으로 채택한다. | 헌법 규칙 1(Spec 우선), `specs/03` §FR-3.1, 정식 경로 구현과 일치 (§9) |
| D-2 | 슬랙(Slack) CSV 파서 | **범위에서 제외**한다. `specs/03`의 슬랙 관련 기술을 삭제하고 카카오톡 단일 형식으로 축소한다. | RR v1.3 변경이력(4) "슬랙 파싱 삭제", 사용자 결정 |
| D-3 | 정식 코드베이스 경로 | **`src/models/parsers/`를 정식(운영) 경로**로 확정한다. (생성 시점이 `qce/model/parsing/`보다 앞섬 — §9 참조) | 사용자 결정(선 생성 경로 우선), 실제 앱 실행 경로(`main.py`) |
| D-4 | HWPX(OWPML) 지원 | Spec 명시 사항으로 **정식 채택**한다. | RR v1.3 FR-1.1·FR-1.2·ASM-3, 변경이력(3) ".hwpx 지원 추가" |
| D-5 | 불용어 사전 선정 근거 | 별도 근거 문서는 부재하며, **FR-3.3 수용기준 3개 카테고리에 직접 매핑**되는 규칙으로 기술한다. | 사용자 확인(근거 문서 없음), RR FR-3.3 수용기준 |
| D-6 | 문서 버전·참조 | v1.0, 상위 문서 = Arch v1.1 / RR v1.3 / dev-constraints v2.0, 관련 Spec = specs/01~03, 관련 ADR = ADR-0003. | 형제 설계 문서 관례 |

---

## 2. DocumentParser (FR-1.1, FR-1.2)

- **책임:** `.docx`/`.pptx`/`.hwpx` 파일을 열어 본문 텍스트에서 **공백·개행·탭을 제외한 유효 글자수**를 추출하고, 문서 메타데이터의 작성자 식별자를 기준으로 집계한다. 확장자에 따라 형식별 추출기(Strategy)로 위임하는 **파사드**이다.
- **시그니처 (레이어 경계 계약, Architecture Overview §5.2):**
  ```python
  class DocumentParser:                   # FR-1.1, FR-1.2
      def parse(self, path: str) -> dict[str, int]:
          """확장자에 따라 OOXML/HWPX 추출기로 위임. 반환 {작성자: 유효 글자수}."""
      def count_shapes(self, path: str) -> int:
          """문서 내 텍스트 도형 개수(.pptx 한정, 그 외 0)."""
  ```
- **형식별 작성자 메타데이터:**

  | 형식 | 작성자 소스 | 유효 글자수 소스 |
  | :--- | :--- | :--- |
  | `.docx` | `core_properties.author` | 전 단락(`paragraphs`) 텍스트 |
  | `.pptx` | `core_properties.last_modified_by` | 전 슬라이드 도형의 `text_frame` 텍스트 |
  | `.hwpx` | 메타 스키마의 `dc:creator` | `Contents/section*.xml`의 `<…:t>` 텍스트 노드 |

- **알고리즘:**
  1. 경로 확장자를 소문자로 식별하여 `_parse_docx` / `_parse_pptx` / `_parse_hwpx`로 분기한다. 미지원 확장자는 빈 dict(`{}`)를 반환한다.
  2. 형식별 추출기로 본문 텍스트를 모은 뒤, 정규식 `\s`(공백·탭·개행 전체)를 제거하고 잔여 문자 길이를 누적한다 (`len(re.sub(r"\s", "", text))`).
  3. 작성자 메타데이터를 읽되, 값이 비어 있으면(`""`/`None`) **`"Unknown"`** 분류로 묶는다 (FR-1.2).
  4. **HWPX 처리 (D-4):** HWPX는 OWPML 기반 ZIP 아카이브이므로 `zipfile`로 열어, 메타 후보 엔트리에서 `dc:creator`(네임스페이스 무관 로컬 태그 `creator`)를 탐색하고, 본문은 `section*.xml`의 텍스트 노드(`t` 태그)를 순회하여 유효 글자수를 누적한다.
  5. 반환 형태: `{"작성자": 총_유효_글자수}`.
- **예외·방어 처리:**
  - 손상 파일·압축 해제 실패·XML 파싱 오류는 추출기 내부에서 흡수하고, 파사드 차원에서 `try/except`로 감싸 **빈 결과를 반환**한다 (FR-1.1 "손상 파일 skip + 분석 계속", ASM-3).
  - 빈 파일 → 글자수 0, 도형수 0, 예외 없음 (FR-1.1 수용기준).
  - `python-docx`/`python-pptx` 미설치 환경에서도 import 단계에서 죽지 않도록, 라이브러리 import는 추출기 내부(지연 import)에서 수행한다.
- **추적:** FR-1.1(유효 글자수·도형수 추출), FR-1.2(작성자별 집계·Unknown 분류), ASM-3(손상 파일 가정). 제약 C-5(Python 스택), C-6(번들). Spec `01-ooxml-pipeline.md` AC-1~AC-3.

---

## 3. GitAnalyzer (FR-2.1)

- **책임:** 로컬 Git 저장소에서 `git log --numstat`을 subprocess로 실행하여 stdout을 파싱하고, **작성자 이메일별 커밋 수·추가 라인·삭제 라인**을 집계한다.
- **시그니처:**
  ```python
  class GitAnalyzer:                      # FR-2.1
      GIT_TIMEOUT: int = 30
      def analyze(self, repo_path: str) -> dict[str, CommitStats]:
          """잘못된 경로·실패 시 빈 dict 반환(예외 비전파)."""
  ```
- **수집 명령:** `git log --numstat --format=%H|%ae|%ai`
  - `%H` 커밋 해시 · `%ae` 작성자 이메일 · `%ai` ISO 8601 타임스탬프.
  - `--numstat`은 커밋별 파일 단위 `추가\t삭제\t경로` 라인을 출력한다.
  - **정식 경로(`src/`)에는 `--no-merges`가 없어 병합 커밋이 집계에 포함된다.** `qce/`에는 적용되어 있으나 현재 정식 경로와 불일치 상태이다 (OI-P7, 추가 권장).
- **알고리즘 (스트리밍 라인 파싱):**
  1. `subprocess.run(..., timeout=30, check=True)`로 명령을 실행한다. Windows에서는 콘솔 창 노출을 막기 위해 `CREATE_NO_WINDOW` 플래그를 적용하고, `stdin`은 `DEVNULL`로 차단한다.
  2. stdout을 줄 단위로 순회하며 상태 기계로 파싱한다.
     - **헤더 라인** (`해시|이메일|타임스탬프`, `|` 분할 시 3필드): 현재 작성자(`current_email`)를 갱신하고 해당 작성자의 커밋 수를 +1 한다.
     - **numstat 라인** (선두가 숫자): 탭 분할하여 추가/삭제를 정수 파싱한다. 바이너리 파일의 `-` 표기는 `0`으로 환산한다. 현재 작성자의 누계(그리고 커밋별 내역)에 가산한다.
  3. 반환 형태: `{"author@email.com": CommitStats(commits, additions, deletions)}`.
- **이상 신호용 확장 (정식 경로):** AnomalySignalDetector(FR-4.2b 빈도 신호)가 **커밋별 일자·변경량 시계열**을 필요로 하므로, 정식 경로 구현은 작성자별 집계에 더해 **커밋 상세 리스트**(`{hash, date, additions, deletions}`)를 함께 반환하는 확장 구조를 채택한다. 집계 합계는 상세 리스트로부터 결정론적으로 재현된다. (§9 인터페이스 정합 참조)
- **예외·방어 처리:**
  - `CalledProcessError`(비-저장소 경로 등), `FileNotFoundError`(`git` 미설치), `TimeoutExpired`(30초 초과), `OSError`는 모두 흡수하여 **빈 dict(`{}`)를 반환**한다 (FR-2.1 "잘못된 경로 → 빈 결과, 예외 없음").
  - 타임아웃 30초는 10,000커밋 저장소를 30초 이내 수집해야 한다는 성능 수용기준(FR-2.1 AC-3)과 정렬된다.
- **추적:** FR-2.1. 제약 C-9(Git CLI 의존성 대응), C-5. Spec `02-git-pipeline.md` AC-1~AC-3.

---

## 4. GitHealthChecker (FR-2.2)

- **책임:** 메인 윈도우 표시 **전**에 `git` 실행 파일의 설치·PATH 등록 여부를 점검한다. Git 부재 시 앱은 계속 실행하되 Git 기능만 비활성화하도록, Controller에 가용성 여부(`bool`)만 보고한다.
- **시그니처:**
  ```python
  class GitHealthChecker:                 # FR-2.2
      def is_available(self) -> bool:
          """git --version (timeout 5s). 메인 윈도우 표시 전 1회 호출."""
  ```
- **알고리즘:**
  1. `subprocess.run(["git", "--version"], capture_output=True, timeout=5)`를 실행한다.
  2. `returncode == 0`이면 `True`(가용), 아니면 `False`.
  3. `FileNotFoundError`(미설치)·`TimeoutExpired`·`OSError`는 흡수하여 `False`를 반환한다.
- **UI 연동 (View/Controller 책임):** `is_available()`이 `False`이면 `GitMissingDialog`가 표시되며, 모달에는 안내 문구 `"Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다."`, 다운로드 링크 `https://git-scm.com/download/win`(클릭 시 `webbrowser.open()`로 OS 브라우저 위임), PATH 설정 안내가 포함된다 (FR-2.2 수용기준). 외부 링크는 OS 위임만 하며 파서가 직접 네트워크 송신을 하지 않는다 (NFR-2.2).
- **추적:** FR-2.2, ASM-1(Git PATH 사전 미상). 제약 C-9. Spec `02-git-pipeline.md` FR-2.2 AC-1~AC-3.

---

## 5. MessengerParser (FR-3.1, FR-3.2)

- **책임:** 카카오톡 `.txt` 내보내기 파일을 발화자·시각·메시지 구조로 정규화한다. 파싱에 실패한 줄은 예외로 중단하지 않고 **건너뛰며 카운트**한다(방어적 파싱).
- **시그니처:**
  ```python
  class MessengerParser:                  # FR-3.1, FR-3.2
      def parse(self, path: str) -> ParseResult:
          """카카오톡 .txt 파싱. 오염 줄 skip + 카운트. 인코딩은 EncodingHandler 경유."""
  ```
- **정규식 정본 (D-1):**

  | 용도 | 패턴 | 비고 |
  | :--- | :--- | :--- |
  | 날짜 구분줄 | `r"^\d{4}년 \d{1,2}월 \d{1,2}일"` | 매칭 시 record 아님 → 정상 무시(skip 카운트 아님) |
  | 발화 분리 | `r"^(.+?)\s:\s(.+)$"` | group(1)=작성자, group(2)=메시지 (`작성자 : 메시지`) |

  > **D-1 정합.** 발화 정규식은 Spec(`specs/03` §FR-3.1) 및 정식 경로(`src/models/parsers/messenger_parser.py`)와 동일한 `작성자 : 메시지` 포맷을 정본으로 한다. 시각(`timestamp`)은 본 포맷에서 별도 캡처되지 않으므로 `MessengerRecord.timestamp`는 빈 문자열로 채워진다.

- **알고리즘:**
  1. `EncodingHandler.read_text(path)`로 파일 전체를 디코드한다(UTF-8 → CP949 순, NFR-3.1). 인코딩 실패 시 에러 마커 dict가 반환되며, 이 경우 빈 `ParseResult`로 귀결시킨다.
  2. 줄 단위 순회:
     - 공백 줄 → 무시.
     - 날짜 구분줄 정규식 매칭 → 무시(레코드도 skip 카운트도 아님).
     - 발화 정규식 매칭 → `MessengerRecord(author, timestamp="", message)`를 records에 추가.
     - 어느 패턴에도 불일치 → `skipped_lines += 1` 후 계속 진행 (FR-3.2).
  3. 반환 형태: `ParseResult(records=[...], skipped_lines=N)`.
- **예외·방어 처리:**
  - 정상 10 + 오염 3 → records 10, skipped 3. 전체 100줄 오염 → records 0, skipped 100, 예외 없음 (FR-3.2 수용기준).
  - 어떤 입력에서도 프로세스가 종료되지 않는다.
- **하위 처리:** records는 `StopwordFilter.count_valid_messages()`로 전달되어 유효 메시지 수로 집계된다(§6). MessengerParser 자체는 불용어 판정을 수행하지 않는다(책임 분리).
- **추적:** FR-3.1(카카오톡 파싱), FR-3.2(오염 줄 방어적 skip). 제약 C-5. 의존 EncodingHandler(NFR-3.1). Spec `03-messenger-pipeline.md` AC-1~AC-2.

---

## 6. StopwordFilter (FR-3.3)

- **책임:** 의미가 희박한 표현을 **자동으로 식별하여** 유효 메시지 집계에서 제외하고, 작성자별 유효 메시지 수를 반환한다. 사용자(조장)는 불용어 사전을 편집할 수 없으며(편집 UI·API 미제공), 동일 입력에 대해 동일 분류가 보장된다(결정론).
- **시그니처:**
  ```python
  class StopwordFilter:                   # FR-3.3
      def count_valid_messages(self, records: list[MessengerRecord]) -> dict[str, int]:
          """자동 불용어 제외 후 {작성자: 유효 메시지 수}. 사용자 편집 미제공·결정론."""
  ```
- **불용어 분류 규칙 (D-5 — FR-3.3 수용기준 3개 카테고리 직접 매핑):**

  | 카테고리 (FR-3.3) | 판정 방식 | 정의 |
  | :--- | :--- | :--- |
  | 단순 리액션 | 정규식 `r"^[ㄱ-ㅎㅏ-ㅣ]+$"` | 자음·모음만으로 구성된 문자열 전체(`ㅇㅇ`, `ㅋㅋ`, `ㅎㅎ`, `ㄱㄱ`, `ㄴㄴ`, `ㄷㄷ`, `ㅠㅠ` 등) |
  | 미디어 태그 | 정규식 `r"^\([^)]+\)$"` | 괄호로 감싼 단일 태그(`(이모티콘)`, `(사진)`, `(동영상)`, `(파일)`) |
  | 1글자 단순 응답 | 고정 집합(`frozenset`) 정확 일치 | 격식·비격식 긍정 및 간투사의 표준형·변이형 (`네`/`넵`/`넹`/`넴`, `예`/`옙`, `응`/`웅`/`엉`, `어`, `음`, `오`, `굳`/`굿`) |

  > **D-5 설계 노트.** 불용어 사전(`_ONE_WORD_STOPWORDS`)과 정규식 패턴의 선정에 대한 외부 근거 문서는 존재하지 않는다. 본 규칙은 FR-3.3 수용기준에 열거된 세 카테고리를 충족하기 위한 **하드코딩 상수**로 설계되며, 사용자 편집 불가 원칙(FR-3.3) 및 결정론(NFR-1.3)을 구조적으로 강제하기 위해 `frozenset`(불변)으로 고정한다. 변이형은 표준형의 구어 변형을 보수적으로 포함한 것이며, 향후 확장 시 본 표를 SSOT로 삼는다.

- **알고리즘:**
  1. 각 레코드의 메시지를 `strip()` 한다. 빈 문자열은 불용어로 간주.
  2. 미디어 태그 정규식 → 리액션 정규식 → 1글자 응답 집합 순으로 판정하여, 하나라도 매칭되면 제외한다.
  3. 불용어가 아닌 메시지만 작성자별로 카운트하여 `{작성자: 유효 메시지 수}`를 반환한다.
- **결정론·NLP 정책 (ADR-0003 관련):** 현재 구현은 형태소 분석기 없이 **규칙 기반(정규식 + 집합)** 으로 동작한다. 이는 JRE 의존을 배제(C-7)하면서 결정론과 경량성을 확보하기 위한 선택이며, ADR-0003(kiwipiepy > KoNLPy)이 상정한 형태소 분석 기반 확장은 본 컴포넌트의 향후 확장점으로 남는다. 어떤 경우에도 사용자에게 불용어 편집 UI를 제공하지 않는다.
- **추적:** FR-3.3. 제약 C-7(JRE 의존 배제), NFR-1.3(결정론). 관련 ADR-0003.

---

## 7. EncodingHandler (NFR-3.1)

- **책임:** 텍스트 파일을 열 때 인코딩을 자동 감지하여 디코드한다. `UTF-8 → CP949` 순으로 시도하고, 둘 다 실패하거나 비지원 인코딩으로 판정되면 **앱을 중단하지 않고** 에러 정보를 결과에 담아 반환한다.
- **시그니처:**
  ```python
  class EncodingHandler:                  # NFR-3.1
      def read_text(self, path: str) -> str | dict[str, str]:
          """UTF-8 → CP949 순. 둘 다 실패 시 {"error": "encoding_failed", "path": path}."""
  ```
- **알고리즘:**
  1. 파일을 바이너리(`'rb'`)로 읽는다(읽기 전용, NFR-2.1).
  2. `charset-normalizer`로 인코딩 계열을 사전 판정하여, 한국어가 아닌 비지원 계열(일본어 `shift_jis`/`euc_jp` 등, 중국어 `gbk`/`gb18030` 등, 서유럽 `windows1252` 등)로 식별되면 즉시 `{"error": "encoding_failed", "path": path}`를 반환한다. — CP949 디코드가 비한국어 바이트열을 **오탐(mojibake)** 으로 통과시키는 것을 방지하기 위한 방어선이다.
  3. `utf-8` → `cp949` 순으로 strict 디코드를 시도하여 성공한 문자열을 반환한다.
  4. 모두 실패하면 에러 마커 dict를 반환한다.
- **예외·방어 처리:** `UnicodeDecodeError`·`LookupError`는 다음 인코딩으로 폴백한다. `charset-normalizer` 미가용 등 사전 판정 실패는 무시하고 표준 폴백 루프로 진행한다. 미지원 인코딩 → 종료 없이 `error` 키 포함 결과 반환 (NFR-3.1 수용기준).
- **소비 주체:** MessengerParser가 본 핸들러를 경유하여 카카오톡 `.txt`를 디코드한다(§5). 반환이 `dict`(에러)이면 호출자는 빈 결과로 귀결시켜 방어한다.
- **추적:** NFR-3.1. 제약 C-5. 정적 게이트 `tests/static/test_no_jre_dep.py`(JRE 비의존), `test_readonly_input.py`(읽기 전용).

---

## 8. 컴포넌트 간 의존 관계 및 데이터 흐름

```
[외부 입력]                 [Parsing 레이어]                          [BusinessLogic 입력]

.docx/.pptx/.hwpx ───────→  DocumentParser ─────────────────────→  docs: {작성자: 글자수}

로컬 Git 저장소 ──────────→  GitAnalyzer ────────────────────────→  git:  {이메일: CommitStats}
(앱 시작 전 1회)  ────────→  GitHealthChecker → bool (UI 게이트)

카카오톡 .txt ───→ EncodingHandler ──(str)──→ MessengerParser ──→ StopwordFilter ──→ msgs: {작성자: 유효수}
                  (UTF-8→CP949)                (records, skipped)   (불용어 제외)
```

- **단방향 의존.** Parsing 레이어 내부 의존은 `MessengerParser → EncodingHandler`, `MessengerParser`의 출력 → `StopwordFilter` 단 두 갈래뿐이며, 3개 입력 파서(Document/Git/Messenger)는 서로를 import하지 않는다(§1.3 불변식).
- **통합은 Controller가 수행.** 위 3개 출력(`docs`/`git`/`msgs`)을 모아 BusinessLogic 레이어(`AliasMapper` → `ContributionAggregator`)로 주입하는 것은 Controller의 `AnalysisOrchestrator` 책임이다. 파서는 BusinessLogic·Controller·View를 일절 import하지 않는다 (NFR-3.2, C-4).
- **격리 보장.** 임의의 1개 파서가 빈 결과/에러를 반환해도, 나머지 파서의 출력만으로 `WeightRebalancer`(FR-4.3)가 가중치를 재정규화하여 분석이 완결된다.

---

## 9. 구현 경로 매핑 및 정합성 (D-3)

> **본 절은 코드 경로 결정(D-3)에 종속되며, §2~7의 설계 본문(아키텍처 §5.2 계약)과 독립적이다.** 정식 경로 판단이 번복되어도 §2~7은 유효하다.

### 9.1 정식 경로 판정
파서 레이어는 동일 역할의 구현이 **두 경로에 중복 존재**한다. 두 디렉터리 모두 단일 커밋(`dbfefdd`, "Add TDD scaffold")에 함께 등장하므로 커밋 순서로는 구분되지 않으나, 작업 트리 파일 생성 시각(mtime)이 결정적이다.

| 경로 | 생성 시각(mtime) | 성격 |
| :--- | :--- | :--- |
| `src/models/parsers/` | 2026-05-28 17:57–18:19 (**선행**) | **정식(운영) 경로** — `main.py → worker_thread.py` 실행 경로 |
| `qce/model/parsing/` | 2026-05-29 01:23–01:42 | 테스트 경로 — `tests/unit/model/parsing/` pytest 대상 |

D-3에 따라 **`src/models/parsers/`를 정식 경로**로 확정한다(선 생성 + 실제 앱 실행 경로).

### 9.2 컴포넌트 ↔ 파일 매핑

| 설계 컴포넌트 | 정식 경로 (`src/models/parsers/`) | 테스트 경로 (`qce/model/parsing/`) |
| :--- | :--- | :--- |
| DocumentParser | `ooxml_parser.py` (함수 `parse_ooxml_file`) | `document_parser.py` (클래스) |
| GitAnalyzer | `git_parser.py` (함수 `parse_git_log`) | `git_analyzer.py` (클래스) |
| GitHealthChecker | *(미존재)* | `git_health_checker.py` (클래스) |
| MessengerParser | `messenger_parser.py` (함수 `parse_messenger_file`) | `messenger_parser.py` (클래스) |
| StopwordFilter | *(미존재)* | `stopword_filter.py` (클래스) |
| EncodingHandler | *(messenger_parser.py에 인라인)* | `encoding_handler.py` (클래스) |

### 9.3 정합성 격차 (Open Issues)
정식 경로(`src/`)와 아키텍처 §5.2/테스트 경로(`qce/`) 사이의 구조적 격차를 기록한다. 헌법 규칙 1(Spec/아키텍처 우선)에 따라, 최종적으로 **아키텍처 §5.2의 6-컴포넌트 클래스 구조로 수렴**시키는 것이 정합 방향이다.

| ID | 격차 | 정식 경로 현황 | 수렴 방향 |
| :--- | :--- | :--- | :--- |
| OI-P1 | 함수형 vs 클래스형 | `src/`는 모듈 수준 함수(`parse_*`) | 아키텍처 §5.2 클래스 인터페이스로 래핑 |
| OI-P2 | 반환 타입 | `src/`는 plain dict 반환 | `CommitStats`/`ParseResult`/`MessengerRecord` 데이터클래스(§1.4)로 정렬 |
| OI-P3 | 컴포넌트 누락 | `src/`에 `GitHealthChecker`·`StopwordFilter` 부재 | `qce/` 구현을 정식 경로로 이관 |
| OI-P4 | EncodingHandler 분리 | `src/`는 인코딩 처리를 messenger 파서에 인라인(UTF-8/CP949 2단 루프, charset-normalizer 사전판정 없음) | 독립 `EncodingHandler`로 추출(NFR-3.1) |
| OI-P5 | 카카오톡 정규식 불일치 | `src/`·Spec = `작성자 : 메시지`(정본, D-1) / `qce/`는 `[작성자] [오전·오후 H:MM]` 브래킷 포맷 사용 | `qce/`를 D-1 정본 포맷으로 정정 |
| OI-P6 | 손상 docx/pptx 반환값 | `src/`는 손상 시 `{"Unknown": 0}` 반환 / 아키텍처는 빈 dict(`{}`) | FR-1.1 "skip" 의미와 일치하도록 `{}`로 통일 검토 |
| OI-P7 | `--no-merges` 플래그 | `src/git_parser.py`에는 없음 / `qce/git_analyzer.py`에만 존재 | 병합 커밋 중복 집계 방지를 위해 `src/`에도 추가 권장 (FR-2.1 정확도 영향) |

> **테스트 커버리지 주의.** 현재 pytest 단위 테스트(`tests/unit/model/parsing/`)는 **테스트 경로(`qce/`)를 대상**으로 한다. 정식 경로를 `src/`로 확정(D-3)함에 따라, 위 OI 수렴 작업 시 테스트의 import 대상도 함께 이관되어야 한다. 그 전까지 운영 경로(`src/`)는 단위 테스트로 직접 검증되지 않는 상태임에 유의한다.

---

## 10. 파서 레이어 추적성 매트릭스

| 컴포넌트 | 실현 FR/NFR | 구속 제약 | 검증 (pytest / 정적 게이트) |
| :--- | :--- | :--- | :--- |
| DocumentParser | FR-1.1, FR-1.2 | C-5, C-6 | `test_document_parser.py` / Spec 01 AC-1~3 |
| GitAnalyzer | FR-2.1 | C-9, C-5 | `test_git_analyzer.py` / Spec 02 AC-1~3 |
| GitHealthChecker | FR-2.2 | C-9 | `test_git_health_checker.py` |
| MessengerParser | FR-3.1, FR-3.2 | C-5 | `test_messenger_parser.py` / Spec 03 AC-1~2 |
| StopwordFilter | FR-3.3 | C-7, NFR-1.3 | `test_stopword_filter.py` |
| EncodingHandler | NFR-3.1 | C-5 | `test_encoding_handler.py` |
| 전 레이어 | NFR-3.2(모듈 격리), NFR-2.1(읽기 전용), NFR-2.2(네트워크 0) | C-1, C-2, C-3, C-4 | `tests/static/test_mvc_layering.py`, `test_forbidden_imports.py`, `test_readonly_input.py`, `test_no_jre_dep.py` |

> **정적 불변식 검증 포인트.** import 그래프에서 (1) Parsing → View/Controller 의존 0건, (2) Parsing 레이어 PyQt6 import 0건, (3) 네트워크 I/O·`pickle` import 0건이어야 한다(C-4, NFR-2.2, NFR-3.2 Fail 조건).

---

## 11. 문서 변경 이력

| 버전 | 일자 | 변경 | 작성자 |
| :--- | :--- | :--- | :--- |
| v1.0 | 2026-05-30 | 최초 작성. 6개 Parsing 컴포넌트(DocumentParser·GitAnalyzer·GitHealthChecker·MessengerParser·StopwordFilter·EncodingHandler) 상세 설계. 설계 결정 6건(D-1~D-6) 확정 기록: 카카오톡 정규식 Spec 정본화, 슬랙 제외(`specs/03` 정리), 정식 경로 `src/models/parsers/` 확정, HWPX Spec 채택, 불용어 규칙 FR-3.3 매핑, 참조 목록 확정. 구현 경로 정합성 격차(OI-P1~P6) 및 파서 레이어 RTM 포함. | QCE 개발팀 (조원희) |
