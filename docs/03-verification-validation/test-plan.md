# Test Plan
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.0 |
| 작성일 | 2026-05-29 |
| 준수 표준 | ISO/IEC/IEEE 29148-2018, ISO/IEC/IEEE 29119 (테스트 프로세스) |
| 상위 문서 | Requirements Record v1.3, Architecture Overview v1.0, Development Constraints v2.0, ConOps v1.2 |
| 하위 문서 | `test-cases.md` (개별 케이스 정의) |
| 작성 주체 | QCE 개발팀 |
| 대상 독자 | **사람 개발자 + 자율 구현 에이전트(AI)** |

---

## 0. 이 문서의 사용법 (AI 에이전트 우선)

본 계획서는 사람이 읽는 동시에, **AI가 스스로 "기능 구현 → 테스트 실행 → 실패 분석 → 수정"을 반복**할 수 있도록 설계되었다. AI 에이전트는 다음 루프를 따른다.

```
LOOP (각 요구사항 ID 단위):
  1. test-cases.md 에서 대상 FR/NFR의 TC를 읽는다.
  2. §6 빌드 순서(DAG)에 따라 의존성이 모두 GREEN인지 확인한다.
  3. 해당 TC를 pytest 테스트 코드로 옮긴다(아직 구현 없음 → RED).
  4. 최소 구현을 작성한다.
  5. `pytest tests/ -k <대상> -x -q` 실행.
  6. RED면: 실패 메시지 → 원인 분류(§9 트러블슈팅 표) → 수정 → 5로.
     GREEN이면: §7 정적 게이트가 깨지지 않았는지 `pytest tests/static -q` 확인.
  7. 다음 ID로.
GLOBAL DONE 조건: §8 전체 합격 기준 충족.
```

> **불변 규칙.** 어떤 구현도 §7 정적 게이트(금지 import, MVC 단방향, read-only)를 깨면 그 변경은 무효다. 기능 테스트가 통과해도 정적 게이트가 RED면 전체 RED로 간주한다.

---

## 1. 문서 개요

### 1.1 목적
QCE의 모든 기능 요구사항(FR)·비기능 요구사항(NFR)·제약(C)이 **Pass/Fail로 판정 가능한 테스트**로 환원됨을 보증하고, 그 실행 방법·환경·순서·합격 기준을 정의한다.

### 1.2 범위
- **포함:** 단위 테스트(Model), 통합 테스트(Controller·파이프라인), UI 테스트(View, pytest-qt), 정적 분석 게이트(제약 검증), 수동 시스템 테스트(E2E 시나리오).
- **제외:** 평가 기준의 교육학적 타당성, 성적 산정 공식의 정당성(Problem Statement §5 범위 외).

### 1.3 기준 문서 정합성 결정 (Source of Truth)
프롬프트 SRS v2.0과 docs/ 최신본 사이의 차이는 다음과 같이 해소한다. **모든 TC는 아래 결정을 따른다.**

| 쟁점 | SRS v2.0(프롬프트) | 최신 docs | **본 계획의 채택** |
| :--- | :--- | :--- | :--- |
| 메신저 소스 | 카톡 + 슬랙 | 카톡 단독 (RR v1.3, ConOps v1.2) | **카카오톡 단독.** 슬랙 CSV 테스트 미작성 |
| 차트 종류 | 막대 + 레이더 (2종) | 막대 + 레이더 + 산점도 (3종, FR-5.1a/b/c) | **3종.** 산점도·12개 pytest 케이스 포함 |
| 불용어 처리 | (명시 없음) | FR-3.3 자동 분류, 사용자 편집 불가 | **자동 StopwordFilter 포함** |
| 문서 파서 | OoxmlParser | DocumentParser 파사드(.pptx/.docx/.hwpx) | **DocumentParser(.hwpx 포함)** |
| Z-Score 신호 ID | 없음 | RR 본문은 `FR-4.2c`, RTM·ConOps·arch는 `FR-4.2d` | **`FR-4.2d`로 통일**(RR 본문 헤더는 오타로 간주) |
| EW-02 빈도 신호 | 없음 | FR-4.2b | **포함** |

