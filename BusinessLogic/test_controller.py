"""
test_controller.py

Controller.py (AppController, AnalysisOrchestrator) 모듈에 대한 통합 단위 테스트.
PyQt6 의존성을 Mocking하여 UI 없이 스레드 동작 및 라우팅 상태를 테스트합니다.
v1.1: 3-스크린 전환(FR-5.4), 결과 화면 계정 병합(FR-5.7), View 타입 격리(INV-V1) 케이스 신설.

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
    MainWindow
)

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

AnalysisOrchestrator = Controller.AnalysisOrchestrator
AppController = Controller.AppController
AnalysisWorker = Controller.AnalysisWorker


# ==========================================
# 3. 테스트 케이스
# ==========================================

@pytest.fixture
def controller_setup():
    # 매 테스트마다 ThreadPool과 Orchestrator 상태 초기화
    QThreadPool._instance = MockThreadPool()
    
    # 클래스 레벨로 공유되는 MockSignal의 상태를 초기화하여 테스트 간 격리 보장
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
        
        # 이전 테스트에서 누적된 emitted 값을 지운다
        orch.completed._emitted_values.clear()
        orch.failed._emitted_values.clear()
        
        # GitAnalyzer만 실패하도록 Mock 교체
        class FailingGit(GitAnalyzer):
            def __init__(self): super().__init__(should_fail=True)
        monkeypatch.setattr(Controller, "GitAnalyzer", FailingGit)
        
        orch.start_analysis({})
        orch.thread_pool.execute_all()
        
        # failed 대신 completed가 방출되었는지 확인
        assert orch.is_analyzing is False
        assert len(orch.completed._emitted_values) == 1
        assert len(orch.failed._emitted_values) == 0


class TestThreeScreenTransitions:
    def test_analyze_clicked_transitions(self, controller_setup):
        """TC-FR-5.4-01: 분석 시작 시 loading 화면 전환 후 완료 시 result 화면 전환"""
        app, orch, mw = controller_setup
        
        # route_event로 분석 시작 트리거
        app.route_event("start_analysis", {})
        assert mw.current_screen == "loading"
        
        # 워커 실행 (분석 완료)
        orch.thread_pool.execute_all()
        assert mw.current_screen == "result"
        
    def test_new_analysis_requested(self, controller_setup):
        """TC-FR-5.4-02: 새로운 분석 요청 시 submit 화면으로 전환"""
        app, orch, mw = controller_setup
        app.route_event("new_analysis_requested", {})
        assert mw.current_screen == "submit"


class TestMergeReaggregation:
    def test_merge_requested_flow(self, controller_setup):
        """TC-FR-5.7-03: 병합 요청 수신 -> 재집계 -> show_result 복귀 검증"""
        app, orch, mw = controller_setup
        
        # 1. 먼저 1차 분석 완료하여 원시 데이터 보유 상태 생성
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        assert orch._raw_docs == {"Alice": 100}  # Mock 반환값 확인
        
        # 2. 병합 요청 이벤트 (AliasMapper Mock이 mapping이 있으면 MergedPerson 반환)
        app.route_event("merge_requested", {"Alice": "MergedPerson"})
        assert mw.current_screen == "loading"
        
        # 3. 병합 워커 실행
        orch.thread_pool.execute_all()
        assert mw.current_screen == "result"
        
        # 병합 후 반환된 데이터가 "MergedPerson" 인지 확인
        rendered_scores = mw.result_screen.rendered_scores
        assert len(rendered_scores) == 1
        assert rendered_scores[0]["author"] == "MergedPerson"

    def test_merge_determinism(self, controller_setup):
        """TC-FR-5.7-05: 동일 병합 매핑 2회 요청 시결과 일치 (결정론)"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        
        # 첫 번째 병합
        app.route_event("merge_requested", {"A": "B"})
        orch.thread_pool.execute_all()
        res1 = mw.result_screen.rendered_scores
        
        # 두 번째 병합
        app.route_event("merge_requested", {"A": "B"})
        orch.thread_pool.execute_all()
        res2 = mw.result_screen.rendered_scores
        
        assert res1 == res2

    def test_merge_overlapping_blocked(self, controller_setup):
        """TC-FR-5.7-06: 병합 재집계 중 중복 요청 차단 (is_analyzing 가드)"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        
        # 첫 번째 병합 요청 (워커 큐에 추가됨)
        app.route_event("merge_requested", {"A": "B"})
        assert orch.is_analyzing is True
        assert len(orch.thread_pool.queue) == 1
        
        # 두 번째 병합 요청 시도
        app.route_event("merge_requested", {"A": "C"})
        # 큐에 추가되지 않아야 함 (가드 작동)
        assert len(orch.thread_pool.queue) == 1


class TestViewTypeIsolation:
    def test_asdict_serialization(self, controller_setup):
        """TC-INV-V1: View에 전달되는 scores가 MemberScore 객체가 아닌 평문 dict 구조여야 함"""
        app, orch, mw = controller_setup
        app.route_event("start_analysis", {})
        orch.thread_pool.execute_all()
        
        rendered_scores = mw.result_screen.rendered_scores
        assert len(rendered_scores) > 0
        
        # 딕셔너리(dict) 타입 검증
        first_score = rendered_scores[0]
        assert isinstance(first_score, dict)
        assert "author" in first_score
        assert "total_score" in first_score
        assert "anomaly_flags" in first_score
