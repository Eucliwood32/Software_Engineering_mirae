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
    completed = pyqtSignal(tuple)       # (scores, raw_git, raw_docs, raw_msgs, weights, doc_details, msg_details)
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
            doc_details = None
            git_data = None
            msg_data = None
            msg_details = None

            if doc_parser:
                try:
                    doc_paths = self.config.get('doc_paths') or ([self.config['doc_path']] if self.config.get('doc_path') else [])
                    doc_data = {}
                    doc_details = {}        # {author: {"chars","blocks","docs"}} — 레이더 세부 축(v1.7)
                    for dp in doc_paths:
                        detailed = (doc_parser.parse_detailed(dp)
                                    if hasattr(doc_parser, 'parse_detailed')
                                    else {a: {"chars": c} for a, c in doc_parser.parse(dp).items()})
                        for author, d in detailed.items():
                            chars = d.get("chars", 0)
                            doc_data[author] = doc_data.get(author, 0) + chars
                            entry = doc_details.setdefault(author, {"chars": 0, "blocks": 0, "docs": 0})
                            entry["chars"] += chars
                            entry["blocks"] += d.get("blocks", 0)
                            entry["docs"] += 1
                    if not doc_data:
                        doc_data = None
                        doc_details = None
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
                    msg_details = {}      # {author: {"count","chars","hours"}} — 레이더 세부 축(v1.7)
                    hour_sets: dict = {}  # {author: set(HH)} → 활동 시간대 수 산출용
                    for rec in parse_result.records:
                        author = rec.author if hasattr(rec, 'author') else "Unknown"
                        msg_counts[author] = msg_counts.get(author, 0) + 1
                        entry = msg_details.setdefault(author, {"count": 0, "chars": 0, "hours": 0})
                        entry["count"] += 1
                        entry["chars"] += len(getattr(rec, 'message', '') or '')
                        ts = getattr(rec, 'timestamp', '') or ''
                        hour_sets.setdefault(author, set()).add(ts.split(":")[0])
                    for author, hours in hour_sets.items():
                        msg_details[author]["hours"] = len(hours)
                    msg_data = msg_counts
                    if not msg_data:
                        msg_details = None
                except Exception as e: print(f"Messenger parsing error (ignored): {e}")
            self.signals.progress.emit(70)
            
            mapped_git = git_data
            mapped_docs = doc_data
            mapped_msgs = msg_data
            mapped_doc_details = doc_details
            mapped_msg_details = msg_details

            if alias_mapper:
                identity = self._create_identity_mapping(git_data, doc_data, msg_data)
                mapped_git = alias_mapper.merge(git_data, identity) if git_data else None
                mapped_docs = alias_mapper.merge(doc_data, identity) if doc_data else None
                mapped_msgs = alias_mapper.merge(msg_data, identity) if msg_data else None
                mapped_doc_details = alias_mapper.merge(doc_details, identity) if doc_details else None
                mapped_msg_details = alias_mapper.merge(msg_details, identity) if msg_details else None

            self.signals.progress.emit(85)
            scores = []
            weights = self.config.get('weights', {"git": 0.4, "docs": 0.4, "msg": 0.2})
            if aggregator:
                scores = aggregator.aggregate(
                    git=mapped_git,
                    docs=mapped_docs,
                    msgs=mapped_msgs,
                    weights=weights,
                    doc_details=mapped_doc_details,
                    msg_details=mapped_msg_details,
                )

            if cache_manager and scores:
                cache_manager.save({"scores": [score.__dict__ for score in scores], "timestamp": "now"})

            self.signals.progress.emit(100)
            self.signals.completed.emit((scores, git_data, doc_data, msg_data, weights, doc_details, msg_details))
            
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
    def __init__(self, raw_git, raw_docs, raw_msgs, weights, mapping,
                 raw_doc_details=None, raw_msg_details=None):
        super().__init__()
        self.raw_git = raw_git
        self.raw_docs = raw_docs
        self.raw_msgs = raw_msgs
        self.weights = weights
        self.mapping = mapping
        self.raw_doc_details = raw_doc_details
        self.raw_msg_details = raw_msg_details
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
            mapped_doc_details = self.raw_doc_details
            mapped_msg_details = self.raw_msg_details

            if alias_mapper:
                mapped_git = alias_mapper.merge(self.raw_git, self.mapping) if self.raw_git else None
                mapped_docs = alias_mapper.merge(self.raw_docs, self.mapping) if self.raw_docs else None
                mapped_msgs = alias_mapper.merge(self.raw_msgs, self.mapping) if self.raw_msgs else None
                mapped_doc_details = alias_mapper.merge(self.raw_doc_details, self.mapping) if self.raw_doc_details else None
                mapped_msg_details = alias_mapper.merge(self.raw_msg_details, self.mapping) if self.raw_msg_details else None

            self.signals.progress.emit(60)
            scores = []
            if aggregator:
                scores = aggregator.aggregate(
                    git=mapped_git,
                    docs=mapped_docs,
                    msgs=mapped_msgs,
                    weights=self.weights,
                    doc_details=mapped_doc_details,
                    msg_details=mapped_msg_details,
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
        self._raw_doc_details = None
        self._raw_msg_details = None
        self._current_weights = None

    def reset(self) -> None:
        """이전 분석 결과 데이터를 초기화한다."""
        self._raw_git = None
        self._raw_docs = None
        self._raw_msgs = None
        self._raw_doc_details = None
        self._raw_msg_details = None
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
        
        worker = MergeWorker(self._raw_git, self._raw_docs, self._raw_msgs, self._current_weights, mapping,
                             self._raw_doc_details, self._raw_msg_details)
        worker.signals.progress.connect(self.progress.emit)
        worker.signals.completed.connect(self._on_merge_worker_completed)
        worker.signals.failed.connect(self._on_worker_failed)
        self.thread_pool.start(worker)
        
    def _on_analysis_worker_completed(self, result_tuple: tuple) -> None:
        scores, git_data, doc_data, msg_data, weights, doc_details, msg_details = result_tuple
        self._raw_git = git_data
        self._raw_docs = doc_data
        self._raw_msgs = msg_data
        self._raw_doc_details = doc_details
        self._raw_msg_details = msg_details
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

        self.tracker = NormalizedSignalsTracker() if NormalizedSignalsTracker else None
        self.alias_extractor = AliasExtractor() if AliasExtractor else None
        self._last_scores = []

        # 입력 상태
        self._doc_paths: List[str] = []
        self._git_path: str = ""
        self._msg_path: str = ""
        self._weights: Dict[str, float] = {"git": 0.4, "doc": 0.4, "msg": 0.2}

        # SubmitScreen 시그널 연결
        submit = main_window.submit
        submit.documents_dropped.connect(self._on_docs_dropped)
        submit.git_repo_chosen.connect(self._on_git_chosen)
        submit.messenger_dropped.connect(self._on_msg_dropped)
        submit.analysis_panel.weights_changed.connect(self._on_weights_changed)
        submit.analysis_panel.analyze_clicked.connect(self._on_analyze_clicked)

        # ResultScreen 시그널 연결
        result = main_window.result
        result.merge_requested.connect(self.on_merge_requested)
        result.new_analysis_requested.connect(self.on_new_analysis_requested)
        result.signal_dismissed.connect(self.on_signal_dismissed)

        # 리포트 저장 — 메뉴(파일>리포트 저장)와 결과 화면 [리포트 저장] 버튼 양쪽에서 동일 흐름
        main_window.save_report_requested.connect(self._on_save_report_requested)
        if hasattr(result, "save_report_requested"):
            result.save_report_requested.connect(self._on_save_report_requested)

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
        self.main_window.set_save_enabled(False)  # 제출 화면 복귀 시 비활성
        if self.tracker:
            self.tracker.clear()
        self._last_scores = []
        
        # Controller 내부 캐시 및 Orchestrator 상태 초기화 (버그 수정)
        self._doc_paths = []
        self._git_path = ""
        self._msg_path = ""
        self.orchestrator.reset()
        
        self.main_window.submit.reset()
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
        self.main_window.set_save_enabled(bool(scores))  # 결과 존재 시에만 활성
        
    def _render_results(self) -> None:
        scores = self._last_scores
        if self.tracker:
            scores = self.tracker.apply(self._last_scores)
            
        score_dicts = [dataclasses.asdict(s) for s in scores]
        missing = self._detect_missing(scores)
        self.main_window.result.render(score_dicts, missing)
        
        if self.alias_extractor:
            identifiers = self.alias_extractor.extract_identifiers(
                self.orchestrator._raw_git,
                self.orchestrator._raw_docs,
                self.orchestrator._raw_msgs
            )
            mapping = self.alias_extractor.suggest_mapping(identifiers)
            if hasattr(self.main_window.result, "set_suggested_mapping"):
                self.main_window.result.set_suggested_mapping(mapping)

    def on_analysis_failed(self, message: str) -> None:
        print(f"FATAL ERROR EMITTED: {message}")
        self.main_window.show_submit()
        # self.main_window.show_error(message)

    def on_progress(self, val: int) -> None:
        pass

    # ── 입력 캡처 ──────────────────────────────────────────────────────────
    def _on_docs_dropped(self, paths: List[str]) -> None:
        self._doc_paths = paths

    def _on_git_chosen(self, path: str) -> None:
        self._git_path = path

    def _on_msg_dropped(self, path: str) -> None:
        self._msg_path = path

    # ── 가중치 검증 ────────────────────────────────────────────────────────
    def _on_weights_changed(self, view_weights: dict) -> None:
        model_weights = {k[2:]: v for k, v in view_weights.items()}  # w_git→git
        total = sum(model_weights.values())
        panel = self.main_window.submit.analysis_panel
        if abs(total - 1.0) < 1e-4:
            self._weights = model_weights
            panel.set_analyze_enabled(True)
            panel.set_weight_warning(None)
        elif total == 0.0:
            panel.set_analyze_enabled(False)
            panel.set_weight_warning(None)
        else:
            panel.set_analyze_enabled(False)
            panel.set_weight_warning(f"가중치 합계가 100%여야 합니다 (현재 {round(total * 100)}%)")

    def _on_analyze_clicked(self) -> None:
        self.main_window.set_save_enabled(False)  # 로딩 중 비활성
        
        if not self._doc_paths and not self._git_path and not self._msg_path:
            from qce.model.business.cache_manager import CacheManager
            from qce.model.business.BusinessLogic import MemberScore
            cache_mgr = CacheManager()
            cached_data = cache_mgr.load()
            if cached_data and "scores" in cached_data:
                self._last_scores = [MemberScore(**s) for s in cached_data["scores"]]
                self._render_results()
                self.main_window.show_result()
                self.main_window.set_save_enabled(True)
                return

        config = {
            "doc_paths": self._doc_paths,
            "git_path": self._git_path,
            "msg_path": self._msg_path,
            "weights": self._weights,
        }
        self.main_window.show_loading()
        self.orchestrator.start_analysis(config)

    # ── 결측 판정 ──────────────────────────────────────────────────────────
    def _detect_missing(self, scores: list) -> set:
        if not scores:
            return set()
        missing: set = set()
        if all(s.git_score == 0.0 for s in scores):
            missing.add("Git")
        if all(s.doc_score == 0.0 for s in scores):
            missing.add("문서")
        if all(s.msg_score == 0.0 for s in scores):
            missing.add("메신저")
        return missing

    # ── 리포트 저장 ────────────────────────────────────────────────────────
    def _do_save(self, path: str, fmt: str) -> None:
        import os
        from qce.model.business.report_exporter import ReportExporter
        if not os.path.splitext(path)[1]:
            path = f"{path}.{fmt}"
        missing = self._detect_missing(self._last_scores)
        ReportExporter().save(path, self._last_scores, missing)

    def _on_save_report_requested(self) -> None:
        from qce.view.dialogs.save_report_dialog import SaveReportDialog
        dialog = SaveReportDialog(self.main_window)
        dialog.path_chosen.connect(self._do_save)
        dialog.prompt(self.main_window)