> 위 표 자체가 회귀 방지 체크리스트다. 구현이 슬랙 파싱·2종 차트로 회귀하면 RR v1.3 위반이다.

---

## 2. 테스트 전략

### 2.1 핵심 원칙
1. **Model-First.** Model 레이어는 PyQt6 심볼을 import하지 않으므로(architecture §3.2 불변식) UI 없이 순수 pytest로 빠르게 검증 가능하다. 따라서 **Model → Controller → View 순으로** 빌드·검증한다.
2. **결정론 우선(NFR-1.3).** 동일 입력은 동일 출력을 내야 한다. 모든 수치 테스트는 고정 시드·고정 픽스처로 작성하며, 부동소수 비교는 명시된 허용오차(`±0.0001`, `±0.001`)로 한다.
3. **격리 검증(NFR-3.2).** 파서 3종은 서로 import하지 않는다. 한 모듈을 제거/Mock해도 나머지가 동작함을 별도 테스트로 강제한다.
4. **제약은 코드로 검증.** "import 금지", "MVC 단방향", "read-only" 같은 제약은 주관적 리뷰가 아니라 **AST·import 그래프 파싱 테스트**로 자동 판정한다(§7).

### 2.2 테스트 피라미드 (작성 비중)

```
        ▲  L4 수동 E2E (시나리오 A/B/C) ........ 소수, 체크리스트
       ███ L3 UI (pytest-qt) ................... 차트 12 + 다이얼로그
      █████ L2 통합 (Orchestrator·파이프라인) ... 중간
    █████████ L1 단위 (Model) ................... 다수, 가장 빠름
   ███████████ L0 정적 게이트 (제약) ............ 항상 실행, 게이트
```

### 2.3 테스트 레벨 정의

| 레벨 | 대상 | 도구 | 의존성 | 실행 빈도 |
| :--- | :--- | :--- | :--- | :--- |
| **L0 정적** | C-2/C-4/C-7/C-8, NFR-2.1/2.2/3.2 | `ast`, import 그래프 | 없음 | 매 커밋 |
| **L1 단위** | Model 13개 컴포넌트 | pytest | 픽스처 팩토리 | 매 변경 |
| **L2 통합** | AnalysisOrchestrator, 결측 파이프라인, 모듈 격리 | pytest + Mock/QSignalSpy | L1 GREEN | 매 변경 |
| **L3 UI** | 다이얼로그 5종, 차트 3종(12 케이스), 배너, 비동기 | pytest-qt | L2 GREEN | 차트/UI 변경 시 |
| **L4 수동** | E2E 시나리오 A/B/C | 사람(체크리스트) | L3 GREEN | 릴리스 전 |

---

## 3. 테스트 환경

### 3.1 런타임·플랫폼
- OS: **Windows 10/11 x64** (C-5). 단, Model/정적 레벨(L0~L2 비-UI)은 CI 편의상 Linux에서도 통과해야 한다(다중 OS 분기문은 작성하지 않되, 테스트는 OS 비의존이도록 `tmp_path`·`os.path.join` 사용).
- Python **3.10+** (C-5). `match`문·`X | Y` 타입 힌트 사용 허용.

### 3.2 의존 패키지

| 패키지 | 용도 | 비고 |
| :--- | :--- | :--- |
| `pytest` | 테스트 러너 | 필수 |
| `pytest-qt` | PyQt6 위젯·Signal 테스트 (`qtbot`, `QSignalSpy`) | L3 |
| `pytest-cov` | 커버리지 측정 | §8 게이트 |
| `python-docx`, `python-pptx` | 문서 픽스처 생성 + 파싱 | FR-1 |
| `kiwipiepy` (또는 `soynlp`) | 형태소 분석 | C-7 (JRE 금지). KoNLPy 금지 |
| (Git CLI 2.x) | Git 픽스처 생성 | `subprocess`로 임시 repo 생성 |

> **C-7 검증:** `konlpy`, `jpype1`이 `pyproject.toml`/`requirements.txt`·소스 어디에도 없어야 한다(§7 정적 테스트로 강제).

### 3.3 디렉토리 구조 (권장)

