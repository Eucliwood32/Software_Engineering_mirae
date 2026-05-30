"""FR-5.6 — LoadingScreen UI (L3)."""
from __future__ import annotations

from qce.view.panels.loading_screen import LoadingScreen


def test_start_shows_zero(qtbot):                               # TC-FR-5.6-01
    w = LoadingScreen()
    qtbot.addWidget(w)
    w.start()
    assert w.is_running()
    assert w.value() == 0


def test_set_value(qtbot):                                      # TC-FR-5.6-02
    w = LoadingScreen()
    qtbot.addWidget(w)
    w.start()
    w.set_value(60)
    assert w.value() == 60


def test_finish(qtbot):                                         # TC-FR-5.6-03
    w = LoadingScreen()
    qtbot.addWidget(w)
    w.start()
    w.finish()
    assert not w.is_running()
