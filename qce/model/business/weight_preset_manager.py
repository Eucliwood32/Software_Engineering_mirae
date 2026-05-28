"""FR-4.4 가중치 프리셋·슬라이더 로직."""
from __future__ import annotations


class WeightPresetManager:
    PRESETS: dict[str, tuple[float, float, float]] = {
        "개발 중심": (0.60, 0.25, 0.15),
        "기획 중심": (0.20, 0.60, 0.20),
        "균형 설정": (0.40, 0.40, 0.20),
    }

    def validate_sum(self, w_git: float, w_doc: float, w_msg: float) -> bool:
        return abs(w_git + w_doc + w_msg - 1.0) < 1e-9
