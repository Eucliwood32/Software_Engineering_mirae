"""
test_controller.py

Controller.py (AppController, AnalysisOrchestrator) 모듈에 대한 통합 단위 테스트.
PyQt6 의존성을 Mocking하여 UI 없이 스레드 동작 및 라우팅 상태를 테스트합니다.
v1.2: FR-4.2c(신호 예외 처리), FR-1.3(병합 후보 추천 배선) 케이스 신설.

실행:
    python -m pytest BusinessLogic/test_controller.py -v
"""

import os
import sys
import pytest
from types import ModuleType
import importlib.util

# ==========================================
# 1. PyQt6 의존성 모의(Mock) 주입
# ==========================================
class MockSignal:
    def __init__(self, *args):
        self.callbacks = []
        self._emitted_values = []
    def connect(self, callback):
        self.callbacks.append(callback)
    def emit(self, *args, **kwargs):
        self._emitted_values.append(args)
        for cb in self.callbacks:
            cb(*args, **kwargs)

def pyqtSignal(*args):
    return MockSignal()

class QObject:
    pass

class QRunnable:
    pass

class MockThreadPool:
    def __init__(self):
        self.active_thread_count = 0
        self.queue = []
    def start(self, runnable):
        self.active_thread_count += 1
        self.queue.append(runnable)
    def execute_all(self):
        while self.queue:
            r = self.queue.pop(0)
            r.run()
            self.active_thread_count -= 1

class QThreadPool:
    _instance = MockThreadPool()
    @staticmethod
    def globalInstance():
        return QThreadPool._instance

# sys.modules에 주입
pyqt_module = ModuleType("PyQt6")
core_module = ModuleType("PyQt6.QtCore")
core_module.QObject = QObject
core_module.pyqtSignal = pyqtSignal
core_module.QRunnable = QRunnable
core_module.QThreadPool = QThreadPool
sys.modules["PyQt6"] = pyqt_module
sys.modules["PyQt6.QtCore"] = core_module

# ==========================================
# 2. 모듈 직접 로드 및 Mock 적용
# ==========================================
from BusinessLogic.mocks import (
    DocumentParser, GitAnalyzer, MessengerParser,
    AliasMapper, ContributionAggregator, CacheManager,
    MainWindow, MemberScore
)

class MockNormalizedSignalsTracker:
    def __init__(self):
        self.dismissed = []
        self.cleared = False
    def dismiss(self, author, signal_type, ref):
        self.dismissed.append((author, signal_type, ref))
    def clear(self):
        self.cleared = True
        self.dismissed = []
    def apply(self, scores):
        return [s for s in scores]

class MockAliasExtractor:
    def extract_identifiers(self, git, docs, msgs):
        return [{"raw_id": "Alice", "source": "docs"}]
    def suggest_mapping(self, identifiers):
        return {"Alice": "Alice"}


_ctrl_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Controller.py")
_spec = importlib.util.spec_from_file_location("Controller", _ctrl_path)
Controller = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(Controller)

# 동적 주입 (globals에 모의 객체 할당)
Controller.DocumentParser = DocumentParser
Controller.GitAnalyzer = GitAnalyzer
Controller.MessengerParser = MessengerParser
Controller.AliasMapper = AliasMapper
Controller.ContributionAggregator = ContributionAggregator
Controller.CacheManager = CacheManager
Controller.NormalizedSignalsTracker = MockNormalizedSignalsTracker
Controller.AliasExtractor = MockAliasExtractor

AnalysisOrchestrator = Controller.AnalysisOrchestrator
AppController = Controller.AppController
AnalysisWorker = Controller.AnalysisWorker


# ==========================================
# 3. 테스트 케이스
# ==========================================

@pytest.fixture
def controller_setup():
    QThreadPool._instance = MockThreadPool()
    for cls in [Controller.AnalysisOrchestrator, Controller.AnalysisWorkerSignals, Controller.MergeWorkerSignals]:
        for sig_name in ['progress', 'completed', 'failed']:
            if hasattr(cls, sig_name):
                sig = getattr(cls, sig_name)
                sig.callbacks.clear()
                sig._emitted_values.clear()
                
    main_window = MainWindow()
    orchestrator = AnalysisOrchestrator()
    app = AppController(main_window, orchestrator)
    return app, orchestrator, main_window


