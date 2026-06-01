"""FR-5.5 — SubmitScreen UI (L3)."""
from __future__ import annotations

import os

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


def test_folder_drop_expands(qtbot, tmp_path):
    """폴더를 드롭하면 내부 문서·.txt를 펼치고 .git 폴더는 Git 저장소로 인식한다.
    Git 저장소 내부 파일(work.txt)은 수집 대상에서 제외된다."""
    proj = tmp_path / "proj"
    (proj / "docs").mkdir(parents=True)
    (proj / "docs" / "a.docx").write_text("x", encoding="utf-8")
    (proj / "docs" / "b.pptx").write_text("x", encoding="utf-8")
    (proj / "chat.txt").write_text("x", encoding="utf-8")
    (proj / "repo" / ".git").mkdir(parents=True)      # Git 저장소로 위장
    (proj / "repo" / "work.txt").write_text("x", encoding="utf-8")

    w = SubmitScreen()
    qtbot.addWidget(w)
    docs_seen, msgs_seen, git_seen = [], [], []
    w.documents_dropped.connect(docs_seen.append)
    w.messenger_dropped.connect(msgs_seen.append)
    w.git_repo_chosen.connect(git_seen.append)

    w._handle_dropped_paths([str(proj)])

    assert {os.path.basename(p) for p in docs_seen[0]} == {"a.docx", "b.pptx"}
    assert [os.path.basename(m) for m in msgs_seen] == ["chat.txt"]   # repo/work.txt 제외
    assert [os.path.basename(g) for g in git_seen] == ["repo"]


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


def test_dropzone_shows_hint_when_empty(qtbot):                 # §6.9 v1.6
    w = SubmitScreen()
    qtbot.addWidget(w)
    assert "끌어다 놓으세요" in w._dropzone.text()
    assert w.loaded_files() == []


def test_dropzone_lists_filenames(qtbot):                       # §6.9 v1.6
    w = SubmitScreen()
    qtbot.addWidget(w)
    w._handle_dropped_paths(["/in/report.docx", "/in/chat.txt"])
    text = w._dropzone.text()
    assert "report.docx" in text
    assert "chat.txt" in text          # basename only, no path
    assert "/in/" not in text
    assert "끌어다 놓으세요" not in text
    assert w.loaded_files() == ["report.docx", "chat.txt"]


def test_dropzone_reverts_to_hint_after_reset(qtbot):           # §6.9 v1.6
    w = SubmitScreen()
    qtbot.addWidget(w)
    w._handle_dropped_paths(["a.docx"])
    assert "a.docx" in w._dropzone.text()
    w.reset()
    assert "끌어다 놓으세요" in w._dropzone.text()
    assert w.loaded_files() == []


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
