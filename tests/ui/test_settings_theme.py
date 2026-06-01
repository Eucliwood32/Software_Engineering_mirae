"""FR-5.8 — 다크 모드/테마 + SettingsDialog + 설정 버튼 (L3, view-design §6.13·§10).

ThemeManager가 테마 상태를 소유하고, SettingsDialog 스위치는 위임만 한다.
다크 토글 시 tokens 팔레트가 전환되고, MainWindow 우측 상단에 설정 버튼이 고정된다.
"""
from __future__ import annotations

import pytest

from qce.view.dialogs.settings_dialog import SettingsDialog
from qce.view.main_window import MainWindow
from qce.view.style import tokens as T
from qce.view.style.theme import MODE_AUTO, theme_manager


@pytest.fixture(autouse=True)
def _reset_theme():
    """각 테스트 후 테마를 시스템 자동(라이트 기본)으로 되돌린다(전역 싱글턴 격리)."""
    yield
    theme_manager.set_mode(MODE_AUTO)
    T.apply_palette(False)


def test_apply_palette_switches_tokens():
    # qce-design-guide §2 팔레트(Product-First Minimalism) 값으로 갱신.
    T.apply_palette(True)
    assert T.COLOR_BG == "#1c1c1e"          # = COLOR_CANVAS(dark)
    assert T.COLOR_TEXT == "#f5f5f7"
    T.apply_palette(False)
    assert T.COLOR_BG == "#ffffff"          # = COLOR_CANVAS(light)
    assert T.COLOR_TEXT == "#1d1d1f"


def test_theme_manager_set_dark_toggles_palette(qtbot):
    theme_manager.set_dark(True)
    assert theme_manager.is_dark() is True
    assert T.COLOR_BG == "#1c1c1e"
    theme_manager.set_dark(False)
    assert theme_manager.is_dark() is False
    assert T.COLOR_BG == "#ffffff"


def test_staff_credit_three_members(qtbot):
    d = SettingsDialog()
    qtbot.addWidget(d)
    assert d.staff_names() == ["이대한", "조원희", "김휘중"]


def test_dark_switch_delegates_to_theme_manager(qtbot):
    d = SettingsDialog()
    qtbot.addWidget(d)
    d._dark_switch.setChecked(True)          # 스위치 조작 → theme_manager.set_dark(True)
    assert theme_manager.is_dark() is True
    assert T.COLOR_BG == "#1c1c1e"
    d._dark_switch.setChecked(False)
    assert theme_manager.is_dark() is False


def test_switch_syncs_with_current_theme(qtbot):
    theme_manager.set_dark(True)
    d = SettingsDialog()                     # 열릴 때 현재 테마와 동기화
    qtbot.addWidget(d)
    assert d.is_dark_checked() is True


def test_settings_button_is_top_right_corner_widget(qtbot):
    w = MainWindow()
    qtbot.addWidget(w)
    assert w.menuBar().cornerWidget() is w.settings_btn


def test_theme_change_emits_signal(qtbot):
    with qtbot.waitSignal(theme_manager.changed, timeout=1000):
        theme_manager.set_dark(True)
