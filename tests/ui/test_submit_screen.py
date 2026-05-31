"""FR-5.5 — SubmitScreen UI (L3)."""
from __future__ import annotations

from qce.view.panels.analysis_panel import AnalysisPanel
from qce.view.panels.submit_screen import SubmitScreen


def test_classify_paths():
    docs, msgs = SubmitScreen._classify_paths(
        ["a.docx", "b.pptx", "c.hwpx", "chat.txt", "ignore.png"]
    )
    assert set(docs) == {"a.docx", "b.pptx", "c.hwpx"}
    assert msgs == ["chat.txt"]


def test_documents_dropped(qtbot):                              # TC-FR-5.5-02
    w = SubmitScreen()
    qtbot.addWidget(w)
    with qtbot.waitSignal(w.documents_dropped, timeout=1000) as blocker:
        w._handle_dropped_paths(["a.docx", "b.pptx", "c.hwpx"])
    assert blocker.args[0] == ["a.docx", "b.pptx", "c.hwpx"]


def test_messenger_dropped(qtbot):                              # TC-FR-5.5-03
    w = SubmitScreen()
    qtbot.addWidget(w)
    with qtbot.waitSignal(w.messenger_dropped, timeout=1000) as blocker:
        w._handle_dropped_paths(["chat.txt"])
    assert blocker.args[0] == "chat.txt"


def test_mixed_drop(qtbot):
    w = SubmitScreen()
    qtbot.addWidget(w)
    docs_seen, msgs_seen = [], []
    w.documents_dropped.connect(docs_seen.append)
    w.messenger_dropped.connect(msgs_seen.append)
    w._handle_dropped_paths(["report.docx", "chat.txt"])
    assert docs_seen == [["report.docx"]]
    assert msgs_seen == ["chat.txt"]


def test_loaded_summary(qtbot):                                 # TC-FR-5.5-04
    w = SubmitScreen()
    qtbot.addWidget(w)
    w._handle_dropped_paths(["a.docx", "b.pptx", "c.hwpx"])
    assert "3" in w.loaded_summary()


def test_has_analysis_panel(qtbot):                             # TC-FR-5.5-05
    w = SubmitScreen()
    qtbot.addWidget(w)
    assert isinstance(w.analysis_panel, AnalysisPanel)
    w.analysis_panel.set_analyze_enabled(False)
    assert w.analysis_panel.analyze_enabled() is False


def test_reset_clears_counts(qtbot):
    p = SubmitScreen()
    qtbot.addWidget(p)
    p._handle_dropped_paths(["a.docx", "b.pptx", "c.txt"])
    assert p._doc_count == 2
    assert p._msg_count == 1
    assert "적재됨" in p.loaded_summary()
    
    p.reset()
    assert p._doc_count == 0
    assert p._msg_count == 0
    assert p.loaded_summary() == ""
