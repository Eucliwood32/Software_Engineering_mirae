"""FR-4.2b, FR-4.2c AnomalySignalDetector: 이상 신호 탐지 (점수 미반영, 표시 전용)."""
from __future__ import annotations
import math
from qce.model.types import CommitStats, MemberScore


class AnomalySignalDetector:
    """STR-7, ConOps P5: 신호는 조장 판단 보조용이며 total_score에 반영하지 않는다."""

    def detect_frequency(self, repo: dict[str, CommitStats]) -> list[dict]:
        """EW-02: 일평균 커밋의 3배 초과 일자를 신호로 반환.
        반환: [{author, period, period_commits, baseline_avg}, ...]
        """
        signals = []
        for author, stats in repo.items():
            if not stats.commits_list:
                continue
            daily: dict[str, int] = {}
            for commit in stats.commits_list:
                date = commit.get("date", "")[:10]
                daily[date] = daily.get(date, 0) + 1
            if not daily:
                continue
            baseline_avg = stats.commits / len(daily)
            for date, count in daily.items():
                if baseline_avg > 0 and count > baseline_avg * 3:
                    signals.append({
                        "author": author,
                        "period": date,
                        "period_commits": count,
                        "baseline_avg": round(baseline_avg, 4),
                    })
        return signals

    def detect_zscore(self, scores: list[MemberScore]) -> list[str]:
        """FR-4.2c: Z-Score ≤ -1.5 인 지표가 2개 이상인 팀원 이름 목록."""
        if not scores:
            return []

        def _z(vals: list[float]) -> list[float]:
            mean = sum(vals) / len(vals)
            std = math.sqrt(sum((x - mean) ** 2 for x in vals) / len(vals))
            if std == 0:
                return [0.0] * len(vals)
            return [(x - mean) / std for x in vals]

        gz = _z([s.git_score for s in scores])
        dz = _z([s.doc_score for s in scores])
        mz = _z([s.msg_score for s in scores])

        return [
            scores[i].author
            for i in range(len(scores))
            if sum([gz[i] <= -1.5, dz[i] <= -1.5, mz[i] <= -1.5]) >= 2
        ]
