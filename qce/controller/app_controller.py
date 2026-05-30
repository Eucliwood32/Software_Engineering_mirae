"""AppController: View ↔ Model 중재, 이벤트 라우팅 (C-4, Architecture Overview §5.4)."""
from __future__ import annotations
import dataclasses
from qce.controller.analysis_orchestrator import AnalysisOrchestrator
from qce.model.business.report_exporter import ReportExporter
from qce.model.business.weight_preset_manager import WeightPresetManager


class AppController:
    """View Signal을 구독하여 Orchestrator에 위임하고 결과를 View에 전달."""

    def __init__(self, main_window, orchestrator: AnalysisOrchestrator) -> None:
        self.main_window = main_window
        self.orchestrator = orchestrator
        self._last_scores: list = []
        self._missing: set[str] = set()
        self._doc_paths: list[str] = []
        self._git_path: str = ""
        self._msg_path: str = ""
        self._weights: dict = {"git": 0.4, "doc": 0.4, "msg": 0.2}
        self._preset_mgr = WeightPresetManager()

        # Orchestrator → Controller
        orchestrator.completed.connect(self.on_analysis_completed)
        orchestrator.failed.connect(self.on_analysis_failed)
        orchestrator.progress.connect(self.on_progress)

        # SubmitScreen → Controller
        s = main_window.submit
        s.documents_dropped.connect(self._on_docs)
        s.git_repo_chosen.connect(self._on_git)
        s.messenger_dropped.connect(self._on_msg)
        s.analysis_panel.analyze_clicked.connect(self._on_analyze_clicked)
        s.analysis_panel.weights_changed.connect(self._on_weights_changed)
        # preset_chosen은 View가 apply_preset 내부에서 발행하는 알림이며,
        # apply_preset이 weights_changed도 함께 발행하므로 검증은 그 경로로 처리된다.
        # (preset_chosen → apply_preset 재호출은 무한 재귀를 유발하므로 연결하지 않는다.)

        # ResultScreen → Controller
        r = main_window.result
        r.merge_requested.connect(self._on_merge)
        r.new_analysis_requested.connect(main_window.show_submit)

        # MainWindow → Controller
        main_window.save_report_requested.connect(self._on_save_report)

    # ── SubmitScreen 핸들러 ──────────────────────────────────────────────

    def _on_docs(self, paths: list[str]) -> None:
        self._doc_paths = paths

    def _on_git(self, path: str) -> None:
        self._git_path = path

    def _on_msg(self, path: str) -> None:
        self._msg_path = path

    @staticmethod
    def _norm_weights(weights: dict) -> dict:
        """View(w_git/w_doc/w_msg) ↔ Model(git/doc/msg) 키 정규화 (C-4 중재)."""
        return {
            "git": weights.get("w_git", weights.get("git", 0.0)),
            "doc": weights.get("w_doc", weights.get("doc", 0.0)),
            "msg": weights.get("w_msg", weights.get("msg", 0.0)),
        }

    def _on_weights_changed(self, weights: dict) -> None:
        self._weights = self._norm_weights(weights)
        valid = self._preset_mgr.validate_sum(
            self._weights["git"], self._weights["doc"], self._weights["msg"]
        )
        panel = self.main_window.submit.analysis_panel
        panel.set_analyze_enabled(valid)
        panel.set_weight_warning(
            None if valid
            else f"가중치 합계가 1.00이어야 합니다. 현재: {sum(self._weights.values()):.2f}"
        )

    def _on_analyze_clicked(self) -> None:
        config = {
            "doc_paths": self._doc_paths,
            "git_path": self._git_path,
            "msg_path": self._msg_path,
            "weights": self._weights,
        }
        self.main_window.show_loading()
        self.orchestrator.start_analysis(config)

    # ── ResultScreen 핸들러 ─────────────────────────────────────────────

    def _on_merge(self, mapping: dict) -> None:
        self.main_window.show_loading()
        self.orchestrator.start_merge_reaggregation(mapping)

    # ── Orchestrator 콜백 ───────────────────────────────────────────────

    def on_analysis_completed(self, scores: list) -> None:
        self._last_scores = scores
        score_dicts = [dataclasses.asdict(s) for s in scores]
        self._missing = self._detect_missing(scores)
        self.main_window.result.render(score_dicts, self._missing)
        self.main_window.show_result()

    def on_analysis_failed(self, _message: str) -> None:
        self.main_window.show_submit()

    def on_progress(self, _val: int) -> None:
        pass

    # ── 리포트 저장 ─────────────────────────────────────────────────────

    def _on_save_report(self) -> None:
        from qce.view.dialogs.save_report_dialog import SaveReportDialog
        dlg = SaveReportDialog()
        dlg.path_chosen.connect(self._do_save)
        dlg.prompt(self.main_window)

    def _do_save(self, path: str, _fmt: str) -> None:
        try:
            ReportExporter().save(path, self._last_scores, self._missing)
            self.main_window.flash_status(f"저장 완료: {path}", 3000)
        except Exception as e:
            print(f"[ReportExporter] save failed: {e}")

    # ── 결측 소스 판정 ──────────────────────────────────────────────────

    def _detect_missing(self, scores: list) -> set[str]:
        if not scores:
            return set()
        missing = set()
        if all(s.git_score == 0.0 for s in scores):
            missing.add("Git")
        if all(s.doc_score == 0.0 for s in scores):
            missing.add("문서")
        if all(s.msg_score == 0.0 for s in scores):
            missing.add("메신저")
        return missing
