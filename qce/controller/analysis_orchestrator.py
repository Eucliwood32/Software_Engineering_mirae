"""NFR-1.1, NFR-1.2 AnalysisOrchestrator: 비동기 분석 파이프라인 관리."""
from __future__ import annotations
import dataclasses
import traceback
from PyQt6.QtCore import QObject, QRunnable, QThreadPool, pyqtSignal

from qce.model.parsing.document_parser import DocumentParser
from qce.model.parsing.git_analyzer import GitAnalyzer
from qce.model.parsing.messenger_parser import MessengerParser
from qce.model.parsing.stopword_filter import StopwordFilter
from qce.model.business.contribution_aggregator import ContributionAggregator
from qce.model.business.cache_manager import CacheManager


class _AnalysisSignals(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(tuple)   # (list[MemberScore], git, docs, msgs, weights)
    failed = pyqtSignal(str)


class _AnalysisWorker(QRunnable):
    """1차 분석 Worker: 파싱 → 집계. QThreadPool에서 실행."""

    def __init__(self, config: dict) -> None:
        super().__init__()
        self.config = config
        self.signals = _AnalysisSignals()

    def run(self) -> None:
        try:
            self.signals.progress.emit(5)

            # 1. OOXML 파싱 (FR-1.1)
            doc_data: dict | None = None
            if doc_paths := self.config.get("doc_paths"):
                doc_data = {}
                parser = DocumentParser()
                for path in doc_paths:
                    for author, chars in parser.parse(path).items():
                        doc_data[author] = doc_data.get(author, 0) + chars
            self.signals.progress.emit(30)

            # 2. Git 분석 (FR-2.1)
            git_data: dict | None = None
            if git_path := self.config.get("git_path"):
                git_data = GitAnalyzer().analyze(git_path)
            self.signals.progress.emit(55)

            # 3. 메신저 파싱 + 불용어 처리 (FR-3.1, FR-3.3)
            msg_data: dict | None = None
            if msg_path := self.config.get("msg_path"):
                parsed = MessengerParser().parse(msg_path)
                filtered = StopwordFilter().count_valid_messages(parsed.records)
                all_authors = {r.author for r in parsed.records}
                msg_data = {a: filtered.get(a, 0) for a in all_authors}
            self.signals.progress.emit(75)

            # 4. 집계
            weights = self.config.get("weights", {"git": 0.4, "doc": 0.4, "msg": 0.2})
            scores = ContributionAggregator().aggregate(
                git=git_data, docs=doc_data, msgs=msg_data, weights=weights
            )

            # 5. 캐시 저장 (NFR-2.3)
            if scores:
                CacheManager().save({"scores": [dataclasses.asdict(s) for s in scores]})

            self.signals.progress.emit(100)
            self.signals.completed.emit((scores, git_data, doc_data, msg_data, weights))

        except Exception as e:
            self.signals.failed.emit(f"{e}\n{traceback.format_exc()}")


class _MergeSignals(QObject):
    progress = pyqtSignal(int)
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)


class _MergeWorker(QRunnable):
    """병합 재집계 Worker: 파싱 생략, AliasMapper → ContributionAggregator 재호출."""

    def __init__(self, git, docs, msgs, weights: dict, mapping: dict) -> None:
        super().__init__()
        self.git = git
        self.docs = docs
        self.msgs = msgs
        self.weights = weights
        self.mapping = mapping
        self.signals = _MergeSignals()

    def run(self) -> None:
        try:
            from qce.model.business.alias_mapper import AliasMapper
            from qce.model.types import CommitStats
            self.signals.progress.emit(20)

            mapper = AliasMapper()

            merged_git: dict | None = None
            if self.git is not None:
                raw = {k: {"additions": v.additions, "commits": v.commits,
                           "deletions": v.deletions}
                       for k, v in self.git.items()}
                mapped = mapper.merge(raw, self.mapping)
                merged_git = {
                    person: CommitStats(
                        commits=vals.get("commits", 0),
                        additions=vals.get("additions", 0),
                        deletions=vals.get("deletions", 0),
                    )
                    for person, vals in mapped.items()
                }

            merged_doc: dict | None = None
            if self.docs is not None:
                mapped = mapper.merge({k: {"v": v} for k, v in self.docs.items()},
                                      self.mapping)
                merged_doc = {k: vals["v"] for k, vals in mapped.items()}

            merged_msg: dict | None = None
            if self.msgs is not None:
                mapped = mapper.merge({k: {"v": v} for k, v in self.msgs.items()},
                                      self.mapping)
                merged_msg = {k: vals["v"] for k, vals in mapped.items()}

            self.signals.progress.emit(60)
            scores = ContributionAggregator().aggregate(
                git=merged_git, docs=merged_doc, msgs=merged_msg, weights=self.weights
            )
            if scores:
                CacheManager().save({"scores": [dataclasses.asdict(s) for s in scores]})

            self.signals.progress.emit(100)
            self.signals.completed.emit(scores)
        except Exception as e:
            self.signals.failed.emit(str(e))


class AnalysisOrchestrator(QObject):
    """NFR-1.2: is_analyzing 가드로 중복 실행 차단."""

    progress = pyqtSignal(int)
    completed = pyqtSignal(list)
    failed = pyqtSignal(str)

    def __init__(self) -> None:
        super().__init__()
        self.is_analyzing: bool = False
        self._pool = QThreadPool.globalInstance()
        self._raw_git = None
        self._raw_docs = None
        self._raw_msgs = None
        self._current_weights: dict | None = None

    def start_analysis(self, config: dict) -> None:
        if self.is_analyzing:
            return
        self.is_analyzing = True
        worker = _AnalysisWorker(config)
        worker.signals.progress.connect(self.progress.emit)
        worker.signals.completed.connect(self._on_analysis_done)
        worker.signals.failed.connect(self._on_failed)
        self._pool.start(worker)

    def start_merge_reaggregation(self, mapping: dict) -> None:
        if self.is_analyzing:
            return
        self.is_analyzing = True
        worker = _MergeWorker(
            self._raw_git, self._raw_docs, self._raw_msgs,
            self._current_weights or {}, mapping,
        )
        worker.signals.progress.connect(self.progress.emit)
        worker.signals.completed.connect(self._on_merge_done)
        worker.signals.failed.connect(self._on_failed)
        self._pool.start(worker)

    def _on_analysis_done(self, result: tuple) -> None:
        scores, git, docs, msgs, weights = result
        self._raw_git, self._raw_docs, self._raw_msgs = git, docs, msgs
        self._current_weights = weights
        self.is_analyzing = False
        self.completed.emit(scores)

    def _on_merge_done(self, scores: list) -> None:
        self.is_analyzing = False
        self.completed.emit(scores)

    def _on_failed(self, msg: str) -> None:
        self.is_analyzing = False
        self.failed.emit(msg)
