"""FR-5.7 — ResultScreen UI: 렌더·병합 후보·병합 발행·새 분석 (L3)."""
from __future__ import annotations

from qce.view.panels.result_screen import ResultScreen


def test_render_updates_dashboard(qtbot, score_dicts):          # TC-FR-5.7-01
    rs = ResultScreen()
    qtbot.addWidget(rs)
    rs.render(score_dicts, set())
    expected = sum(m["total_score"] for m in score_dicts) / len(score_dicts)
    assert abs(rs.dashboard.bar.average_line_y - expected) < 1e-4


def test_populate_merge_lists_all_members(qtbot, score_dicts):  # TC-FR-5.7-01
    rs = ResultScreen()
    qtbot.addWidget(rs)
    rs.render(score_dicts, set())
    assert rs.merge.row_count() == len(score_dicts)


def test_render_shows_banner_on_missing(qtbot, score_dicts):
    rs = ResultScreen()
    qtbot.addWidget(rs)
    rs.render(score_dicts, {"messenger"})
    assert rs.banner.is_banner_visible()
    assert "메신저" in rs.banner.current_text()


def test_merge_requested_emitted(qtbot, score_dicts):           # TC-FR-5.7-02
    rs = ResultScreen()
    qtbot.addWidget(rs)
    rs.render(score_dicts, set())
    a0 = score_dicts[0]["author"]
    a1 = score_dicts[1]["author"]
    # a1을 a0로 병합
    rs.merge.combo_for(a1).setCurrentText(a0)
    with qtbot.waitSignal(rs.merge_requested, timeout=1000) as blocker:
        rs.merge._confirm()
    assert blocker.args[0][a1] == a0


def test_new_analysis_requested(qtbot, score_dicts):            # TC-FR-5.4-05
    rs = ResultScreen()
    qtbot.addWidget(rs)
    rs.render(score_dicts, set())
    with qtbot.waitSignal(rs.new_analysis_requested, timeout=1000):
        rs._new_btn.click()