```
qce/                              # 구현 소스 (src 레이아웃)
  model/
    parsing/   document_parser.py git_analyzer.py git_health_checker.py
               messenger_parser.py stopword_filter.py encoding_handler.py
    business/  normalizer.py capping_scaler.py anomaly_signal_detector.py
               weight_preset_manager.py weight_rebalancer.py alias_mapper.py
               contribution_aggregator.py cache_manager.py report_exporter.py
    types.py   # CommitStats, MessengerRecord, ParseResult, MemberScore
  controller/  app_controller.py analysis_orchestrator.py
  view/        main_window.py dialogs.py charts/ panels.py banner.py
  main.py
tests/
  conftest.py
  fixtures/        factories.py
  unit/model/parsing/  test_*.py
  unit/model/business/ test_*.py
  integration/     test_orchestrator.py test_module_isolation.py
                   test_pipeline_missing_source.py
  ui/              test_*_dialog.py test_bar_chart.py test_radar_chart.py
                   test_scatter_chart.py test_chart_acceptance.py
                   test_warning_banner.py test_async_progress.py
  static/          test_forbidden_imports.py test_mvc_layering.py
                   test_readonly_input.py test_no_jre_dep.py
  system/          manual_checklist.md
```

### 3.4 실행 명령어 (표준)

```bash
# 전체 (정적 게이트 포함)
pytest tests/ -q

# 레벨별
pytest tests/static  -q          # L0 — 항상 먼저, 게이트
pytest tests/unit    -q          # L1
pytest tests/integration -q      # L2
pytest tests/ui      -q          # L3 (pytest-qt; headless 시 QT_QPA_PLATFORM=offscreen)
pytest tests/unit/model/business/test_normalizer.py -k zero_variance -x  # 단건 디버그

# 커버리지
pytest tests/unit tests/integration --cov=qce/model --cov=qce/controller --cov-report=term-missing
```

> Headless(CI/서버) UI 테스트: 환경변수 `QT_QPA_PLATFORM=offscreen` 설정.

---

## 4. 테스트 픽스처 / 데이터 생성 전략

테스트 데이터는 **정적 파일을 저장소에 두지 않고, 팩토리 함수로 매 실행 생성**한다(재현성·이식성). 모든 팩토리는 `tests/fixtures/factories.py`에 둔다. 아래는 **구현해야 할 팩토리의 계약(시그니처 + 보장)**이다. AI는 이 계약을 먼저 구현해야 L1을 시작할 수 있다.

### 4.1 문서 팩토리 (FR-1)

```python
# tests/fixtures/factories.py
from docx import Document
from pptx import Presentation
from pptx.util import Inches

def make_docx(path, author: str | None, text: str) -> str:
    """author=None이면 core_properties.author를 비운다(Unknown 검증용).
       text는 단락 1개로 기록. 반환: path."""
    doc = Document()
    doc.add_paragraph(text)
    if author is not None:
        doc.core_properties.author = author
    doc.save(path); return path

def make_pptx(path, last_modified_by: str | None,
              slides: list[list[str]]) -> str:
    """slides = [[box1_text, box2_text, ...], ...]. 슬라이드당 텍스트박스 N개 생성.
       last_modified_by=None이면 메타 공란. 반환: path."""
    prs = Presentation()
    blank = prs.slide_layouts[6]
    for boxes in slides:
        slide = prs.slides.add_slide(blank)
        for i, t in enumerate(boxes):
            tb = slide.shapes.add_textbox(Inches(1), Inches(1 + i), Inches(4), Inches(1))
            tb.text_frame.text = t
    if last_modified_by is not None:
        prs.core_properties.last_modified_by = last_modified_by
    prs.save(path); return path

def make_hwpx(path, author: str | None, text: str) -> str:
    """최소 HWPX(zip) 생성. 표준 메타 스키마에 author 기록, 본문 text 1문단.
       반환: path. (HWPX = OWPML zip; mimetype + Contents/ + 메타 XML)"""
    # 구현: zipfile로 mimetype('application/hwp+zip'), version.xml,
    #       Contents/content.hpf, Contents/section0.xml, 메타(설정상 작성자) 작성.
    ...

def make_corrupted(path) -> str:
    """확장자만 .docx/.pptx/.hwpx, 내용은 무작위 바이트(zip 헤더 아님)."""
    with open(path, "wb") as f: f.write(b"\x00\x01NOT_A_ZIP\xff")
    return path

def make_empty_docx(path) -> str: ...   # 단락 0개
```

