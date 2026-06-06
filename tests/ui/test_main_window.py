"""FR-5.4 — MainWindow QStackedWidget 셸·화면 전환·상태바 (L3)."""
from __future__ import annotations

from qce.view.main_window import MainWindow, _RESOLUTION_PRESETS
from qce.view.panels.loading_screen import LoadingScreen
from qce.view.panels.result_screen import ResultScreen
from qce.view.panels.submit_screen import SubmitScreen


def test_initial_screen_is_submit(qtbot):                       # TC-FR-5.4-01
    w = MainWindow()
    qtbot.addWidget(w)
    assert w.current_screen() is w.submit
    assert isinstance(w.submit, SubmitScreen)


def test_show_loading(qtbot):                                   # TC-FR-5.4-02
    w = MainWindow()
    qtbot.addWidget(w)
    w.show_loading()
    assert w.current_screen() is w.loading
    assert isinstance(w.loading, LoadingScreen)


def test_show_result(qtbot):                                    # TC-FR-5.4-03
    w = MainWindow()
    qtbot.addWidget(w)
    w.show_result()
    assert w.current_screen() is w.result
    assert isinstance(w.result, ResultScreen)


def test_show_submit_returns(qtbot):                            # TC-FR-5.4-04/05
    w = MainWindow()
    qtbot.addWidget(w)
    w.show_result()
    w.show_submit()
    assert w.current_screen() is w.submit


def test_flash_status(qtbot):                                   # FR-5.2/NFR-2.4
    w = MainWindow()
    qtbot.addWidget(w)
    w.flash_status("저장 완료", 3000)
    assert w.statusBar().currentMessage() == "저장 완료"


def test_save_report_menu_signal(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    # 파일 메뉴('파일' 코너 버튼)의 '리포트 저장…' 액션 트리거 → save_report_requested 발행
    menu = w.file_btn.menu()
    save_action = menu.actions()[0]
    # 저장 메뉴는 초기 비활성(제출·로딩 화면). 결과 화면에서만 활성.
    assert not save_action.isEnabled()
    w.set_save_enabled(True)
    with qtbot.waitSignal(w.save_report_requested, timeout=1000):
        save_action.trigger()


def test_screen_menu_has_portrait_presets(qtbot):
    """'화면' 버튼 메뉴는 세로(높이>너비) 해상도 프리셋을 제공한다."""
    w = MainWindow()
    qtbot.addWidget(w)
    assert w.screen_btn.text() == "화면"
    w._rebuild_screen_menu()
    actions = w.screen_btn.menu().actions()
    assert len(actions) == len(_RESOLUTION_PRESETS)
    # 모든 프리셋은 세로 지향(height > width)
    for (pw, ph) in _RESOLUTION_PRESETS:
        assert ph > pw


def test_screen_menu_marks_single_recommendation(qtbot):
    """화면 맞춤 '권장'은 정확히 한 항목에만 표시된다."""
    w = MainWindow()
    qtbot.addWidget(w)
    w._rebuild_screen_menu()
    labels = [a.text() for a in w.screen_btn.menu().actions()]
    recommended = [t for t in labels if "권장" in t]
    assert len(recommended) == 1
    assert w._recommended_resolution() in _RESOLUTION_PRESETS


def test_apply_resolution_resizes_window(qtbot):
    """프리셋 선택 시 창 크기가 해당 해상도로 변경된다."""
    w = MainWindow()
    qtbot.addWidget(w)
    w.show()
    w._apply_resolution(720, 1280)
    assert (w.size().width(), w.size().height()) == (720, 1280)
