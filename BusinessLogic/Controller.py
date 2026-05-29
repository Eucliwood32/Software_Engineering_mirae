import traceback
from typing import Optional, List, Dict
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

# 향후 개발 시 BusinessLogic 및 Models 내 실제 파서/집계기 import 필요
# from BusinessLogic.Parsers import DocumentParser, GitAnalyzer, MessengerParser
# from BusinessLogic.BusinessLogic import ContributionAggregator, AliasMapper, CacheManager
# from BusinessLogic.DataTypes import MemberScore

class AnalysisWorkerSignals(QObject):
    """
    Worker Thread에서 메인 스레드로 전달할 시그널 정의.
    (C-5, NFR-1.1 UI 응답성 보장)
    """
    progress = pyqtSignal(int)          # 0~100 진행률
    completed = pyqtSignal(list)        # list[MemberScore] 완료 결과
    failed = pyqtSignal(str)            # 오류 메시지


class AnalysisWorker(QRunnable):
    """
    백그라운드에서 실제 분석(파싱, 정규화, 집계) 코드를 실행하는 워커.
    (NFR-1.1) 메인 UI 스레드를 블로킹하지 않음.
    (NFR-1.2, C-4) UI 객체를 직접 참조하지 않으며, Signal을 통해서만 상태를 알림.
    """
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.signals = AnalysisWorkerSignals()

    def run(self):
        try:
            self.signals.progress.emit(5)
            
            # Model 레이어 인스턴스화 (의존성 주입 시뮬레이션을 위해 전역 모듈 속성 사용)
            doc_parser = DocumentParser() if 'DocumentParser' in globals() else None
            git_analyzer = GitAnalyzer() if 'GitAnalyzer' in globals() else None
            msg_parser = MessengerParser() if 'MessengerParser' in globals() else None
            alias_mapper = AliasMapper() if 'AliasMapper' in globals() else None
            aggregator = ContributionAggregator() if 'ContributionAggregator' in globals() else None
            cache_manager = CacheManager() if 'CacheManager' in globals() else None
            
            self.signals.progress.emit(10)
            
            doc_data = None
            git_data = None
            msg_data = None
            
            # 파이프라인 단계 1: 데이터 수집 
            # (NFR-3.2 데이터 모듈 상호 격리: 실패 시 예외 전파 대신 None 혹은 빈 데이터를 반환해 타 모듈 영향 최소화)
            
            if doc_parser:
                try: 
                    doc_data = doc_parser.parse(self.config.get('doc_path', ''))
                except Exception as e: 
                    print(f"Doc parsing error (ignored): {e}")
                    
            self.signals.progress.emit(30)
            
            if git_analyzer:
                try: 
                    git_data = git_analyzer.analyze(self.config.get('git_path', ''))
                except Exception as e: 
                    print(f"Git analyzing error (ignored): {e}")
                    
            self.signals.progress.emit(50)
            
            if msg_parser:
                try: 
                    parse_result = msg_parser.parse(self.config.get('msg_path', ''))
                    msg_data = parse_result.records
                except Exception as e: 
                    print(f"Messenger parsing error (ignored): {e}")
                    
            self.signals.progress.emit(70)
            
            # 파이프라인 단계 2: 식별자 통합 (FR-1.3 신원 매핑)
            mapped_data = {}
            if alias_mapper:
                raw_data = {"docs": doc_data, "git": git_data, "msg": msg_data}
                mapped_data = alias_mapper.merge(raw_data, self.config.get('alias_mapping', {}))
            
            # 파이프라인 단계 3: 집계 및 스케일링
            self.signals.progress.emit(85)
            scores = []
            if aggregator:
                scores = aggregator.aggregate(
                    git=mapped_data.get("git"),
                    docs=mapped_data.get("docs"),
                    msgs=mapped_data.get("msg"),
                    weights=self.config.get('weights', {"git": 0.4, "docs": 0.4, "msg": 0.2})
                )
            
            # 파이프라인 단계 4: 캐싱 (NFR-2.3, C-8 JSON 전용 직렬화)
            if cache_manager and scores:
                cache_manager.save({"scores": [score.__dict__ for score in scores], "timestamp": "now"})
            
            self.signals.progress.emit(100)
            self.signals.completed.emit(scores)
            
        except Exception as e:
            # 예상치 못한 중대 에러 처리
            err_msg = f"분석 중 치명적 오류 발생: {str(e)}\n{traceback.format_exc()}"
            self.signals.failed.emit(err_msg)