**팩토리 자체 검증(메타-테스트):** `make_docx(p, "Alice", "가"*200)` 로 만든 파일을 다시 열어 `core_properties.author == "Alice"` 인지 확인하는 테스트를 1개 둔다(픽스처 신뢰성 보장).

### 4.2 Git 저장소 팩토리 (FR-2)

```python
import subprocess, os
def make_git_repo(path, commits: list[dict]) -> str:
    """commits[i] = {"email": str, "date": "YYYY-MM-DD HH:MM:SS",
                     "add": int, "del": int}
       각 커밋마다 add줄 추가 / del줄 삭제를 정확히 발생시킨다.
       env GIT_AUTHOR_EMAIL/GIT_AUTHOR_DATE/GIT_COMMITTER_* 로 결정론 보장.
       잘못된 경로 테스트는 이 함수를 쓰지 않고 존재하지 않는 경로 문자열 전달."""
    subprocess.run(["git","init","-q",path], check=True)
    # 라인 수 정확 제어: 파일에 알려진 N줄 작성 후 일부 삭제하는 시퀀스로 구성
    ...
```

**정확한 +10/-5 보장 레시피:** 커밋①에서 15줄 파일 생성(`+15`)은 케이스에 맞지 않으므로, "+10/-5"가 필요하면 ①에서 충분히 큰 베이스를 만든 뒤 ②에서 10줄 추가·5줄 삭제하는 식으로 **검증 대상 커밋만** 측정값이 되도록 베이스 커밋은 별도 author/날짜로 분리한다. (TC-FR-2.1 참조)

### 4.3 카카오톡 txt 팩토리 (FR-3) — **입력 형식 계약**

KakaoTalk 실제 export 형식은 버전마다 다르므로, **본 프로젝트의 정식 입력 형식을 아래로 고정**한다. 파서·픽스처는 항상 이 형식에 합의한다.

```
2024년 1월 15일 월요일
[조원희] [오후 2:30] 안녕하세요 회의 시작합니다
[이대한] [오후 2:31] ㅇㅇ
[김휘중] [오후 2:32] (이모티콘)
```

- 날짜 구분줄: `^\d{4}년 \d{1,2}월 \d{1,2}일`
- 발화줄: `^\[(?P<author>.+?)\] \[(?P<ap>오전|오후) (?P<h>\d{1,2}):(?P<m>\d{2})\] (?P<msg>.*)$`
- 위 두 패턴에 모두 불일치하는 줄 = **오염 줄(skip 대상)**.

```python
def make_katalk(path, lines: list[tuple[str,str]] | list[str],
                encoding: str = "utf-8", header_date="2024년 1월 15일 월요일") -> str:
    """lines가 (author, msg) 튜플이면 정상 발화줄로 직렬화.
       lines가 str이면 그 줄을 그대로(오염줄 주입용) 기록.
       encoding="cp949" 로 CP949 파일 생성 가능."""
    ...
```

> 만약 실제 KakaoTalk 형식이 위와 다르면 **본 §4.3과 파서를 같은 PR에서 함께** 수정한다(픽스처-구현 동기). 둘 중 하나만 바꾸면 회귀다.

### 4.4 MemberScore 픽스처 (FR-5 차트용)

차트 테스트는 파이프라인 전체를 돌리지 않고 `MemberScore` 리스트를 직접 주입한다(View는 점수의 출처를 모름 — architecture §5.5).

```python
from qce.model.types import MemberScore
def sample_scores(n=4) -> list[MemberScore]:
    return [
        MemberScore("조원희",0.30,0.20,0.40,0.28,800,1500,120,False,[]),
        MemberScore("B팀원", 0.55,0.10,0.30,0.31,1000,400,90,True,["EW-01"]),
        MemberScore("C팀원", 0.40,0.45,0.20,0.29,600,2000,50,False,[]),
        MemberScore("D팀원", 0.05,0.08,0.05,0.12,50,200,10,False,["ZSCORE"]),
    ][:n]
```

