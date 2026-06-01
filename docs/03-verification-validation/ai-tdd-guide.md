# AI TDD 계속 진행 지침서
## QCE — 부탁해 꼬마선장

> **이 문서는 AI 에이전트(Claude Code 등)에게 직접 줄 수 있는 지침서입니다.**
> 작업 시작 시 이 파일을 AI에게 보여주고, 아래 섹션 중 해당 담당자 파트를 수행하도록 지시하세요.

---

## 0. 현재 상태 (2026-05-29 기준)

```bash
pytest tests/unit tests/static -q
# → 78 passed in 1.74s   ← 전부 GREEN
```

**완료된 STAGE:** 0(정적 게이트) · 1(타입·수학) · 2(파싱 인프라) · 3(소스 파서 5종)

**미구현 스텁:** `qce/model/business/anomaly_signal_detector.py`, `contribution_aggregator.py`, `cache_manager.py`, `report_exporter.py`, `qce/controller/`, `qce/view/` 전체

---

## 1. 프로젝트 구조 필독

```
qce/
  model/
    types.py                      ← CommitStats, MessengerRecord, ParseResult, MemberScore
    parsing/   document_parser.py  git_analyzer.py  git_health_checker.py
               messenger_parser.py stopword_filter.py encoding_handler.py
    business/  normalizer.py  capping_scaler.py  weight_preset_manager.py
               weight_rebalancer.py  alias_mapper.py
               [미구현] anomaly_signal_detector.py  contribution_aggregator.py
                        cache_manager.py  report_exporter.py
  controller/  [미구현] app_controller.py  analysis_orchestrator.py
  view/        [미구현] main_window.py  dialogs.py  charts/  panels.py  banner.py

tests/
  conftest.py              ← 픽스처: tmp_docx, git_repo, katalk, _no_network(autouse)
  fixtures/factories.py    ← 팩토리: make_docx/pptx/hwpx, make_git_repo, make_katalk, sample_scores
  static/                  ← STAGE 0 정적 게이트 (항상 GREEN 유지)
  unit/                    ← L1 단위 테스트
  integration/             ← L2 통합 테스트 (미작성)
  ui/                      ← L3 UI 테스트 (미작성)
```

---

## 2. TDD 루프 — AI가 따라야 할 절차

```
각 STAGE / 각 클래스마다:

  1. test-cases.md에서 해당 FR/NFR 케이스를 읽는다.
  2. tests/ 아래 테스트 파일을 작성한다 → pytest 실행 → ImportError/FAILED 확인(RED).
  3. qce/ 아래 최소 구현을 작성한다.
  4. pytest tests/unit -k <대상> -x -q 실행 → GREEN 확인.
  5. pytest tests/static -q 실행 → 정적 게이트 여전히 GREEN 확인.
  6. GREEN이면 다음 클래스로.
```

**불변 규칙:**
- `tests/static/` 9개 테스트는 **항상 GREEN**이어야 한다. 구현 중에 RED가 되면 해당 변경을 즉시 되돌린다.
- `qce/model/` 파일에 `PyQt6`, `PySide6`, `requests`, `urllib`, `httpx`, `socket`, `pickle`, `konlpy`, `jpype` import 금지.
- `qce/view/` 파일에서 `qce.model.*` 직접 import 금지 (Signal/Callback만 허용).
- `qce/model/parsing/` 3개 파서(git_analyzer, document_parser, messenger_parser)는 서로 import 금지.

---

## 3. 테스트 실행 명령어

```bash
# 작업 디렉토리: 프로젝트 루트 (pytest.ini 위치)
cd <프로젝트 루트>

# 정적 게이트 (항상 먼저)
pytest tests/static -q

# 단위 테스트 전체
pytest tests/unit -q

# 통합 테스트 (STAGE 8)
pytest tests/integration -q

# UI 테스트 (headless)
set QT_QPA_PLATFORM=offscreen
pytest tests/ui -q

# 특정 케이스 디버그
pytest tests/unit/model/business/test_normalizer.py -k zero_variance -x -v

# 커버리지 (STAGE 8 이후)
pytest tests/unit tests/integration --cov=qce/model --cov=qce/controller --cov-report=term-missing
```