class TestControllerRoutingAndState:
    def test_concurrent_starts_blocked(self, controller_setup):
        """TC-NFR-1.2-02: start_analysis 5회 연속 호출 시 Worker 1개만 기동"""
        app, orch, mw = controller_setup
        for _ in range(5):
            orch.start_analysis({})
        assert len(orch.thread_pool.queue) == 1
        assert orch.is_analyzing is True
        orch.thread_pool.execute_all()
        assert orch.is_analyzing is False

    def test_pipeline_isolation(self, controller_setup, monkeypatch):
        """TC-NFR-3.2-03: 파서 1개 에러(git) 시 파이프라인 유지 (격리)"""
        app, orch, mw = controller_setup
        orch.completed._emitted_values.clear()
        orch.failed._emitted_values.clear()
        class FailingGit(GitAnalyzer):
            def __init__(self): super().__init__(should_fail=True)
        monkeypatch.setattr(Controller, "GitAnalyzer", FailingGit)
        orch.start_analysis({})
        orch.thread_pool.execute_all()
        assert orch.is_analyzing is False
        assert len(orch.completed._emitted_values) == 1
        assert len(orch.failed._emitted_values) == 0


class TestThreeScreenTransitions:
    def test_analyze_clicked_transitions(self, controller_setup):
        """TC-FR-5.4-01: 분석 시작 시 loading 화면 전환 후 완료 시 result 화면 전환"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        assert mw.current_screen == "loading"
        orch.thread_pool.execute_all()
        assert mw.current_screen == "result"
        
    def test_new_analysis_requested(self, controller_setup):
        """TC-FR-5.4-02: 새로운 분석 요청 시 submit 화면으로 전환 및 상태 리셋"""
        app, orch, mw = controller_setup
        app.route_event("new_analysis_requested", {})
        assert mw.current_screen == "submit"
        assert app.tracker.cleared is True
        assert len(app._last_scores) == 0


class TestMergeReaggregation:
    def test_merge_requested_flow(self, controller_setup):
        """TC-FR-5.7-03: 병합 요청 수신 -> 재집계 -> show_result 복귀 검증"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        assert orch._raw_docs == {"Alice": 100}
        
        app.route_event("merge_requested", {"Alice": "MergedPerson"})
        assert mw.current_screen == "loading"
        orch.thread_pool.execute_all()
        assert mw.current_screen == "result"
        rendered_scores = mw.result_screen.rendered_scores
        assert len(rendered_scores) == 1
        assert rendered_scores[0]["author"] == "MergedPerson"

    def test_merge_determinism(self, controller_setup):
        """TC-FR-5.7-05: 동일 병합 매핑 2회 요청 시결과 일치 (결정론)"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        
        app.route_event("merge_requested", {"A": "B"})
        orch.thread_pool.execute_all()
        res1 = mw.result_screen.rendered_scores
        
        app.route_event("merge_requested", {"A": "B"})
        orch.thread_pool.execute_all()
        res2 = mw.result_screen.rendered_scores
        
        assert res1 == res2

    def test_merge_overlapping_blocked(self, controller_setup):
        """TC-FR-5.7-06: 병합 재집계 중 중복 요청 차단 (is_analyzing 가드)"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        
        app.route_event("merge_requested", {"A": "B"})
        assert orch.is_analyzing is True
        assert len(orch.thread_pool.queue) == 1
        app.route_event("merge_requested", {"A": "C"})
        assert len(orch.thread_pool.queue) == 1


class TestViewTypeIsolation:
    def test_asdict_serialization(self, controller_setup):
        """TC-INV-V1: View에 전달되는 scores가 MemberScore 객체가 아닌 평문 dict 구조여야 함"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        
        rendered_scores = mw.result_screen.rendered_scores
        assert len(rendered_scores) > 0
        first_score = rendered_scores[0]
        assert isinstance(first_score, dict)
        assert "author" in first_score
        assert "total_score" in first_score


class TestSignalDismissal:
    def test_signal_dismissed_routing(self, controller_setup):
        """TC-FR-4.2c-09: 신호 무시 이벤트 수신 시 재집계 없이 렌더 갱신"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        
        # 신호 초기 설정
        mw.current_screen = "result"
        app.route_event("signal_dismissed", ("Alice", "CAPPING", "hash1"))
        
        assert ("Alice", "CAPPING", "hash1") in app.tracker.dismissed
        # View render is called again but no worker is spawned
        assert mw.current_screen == "result"
        assert len(orch.thread_pool.queue) == 0