---

## 5. conftest.py 핵심 픽스처

```python
import pytest, os
from tests.fixtures import factories

@pytest.fixture
def tmp_docx(tmp_path):
    return lambda author, text, name="d.docx": factories.make_docx(
        str(tmp_path / name), author, text)

@pytest.fixture
def git_repo(tmp_path):
    return lambda commits, name="repo": factories.make_git_repo(
        str(tmp_path / name), commits)

@pytest.fixture
def katalk(tmp_path):
    return lambda lines, enc="utf-8", name="chat.txt": factories.make_katalk(
        str(tmp_path / name), lines, enc)

@pytest.fixture
def qtbot_app(qtbot):          # pytest-qt 제공 qtbot 래핑
    return qtbot

@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """모든 테스트에서 실수로라도 네트워크가 열리면 즉시 실패(NFR-2.2 런타임 보강)."""
    import socket
    def deny(*a, **k): raise RuntimeError("Network access attempted (NFR-2.2 violation)")
    monkeypatch.setattr(socket.socket, "connect", deny)
```

---

## 6. 빌드·검증 순서 (의존성 DAG)

AI는 **위에서 아래로** 진행한다. 각 단계는 직전 단계가 모두 GREEN일 때만 시작한다. 괄호는 의존 컴포넌트.

```
STAGE 0  정적 게이트 골격 작성 (빈 패키지에 대해 통과하도록)
         └ tests/static/* — 소스가 비어도 통과해야 함(위반 0건이므로)

STAGE 1  순수 타입·수학 (의존 없음)
         ├ types.py (CommitStats/MessengerRecord/ParseResult/MemberScore)
         ├ Normalizer            (FR-4.1)
         ├ CappingScaler         (FR-4.2)
         ├ WeightPresetManager   (FR-4.4 로직)
         └ WeightRebalancer      (FR-4.3)

STAGE 2  파싱 인프라
         ├ EncodingHandler       (NFR-3.1)            ← 의존 없음
         └ AliasMapper           (FR-1.3 로직)         ← types

STAGE 3  소스 파서 (← EncodingHandler)
         ├ DocumentParser        (FR-1.1/1.2)         ← (자체)
         ├ GitAnalyzer           (FR-2.1)             ← subprocess
         ├ GitHealthChecker      (FR-2.2 로직)        ← subprocess
         ├ MessengerParser       (FR-3.1/3.2)         ← EncodingHandler
         └ StopwordFilter        (FR-3.3)             ← kiwipiepy

STAGE 4  분석 통합
         ├ AnomalySignalDetector (FR-4.2b/4.2d)       ← types
         └ ContributionAggregator(FR-4.* 통합)        ← Normalizer,CappingScaler,
                                                         WeightRebalancer,AliasMapper

STAGE 5  영속·출력
         ├ CacheManager          (NFR-2.3/2.4)        ← json
         └ ReportExporter        (FR-5.2/5.3)         ← MemberScore

STAGE 6  컨트롤러 (← 모든 Model)
         ├ AnalysisOrchestrator  (NFR-1.1/1.2/3.2)    ← pytest-qt
         └ AppController         (라우팅)

STAGE 7  뷰 (← MemberScore 형태만)
         ├ GitMissingDialog      (FR-2.2 UI)
         ├ AnalysisPanel         (FR-4.4 UI)
         ├ BarChartWidget        (FR-5.1a)
         ├ RadarChartWidget      (FR-5.1b)
         ├ ScatterChartWidget    (FR-5.1c)
         ├ WarningBanner         (FR-5.3 UI)
         └ [FR-5.1d] 차트 12 케이스 — 위 3 차트 GREEN 후 일괄 검증

STAGE 8  통합·시스템
         ├ test_module_isolation (NFR-3.2)
         ├ test_pipeline_missing_source (FR-4.3 E2E)
         └ manual_checklist (시나리오 A/B/C)
```

