"""FR-5.3 — WarningBanner UI 동작 (L3)."""
from __future__ import annotations

from qce.view.contract import SRC_GIT, SRC_MSG
from qce.view.panels.warning_banner import WarningBanner


def test_banner_shows_missing_messenger(qtbot):                 # TC-FR-5.3-01
    w = WarningBanner()
    qtbot.addWidget(w)
    w.show_missing({SRC_MSG})
    assert w.is_banner_visible()
    assert "메신저" in w.current_text()


def test_banner_hidden_when_empty(qtbot):                       # TC-FR-5.3-05
    w = WarningBanner()
    qtbot.addWidget(w)
    w.show_missing(set())
    assert not w.is_banner_visible()
    assert w.current_text() == ""


def test_banner_multiple_sources(qtbot):                        # TC-FR-5.3-04
    w = WarningBanner()
    qtbot.addWidget(w)
    w.show_missing({SRC_GIT, SRC_MSG})
    text = w.current_text()
    assert "Git" in text and "메신저" in text
    assert len(text.splitlines()) == 2


def test_banner_clear(qtbot):
    w = WarningBanner()
    qtbot.addWidget(w)
    w.show_missing({SRC_MSG})
    w.clear()
    assert not w.is_banner_visible()
