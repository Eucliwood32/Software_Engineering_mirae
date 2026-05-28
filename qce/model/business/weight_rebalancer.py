"""FR-4.3 데이터 소스 결측 → 동적 가중치 재조정."""
from __future__ import annotations


class WeightRebalancer:
    def rebalance(self, weights: dict[str, float],
                  available: set[str]) -> dict[str, float]:
        """결측 소스 가중치 0, 가용 소스는 상대 비율 유지 재정규화.
        반환 합 1.0±0.0001."""
        total = sum(weights[k] for k in available if k in weights)
        result: dict[str, float] = {}
        for k, v in weights.items():
            if k not in available:
                result[k] = 0.0
            else:
                result[k] = round(v / total, 10) if total > 0 else 0.0
        return result
