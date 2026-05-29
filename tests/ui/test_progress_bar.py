"""NFR-1.1 — ProgressBar 표시·갱신·종료 (L3)."""
from __future__ import annotations

from qce.view.panels.progress_bar import ProgressBar


def test_start_shows_at_zero(qtbot):
    w = ProgressBar()
    qtbot.addWidget(w)
    w.start()
    assert w.is_running()
    assert w.value() == 0


def test_set_value(qtbot):
    w = ProgressBar()
    qtbot.addWidget(w)
    w.start()
    w.set_value(50)
    assert w.value() == 50


def test_set_value_clamped(qtbot):
    w = ProgressBar()
    qtbot.addWidget(w)
    w.set_value(150)
    assert w.value() == 100
    w.set_value(-10)
    assert w.value() == 0


def test_finish_hides(qtbot):
    w = ProgressBar()
    qtbot.addWidget(w)
    w.start()
    w.finish()
    assert not w.is_running()