---

## 4. 참조 문서 경로

| 문서 | 경로 |
|---|---|
| 테스트 계획 | `docs/03-verification-validation/test-plan.md` |
| 테스트 케이스 | `docs/03-verification-validation/test-cases.md` |
| 요구사항 | `docs/00-requirements/00-Requirement-records.md` |
| 아키텍처 | `docs/01-architecture/architecture-overview.md` |
| 진행 로그 | `test-log.md` (루트) |

---

## 5. STAGE 4~5 — 분석 통합 + 저장·내보내기 (담당: 김휘중)

### 전제 조건

```bash
pytest tests/unit tests/static -q   # 78 passed — 이 상태에서 시작
```

### STAGE 4: AnomalySignalDetector + ContributionAggregator

#### 5-1. AnomalySignalDetector (FR-4.2b, FR-4.2d)

**계약 (`qce/model/business/anomaly_signal_detector.py`):**
```python
class AnomalySignalDetector:
    def detect_frequency(self, repo: dict[str, CommitStats]) -> list[dict]:
        """작성자 단기 커밋 빈도가 평소 일평균의 3배 초과 구간을 신호로.
           각 항목: {author, period, period_commits, baseline_avg}."""

    def detect_zscore(self, scores: list[MemberScore]) -> list[str]:
        """정규화 지표 Z-Score ≤ -1.5 가 2개 이상인 팀원명 리스트. (FR-4.2d)"""
```

**테스트 파일 생성 위치:** `tests/unit/model/business/test_anomaly_signal_detector.py`

**핵심 케이스 (test-cases.md §FR-4.2b, §FR-4.2d):**

```python
# TC-FR-4.2b-01: 평소 일 1커밋, 특정일 4커밋(>3배) → 신호 1건
# TC-FR-4.2b-02: 신호 항목에 author·기간·해당기간커밋수·평소평균 포함
# TC-FR-4.2b-03: 균일 빈도 → 신호 0건 (오탐 방지)
# TC-FR-4.2d-01: Z ≤ -1.5 지표 2개 이상인 팀원 → 신호에 포함
# TC-FR-4.2d-02: Z ≤ -1.5 지표 1개뿐 → 신호 아님

def test_zscore_two_low_axes():   # TC-FR-4.2d-01
    from tests.fixtures.factories import sample_scores
    scores = sample_scores(4)      # D팀원이 전 지표 하위
    flagged = AnomalySignalDetector().detect_zscore(scores)
    assert "D팀원" in flagged
```

**구현 힌트:**
- `detect_zscore`: `MemberScore`의 `git_score`, `doc_score`, `msg_score` 3개 축에 대해 Z-Score 계산. Z ≤ -1.5인 축이 2개 이상이면 해당 팀원 포함.
- Z-Score = (x - mean) / std. std = 0이면 해당 축 skip.

#### 5-2. ContributionAggregator (FR-4.* 통합)

**계약 (`qce/model/business/contribution_aggregator.py`):**
```python
class ContributionAggregator:
    def aggregate(
        self,
        git: dict[str, CommitStats] | None,
        docs: dict[str, int] | None,
        msgs: dict[str, int] | None,
        weights: dict[str, float],   # {"git": 0.4, "doc": 0.4, "msg": 0.2}
    ) -> list[MemberScore]:
        """각 소스 정규화 → 가중 합산 → MemberScore 리스트.
           결측 소스(None)는 WeightRebalancer로 가중치 0 처리.
           CappingScaler로 git additions 상한 적용."""
```

**테스트 파일 생성 위치:** `tests/unit/model/business/test_contribution_aggregator.py`

