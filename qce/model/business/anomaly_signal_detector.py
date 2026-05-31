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

    def detect_capping(self, repo: dict[str, CommitStats]) -> list[dict]:
        """FR-4.2: 단일 커밋 변경 라인 > 1000 인 커밋을 신호로 반환.
        반환: [{author, hash, date, additions}, ...] (해시는 7자 축약).
        """
        signals = []
        for author, stats in repo.items():
            for commit in stats.commits_list or []:
                adds = int(commit.get("additions", 0))
                if adds > 1000:
                    raw_hash = str(commit.get("hash", ""))
                    signals.append({
                        "author": author,
                        "hash": raw_hash[:7],
                        "date": commit.get("date", ""),
                        "additions": adds,
                    })
        return signals

    def detect_zscore(self, scores: list[MemberScore]) -> list[str]:
        """FR-4.2c: Z-Score ≤ -1.5 인 지표가 2개 이상인 팀원 이름 목록."""
        return [d["author"] for d in self.detect_zscore_detail(scores)]

    def detect_zscore_detail(self, scores: list[MemberScore]) -> list[dict]:
        """detect_zscore의 상세판: 어떤 지표가 하위 이상치인지 함께 반환.
        반환: [{author, metrics: ["git","doc",...]}, ...]
        """
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

        out = []
        for i in range(len(scores)):
            low = [
                name
                for name, z in (("git", gz[i]), ("doc", dz[i]), ("msg", mz[i]))
                if z <= -1.5
            ]
            if len(low) >= 2:
                out.append({"author": scores[i].author, "metrics": low})
        return out

    def build_signal_details(
        self, repo: dict[str, CommitStats] | None, scores: list[MemberScore]
    ) -> dict[str, list[dict]]:
        """팀원별 구조화 신호 상세 묶음 {author: [detail, ...]} 생성(카드 표시용).
        detail 공통키: type(CAPPING|EW-02|ZSCORE) + 유형별 메타. STR-7: 점수 미반영.
        """
        by_author: dict[str, list[dict]] = {s.author: [] for s in scores}

        if repo is not None:
            for cap in self.detect_capping(repo):
                by_author.setdefault(cap["author"], []).append({
                    "type": "CAPPING", **{k: cap[k] for k in ("hash", "date", "additions")},
                })
            for freq in self.detect_frequency(repo):
                by_author.setdefault(freq["author"], []).append({
                    "type": "EW-02",
                    "date": freq["period"],
                    "period_commits": freq["period_commits"],
                    "baseline_avg": freq["baseline_avg"],
                })

        for z in self.detect_zscore_detail(scores):
            by_author.setdefault(z["author"], []).append({
                "type": "ZSCORE", "metrics": z["metrics"],
            })
        return by_author
