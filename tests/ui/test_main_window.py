"""§6.1 — MainWindow 셸·Drag&Drop 분기·상태바 (L3)."""
from __future__ import annotations

from qce.view.main_window import MainWindow


def test_classify_paths():
    docs, msgs = MainWindow._classify_paths(
        ["a.docx", "b.pptx", "c.hwpx", "chat.txt", "ignore.png"]
    )
    assert set(docs) == {"a.docx", "b.pptx", "c.hwpx"}
    assert msgs == ["chat.txt"]


def test_documents_dropped_signal(qtbot):                       # FR-1.1
    w = MainWindow()
    qtbot.addWidget(w)
    with qtbot.waitSignal(w.documents_dropped, timeout=1000) as blocker:
        w._handle_dropped_paths(["a.docx", "b.pptx"])
    assert blocker.args[0] == ["a.docx", "b.pptx"]


def test_messenger_dropped_signal(qtbot):                       # FR-3.1
    w = MainWindow()
    qtbot.addWidget(w)
    with qtbot.waitSignal(w.messenger_dropped, timeout=1000) as blocker:
        w._handle_dropped_paths(["chat.txt"])
    assert blocker.args[0] == "chat.txt"


def test_flash_status(qtbot):                                   # FR-5.2/NFR-2.4
    w = MainWindow()
    qtbot.addWidget(w)
    w.flash_status("저장 완료", 3000)
    assert w.statusBar().currentMessage() == "저장 완료"


def test_mixed_drop_routes_both(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    docs_seen = []
    msgs_seen = []
    w.documents_dropped.connect(docs_seen.append)
    w.messenger_dropped.connect(msgs_seen.append)
    w._handle_dropped_paths(["report.docx", "chat.txt"])
    assert docs_seen == [["report.docx"]]
    assert msgs_seen == ["chat.txt"]
