"""
FR-4.4 가중치 프리셋 로직 단위 테스트 (L1)
TC-FR-4.4-01 ~ TC-FR-4.4-05
"""
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
