"""FR-4.2c NormalizedSignalsTracker 단위 테스트 — 신호 예외(정상 표시) 상태."""
from qce.model.business.normalized_signals_tracker import NormalizedSignalsTracker
from qce.model.types import MemberScore


def _score(author="A", signals=None, details=None):
    return MemberScore(
        author, 0.5, 0.5, 0.5, 0.5, 100, 100, 100, True,
        signals or [], details or [],
    )


def test_dismiss_and_query():
    t = NormalizedSignalsTracker()
    assert t.is_dismissed("A", "CAPPING", "abc1234") is False
    t.dismiss("A", "CAPPING", "abc1234")
    assert t.is_dismissed("A", "CAPPING", "abc1234") is True
    assert t.dismissed_count() == 1


def test_restore():
    t = NormalizedSignalsTracker()
    t.dismiss("A", "ZSCORE")
    t.restore("A", "ZSCORE")
    assert t.is_dismissed("A", "ZSCORE") is False


def test_clear():
    t = NormalizedSignalsTracker()
    t.dismiss("A", "CAPPING", "h1")
    t.dismiss("B", "EW-02", "2024-01-01")
    t.clear()
    assert t.dismissed_count() == 0


def test_ref_of_per_type():
    assert NormalizedSignalsTracker.ref_of({"type": "CAPPING", "hash": "deadbee"}) == "deadbee"
    assert NormalizedSignalsTracker.ref_of({"type": "EW-02", "date": "2024-01-01"}) == "2024-01-01"
    assert NormalizedSignalsTracker.ref_of({"type": "ZSCORE", "metrics": ["git"]}) == ""


def test_filter_details_removes_dismissed():
    t = NormalizedSignalsTracker()
    details = [
        {"type": "CAPPING", "hash": "h1", "date": "d", "additions": 2000},
        {"type": "CAPPING", "hash": "h2", "date": "d", "additions": 3000},
    ]
    t.dismiss("A", "CAPPING", "h1")
    kept = t.filter_details("A", details)
    assert len(kept) == 1
    assert kept[0]["hash"] == "h2"


def test_apply_drops_signal_label_when_all_details_dismissed():
    s = _score(
        author="A",
        signals=["CAPPING"],
        details=[{"type": "CAPPING", "hash": "h1", "date": "d", "additions": 2000}],
    )
    t = NormalizedSignalsTracker()
    t.dismiss("A", "CAPPING", "h1")
    out = t.apply([s])
    assert out[0].signal_details == []
    assert "CAPPING" not in out[0].signals


def test_apply_keeps_label_if_some_details_remain():
    s = _score(
        author="A",
        signals=["CAPPING"],
        details=[
            {"type": "CAPPING", "hash": "h1", "date": "d", "additions": 2000},
            {"type": "CAPPING", "hash": "h2", "date": "d", "additions": 3000},
        ],
    )
    t = NormalizedSignalsTracker()
    t.dismiss("A", "CAPPING", "h1")
    out = t.apply([s])
    assert len(out[0].signal_details) == 1
    assert "CAPPING" in out[0].signals


def test_apply_preserves_non_detail_labels():
    s = _score(author="A", signals=["EW-01"], details=[])
    out = NormalizedSignalsTracker().apply([s])
    assert out[0].signals == ["EW-01"]


def test_apply_does_not_mutate_original():
    s = _score(
        author="A",
        signals=["ZSCORE"],
        details=[{"type": "ZSCORE", "metrics": ["git", "doc"]}],
    )
    t = NormalizedSignalsTracker()
    t.dismiss("A", "ZSCORE")
    t.apply([s])
    # 원본은 그대로 유지
    assert s.signals == ["ZSCORE"]
    assert len(s.signal_details) == 1