**핵심 케이스:**
```python
# TC-NFR-1.3-01: 동일 입력·가중치 2회 aggregate → 두 결과 완전 일치 (결정론)
# TC-FR-4.3-05: 단일 소스만 가용 → total == 해당 소스 정규화 점수
# TC-NFR-3.2: 격리 테스트 — git=None으로 호출해도 doc·msg 결과 반영됨
```

**구현 순서:**
1. 각 소스의 author 집합을 union → 전체 팀원 목록
2. git: `CommitStats.additions`에 `CappingScaler.cap()` 적용 후 `log_scale()`
3. 각 소스별 점수 벡터 → `Normalizer.normalize()`
4. `WeightRebalancer.rebalance()`로 결측 소스 처리
5. 가중 합산 → `MemberScore` 생성

---

### STAGE 5: CacheManager + ReportExporter

#### 5-3. CacheManager (NFR-2.3, NFR-2.4)

**계약 (`qce/model/business/cache_manager.py`):**
```python
class CacheManager:
    CACHE_FILE = ".qce_cache"
    TMP_FILE   = ".qce_cache.tmp"

    def save(self, data: dict) -> None:
        """tmp 쓰기 → fsync → os.replace (원자 쓰기). json만 사용."""

    def load(self) -> dict:
        """JSONDecodeError/KeyError → 파일 삭제 + 빈 dict 반환."""
```

**테스트 파일:** `tests/unit/model/business/test_cache_manager.py`

**핵심 케이스 (test-cases.md §NFR-2.3):**
```python
# TC-NFR-2.3-01: save 후 load → 정상 복원
# TC-NFR-2.3-02: 메시지 본문 저장 시도 → 캐시에 본문 미포함 (화이트리스트 저장만)
# TC-NFR-2.3-04: 손상 캐시 load → 파일 삭제 + 빈 dict, 예외 없음
# TC-NFR-2.3-05: save 직후 → .qce_cache.tmp 잔존 없음

def test_atomic_no_tmp_left(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    CacheManager().save({"scores": {"A": 0.3}, "ts": "2026-01-01T00:00"})
    assert not os.path.exists(".qce_cache.tmp")
    assert os.path.exists(".qce_cache")

def test_corrupt_cache_recovers(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    open(".qce_cache", "w").write("{not json")
    out = CacheManager().load()
    assert out == {} and not os.path.exists(".qce_cache")
```

**주의:** `CacheManager`는 `open(..., 'w')` 사용이 허용된 화이트리스트 파일입니다 (`tests/static/test_readonly_input.py`의 `WRITE_OK`에 등록됨).

#### 5-4. ReportExporter (FR-5.2, FR-5.3)

**계약 (`qce/model/business/report_exporter.py`):**
```python
class ReportExporter:
    def to_markdown(self, scores: list[MemberScore], missing: set[str]) -> str:
        """마크다운 테이블 + 결측 소스 blockquote 경고."""

    def to_csv(self, scores: list[MemberScore], missing: set[str]) -> bytes:
        """UTF-8 BOM(\xef\xbb\xbf)으로 시작. Excel 한글 호환."""
```

**테스트 파일:** `tests/unit/model/business/test_report_exporter.py`

**핵심 케이스 (test-cases.md §FR-5.2, §FR-5.3):**
```python
# TC-FR-5.2-01: .md 출력 → 마크다운 테이블 구조 정상
# TC-FR-5.2-02: .csv → b"\xef\xbb\xbf" 로 시작 (BOM)
# TC-FR-5.2-03: 한글 author CSV → 디코딩 무손상
# TC-FR-5.2-04: 헤더에 "최종 평가" 금지, "종합 지표" 포함
# TC-FR-5.3-02: md(missing={"메신저"}) → blockquote 경고 문구 포함
# TC-FR-5.3-03: csv(missing={"메신저"}) → "WARNING" 행 포함
# TC-FR-5.3-05: missing=∅ → 경고 미포함

def test_csv_has_bom():
    data = ReportExporter().to_csv(sample_scores(2), missing=set())
    assert data[:3] == b"\xef\xbb\xbf"

def test_no_verdict_wording():
    md = ReportExporter().to_markdown(sample_scores(2), missing=set())
    assert "최종 평가" not in md and ("종합 지표" in md or "종합" in md)
```

