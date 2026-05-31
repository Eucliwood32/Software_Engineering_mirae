import traceback
import dataclasses
from typing import Optional, List, Dict, Any, Tuple
# pyrefly: ignore [missing-import]
from PyQt6.QtCore import QObject, pyqtSignal, QRunnable, QThreadPool

try:
    from qce.model.parsing.document_parser import DocumentParser
    from qce.model.parsing.git_analyzer import GitAnalyzer
    from qce.model.parsing.messenger_parser import MessengerParser
except ImportError:
    DocumentParser = GitAnalyzer = MessengerParser = None

try:
    from qce.model.business.BusinessLogic import (
        ContributionAggregator, AliasMapper, CacheManager,
        NormalizedSignalsTracker, AliasExtractor
    )
except ImportError:
    ContributionAggregator = AliasMapper = CacheManager = NormalizedSignalsTracker = AliasExtractor = None


class AnalysisWorkerSignals(QObject):
    progress = pyqtSignal(int)          # 0~100 진행률
    completed = pyqtSignal(tuple)       # (list[MemberScore], raw_git, raw_docs, raw_msgs, weights)
    failed = pyqtSignal(str)            # 오류 메시지

class AnalysisWorker(QRunnable):
    """
    1차 분석: 파싱, 정규화, 집계 실행. (FR-1.3 개정에 따라 1차는 항등 매핑)
    """
    def __init__(self, config: dict):
        super().__init__()
        self.config = config
        self.signals = AnalysisWorkerSignals()

    def _create_identity_mapping(self, git, docs, msgs) -> dict:
        aliases = set()
        if git: aliases.update(git.keys())
        if docs: aliases.update(docs.keys())
        if msgs: aliases.update(msgs.keys())
        return {a: a for a in aliases}

    def run(self):
        try:
            self.signals.progress.emit(5)
            doc_parser = DocumentParser() if DocumentParser else globals().get('DocumentParser')() if 'DocumentParser' in globals() else None
            git_analyzer = GitAnalyzer() if GitAnalyzer else globals().get('GitAnalyzer')() if 'GitAnalyzer' in globals() else None
            msg_parser = MessengerParser() if MessengerParser else globals().get('MessengerParser')() if 'MessengerParser' in globals() else None
            alias_mapper = AliasMapper() if AliasMapper else globals().get('AliasMapper')() if 'AliasMapper' in globals() else None
            aggregator = ContributionAggregator() if ContributionAggregator else globals().get('ContributionAggregator')() if 'ContributionAggregator' in globals() else None
            cache_manager = CacheManager() if CacheManager else globals().get('CacheManager')() if 'CacheManager' in globals() else None
            
            self.signals.progress.emit(10)
            doc_data = None
            git_data = None
            msg_data = None
            
            if doc_parser:
                try: doc_data = doc_parser.parse(self.config.get('doc_path', ''))
                except Exception as e: print(f"Doc parsing error (ignored): {e}")
            self.signals.progress.emit(30)
            
            if git_analyzer:
                try: git_data = git_analyzer.analyze(self.config.get('git_path', ''))
                except Exception as e: print(f"Git analyzing error (ignored): {e}")
            self.signals.progress.emit(50)
            
            if msg_parser:
                try: 
                    parse_result = msg_parser.parse(self.config.get('msg_path', ''))
                    msg_counts = {}
                    for rec in parse_result.records:
                        if hasattr(rec, 'author'):
                            msg_counts[rec.author] = msg_counts.get(rec.author, 0) + 1
                        elif isinstance(rec, str):
                            msg_counts["Unknown"] = msg_counts.get("Unknown", 0) + 1
                    msg_data = msg_counts
                except Exception as e: print(f"Messenger parsing error (ignored): {e}")
            self.signals.progress.emit(70)
            
            mapped_git = git_data
            mapped_docs = doc_data
            mapped_msgs = msg_data
            
            if alias_mapper:
                identity = self._create_identity_mapping(git_data, doc_data, msg_data)
                mapped_git = alias_mapper.merge(git_data, identity) if git_data else None
                mapped_docs = alias_mapper.merge(doc_data, identity) if doc_data else None
                mapped_msgs = alias_mapper.merge(msg_data, identity) if msg_data else None
            
            self.signals.progress.emit(85)
            scores = []
            weights = self.config.get('weights', {"git": 0.4, "docs": 0.4, "msg": 0.2})
            if aggregator:
                scores = aggregator.aggregate(
                    git=mapped_git,
                    docs=mapped_docs,
                    msgs=mapped_msgs,
                    weights=weights
                )
            
            if cache_manager and scores:
                cache_manager.save({"scores": [score.__dict__ for score in scores], "timestamp": "now"})
            
            self.signals.progress.emit(100)
            self.signals.completed.emit((scores, git_data, doc_data, msg_data, weights))
            
        except Exception as e:
            err_msg = f"분석 중 치명적 오류 발생: {str(e)}\n{traceback.format_exc()}"
            self.signals.failed.emit(err_msg)