class AnalysisOrchestrator(QObject):
    """
    비동기 분석 작업의 상태 관리와 Model 레이어 통합을 전담하는 QObject 기반 컴포넌트.
    """
    progress = pyqtSignal(int)          # 메인 스레드 UI(ProgressBar)로 전달될 진행률 Signal
    completed = pyqtSignal(list)        # 완료 결과 Signal
    failed = pyqtSignal(str)            # 실패 Signal

    def __init__(self):
        super().__init__()
        self.is_analyzing: bool = False
        self.thread_pool = QThreadPool.globalInstance()

    def start_analysis(self, config: dict) -> None:
        """
        분석을 시작하며 Worker Thread를 기동.
        (NFR-1.2) is_analyzing이 True면 즉시 return하여 중복 실행을 차단.
        """
        if self.is_analyzing:
            return
            
        self.is_analyzing = True
        
        # Worker Thread 생성 및 Signal 연결 (단방향 통신 보장)
        worker = AnalysisWorker(config)
        worker.signals.progress.connect(self.progress.emit)
        worker.signals.completed.connect(self._on_worker_completed)
        worker.signals.failed.connect(self._on_worker_failed)
        
        self.thread_pool.start(worker)
        
    def _on_worker_completed(self, scores: list) -> None:
        """성공 시 is_analyzing 해제 및 결과 반환"""
        self._on_worker_finished()
        self.completed.emit(scores)
        
    def _on_worker_failed(self, err_msg: str) -> None:
        """실패 시 is_analyzing 해제 및 에러 메시지 반환"""
        self._on_worker_finished()
        self.failed.emit(err_msg)

    def _on_worker_finished(self) -> None:
        """종료 시 (성공, 실패, 취소 무관) is_analyzing=False 처리하여 UI 버튼 재활성화를 지원"""
        self.is_analyzing = False


class AppController:
    """
    애플리케이션의 진입점(Entry Point)과 각 View 위젯 간의 이벤트를 라우팅하는 최상위 컨트롤러.
    (C-4) 엄격한 MVC 단방향 흐름을 유지하며, View 위젯을 직접 렌더링하거나 도메인 로직을 갖지 않음.
    """
    def __init__(self, main_window, orchestrator: AnalysisOrchestrator):
        self.main_window = main_window
        self.orchestrator = orchestrator
        
        # AnalysisOrchestrator의 메인 시그널들을 AppController에서 라우팅 연결
        self.orchestrator.completed.connect(self.on_analysis_completed)
        # self.orchestrator.progress.connect(self.main_window.update_progress)
        # self.orchestrator.failed.connect(self.main_window.show_error)

    def route_event(self, event: str, payload: dict) -> None:
        """View에서 발생한 이벤트를 식별하여 라우팅"""
        if event == "start_analysis":
            # 분석 시작 이벤트 -> AnalysisOrchestrator 위임
            self.orchestrator.start_analysis(payload)
        elif event == "save_report":
            # FR-5.2 리포트 저장 (ReportExporter 호출)
            pass
        elif event == "update_weights":
            # FR-4.4 가중치 프리셋 조정 연동
            pass
        else:
            print(f"Unknown event: {event}")

    def on_analysis_completed(self, scores: list) -> None:
        """
        완료 Signal 수신 후 DashboardView 갱신을 지시 (메인 스레드).
        """
        # self.main_window.update_dashboard(scores)
        pass