> **격리 불변식(NFR-3.2):** STAGE 3의 파서 3종은 서로 import 금지. STAGE 8의 격리 테스트가 이를 강제한다. STAGE 3 구현 중에도 `from qce.model.parsing.messenger_parser import` 가 git/document 파서에 등장하면 STAGE 8에서 즉시 RED.

---

## 7. 정적 게이트 (제약을 코드로 검증) — **항상 실행**

기능 통과 여부와 무관하게 아래 테스트가 RED면 전체 RED다. 모두 `tests/static/`에 둔다. 핵심 구현 스케치를 제공한다.

### 7.1 금지 import (C-2·C-8, NFR-2.2·NFR-2.3)

```python
# tests/static/test_forbidden_imports.py
import ast, pathlib
FORBIDDEN = {"requests","urllib","httpx","socket","http.client","pickle"}
SRC = pathlib.Path("qce")

def _imports(pyfile):
    tree = ast.parse(pyfile.read_text(encoding="utf-8"))
    for n in ast.walk(tree):
        if isinstance(n, ast.Import):
            for a in n.names: yield a.name.split(".")[0], a.name
        elif isinstance(n, ast.ImportFrom):
            mod = (n.module or "")
            yield mod.split(".")[0], mod

def test_no_forbidden_imports():
    bad = []
    for f in SRC.rglob("*.py"):
        for top, full in _imports(f):
            if top in FORBIDDEN or full in FORBIDDEN:
                bad.append((str(f), full))
    assert not bad, f"금지 import 발견(C-2/C-8): {bad}"
```

### 7.2 JRE/KoNLPy 의존 배제 (C-7)

```python
def test_no_jre_dependency():
    bad=[]
    for f in pathlib.Path("qce").rglob("*.py"):
        for _, full in _imports(f):
            if full.split(".")[0] in {"konlpy","jpype","jpype1"}:
                bad.append((str(f), full))
    assert not bad, f"JRE 의존 형태소 분석기 발견(C-7): {bad}"
# 추가: requirements.txt / pyproject.toml 에 konlpy·jpype1 부재 검증
```

### 7.3 MVC 단방향 — View→Model 직접 의존 0건 (C-4)

```python
# tests/static/test_mvc_layering.py
def test_view_does_not_import_model():
    offenders=[]
    for f in pathlib.Path("qce/view").rglob("*.py"):
        for top, full in _imports(f):
            if full.startswith("qce.model"):
                offenders.append((str(f), full))
    assert not offenders, f"View가 Model을 직접 import(C-4 위반): {offenders}"

def test_model_does_not_import_pyqt():
    offenders=[]
    for f in pathlib.Path("qce/model").rglob("*.py"):
        for top, _ in _imports(f):
            if top in {"PyQt6","PySide6"}:
                offenders.append(str(f))
    assert not offenders, f"Model이 UI 프레임워크 import(architecture 불변식 위반): {offenders}"
```

### 7.4 파서 상호 격리 (NFR-3.2 정적 부분)

```python
def test_parsers_do_not_cross_import():
    parsers = {"git_analyzer","document_parser","messenger_parser"}
    offenders=[]
    base = pathlib.Path("qce/model/parsing")
    for name in parsers:
        f = base / f"{name}.py"
        for _, full in _imports(f):
            others = parsers - {name}
            if any(o in full for o in others):
                offenders.append((name, full))
    assert not offenders, f"파서 상호 import(NFR-3.2 위반): {offenders}"
```

### 7.5 입력 read-only (NFR-2.1)

```python
# tests/static/test_readonly_input.py
# 분석 경로에 대한 쓰기 모드 open / shutil.move / os.remove 호출 정적 탐지.
# 휴리스틱: 파서·분석 모듈에서 open(..., 'w'|'a'|'x'|'wb'|'r+') 호출 시 Fail.
# (ReportExporter·CacheManager는 '쓰기 허용 화이트리스트'로 제외)
WRITE_MODES = {"w","a","x","w+","r+","wb","ab","xb"}
WRITE_OK = {"qce/model/business/report_exporter.py",
            "qce/model/business/cache_manager.py"}
```

