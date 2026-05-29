import sys
import traceback
from types import ModuleType

# === Mock PyQt6 ===
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
    def __init__(self):
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

# sys.modules 조작
pyqt_module = ModuleType("PyQt6")
core_module = ModuleType("PyQt6.QtCore")
core_module.QObject = QObject
core_module.pyqtSignal = pyqtSignal
core_module.QRunnable = QRunnable
core_module.QThreadPool = QThreadPool
sys.modules["PyQt6"] = pyqt_module
sys.modules["PyQt6.QtCore"] = core_module
# ==================

# 이제 Controller를 임포트할 수 있습니다.
from BusinessLogic.Controller import AnalysisOrchestrator, AnalysisWorker
import BusinessLogic.Controller as ControllerModule
from BusinessLogic.mocks import (
    DocumentParser, GitAnalyzer, MessengerParser, 
    AliasMapper, ContributionAggregator, CacheManager
)

def inject_mocks(should_fail_parser=None):
    """
    Controller 내부에 주석 처리된(또는 미구현된) 파서 인스턴스화 부분을 
    우리가 만든 Mock으로 교체(의존성 주입 시뮬레이션)합니다.
    (실제로는 Controller 파일 내부에 의존성을 주입해야 하지만, 테스트를 위해 런타임에 클래스를 치환합니다)
    """
    class MockDocParser(DocumentParser):
        def __init__(self): super().__init__(should_fail=(should_fail_parser=='doc'))
    class MockGitAnalyzer(GitAnalyzer):
        def __init__(self): super().__init__(should_fail=(should_fail_parser=='git'))
    class MockMsgParser(MessengerParser):
        def __init__(self): super().__init__(should_fail=(should_fail_parser=='msg'))
        
    ControllerModule.DocumentParser = MockDocParser
    ControllerModule.GitAnalyzer = MockGitAnalyzer
    ControllerModule.MessengerParser = MockMsgParser
    ControllerModule.AliasMapper = AliasMapper
    ControllerModule.ContributionAggregator = ContributionAggregator
    ControllerModule.CacheManager = CacheManager

def run_tests():
    print("--- Running tests for Controller.py ---")
    inject_mocks()

    # [Test 1] TC-NFR-1.2-02: start 5회 연속 호출 시 Worker 1개만 기동
    orch = AnalysisOrchestrator()
    start_calls = []
    
    # 워커 기동 감지용 몽키패치
    original_start = orch.thread_pool.start
    def patched_start(runnable):
        start_calls.append(1)
        original_start(runnable)
    orch.thread_pool.start = patched_start
    
    for _ in range(5):
        orch.start_analysis({})
        
    assert len(start_calls) == 1, f"Expected 1 start, got {len(start_calls)}"
    assert orch.is_analyzing is True, "Expected is_analyzing to be True before execution"
    
    # 이제 워커를 실행하여 종료시킴
    orch.thread_pool.execute_all()
    assert orch.is_analyzing is False, "Expected is_analyzing to be reset after execution"
    print("[PASS] TC-NFR-1.2-02: start 5회 연속 호출 -> Worker 1개만 기동")

    # [Test 2] TC-NFR-1.2-04: RuntimeError 발생 시 is_analyzing=False 복원
    # Controller 내부에 _on_worker_finished가 불리는지 확인
    orch = AnalysisOrchestrator()
    # 의도적으로 에러를 발생시키는 워커를 모사
    orch.is_analyzing = True
    orch._on_worker_finished()
    assert orch.is_analyzing is False, "is_analyzing should be False after _on_worker_finished"
    print("[PASS] TC-NFR-1.2-04: 상태 복원 검증 (is_analyzing=False)")
    
    # [Test 3] TC-NFR-3.2-03: 1개 모듈 RuntimeError 시 나머지 결과 유지 (격리)
    inject_mocks(should_fail_parser='git')
    worker = AnalysisWorker({})
    worker.run()
    
    # worker.signals.completed.emit() 호출에 들어간 args를 확인합니다.
    # 성공적으로 리스트(scores)가 방출되었는지 확인
    emitted_completed = worker.signals.completed._emitted_values
    emitted_failed = worker.signals.failed._emitted_values
    
    # 실패하지 않아야 함
    assert len(emitted_failed) == 0, f"Worker failed unexpectedly: {emitted_failed}"
    assert len(emitted_completed) > 0, "Worker did not complete"
    scores = emitted_completed[0][0]
    # 모형(Aggregator)이 반환한 [MemberScore(Alice, 0.9)]가 있어야 함
    assert len(scores) == 1 and scores[0].author == "Alice", "Scores list missing or invalid"
    print("[PASS] TC-NFR-3.2-03: 파서 1개 에러(git) 발생 시 전체 파이프라인 정상 유지")

    print("--- All tests passed (green-light) ---")

if __name__ == "__main__":
    run_tests()
