"""FR-5.2 — SaveReportDialog 경로·형식 도출 (L3)."""
from __future__ import annotations

from PyQt6.QtWidgets import QFileDialog

from qce.view.dialogs.save_report_dialog import SaveReportDialog


def test_fmt_from_extension():
    d = SaveReportDialog()
    assert d._fmt_for("report.md") == "md"
    assert d._fmt_for("report.csv") == "csv"


def test_fmt_from_filter_when_no_ext():
    d = SaveReportDialog()
    assert d._fmt_for("report", "CSV (*.csv)") == "csv"
    assert d._fmt_for("report", "Markdown (*.md)") == "md"


def test_handle_result_emits(qtbot):
    d = SaveReportDialog()
    with qtbot.waitSignal(d.path_chosen, timeout=1000) as blocker:
        d._handle_result("out.csv", "CSV (*.csv)")
    assert blocker.args == ["out.csv", "csv"]


def test_prompt_emits_on_selection(qtbot, monkeypatch):         # TC-FR-5.2-05 (경로 확정)
    d = SaveReportDialog()
    monkeypatch.setattr(
        QFileDialog, "getSaveFileName",
        staticmethod(lambda *a, **k: ("/tmp/report.md", "Markdown (*.md)")),
    )
    with qtbot.waitSignal(d.path_chosen, timeout=1000) as blocker:
        d.prompt(None)
    assert blocker.args == ["/tmp/report.md", "md"]