> 런타임 보강: `NFR-2.1` 단위 테스트에서 분석 전후 `os.path.getmtime(원본)` 동일 검증(§test-cases TC-NFR-2.1).

---

## 8. 전체 합격 기준 (Definition of Done)

프로젝트 전체가 **DONE**으로 선언되려면 아래가 모두 충족되어야 한다.

| # | 기준 | 측정 방법 |
| :--- | :--- | :--- |
| G1 | 모든 L0 정적 게이트 GREEN | `pytest tests/static` 종료코드 0 |
| G2 | 모든 L1 단위 테스트 GREEN | `pytest tests/unit` 종료코드 0 |
| G3 | 모든 L2 통합 테스트 GREEN | `pytest tests/integration` 종료코드 0 |
| G4 | FR-5.1d의 **12개 차트 pytest 케이스 전부 통과** | `pytest tests/ui/test_chart_acceptance.py` |
| G5 | Model+Controller 라인 커버리지 ≥ **90%** | `pytest --cov=qce/model --cov=qce/controller` |
| G6 | 전체 파서/분석 결정론 | NFR-1.3 테스트 2회 실행 결과 동일 |
| G7 | 수동 시나리오 A/B/C 체크리스트 전 항목 PASS | `system/manual_checklist.md` |
| G8 | RR v1.3 ↔ TC 추적 100% (미커버 FR/NFR 0) | §10 추적 매트릭스 |

> 커버리지 목표는 레이어별로 차등한다: **Model 95% 권장 / Controller 90% / View(로직부) 70%**(렌더 코드는 시각 검증으로 보완).

---

## 9. 트러블슈팅 — 실패 분류 → 조치 (AI 자가수정용)

| 증상(테스트 출력) | 1차 원인 가설 | 표준 조치 |
| :--- | :--- | :--- |
| `ZeroDivisionError` in Normalizer | max==min 분기 누락 | `if max==min: return [0.5]*len(v)` (FR-4.1) |
| 가중치 합 ≠ 1.0 | 결측 재정규화 시 분모 오류 | `w_i/(1-sum(missing))` 후 `round(_,4)`; 합 `±0.0001` 재검 (FR-4.3) |
| capping 5000 → 5000 | 임계 비교 `>` vs `>=` 혼동 | `>1000`만 cap, 999/1000 경계 확인 (FR-4.2) |
| Git 결과 빈 dict 기대인데 예외 전파 | `CalledProcessError`/`FileNotFoundError` 미포획 | try/except로 `{}` 반환 (FR-2.1) |
| 한글 깨짐 | CP949 폴백 누락 | UTF-8→CP949 순, 둘 다 실패 시 error dict (NFR-3.1) |
| `QSignalSpy` 0 emit | Worker가 메인스레드서 Signal 미발행 | Signal 객체/connect 확인, `qtbot.waitSignal` 사용 (FR-5.1c/NFR-1.2) |
| 차트 높이 ≠ 점수 | 애니메이션 종료 전 측정 | `qtbot.waitUntil(lambda: widget.animation_done)` 후 측정 (FR-5.1a) |
| 정적 게이트 RED, 기능 GREEN | 금지 import/레이어 위반 | 해당 모듈에서 import 제거; 우회 불가 — 설계 수정 |
| 격리 테스트 RED | 파서 상호 import | 공통 타입을 `types.py`로 끌어올려 의존 제거 (NFR-3.2) |
| 캐시 손상 후 크래시 | load의 예외 미포획 | `JSONDecodeError/KeyError → remove + 빈상태` (NFR-2.3) |

---

## 10. 추적성 매트릭스 (FR/NFR → 테스트 산출물)

`test-cases.md`가 케이스를 정의하고, 본 표는 **요구사항이 어느 파일에서 검증되는지**를 매핑한다. **빈칸(미커버) = G8 위반.**

