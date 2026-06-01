"""L2 통합: AppController View Signal 배선 + 라우팅 검증 (C-4).

실제 MainWindow를 붙이고 View Signal을 발행해 Controller 핸들러가 상태를 갱신하고
화면 전환/Orchestrator 위임을 수행하는지 확인한다. Orchestrator의 실제 분석 실행은
monkeypatch로 가로채 호출 인자만 검증한다(무거운 파이프라인 배제).
"""
from __future__ import annotations

import pytest

from qce.view.main_window import MainWindow
from qce.controller.analysis_orchestrator import AnalysisOrchestrator
from qce.controller.app_controller import AppController
from qce.model.types import MemberScore


@pytest.fixture
def ctx(qtbot, monkeypatch):
    """MainWindow + Orchestrator + AppController 조립. Orchestrator 실행은 가로챔."""
    mw = MainWindow()
    qtbot.addWidget(mw)
    orch = AnalysisOrchestrator()

    calls = {"analysis": [], "merge": []}
    monkeypatch.setattr(orch, "start_analysis", lambda cfg: calls["analysis"].append(cfg))
    monkeypatch.setattr(orch, "start_merge_reaggregation", lambda m: calls["merge"].append(m))

    ctrl = AppController(mw, orch)
    return ctrl, mw, orch, calls


# ── SubmitScreen Signal → 상태 캡처 ──────────────────────────────────────

def test_source_signals_captured(ctx):
    ctrl, mw, _, _ = ctx
    mw.submit.documents_dropped.emit(["a.docx", "b.pptx"])
    mw.submit.git_repo_chosen.emit("/repo")
    mw.submit.messenger_dropped.emit("chat.txt")

    assert ctrl._doc_paths == ["a.docx", "b.pptx"]
    assert ctrl._git_path == "/repo"
    assert ctrl._msg_path == "chat.txt"


def test_weights_valid_enables_analyze(ctx):
    """View는 w_git/w_doc/w_msg 키로 발행 → Controller가 정규화·검증."""
    ctrl, mw, _, _ = ctx
    mw.submit.analysis_panel.weights_changed.emit({"w_git": 0.4, "w_doc": 0.4, "w_msg": 0.2})
    assert mw.submit.analysis_panel.analyze_enabled() is True
    assert mw.submit.analysis_panel.weight_warning_text() == ""
    # Controller 내부는 Model 키(git/doc/msg)로 정규화 저장
    assert ctrl._weights == {"git": 0.4, "doc": 0.4, "msg": 0.2}


def test_weights_invalid_disables_and_warns(ctx):
    ctrl, mw, _, _ = ctx
    mw.submit.analysis_panel.weights_changed.emit({"w_git": 0.5, "w_doc": 0.5, "w_msg": 0.5})
    assert mw.submit.analysis_panel.analyze_enabled() is False
    assert "100%" in mw.submit.analysis_panel.weight_warning_text()


def test_preset_apply_drives_weights_and_validation(ctx):
    """프리셋 적용(버튼 클릭=apply_preset) → weights_changed 경유로 검증까지 수행."""
    ctrl, mw, _, _ = ctx
    panel = mw.submit.analysis_panel
    panel.apply_preset("개발 중심")        # View가 버튼 클릭 시 직접 호출하는 경로

    w = panel.current_weights()             # View 키(w_*)
    assert abs(w["w_git"] - 0.60) < 1e-6
    assert abs(w["w_doc"] - 0.25) < 1e-6
    assert abs(w["w_msg"] - 0.15) < 1e-6
    # 합 1.0이므로 weights_changed → _on_weights_changed가 분석 버튼을 활성화
    assert panel.analyze_enabled() is True
    # Controller는 Model 키(git/doc/msg)로 정규화 저장
    assert ctrl._weights == {"git": 0.60, "doc": 0.25, "msg": 0.15}


# ── analyze_clicked → Orchestrator 위임 + 로딩 전환 ──────────────────────