class MergeWorkerSignals(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)

class MergeWorker(QRunnable):
    """
    병합 재집계 (FR-5.7): 파서를 생략하고 원시 데이터를 기반으로 AliasMapper와 ContributionAggregator 재호출
    """
    def __init__(self, raw_git, raw_docs, raw_msgs, weights, mapping):
        super().__init__()
        self.raw_git = raw_git
        self.raw_docs = raw_docs
        self.raw_msgs = raw_msgs
        self.weights = weights
        self.mapping = mapping
        self.signals = MergeWorkerSignals()

    def run(self):
        try:
            self.signals.progress.emit(10)
            alias_mapper = AliasMapper() if AliasMapper else globals().get('AliasMapper')() if 'AliasMapper' in globals() else None
            aggregator = ContributionAggregator() if ContributionAggregator else globals().get('ContributionAggregator')() if 'ContributionAggregator' in globals() else None
            cache_manager = CacheManager() if CacheManager else globals().get('CacheManager')() if 'CacheManager' in globals() else None
            
            self.signals.progress.emit(30)
            
            mapped_git = self.raw_git
            mapped_docs = self.raw_docs
            mapped_msgs = self.raw_msgs
            
            if alias_mapper:
                mapped_git = alias_mapper.merge(self.raw_git, self.mapping) if self.raw_git else None
                mapped_docs = alias_mapper.merge(self.raw_docs, self.mapping) if self.raw_docs else None
                mapped_msgs = alias_mapper.merge(self.raw_msgs, self.mapping) if self.raw_msgs else None
            
            self.signals.progress.emit(60)
            scores = []
            if aggregator:
                scores = aggregator.aggregate(
                    git=mapped_git,
                    docs=mapped_docs,
                    msgs=mapped_msgs,
                    weights=self.weights
                )
            
            self.signals.progress.emit(90)
            if cache_manager and scores:
                cache_manager.save({"scores": [score.__dict__ for score in scores], "timestamp": "now_merged"})
            
            self.signals.progress.emit(100)
            self.signals.completed.emit(scores)
        except Exception as e:
            err_msg = f"병합 중 치명적 오류 발생: {str(e)}\n{traceback.format_exc()}"
            self.signals.failed.emit(err_msg)


