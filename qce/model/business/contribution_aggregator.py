"""FR-4.* ContributionAggregator: 지표 통합 파이프라인."""
from __future__ import annotations
from typing import Optional
from qce.model.types import CommitStats, MemberScore
from qce.model.business.normalizer import Normalizer
from qce.model.business.capping_scaler import CappingScaler
from qce.model.business.anomaly_signal_detector import AnomalySignalDetector
from qce.model.business.weight_rebalancer import WeightRebalancer


class ContributionAggregator:
    """가용 소스만으로 종합 점수 산출(NFR-3.2). None 소스는 WeightRebalancer 경유."""

    def __init__(self) -> None:
        self.normalizer = Normalizer()
        self.capping_scaler = CappingScaler()
        self.anomaly_detector = AnomalySignalDetector()
        self.weight_rebalancer = WeightRebalancer()

    def aggregate(
        self,
        git: Optional[dict[str, CommitStats]] = None,
        docs: Optional[dict[str, int]] = None,
        msgs: Optional[dict[str, int]] = None,
        weights: Optional[dict[str, float]] = None,
    ) -> list[MemberScore]:
        if weights is None:
            weights = {"git": 0.4, "doc": 0.4, "msg": 0.2}

        # 1. 가용 소스 판별
        available: set[str] = set()
        if git is not None:
            available.add("git")
        if docs is not None:
            available.add("doc")
        if msgs is not None:
            available.add("msg")

        # 2. 가중치 재조정
        rebalanced = self.weight_rebalancer.rebalance(weights, available)

        # 3. 통합 인원 집합
        author_set: set[str] = set()
        if git is not None:
            author_set |= set(git.keys())
        if docs is not None:
            author_set |= set(docs.keys())
        if msgs is not None:
            author_set |= set(msgs.keys())
        authors = sorted(author_set)

        # 4. 원시 값 추출
        raw_add = [git[a].additions if (git and a in git) else 0 for a in authors]
        raw_doc = [docs.get(a, 0) if docs else 0 for a in authors]
        raw_msg = [msgs.get(a, 0) if msgs else 0 for a in authors]

        # 5. Git Capping + Log Scaling (FR-4.2 / EW-01: 캡핑은 "단일 커밋" 단위)
        #    커밋별 추가줄을 1000으로 제한해 합산 → 로그 스케일. commits_list가
        #    없으면(구버전·병합 누락) 총합 캡핑으로 폴백한다.
        log_add, cap_flags = [], []
        for a in authors:
            stats = git.get(a) if git else None
            if stats is not None and stats.commits_list:
                capped_sum = 0
                any_capped = False
                for c in stats.commits_list:
                    cv, flag = self.capping_scaler.cap(c.get("additions", 0))
                    capped_sum += cv
                    any_capped = any_capped or flag
                cap_flags.append(any_capped)
                log_add.append(self.capping_scaler.log_scale(capped_sum))
            else:
                add = stats.additions if stats is not None else 0
                capped, is_capped = self.capping_scaler.cap(add)
                cap_flags.append(is_capped)
                log_add.append(self.capping_scaler.log_scale(capped))

        # 6. Min-Max 정규화
        git_norm = self.normalizer.normalize(log_add) if git is not None else [0.0] * len(authors)
        doc_norm = self.normalizer.normalize(raw_doc) if docs is not None else [0.0] * len(authors)
        msg_norm = self.normalizer.normalize(raw_msg) if msgs is not None else [0.0] * len(authors)

        # 7. MemberScore 조립 (qce/model/types.py 필드명 사용)
        scores = [
            MemberScore(
                author=authors[i],
                git_score=git_norm[i],
                doc_score=doc_norm[i],
                msg_score=msg_norm[i],
                total_score=round(
                    git_norm[i] * rebalanced.get("git", 0.0)
                    + doc_norm[i] * rebalanced.get("doc", 0.0)
                    + msg_norm[i] * rebalanced.get("msg", 0.0),
                    4,
                ),
                raw_additions=raw_add[i],
                raw_chars=raw_doc[i],
                raw_messages=raw_msg[i],
                capping_applied=cap_flags[i],
                signals=[],
            )
            for i in range(len(authors))
        ]

        # 8. 이상 신호 탐지 (STR-7: 점수 미반영)
        z_flagged = set(self.anomaly_detector.detect_zscore(scores))
        freq_flagged = (
            {s["author"] for s in self.anomaly_detector.detect_frequency(git)}
            if git is not None else set()
        )
        for s in scores:
            if s.author in z_flagged:
                s.signals.append("ZSCORE")
            if s.capping_applied:
                s.signals.append("CAPPING")
            if s.author in freq_flagged:
                s.signals.append("EW-02")

        return scores
