"""
FR-4.4 가중치 프리셋 로직 단위 테스트 (L1)
TC-FR-4.4-01 ~ TC-FR-4.4-05
"""
import pytest

from qce.model.business.weight_preset_manager import WeightPresetManager


def test_preset_dev_focused():           # TC-FR-4.4-01
    assert WeightPresetManager.PRESETS["개발 중심"] == (0.60, 0.25, 0.15)


def test_preset_plan_focused():          # TC-FR-4.4-02
    assert WeightPresetManager.PRESETS["기획 중심"] == (0.20, 0.60, 0.20)


def test_preset_balanced():              # TC-FR-4.4-03
    assert WeightPresetManager.PRESETS["균형 설정"] == (0.40, 0.40, 0.20)


def test_validate_sum_invalid():         # TC-FR-4.4-04
    assert WeightPresetManager().validate_sum(0.5, 0.5, 0.5) is False


def test_validate_sum_valid():           # TC-FR-4.4-05
    assert WeightPresetManager().validate_sum(0.4, 0.4, 0.2) is True


def test_all_presets_sum_to_one():
    for name, (g, d, m) in WeightPresetManager.PRESETS.items():
        assert abs(g + d + m - 1.0) < 1e-9, f"프리셋 '{name}' 합계 오류"


# --- 재분배/정규화/역추적 (FR-4.4 확장) ---

def test_preset_names():
    assert WeightPresetManager().preset_names() == ["개발 중심", "기획 중심", "균형 설정"]


def test_get_preset_as_dict():
    assert WeightPresetManager().get_preset("균형 설정") == {"git": 0.40, "doc": 0.40, "msg": 0.20}


def test_match_preset_found():
    assert WeightPresetManager().match_preset(0.60, 0.25, 0.15) == "개발 중심"


def test_match_preset_none_for_custom():
    assert WeightPresetManager().match_preset(0.33, 0.33, 0.34) is None


def test_clamp_bounds():
    assert WeightPresetManager.clamp(-0.5) == 0.0
    assert WeightPresetManager.clamp(1.5) == 1.0
    assert WeightPresetManager.clamp(0.3) == 0.3


def test_normalize_scales_to_one():
    out = WeightPresetManager().normalize({"git": 2.0, "doc": 1.0, "msg": 1.0})
    assert abs(sum(out.values()) - 1.0) < 1e-9
    assert out["git"] == 0.5


def test_normalize_zero_is_uniform():
    out = WeightPresetManager().normalize({"git": 0.0, "doc": 0.0, "msg": 0.0})
    assert abs(sum(out.values()) - 1.0) < 1e-9
    for k in ("git", "doc", "msg"):
        assert abs(out[k] - 1.0 / 3) < 1e-3


def test_redistribute_keeps_sum_one():
    current = {"git": 0.40, "doc": 0.40, "msg": 0.20}
    out = WeightPresetManager().redistribute("git", 0.70, current)
    assert out["git"] == 0.70
    assert abs(sum(out.values()) - 1.0) < 1e-9
    # 나머지 두 축은 기존 비율(2:1) 유지 → doc=0.20, msg=0.10
    assert out["doc"] == 0.20
    assert out["msg"] == 0.10


def test_redistribute_others_zero_splits_evenly():
    current = {"git": 1.0, "doc": 0.0, "msg": 0.0}
    out = WeightPresetManager().redistribute("git", 0.40, current)
    assert abs(sum(out.values()) - 1.0) < 1e-9
    assert out["doc"] == out["msg"] == 0.30


def test_redistribute_clamps_over_one():
    out = WeightPresetManager().redistribute("git", 1.5, {"git": 0.3, "doc": 0.4, "msg": 0.3})
    assert out["git"] == 1.0
    assert abs(sum(out.values()) - 1.0) < 1e-9


def test_redistribute_unknown_key_raises():
    with pytest.raises(ValueError):
        WeightPresetManager().redistribute("w_xxx", 0.5, {"git": 0.4, "doc": 0.4, "msg": 0.2})
