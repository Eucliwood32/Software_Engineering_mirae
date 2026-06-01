"""FR-5.1b v2.0 — 레이더 축 소스 명시 + 종합/개인 병렬 배치 (L3, view-design §7.3).

가용 소스별 세부 축에 소스(Git/문서/메신저)를 눈금 라벨로 명시하고, 한 figure에
종합 레이더 + 인원별 개인 레이더를 나란히 배치한다. 순수 라벨 접근자(axis_labels)는
소스 접두 없이 유지되어 기존 테스트와 회귀하지 않는다.
"""
from __future__ import annotations

from qce.view.charts.radar_chart import RadarChartWidget
from qce.view.contract import K_AUTHOR, K_DIMENSIONS

_GIT = {"git_commits": 0.5, "git_additions": 0.8, "git_deletions": 0.3}
_DOC = {"doc_chars": 0.6, "doc_count": 0.4, "doc_blocks": 0.7}
_MSG = {"msg_count": 0.2, "msg_chars": 0.9, "msg_hours": 0.5}


def _member(author: str, *parts: dict) -> dict:
    dims: dict = {}
    for p in parts:
        dims.update(p)
    return {K_AUTHOR: author, K_DIMENSIONS: dims}


def test_comprehensive_plus_individual_subplots(qtbot):
    """종합 1 + 범례 1 + 개인 N개의 subplot이 한 figure에 배치된다."""
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("A", _GIT, _DOC, _MSG), _member("B", _GIT, _DOC, _MSG)], set())
    # 종합(1) + 범례(1) + 개인(2) = 4
    assert len(w.figure.axes) == 4


def test_individual_radars_titled_by_author(qtbot):
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("나나", _GIT, _DOC), _member("두두", _GIT, _DOC)], set())
    titles = [ax.get_title() for ax in w.figure.axes]
    assert "종합" in titles
    assert "나나" in titles and "두두" in titles


def test_axis_tick_labels_name_their_source(qtbot):
    """눈금 라벨에 소스(Git/문서/메신저)가 명시된다. 순수 라벨 접근자는 접두 없음."""
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("A", _GIT, _MSG)], set())
    # axis_labels는 소스 접두 없는 순수 라벨 (회귀 보존)
    assert w.axis_labels == ["커밋 수", "코드 추가", "코드 정리", "발화 수", "발화량", "활동 시간대"]
    # 렌더된 종합 레이더 눈금 라벨에는 소스명이 포함
    ticks = [t.get_text() for t in w.ax.get_xticklabels()]
    assert any("Git" in t for t in ticks)
    assert any("메신저" in t for t in ticks)


def test_individual_polygons_animate_to_final(qtbot):
    """개인 레이더 폴리곤도 애니메이션 대상에 포함되어 최종 상태에 도달한다."""
    w = RadarChartWidget()
    qtbot.addWidget(w)
    w.render([_member("A", _GIT, _DOC, _MSG)], set())
    w.finish_animation()
    assert w.animation_done is True
    # 종합 폴리곤(접근자 대상) 가시
    assert w.is_polygon_visible(0) is True
