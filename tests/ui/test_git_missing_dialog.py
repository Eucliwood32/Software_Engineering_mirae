"""FR-2.2 — GitMissingDialog UI (L3)."""
from __future__ import annotations

import webbrowser

from qce.view.dialogs.git_missing_dialog import GitMissingDialog


def _all_label_text(dlg) -> str:
    from PyQt6.QtWidgets import QLabel

    return "\n".join(lbl.text() for lbl in dlg.findChildren(QLabel))


def test_dialog_message(qtbot):                                 # TC-FR-2.2-06
    dlg = GitMissingDialog()
    qtbot.addWidget(dlg)
    assert "Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다." in _all_label_text(dlg)


def test_dialog_path_hint(qtbot):                               # TC-FR-2.2-08
    dlg = GitMissingDialog()
    qtbot.addWidget(dlg)
    assert "PATH" in _all_label_text(dlg)


def test_dialog_opens_link(qtbot, monkeypatch):                 # TC-FR-2.2-07
    calls = []
    monkeypatch.setattr(webbrowser, "open", lambda u: calls.append(u))
    dlg = GitMissingDialog()
    qtbot.addWidget(dlg)
    dlg.download_button.click()
    assert calls == ["https://git-scm.com/download/win"]
