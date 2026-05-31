"""FR-4.4 가중치 프리셋·슬라이더 로직."""
from __future__ import annotations

_KEYS = ("git", "doc", "msg")
_EPS = 1e-9


class WeightPresetManager:
    PRESETS: dict[str, tuple[float, float, float]] = {
        "개발 중심": (0.60, 0.25, 0.15),
        "기획 중심": (0.20, 0.60, 0.20),
        "균형 설정": (0.40, 0.40, 0.20),
    }

    def validate_sum(self, w_git: float, w_doc: float, w_msg: float) -> bool:
        return abs(w_git + w_doc + w_msg - 1.0) < _EPS

    # ------------------------------------------------------------------ #
    # 프리셋 조회
    # ------------------------------------------------------------------ #
    def preset_names(self) -> list[str]:
        return list(self.PRESETS.keys())

    def get_preset(self, name: str) -> dict[str, float]:
        """프리셋명 → {"git","doc","msg"} dict. 미존재 시 KeyError."""
        g, d, m = self.PRESETS[name]
        return {"git": g, "doc": d, "msg": m}

    def match_preset(self, w_git: float, w_doc: float, w_msg: float) -> str | None:
        """현재 가중치와 일치하는 프리셋명 역추적. 없으면 None(=사용자 조정)."""
        for name, (g, d, m) in self.PRESETS.items():
            if (
                abs(g - w_git) < _EPS
                and abs(d - w_doc) < _EPS
                and abs(m - w_msg) < _EPS
            ):
                return name
        return None

    # ------------------------------------------------------------------ #
    # 슬라이더 재분배
    # ------------------------------------------------------------------ #
    @staticmethod
    def clamp(value: float) -> float:
        """가중치를 [0.0, 1.0] 범위로 제한."""
        return max(0.0, min(1.0, value))

    def normalize(self, weights: dict[str, float]) -> dict[str, float]:
        """세 축 합이 1.0이 되도록 비례 정규화. 음수는 0으로, 합이 0이면 균등 분배.
        (상한 클램프는 하지 않는다 — 임의 크기 입력을 비례 축소하기 위함.)"""
        vals = {k: max(0.0, weights.get(k, 0.0)) for k in _KEYS}
        total = sum(vals.values())
        if total <= _EPS:
            result = {k: round(1.0 / len(_KEYS), 4) for k in _KEYS}
        else:
            result = {k: round(vals[k] / total, 4) for k in _KEYS}
        return self._absorb_drift(result)

    @staticmethod
    def _absorb_drift(result: dict[str, float]) -> dict[str, float]:
        """반올림 잔차를 마지막 축에 흡수해 합을 정확히 1.0으로 보정."""
        last = _KEYS[-1]
        drift = round(1.0 - sum(result.values()), 4)
        if abs(drift) >= _EPS:
            result[last] = round(result[last] + drift, 4)
        return result

    def redistribute(
        self, changed_key: str, new_value: float, current: dict[str, float]
    ) -> dict[str, float]:
        """슬라이더 하나(changed_key)를 new_value로 바꿀 때 나머지 두 축을
        기존 비율대로 비례 재분배해 합 1.0을 유지한다(FR-4.4).

        - new_value는 [0,1]로 클램프.
        - 나머지 두 축의 기존 합이 0이면 잔여를 균등 분배.
        """
        if changed_key not in _KEYS:
            raise ValueError(f"알 수 없는 가중치 키: {changed_key}")

        fixed = self.clamp(new_value)
        remainder = 1.0 - fixed
        others = [k for k in _KEYS if k != changed_key]
        others_sum = sum(self.clamp(current.get(k, 0.0)) for k in others)

        result: dict[str, float] = {changed_key: round(fixed, 4)}
        if others_sum <= _EPS:
            share = remainder / len(others)
            for k in others:
                result[k] = round(share, 4)
        else:
            for k in others:
                ratio = self.clamp(current.get(k, 0.0)) / others_sum
                result[k] = round(remainder * ratio, 4)

        # 반올림 잔차를 마지막 축에 흡수해 정확히 1.0 보정.
        drift = round(1.0 - sum(result.values()), 4)
        if abs(drift) >= _EPS:
            result[others[-1]] = round(result[others[-1]] + drift, 4)
        return result
