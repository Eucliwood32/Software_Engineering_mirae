"""FR-4.2c NormalizedSignalsTracker: "정상으로 표시"한 이상 신호의 세션 내 예외 상태.

조장이 신호 카드에서 특정 항목을 "정상으로 표시"하면 해당 (작성자, 신호유형, 참조)
조합을 기억하고, 이후 재렌더 시 그 신호를 제외한다. 점수에는 애초에 신호가 반영되지
않으므로(STR-7), 본 트래커는 *표시 전용* 상태만 다룬다. 영속 저장하지 않는다
(세션 한정, NFR-2.3 휘발 정책 부합).

INV: model 레이어 — view/controller import 금지.
"""
from __future__ import annotations

import dataclasses

from qce.model.types import MemberScore

# 구조화 상세(signal_details)가 가지는 신호 유형. 이 유형의 라벨만 카드/예외 대상.
DETAIL_TYPES = frozenset({"CAPPING", "EW-02", "ZSCORE"})


class NormalizedSignalsTracker:
    def __init__(self) -> None:
        # (author, signal_type, ref) 튜플 집합. ref는 유형별 식별자(해시/일자/"").
        self._dismissed: set[tuple[str, str, str]] = set()

    # ------------------------------------------------------------------ #
    # 예외 등록/해제/조회
    # ------------------------------------------------------------------ #
    def dismiss(self, author: str, signal_type: str, ref: str = "") -> None:
        """해당 신호를 '정상으로 표시'(예외 등록)."""
        self._dismissed.add((author, signal_type, ref))

    def restore(self, author: str, signal_type: str, ref: str = "") -> None:
        """예외 해제(다시 신호로 표시)."""
        self._dismissed.discard((author, signal_type, ref))

    def is_dismissed(self, author: str, signal_type: str, ref: str = "") -> bool:
        return (author, signal_type, ref) in self._dismissed

    def dismissed_count(self) -> int:
        return len(self._dismissed)

    def clear(self) -> None:
        """전체 예외 초기화(예: 새 분석 시작 시)."""
        self._dismissed.clear()

    # ------------------------------------------------------------------ #
    # 필터링
    # ------------------------------------------------------------------ #
    @staticmethod
    def ref_of(detail: dict) -> str:
        """상세 dict에서 예외 식별자(ref)를 추출. CAPPING=hash, EW-02=date, ZSCORE=""."""
        t = detail.get("type", "")
        if t == "CAPPING":
            return str(detail.get("hash", ""))
        if t == "EW-02":
            return str(detail.get("date", ""))
        return ""

    def filter_details(self, author: str, details: list[dict]) -> list[dict]:
        """예외 등록되지 않은 상세만 남긴다."""
        return [
            d
            for d in details
            if not self.is_dismissed(author, d.get("type", ""), self.ref_of(d))
        ]

    def apply(self, scores: list[MemberScore]) -> list[MemberScore]:
        """예외를 반영한 새 MemberScore 목록을 반환(원본 불변).
        - signal_details: 예외 항목 제거.
        - signals: 상세가 모두 제거된 유형 라벨만 제거(EW-01 등 비상세 라벨은 보존).
        """
        result: list[MemberScore] = []
        for s in scores:
            kept = self.filter_details(s.author, s.signal_details)
            kept_types = {d.get("type", "") for d in kept}
            new_signals = [
                lbl
                for lbl in s.signals
                if lbl not in DETAIL_TYPES or lbl in kept_types
            ]
            result.append(
                dataclasses.replace(s, signals=new_signals, signal_details=kept)
            )
        return result
