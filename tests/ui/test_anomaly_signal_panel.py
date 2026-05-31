"""FR-4.2/4.2b/4.2d — AnomalySignalPanel 카드 UI (L3)."""
from __future__ import annotations

from qce.view.panels.anomaly_signal_panel import AnomalySignalPanel


def _score(author, details):
    return {
        "author": author,
        "git_score": 0.5, "doc_score": 0.5, "msg_score": 0.5, "total_score": 0.5,
        "raw_additions": 0, "raw_chars": 0, "raw_messages": 0,
        "capping_applied": False, "signals": [],
        "signal_details": details,
    }


def test_empty_when_no_signals(qtbot):
    p = AnomalySignalPanel()
    qtbot.addWidget(p)
    p.render([_score("A", [])])
    assert p.card_count() == 0


def test_renders_card_per_detail(qtbot):
    p = AnomalySignalPanel()
    qtbot.addWidget(p)
    p.render([
        _score("A", [
            {"type": "CAPPING", "hash": "abc1234", "date": "2024-01-01", "additions": 2500},
            {"type": "ZSCORE", "metrics": ["git", "doc"]},
        ]),
        _score("B", [{"type": "EW-02", "date": "2024-01-05", "period_commits": 7, "baseline_avg": 2.2}]),
    ])
    assert p.card_count() == 3
    assert len(p.cards_of_type("CAPPING")) == 1
    assert len(p.cards_of_type("EW-02")) == 1
    assert len(p.cards_of_type("ZSCORE")) == 1


def test_dismiss_emits_signal_with_ref(qtbot):
    p = AnomalySignalPanel()
    qtbot.addWidget(p)
    p.render([_score("A", [
        {"type": "CAPPING", "hash": "abc1234", "date": "2024-01-01", "additions": 2500},
    ])])
    card = p.cards_of_type("CAPPING")[0]
    with qtbot.waitSignal(p.signal_dismissed, timeout=1000) as blocker:
        card._emit_dismiss()
    assert blocker.args == ["A", "CAPPING", "abc1234"]


def test_rerender_clears_previous_cards(qtbot):
    p = AnomalySignalPanel()
    qtbot.addWidget(p)
    p.render([_score("A", [{"type": "ZSCORE", "metrics": ["git", "doc"]}])])
    assert p.card_count() == 1
    p.render([_score("A", [])])      # 재렌더로 비워짐
    assert p.card_count() == 0