**경고 문구 형식 (FR-5.3):**
```
⚠ [데이터 소스명] 데이터의 형식 불일치 또는 부재로 인해 해당 지표가 평가에서 제외되었습니다.
```
`[데이터 소스명]` ∈ {Git, 문서, 메신저}

---

## 6. STAGE 6~7 — 컨트롤러 + 뷰 (담당: 이대한)

### 전제 조건

```bash
pytest tests/unit tests/static -q   # STAGE 5까지 모두 GREEN인 상태에서 시작
```

### STAGE 6: AnalysisOrchestrator + AppController

#### 6-1. AnalysisOrchestrator (NFR-1.1, NFR-1.2)

**계약 (`qce/controller/analysis_orchestrator.py`):**
```python
from PyQt6.QtCore import QObject, pyqtSignal

class AnalysisOrchestrator(QObject):
    progress  = pyqtSignal(int)   # 0~100
    completed = pyqtSignal(list)  # list[MemberScore]
    failed    = pyqtSignal(str)   # 오류 메시지

    is_analyzing: bool = False

    def start_analysis(self, config: dict) -> None:
        """is_analyzing True면 즉시 return. 아니면 True 잠금 후 Worker 기동."""

    def _on_worker_finished(self) -> None:
        """성공·오류·취소 무관 is_analyzing=False + 버튼 재활성 Signal."""
```

**테스트 파일:** `tests/integration/test_orchestrator.py`

**핵심 케이스 (test-cases.md §NFR-1.2):**
```python
# TC-NFR-1.2-02: start 5회 연속 호출 → Worker 1개만 기동
def test_guard_blocks_duplicates(qtbot, monkeypatch):
    orch = AnalysisOrchestrator()
    started = []
    monkeypatch.setattr(orch, "_spawn_worker", lambda cfg: started.append(1))
    for _ in range(5):
        orch.start_analysis({"dummy": True})
    assert sum(started) == 1 and orch.is_analyzing is True

# TC-NFR-1.2-04: Worker RuntimeError → is_analyzing=False 복원
def test_state_restored_on_error(qtbot):
    orch = AnalysisOrchestrator()
    orch.is_analyzing = True
    orch._on_worker_finished()
    assert orch.is_analyzing is False
```

**주의:** 이 테스트는 `pytest-qt`가 필요합니다. `pip install pytest-qt` 후 진행.

#### 6-2. AppController

라우팅 역할. `GitHealthChecker.is_available()`을 확인하여:
- False → `GitMissingDialog` 표시
- True → 정상 흐름

**테스트:** `tests/integration/test_orchestrator.py`에 함께 작성 가능.

---

### STAGE 7: View — 다이얼로그 + 차트 3종

**주의:** View 테스트는 `pytest-qt`(qtbot) 필요. headless CI에서 `QT_QPA_PLATFORM=offscreen` 환경변수 설정 필요.

```bash
pip install pytest-qt
set QT_QPA_PLATFORM=offscreen   # CI/headless 환경
pytest tests/ui -q
```

#### 7-1. GitMissingDialog (FR-2.2 UI)

**테스트 파일:** `tests/ui/test_git_missing_dialog.py`

```python
# TC-FR-2.2-06: 모달 텍스트에 "Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다." 포함
# TC-FR-2.2-07: 다운로드 버튼 클릭 → webbrowser.open("https://git-scm.com/download/win")
# TC-FR-2.2-09: [확인] 클릭 → 앱 계속, Git 기능 비활성

def test_dialog_opens_link(qtbot, monkeypatch):
    calls = []
    import webbrowser
    monkeypatch.setattr(webbrowser, "open", lambda u: calls.append(u))
    dlg = GitMissingDialog()
    qtbot.addWidget(dlg)
    dlg.download_button.click()
    assert calls == ["https://git-scm.com/download/win"]
```