def test_analyze_clicked_delegates_with_config(ctx):
    ctrl, mw, _, calls = ctx
    mw.submit.documents_dropped.emit(["d.docx"])
    mw.submit.git_repo_chosen.emit("/r")
    mw.submit.messenger_dropped.emit("c.txt")
    # View 발행 키(w_*) → Controller가 Model 키로 정규화해 config에 실어야 함
    mw.submit.analysis_panel.weights_changed.emit({"w_git": 0.4, "w_doc": 0.4, "w_msg": 0.2})

    mw.submit.analysis_panel.analyze_clicked.emit()

    assert len(calls["analysis"]) == 1
    cfg = calls["analysis"][0]
    assert cfg["doc_paths"] == ["d.docx"]
    assert cfg["git_path"] == "/r"
    assert cfg["msg_path"] == "c.txt"
    assert cfg["weights"] == {"git": 0.4, "doc": 0.4, "msg": 0.2}
    assert mw.current_screen() is mw.loading


# ── ResultScreen Signal → 위임/전환 ──────────────────────────────────────

def test_merge_requested_delegates(ctx):
    ctrl, mw, _, calls = ctx
    mapping = {"alice@t.com": "Alice", "Alice": "Alice"}
    mw.result.merge_requested.emit(mapping)
    assert calls["merge"] == [mapping]
    assert mw.current_screen() is mw.loading


def test_new_analysis_requested_resets_state(ctx):
    ctrl, mw, orchestrator, _ = ctx
    # 가짜 캐시 주입
    ctrl._doc_paths = ["fake.docx"]
    ctrl._git_path = "fake_git"
    ctrl._msg_path = "fake.txt"
    orchestrator._raw_git = {"user": 1}
    
    mw.result.new_analysis_requested.emit()
    
    # 내부 상태가 리셋되었는지 확인
    assert ctrl._doc_paths == []
    assert ctrl._git_path == ""
    assert ctrl._msg_path == ""
    assert orchestrator._raw_git is None
    
    # 화면 전환
    assert mw.current_screen() is mw.submit


# ── Orchestrator 콜백 → View 렌더/전환 ───────────────────────────────────

def test_completed_renders_and_shows_result(ctx):
    ctrl, mw, orch, _ = ctx
    scores = [
        MemberScore("Alice", 0.8, 0.6, 0.4, 0.66, 800, 1500, 30, False, []),
        MemberScore("Bob", 0.2, 0.1, 0.9, 0.34, 200, 300, 90, True, ["CAPPING"]),
    ]
    orch.completed.emit(scores)
    assert ctrl._last_scores == scores
    assert mw.current_screen() is mw.result


def test_failed_returns_to_submit(ctx):
    ctrl, mw, orch, _ = ctx
    mw.show_loading()
    orch.failed.emit("boom")
    assert mw.current_screen() is mw.submit


# ── 결측 소스 판정 ───────────────────────────────────────────────────────

def test_detect_missing_all_zero_git():
    ctrl = AppController.__new__(AppController)   # __init__ 우회(순수 로직 검증)
    scores = [
        MemberScore("A", 0.0, 0.5, 0.5, 0.4, 0, 100, 10, False, []),
        MemberScore("B", 0.0, 0.7, 0.3, 0.4, 0, 200, 5, False, []),
    ]
    assert ctrl._detect_missing(scores) == {"Git"}


def test_detect_missing_empty():
    ctrl = AppController.__new__(AppController)
    assert ctrl._detect_missing([]) == set()


# ── 리포트 저장 ──────────────────────────────────────────────────────────

def test_do_save_writes_file(ctx, tmp_path):
    ctrl, mw, _, _ = ctx
    ctrl._last_scores = [MemberScore("Alice", 0.8, 0.6, 0.4, 0.66, 800, 1500, 30, False, [])]
    path = str(tmp_path / "out.md")
    ctrl._do_save(path, "md")
    assert (tmp_path / "out.md").read_text(encoding="utf-8").find("Alice") >= 0


def test_save_report_requested_invokes_dialog(ctx, monkeypatch, tmp_path):
    ctrl, mw, _, _ = ctx
    ctrl._last_scores = [MemberScore("Alice", 0.8, 0.6, 0.4, 0.66, 800, 1500, 30, False, [])]
    out = str(tmp_path / "r.csv")

    # SaveReportDialog.prompt가 즉시 path_chosen을 발행하도록 가로챔
    import qce.view.dialogs.save_report_dialog as srd

    def fake_prompt(self, parent=None):
        self.path_chosen.emit(out, "csv")

    monkeypatch.setattr(srd.SaveReportDialog, "prompt", fake_prompt)
    mw.save_report_requested.emit()

    assert (tmp_path / "r.csv").exists()
