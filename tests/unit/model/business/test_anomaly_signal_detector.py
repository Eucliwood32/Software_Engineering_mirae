"""FR-4.2b/4.2c AnomalySignalDetector 단위 테스트."""
from __future__ import annotations

from qce.model.types import CommitStats, MemberScore
from qce.model.business.anomaly_signal_detector import AnomalySignalDetector


# ── FR-4.2b detect_frequency (EW-02) ────────────────────────────────────

def _commits(dates: list[str]) -> CommitStats:
    cl = [{"hash": f"h{i}", "date": d, "additions": 1, "deletions": 0}
          for i, d in enumerate(dates)]
    return CommitStats(commits=len(cl), additions=len(cl), deletions=0, commits_list=cl)


def test_frequency_flags_burst_day():
    """일평균의 3배 초과 일자가 신호로 잡힌다."""
    # 4일은 1커밋씩, 하루는 7커밋 → 총 11커밋/5일, 평균 2.2, 7 > 6.6
    dates = ["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"] + \
            ["2024-01-05"] * 7
    repo = {"heavy@t.com": _commits(dates)}

    signals = AnomalySignalDetector().detect_frequency(repo)

    assert len(signals) == 1
    sig = signals[0]
    assert sig["author"] == "heavy@t.com"
    assert sig["period"] == "2024-01-05"
    assert sig["period_commits"] == 7
    assert sig["baseline_avg"] == round(11 / 5, 4)


def test_frequency_no_signal_when_even():
    """고른 분포는 신호 없음."""
    repo = {"steady@t.com": _commits(["2024-01-01", "2024-01-02", "2024-01-03"])}
    assert AnomalySignalDetector().detect_frequency(repo) == []


def test_frequency_empty_commits_list():
    """commits_list 없는 작성자는 건너뛴다."""
    repo = {"empty@t.com": CommitStats(0, 0, 0, [])}
    assert AnomalySignalDetector().detect_frequency(repo) == []


# ── FR-4.2c detect_zscore ────────────────────────────────────────────────

def test_zscore_flags_low_outlier():
    """2개 이상 지표가 Z-Score ≤ -1.5 인 팀원 탐지."""
    scores = [
        MemberScore("High1", 0.9, 0.9, 0.9, 0.9, 0, 0, 0, False, []),
        MemberScore("High2", 0.85, 0.85, 0.85, 0.85, 0, 0, 0, False, []),
        MemberScore("High3", 0.88, 0.88, 0.88, 0.88, 0, 0, 0, False, []),
        MemberScore("Low", 0.0, 0.0, 0.85, 0.3, 0, 0, 0, False, []),  # git·doc 하위
    ]
    flagged = AnomalySignalDetector().detect_zscore(scores)
    assert "Low" in flagged


def test_zscore_empty():
    assert AnomalySignalDetector().detect_zscore([]) == []


# ── FR-4.2 detect_capping ────────────────────────────────────────────────

def test_capping_flags_large_commit():
    repo = {
        "x@t.com": CommitStats(
            2, 0, 0,
            [
                {"hash": "abc1234567", "date": "2024-01-01", "additions": 2500},
                {"hash": "def7654321", "date": "2024-01-02", "additions": 10},
            ],
        )
    }
    caps = AnomalySignalDetector().detect_capping(repo)
    assert len(caps) == 1
    assert caps[0]["author"] == "x@t.com"
    assert caps[0]["hash"] == "abc1234"          # 7자 축약
    assert caps[0]["additions"] == 2500


def test_capping_none_under_threshold():
    repo = {"y@t.com": CommitStats(1, 0, 0, [{"hash": "h", "date": "d", "additions": 1000}])}
    assert AnomalySignalDetector().detect_capping(repo) == []


# ── 구조화 상세 (카드용) ───────────────────────────────────────────────

def test_zscore_detail_reports_metrics():
    scores = [
        MemberScore("High1", 0.9, 0.9, 0.9, 0.9, 0, 0, 0, False, []),
        MemberScore("High2", 0.85, 0.85, 0.85, 0.85, 0, 0, 0, False, []),
        MemberScore("High3", 0.88, 0.88, 0.88, 0.88, 0, 0, 0, False, []),
        MemberScore("Low", 0.0, 0.0, 0.85, 0.3, 0, 0, 0, False, []),
    ]
    detail = AnomalySignalDetector().detect_zscore_detail(scores)
    low = next(d for d in detail if d["author"] == "Low")
    assert set(low["metrics"]) == {"git", "doc"}


def test_build_signal_details_groups_by_author():
    repo = {
        "x@t.com": CommitStats(
            1, 0, 0, [{"hash": "cap1abcd", "date": "2024-01-01", "additions": 5000}]
        )
    }
    scores = [MemberScore("x@t.com", 0.5, 0.5, 0.5, 0.5, 5000, 0, 0, True, [])]
    by_author = AnomalySignalDetector().build_signal_details(repo, scores)
    types = {d["type"] for d in by_author["x@t.com"]}
    assert "CAPPING" in types