#### 7-2. AnalysisPanel (FR-4.4 UI)

**테스트 파일:** `tests/ui/test_analysis_panel.py`

```python
# TC-FR-4.4-06: "개발 중심" 버튼 클릭 → 슬라이더 0.60/0.25/0.15 반영
# TC-FR-4.4-07: 합 1.5 설정 → [분석 시작] disabled + 경고 문구
# TC-FR-4.4-08: 합 1.0 → [분석 시작] enabled
# TC-FR-4.4-09: 슬라이더 step 0.05
```

#### 7-3. 차트 3종 (FR-5.1a/b/c) + 차트 수락 테스트 12개 (FR-5.1d)

**테스트 파일:** `tests/ui/test_bar_chart.py`, `tests/ui/test_radar_chart.py`, `tests/ui/test_scatter_chart.py`, `tests/ui/test_chart_acceptance.py`

차트 위젯은 반드시 다음 **테스트 가능 접근자**를 노출해야 합니다:
```python
# BarChartWidget
widget.average_line_y() -> float
widget.bar_height(author: str) -> float
widget.animation_done -> bool

# RadarChartWidget
widget.vertex_labels() -> list[str]      # ["Git", "문서", "메신저"]

# ScatterChartWidget
widget.dot_color_saturation(author: str) -> float
widget.crosshair_xy() -> tuple[float, float] # (x_avg, y_avg)
widget.simulate_point_click(index: int) -> None
widget.member_selected: pyqtSignal(str)  # 클릭 시 발행
```

**FR-5.1d 12개 필수 케이스 (G4 게이트):**

```python
# tests/ui/test_chart_acceptance.py
# 1. test_bar_tooltip_items         — 막대 hover 툴팁 6항목
# 2. test_bar_average_line          — Y == 산술평균 ±0.0001
# 3. test_bar_animation_final_height — 애니 완료 후 높이 == total_score ±0.001
# 4. test_radar_vertex_labels        — "Git"/"문서"/"메신저"
# 5. test_radar_toggle_hide          — 범례 토글 후 visible=False
# 6. test_radar_missing_data         — "(제외됨)" 레이블
# 7. test_scatter_dynamic_axes        — 데이터 개수에 따른 축/텍스트 표시
# 8. test_scatter_dot_color_saturation — 3개 소스일 때 색상 채도 범위 검증
# 9. test_scatter_signal_emission     — 클릭 시 Signal 발행 (QSignalSpy)
# 10. test_scatter_label_overlap      — 라벨 최소거리 ≥30px
# 11. test_scatter_dynamic_crosshair  — X/Y == 동적 축 평균 ±0.0001
# 12. test_scatter_placeholder_text   — 1개 소스일 때 안내 텍스트 유무 검증
```

---

## 7. STAGE 8 — 통합 테스트 (전체)

**전제 조건:** STAGE 7까지 모두 GREEN.

### 필수 테스트 파일 생성

| 파일 | 검증 |
|---|---|
| `tests/integration/test_module_isolation.py` | NFR-3.2: 파서 1개 RuntimeError 시 나머지 결과 유지 |
| `tests/integration/test_pipeline_missing_source.py` | FR-4.3 E2E: 소스 결측 시 재조정 후 분석 성공 |

**핵심 케이스:**
```python
# TC-NFR-3.2-03: git 파서가 RuntimeError → 문서·메신저 결과는 MemberScore에 반영
def test_isolation_one_module_fails(monkeypatch):
    monkeypatch.setattr(GitAnalyzer, "analyze",
        lambda self, p: (_ for _ in ()).throw(RuntimeError("git down")))
    result = ContributionAggregator().aggregate(
        git=None, docs={"A": 100}, msgs={"A": 5},
        weights={"git": 0.4, "doc": 0.4, "msg": 0.2})
    assert any(m.author == "A" for m in result)
```

