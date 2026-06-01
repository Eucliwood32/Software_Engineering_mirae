"""FR-4.4 — AnalysisPanel UI (L3)."""
from __future__ import annotations

import pytest

from qce.view.panels.analysis_panel import AnalysisPanel


@pytest.mark.parametrize(
    "name,expected",
    [
        ("개발 중심", {"w_git": 0.60, "w_doc": 0.25, "w_msg": 0.15}),
        ("기획 중심", {"w_git": 0.20, "w_doc": 0.60, "w_msg": 0.20}),
        ("균형 설정", {"w_git": 0.40, "w_doc": 0.40, "w_msg": 0.20}),
    ],
)
def test_apply_preset(qtbot, name, expected):                   # TC-FR-4.4-06
    p = AnalysisPanel()
    qtbot.addWidget(p)
    p.apply_preset(name)
    assert p.current_weights() == expected


def test_preset_emits_signal(qtbot):
    p = AnalysisPanel()
    qtbot.addWidget(p)
    with qtbot.waitSignal(p.preset_chosen, timeout=1000) as blocker:
        p.apply_preset("균형 설정")
    assert blocker.args[0] == "균형 설정"


def test_set_analyze_enabled(qtbot):                            # TC-FR-4.4-07/08
    p = AnalysisPanel()
    qtbot.addWidget(p)
    p.set_analyze_enabled(False)
    assert p.analyze_enabled() is False
    p.set_analyze_enabled(True)
    assert p.analyze_enabled() is True


def test_weight_warning(qtbot):                                 # TC-FR-4.4-07
    p = AnalysisPanel()
    qtbot.addWidget(p)
    msg = "가중치 합계가 100%여야 합니다 (현재 150%)"
    p.set_weight_warning(msg)
    assert p.weight_warning_text() == msg
    p.set_weight_warning(None)
    assert p.weight_warning_text() == ""


def test_slider_step_is_005(qtbot):                             # TC-FR-4.4-09
    p = AnalysisPanel()
    qtbot.addWidget(p)
    assert p.weight_step == 0.05


def test_weights_changed_emitted(qtbot):
    p = AnalysisPanel()
    qtbot.addWidget(p)
    with qtbot.waitSignal(p.weights_changed, timeout=1000) as blocker:
        p.apply_preset("개발 중심")
    assert blocker.args[0] == {"w_git": 0.60, "w_doc": 0.25, "w_msg": 0.15}


def test_slider_auto_balancing(qtbot):
    p = AnalysisPanel()
    qtbot.addWidget(p)
    p.apply_preset("균형 설정")  # 0.40, 0.40, 0.20
    
    # Simulate user dragging w_git from 0.40 to 0.60 (value: 12)
    s = p._sliders["w_git"]
    s.sliderMoved.emit(12)
    
    weights = p.current_weights()
    assert weights["w_git"] == 0.60
    assert weights["w_doc"] == 0.25
    assert weights["w_msg"] == 0.15
    assert sum(weights.values()) == 1.0


def test_slider_value_labels(qtbot):
    p = AnalysisPanel()
    qtbot.addWidget(p)
    p.apply_preset("균형 설정")
    
    assert p._value_labels["w_git"].text() == "40%"
    assert p._value_labels["w_doc"].text() == "40%"
    assert p._value_labels["w_msg"].text() == "20%"
