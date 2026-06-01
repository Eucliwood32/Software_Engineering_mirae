"""
FR-5.1d — 차트 자동 검증 12개 케이스 (G4 게이트).

TC-ID = 함수명으로 1:1 고정(test-cases.md §FR-5.1d). 접근자는 view-design §11 기준.
입력은 §5.3 dict 스키마(score_dicts 픽스처). 애니메이션은 finish_animation()으로
최종 상태까지 동기 전진 후 검증한다(타이머 대기 없음).
"""
from __future__ import annotations

from qce.view.charts.bar_chart import BarChartWidget
from qce.view.charts.radar_chart import RadarChartWidget
from qce.view.charts.scatter_chart import ScatterChartWidget
from qce.view.contract import K_TOTAL, SRC_MSG, SRC_DOC


# ----------------------------- 막대 (FR-5.1a) ----------------------------- #
def test_bar_tooltip_items(qtbot, score_dicts):                 # 1
    w = BarChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    fields = w.tooltip_fields(score_dicts[0]["author"])
    assert len(fields) == 6


def test_bar_average_line(qtbot, score_dicts):                  # 2
    w = BarChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    expected = sum(m[K_TOTAL] for m in score_dicts) / len(score_dicts)
    assert abs(w.average_line_y - expected) < 1e-4


def test_bar_animation_final_height(qtbot, score_dicts):        # 3
    w = BarChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    w.finish_animation()
    for m in score_dicts:
        assert abs(w.bar_height(m["author"]) - m[K_TOTAL]) < 1e-3


# ----------------------------- 레이더 (FR-5.1b) --------------------------- #
def test_radar_vertex_labels(qtbot, score_dicts):               # 4
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    assert w.axis_labels == ["Git", "문서", "메신저"]


def test_radar_toggle_hide(qtbot, score_dicts):                 # 5
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    assert w.is_polygon_visible(0) is True
    w.toggle_member(0)
    assert w.is_polygon_visible(0) is False


def test_radar_missing_data(qtbot, score_dicts):                # 6
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, {SRC_MSG})
    assert any("(제외됨)" in label for label in w.excluded_axis_labels)


# ----------------------------- 산점도 (FR-5.1c) --------------------------- #
def test_scatter_dynamic_axes(qtbot, score_dicts):              # 7
    w = ScatterChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, {SRC_MSG})  # 2개 소스 (Git, Doc)
    assert w.ax.get_ylabel() == "Git 점수"
    assert w.ax.get_xlabel() == "문서 점수"


def test_scatter_dot_color_saturation(qtbot, score_dicts):      # 8
    w = ScatterChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())  # 3개 소스 가용
    for m in score_dicts:
        alpha = w.dot_color_saturation(m["author"])
        assert 0.0 <= alpha <= 1.0


def test_scatter_signal_emission(qtbot, score_dicts):           # 9
    w = ScatterChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    w.finish_animation()
    with qtbot.waitSignal(w.member_selected, timeout=1000) as blocker:
        w.simulate_point_click(0)
    assert isinstance(blocker.args[0], str)


def test_scatter_label_overlap(qtbot, score_dicts):             # 10
    w = ScatterChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    assert w.min_label_distance() >= 30.0


def test_scatter_dynamic_crosshair(qtbot, score_dicts):         # 11
    w = ScatterChartWidget()
    qtbot.addWidget(w)
    w.render(score_dicts, set())
    # Y = Git, X = Doc (순서에 따라 Git이 첫번째 가용)
    cx, cy = w.crosshair_xy
    expected_x = sum(m["doc_score"] for m in score_dicts) / len(score_dicts)
    expected_y = sum(m["git_score"] for m in score_dicts) / len(score_dicts)
    assert abs(cx - expected_x) < 1e-4
    assert abs(cy - expected_y) < 1e-4


def test_scatter_placeholder_text(qtbot, score_dicts):          # 12
    w = ScatterChartWidget()
    qtbot.addWidget(w)
    # 1개 소스만 가용하게 만듦
    w.render(score_dicts, {SRC_MSG, SRC_DOC})
    # 안내 텍스트가 표시되는지 확인
    assert any("자료가 한 종류인 경우" in t.get_text() for t in w.ax.texts)
