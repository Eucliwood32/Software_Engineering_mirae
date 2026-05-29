"""FR-5.1 — DashboardView 합성·동시 갱신·차트간 중재 (L3)."""
from __future__ import annotations

from qce.view.panels.dashboard_view import DashboardView


def test_placeholder_no_scores(qtbot):                          # TC-FR-5.1-01
    dv = DashboardView()
    qtbot.addWidget(dv)
    dv.show_placeholder()
    assert dv.bar.is_animating is False
    assert dv.signal_text() == ""


def test_render_updates_all_charts(qtbot, score_dicts):         # TC-FR-5.1-03
    dv = DashboardView()
    qtbot.addWidget(dv)
    dv.render(score_dicts, set())
    # 세 차트 모두 데이터 반영
    assert dv.radar.axis_labels == ["Git", "문서", "메신저"]
    assert abs(dv.bar.average_line_y
               - sum(m["total_score"] for m in score_dicts) / len(score_dicts)) < 1e-4
    cx, cy = dv.scatter.crosshair_xy
    assert 0.0 <= cx <= 1.0 and 0.0 <= cy <= 1.0


def test_scatter_click_highlights_radar(qtbot, score_dicts):    # TC-FR-5.1c-08 (중재 INV-V4)
    dv = DashboardView()
    qtbot.addWidget(dv)
    dv.render(score_dicts, set())
    dv.bar.finish_animation()
    dv.radar.finish_animation()
    dv.scatter.finish_animation()

    base = dv.radar.member_linewidth(1)
    dv.scatter.simulate_point_click(0)          # scores[0] == "조원희" == radar index 0
    assert dv.radar.member_linewidth(0) > base


def test_signal_label_shows_flags(qtbot, score_dicts):
    dv = DashboardView()
    qtbot.addWidget(dv)
    dv.render(score_dicts, set())
    assert "EW-01" in dv.signal_text()
