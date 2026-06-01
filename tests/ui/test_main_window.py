"""FR-5.4 — MainWindow QStackedWidget 셸·화면 전환·상태바 (L3)."""
from __future__ import annotations

from qce.view.main_window import MainWindow
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
    # 파일 메뉴의 '리포트 저장…' 액션 트리거 → save_report_requested 발행
    menu = w.menuBar().actions()[0].menu()
    save_action = menu.actions()[0]
    # 저장 메뉴는 초기 비활성(제출·로딩 화면). 결과 화면에서만 활성.
    assert not save_action.isEnabled()
    w.set_save_enabled(True)
    with qtbot.waitSignal(w.save_report_requested, timeout=1000):
        save_action.trigger()