class AnalysisOrchestrator(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.is_analyzing: bool = False
        self.thread_pool = QThreadPool.globalInstance()
        
        self._raw_git = None
        self._raw_docs = None
        self._raw_msgs = None
        self._current_weights = None

    def start_analysis(self, config: dict) -> None:
        if self.is_analyzing:
            return
        self.is_analyzing = True
        
        worker = AnalysisWorker(config)
        worker.signals.progress.connect(self.progress.emit)
        worker.signals.completed.connect(self._on_analysis_worker_completed)
        worker.signals.failed.connect(self._on_worker_failed)
        self.thread_pool.start(worker)

    def start_merge_reaggregation(self, mapping: dict) -> None:
        if self.is_analyzing:
            return
        self.is_analyzing = True
        
        worker = MergeWorker(self._raw_git, self._raw_docs, self._raw_msgs, self._current_weights, mapping)
        worker.signals.progress.connect(self.progress.emit)
        worker.signals.completed.connect(self._on_merge_worker_completed)
        worker.signals.failed.connect(self._on_worker_failed)
        self.thread_pool.start(worker)
        
    def _on_analysis_worker_completed(self, result_tuple: tuple) -> None:
        scores, git_data, doc_data, msg_data, weights = result_tuple
        self._raw_git = git_data
        self._raw_docs = doc_data
        self._raw_msgs = msg_data
        self._current_weights = weights
        
        self.is_analyzing = False
        self.completed.emit(scores)
        
    def _on_merge_worker_completed(self, scores: list) -> None:
        self.is_analyzing = False
        self.completed.emit(scores)
        
    def _on_worker_failed(self, err_msg: str) -> None:
        self.is_analyzing = False
        self.failed.emit(err_msg)


class AppController:
    def __init__(self, main_window, orchestrator: AnalysisOrchestrator):
        self.main_window = main_window
        self.orchestrator = orchestrator
        self.orchestrator.completed.connect(self.on_analysis_completed)
        self.orchestrator.failed.connect(self.on_analysis_failed)
        self.orchestrator.progress.connect(self.on_progress)
        
        self.tracker = NormalizedSignalsTracker() if NormalizedSignalsTracker else globals().get('NormalizedSignalsTracker')() if 'NormalizedSignalsTracker' in globals() else None
        self.alias_extractor = AliasExtractor() if AliasExtractor else globals().get('AliasExtractor')() if 'AliasExtractor' in globals() else None
        self._last_scores = []

    def route_event(self, event: str, payload: Any = None) -> None:
        if event == "start_analysis":
            self.main_window.show_loading()
            self.orchestrator.start_analysis(payload)
        elif event == "merge_requested":
            self.on_merge_requested(payload)
        elif event == "new_analysis_requested":
            self.on_new_analysis_requested()
        elif event == "signal_dismissed":
            author, sig_type, ref = payload
            self.on_signal_dismissed(author, sig_type, ref)

    def on_merge_requested(self, mapping: dict) -> None:
        self.main_window.show_loading()
        self.orchestrator.start_merge_reaggregation(mapping)

    def on_new_analysis_requested(self) -> None:
        if self.tracker:
            self.tracker.clear()
        self._last_scores = []
        self.main_window.show_submit()

    def on_signal_dismissed(self, author: str, signal_type: str, ref: str) -> None:
        if self.tracker:
            self.tracker.dismiss(author, signal_type, ref)
        self._render_results()

    def on_analysis_completed(self, scores: list) -> None:
        self._last_scores = scores
        if self.tracker:
            self.tracker.clear()
        self._render_results()
        self.main_window.show_result()
        
    def _render_results(self) -> None:
        scores = self._last_scores
        if self.tracker:
            scores = self.tracker.apply(self._last_scores)
            
        score_dicts = [dataclasses.asdict(s) for s in scores]
        self.main_window.result_screen.render(score_dicts, set())
        
        if self.alias_extractor:
            identifiers = self.alias_extractor.extract_identifiers(
                self.orchestrator._raw_git,
                self.orchestrator._raw_docs,
                self.orchestrator._raw_msgs
            )
            mapping = self.alias_extractor.suggest_mapping(identifiers)
            if hasattr(self.main_window.result_screen, "set_suggested_mapping"):
                self.main_window.result_screen.set_suggested_mapping(mapping)

    def on_analysis_failed(self, message: str) -> None:
        print(f"FATAL ERROR EMITTED: {message}")
        self.main_window.show_submit()
        # self.main_window.show_error(message)

    def on_progress(self, val: int) -> None:
        pass
