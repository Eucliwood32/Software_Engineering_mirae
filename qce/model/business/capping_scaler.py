"""FR-4.2 Capping + 로그 스케일."""
from __future__ import annotations
import math


class CappingScaler:
    CAPPING_THRESHOLD: int = 1000

    def cap(self, additions: int) -> tuple[int, bool]:
        """additions > 1000 → (1000, True). 그 외 (additions, False)."""
        if additions > self.CAPPING_THRESHOLD:
            return (self.CAPPING_THRESHOLD, True)
        return (additions, False)

    def log_scale(self, total: int) -> float:
        return math.log1p(total)