| FR/NFR | 테스트 파일 | 레벨 |
| :--- | :--- | :--- |
| FR-1.1 | unit/model/parsing/test_document_parser.py | L1 |
| FR-1.2 | unit/model/parsing/test_document_parser.py | L1 |
| FR-1.3 | unit/model/business/test_alias_mapper.py | L1 |
| FR-2.1 | unit/model/parsing/test_git_analyzer.py | L1 |
| FR-2.2 | unit/model/parsing/test_git_health_checker.py + ui/test_git_missing_dialog.py | L1+L3 |
| FR-3.1 | unit/model/parsing/test_messenger_parser.py | L1 |
| FR-3.2 | unit/model/parsing/test_messenger_parser.py | L1 |
| FR-3.3 | unit/model/parsing/test_stopword_filter.py | L1 |
| FR-4.1 | unit/model/business/test_normalizer.py | L1 |
| FR-4.2 | unit/model/business/test_capping_scaler.py | L1 |
| FR-4.2b | unit/model/business/test_anomaly_signal_detector.py | L1 |
| FR-4.2d | unit/model/business/test_anomaly_signal_detector.py + ui/test_scatter_chart.py | L1+L3 |
| FR-4.3 | unit/model/business/test_weight_rebalancer.py + integration/test_pipeline_missing_source.py | L1+L2 |
| FR-4.4 | unit/model/business/test_weight_preset_manager.py + ui/test_analysis_panel.py | L1+L3 |
| FR-5.1 | ui/test_*_chart.py (공통 규칙) | L3 |
| FR-5.1a | ui/test_bar_chart.py | L3 |
| FR-5.1b | ui/test_radar_chart.py | L3 |
| FR-5.1c | ui/test_scatter_chart.py | L3 |
| FR-5.1d | ui/test_chart_acceptance.py (12 케이스) | L3 |
| FR-5.2 | unit/model/business/test_report_exporter.py | L1 |
| FR-5.3 | unit/model/business/test_report_exporter.py + ui/test_warning_banner.py | L1+L3 |
| NFR-1.1 | ui/test_async_progress.py | L3 |
| NFR-1.2 | integration/test_orchestrator.py | L2 |
| NFR-1.3 | unit/model/business/test_contribution_aggregator.py (결정론) | L1 |
| NFR-2.1 | unit/.../test_*_parser.py(mtime) + static/test_readonly_input.py | L1+L0 |
| NFR-2.2 | static/test_forbidden_imports.py + conftest `_no_network` | L0 |
| NFR-2.3 | unit/model/business/test_cache_manager.py + static/test_forbidden_imports.py | L1+L0 |
| NFR-2.4 | unit/model/business/test_cache_manager.py | L1 |
| NFR-3.1 | unit/model/parsing/test_encoding_handler.py | L1 |
| NFR-3.2 | integration/test_module_isolation.py + static/test_mvc_layering.py | L2+L0 |
| C-1~C-9 | static/* (가능한 항목) + 빌드 단계 | L0 |

---

## 11. 위험·한계

- **HWPX 스키마 변동:** HWPX 메타/본문 스키마는 버전별 차이가 있다. 팩토리·파서가 같은 스키마 가정에 합의해야 하며, 실제 한글 파일과 차이 시 §4.1 팩토리와 파서를 동시 수정한다.
- **KakaoTalk 형식 변동:** §4.3에 형식을 고정했다. 실제 export와 다르면 회귀로 간주하고 동기 수정.
- **차트 렌더 검증 한계:** matplotlib 픽셀 단위 비교는 불안정하므로, **데이터 계약(축 레이블·평균선 Y값·점 크기 매핑·Signal 발행)** 을 검증하고 시각적 완성도는 L4 수동으로 보완한다.
- **pytest-qt headless:** CI에서 `QT_QPA_PLATFORM=offscreen` 필요. 일부 애니메이션 타이밍은 `qtbot.waitUntil`로 폴링.

---

## 12. 변경 이력

| 버전 | 일자 | 변경 | 작성자 |
| :--- | :--- | :--- | :--- |
| v1.0 | 2026-05-29 | 최초 작성. RR v1.3·architecture v1.0 기준. AI TDD 루프, 정적 게이트(C 제약 코드화), 빌드 DAG, 픽스처 팩토리 계약, 추적 매트릭스 포함. SRS v2.0과의 차이 §1.3에 해소. | QCE 개발팀 |