### 커버리지 목표
```bash
pytest tests/unit tests/integration --cov=qce/model --cov=qce/controller --cov-report=term-missing
# Model 95% / Controller 90% 달성 확인
```

### 전체 합격 기준 (G1~G8)

| # | 기준 | 확인 명령 |
|---|---|---|
| G1 | L0 정적 게이트 ALL GREEN | `pytest tests/static` |
| G2 | L1 단위 ALL GREEN | `pytest tests/unit` |
| G3 | L2 통합 ALL GREEN | `pytest tests/integration` |
| G4 | 차트 12케이스 ALL GREEN | `pytest tests/ui/test_chart_acceptance.py` |
| G5 | Model+Controller 커버리지 ≥90% | `pytest --cov=qce/model --cov=qce/controller` |
| G6 | 결정론: 동일 입력 2회 결과 동일 | NFR-1.3 테스트 |
| G7 | 수동 시나리오 A/B/C PASS | `docs/03-verification-validation/test-cases.md` 부록 A |
| G8 | RTM 미커버 FR/NFR 0건 | test-plan §10 추적표 |

---

## 8. PyInstaller 빌드

**전제 조건:** STAGE 8 G1~G6 모두 GREEN.

```bash
# 의존성 최종 확인
pip install pyinstaller>=6.3.0

# 빌드 (QCE.spec 이미 존재함)
pyinstaller QCE.spec

# 또는 spec 없이 직접
pyinstaller --name QCE --onefile --windowed main.py \
  --add-data "qce;qce"

# 산출물 위치
dist/QCE.exe
```

**주의사항:**
- `kiwipiepy` 모델 파일이 번들에 포함되어야 합니다. `QCE.spec`의 `datas`에 경로 추가 필요.
- `QT_QPA_PLATFORM` 환경변수가 `exe`에서는 불필요 (Windows native).
- 빌드 후 `dist/QCE.exe`를 실제 실행하여 수동 시나리오 A 체크리스트(test-cases.md 부록 A) 수행.

---

## 9. 주요 트러블슈팅 (이전 작업에서 발생)

| 증상 | 원인 | 해결 |
|---|---|---|
| `cp949` 디코딩이 Shift-JIS 바이트를 예외 없이 통과 | Shift-JIS 바이트 일부가 CP949 유효 시퀀스와 겹침 | `charset-normalizer`로 `cp932` 감지 시 사전 거부 |
| `make_docx(author=None)` → 파서가 `"python-docx"` 반환 | python-docx의 기본 author 값 | 팩토리에서 `author=""` 명시 설정 |
| 정적 게이트: `View가 Model을 직접 import` | View에서 `from qce.model...` 실수 | View는 Controller의 Signal만 구독, Model 직접 참조 금지 |
| `ZeroDivisionError` in Normalizer | max==min 분기 누락 | `if hi == lo: return [0.5]*len(values)` |
| 가중치 합 ≠ 1.0 | 재정규화 분모 오류 | `w_i / sum(가용 소스 가중치)` |

---

## 10. 빠른 시작 체크리스트 (새 담당자용)

```
□ 1. 프로젝트 클론 및 의존성 설치
      pip install -r requirements.txt
      pip install pytest-qt   # STAGE 6 이후 필요

□ 2. 현재 상태 확인
      pytest tests/unit tests/static -q
      → 78 passed 확인

□ 3. 기준 문서 읽기
      docs/03-verification-validation/test-cases.md (해당 STAGE 섹션)

□ 4. 테스트 파일 먼저 작성 (RED)
      pytest tests/unit/model/business/test_<대상>.py -q
      → ImportError/FAILED 확인

□ 5. 최소 구현 작성 (GREEN)
      pytest tests/unit/model/business/test_<대상>.py -q
      → Passed 확인

□ 6. 정적 게이트 재확인
      pytest tests/static -q
      → 9 passed 확인

□ 7. 전체 누적 실행
      pytest tests/unit tests/static -q
      → 모두 passed 확인

□ 8. test-log.md 업데이트 (완료된 STAGE 기록)
```
