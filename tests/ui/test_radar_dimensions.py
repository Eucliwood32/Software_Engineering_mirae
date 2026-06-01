"""FR-5.1b v1.7 — RadarChartWidget 가변 세부 축(3/6/9) 검증 (L3).

dimensions가 담긴 점수 dict에서는 가용 소스마다 3개 세부 축이 그려지고,
dimensions가 없으면 레거시 3축(Git/문서/메신저)으로 폴백한다.
"""
from __future__ import annotations

from qce.view.charts.radar_chart import RadarChartWidget
from qce.view.contract import K_AUTHOR, K_DIMENSIONS

_GIT = {"git_commits": 0.5, "git_additions": 0.8, "git_deletions": 0.3}
_DOC = {"doc_chars": 0.6, "doc_count": 0.4, "doc_blocks": 0.7}
_MSG = {"msg_count": 0.2, "msg_chars": 0.9, "msg_hours": 0.5}


def _member(author: str, *dim_parts: dict) -> dict:
    dims: dict = {}
    for p in dim_parts:
        dims.update(p)
    return {K_AUTHOR: author, K_DIMENSIONS: dims}


def test_single_source_draws_three_axes(qtbot):
    """문서 하나만 들어와도 3개 세부 축으로 그려진다(3축 레이더)."""
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("혼자", _DOC)], set())
    assert w.axis_labels == ["문서 분량", "문서 수", "구성 요소"]


def test_two_sources_draw_six_axes(qtbot):
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("A", _GIT, _DOC), _member("B", _GIT, _DOC)], set())
    assert len(w.axis_labels) == 6
    assert w.axis_labels == ["커밋 수", "코드 추가", "코드 정리", "문서 분량", "문서 수", "구성 요소"]


def test_three_sources_draw_nine_axes(qtbot):
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("A", _GIT, _DOC, _MSG)], set())
    assert len(w.axis_labels) == 9
    # 표시 순서: Git → 문서 → 메신저
    assert w.axis_labels[:3] == ["커밋 수", "코드 추가", "코드 정리"]
    assert w.axis_labels[-3:] == ["발화 수", "발화량", "활동 시간대"]


def test_single_member_polygon_renders(qtbot):
    """팀원 1명이어도 폴리곤이 정상 형성되고 애니메이션이 최종값에 도달한다."""
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("혼자", _GIT)], set())
    w.finish_animation()
    assert w.is_polygon_visible(0) is True
    assert w.animation_done is True


def test_falls_back_to_legacy_three_axes_without_dimensions(qtbot):
    """dimensions가 없으면(레거시 합성 데이터) 종전 3축으로 폴백한다."""
    legacy = {K_AUTHOR: "X", "git_score": 0.3, "doc_score": 0.5, "msg_score": 0.2}
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([legacy], set())
    assert w.axis_labels == ["Git", "문서", "메신저"]
