"""FR-4.1 Min-Max 정규화."""
from __future__ import annotations
from collections.abc import Sequence


class Normalizer:
    def normalize(self, values: Sequence[float]) -> list[float]:
        """(x-min)/(max-min). max==min → 전원 0.5. round(_,4). 결과 0.0~1.0."""
        if not values:
            return []
        lo, hi = min(values), max(values)
        if hi == lo:
            return [0.5] * len(values)
        return [round((v - lo) / (hi - lo), 4) for v in values]
