"""
ThemeManager — 라이트/다크 테마 상태의 단일 소유자 (view-design §10.2, FR-5.8).

전역 싱글턴 ``theme_manager``로 노출된다. 모드는 ``auto``/``light``/``dark`` 3종이며,
``auto``일 때 시스템 라이트/다크는 ``QApplication.styleHints().colorScheme()``로
감지하고 시스템 변경(``colorSchemeChanged``)에도 자동 반응한다. ``apply()``는
tokens 팔레트 적용 + 앱 QPalette 설정 후 ``changed``를 발행하며, MainWindow와
각 차트가 이를 구독해 재채색한다.

INV-V1: 본 모듈은 model/controller/common을 import하지 않는다(qce.view 내부 모듈).
"""
from __future__ import annotations

from PyQt6.QtCore import QObject, Qt, pyqtSignal
from PyQt6.QtGui import QColor, QPalette
from PyQt6.QtWidgets import QApplication

from qce.view.style import tokens as T

MODE_AUTO = "auto"
MODE_LIGHT = "light"
MODE_DARK = "dark"


class ThemeManager(QObject):
    changed = pyqtSignal()        # 팔레트 적용 완료 통지

    def __init__(self) -> None:
        super().__init__()
        self._mode = MODE_AUTO
        self._system_hooked = False

    # ------------------------------------------------------------------ #
    # 상태 조회
    # ------------------------------------------------------------------ #
    def mode(self) -> str:
        return self._mode

    def is_dark(self) -> bool:
        """현재 적용해야 할 다크 여부. auto면 시스템 감지, 아니면 명시값."""
        if self._mode == MODE_DARK:
            return True
        if self._mode == MODE_LIGHT:
            return False
        return self._system_is_dark()

    @staticmethod
    def _system_is_dark() -> bool:
        app = QApplication.instance()
        if app is None:
            return False
        try:
            return app.styleHints().colorScheme() == Qt.ColorScheme.Dark
        except Exception:
            return False

    # ------------------------------------------------------------------ #
    # 상태 변경
    # ------------------------------------------------------------------ #
    def set_mode(self, mode: str) -> None:
        if mode not in (MODE_AUTO, MODE_LIGHT, MODE_DARK):
            raise ValueError(f"unknown theme mode: {mode!r}")
        self._mode = mode
        self.apply()

    def set_dark(self, on: bool) -> None:
        """다크모드 스위치 토글 슬롯. 시스템 자동 추종을 끄고 명시값으로 고정."""
        self.set_mode(MODE_DARK if on else MODE_LIGHT)

    # ------------------------------------------------------------------ #
    # 적용
    # ------------------------------------------------------------------ #
    def apply(self) -> None:
        """tokens 팔레트 + 앱 QPalette 적용 후 changed 발행(view-design §10.2)."""
        dark = self.is_dark()
        T.apply_palette(dark)
        self._apply_app_palette()
        self._hook_system_changes()
        self.changed.emit()

    def _apply_app_palette(self) -> None:
        """Fusion 스타일 네이티브 위젯(메뉴·다이얼로그 등)을 위한 QPalette 설정.

        색은 활성 토큰 팔레트(apply()가 _apply_app_palette 직전 apply_palette를 호출)에서
        읽어 단일 출처를 유지한다. 라이트는 빈 팔레트를 두면 시스템(다크)이 채워
        배경이 미전환되므로 명시 적용한다.
        """
        app = QApplication.instance()
        if app is None:
            return
        pal = QPalette()
        canvas = QColor(T.COLOR_CANVAS)
        surface = QColor(T.COLOR_SURFACE)
        surface2 = QColor(T.COLOR_SURFACE_2)
        text = QColor(T.COLOR_TEXT)
        disabled = QColor(T.COLOR_TEXT_DISABLED)
        primary = QColor(T.COLOR_PRIMARY)
        on_primary = QColor("#ffffff")

        pal.setColor(QPalette.ColorRole.Window, canvas)
        pal.setColor(QPalette.ColorRole.WindowText, text)
        pal.setColor(QPalette.ColorRole.Base, canvas)
        pal.setColor(QPalette.ColorRole.AlternateBase, surface)
        pal.setColor(QPalette.ColorRole.Text, text)
        pal.setColor(QPalette.ColorRole.Button, surface2)
        pal.setColor(QPalette.ColorRole.ButtonText, text)
        pal.setColor(QPalette.ColorRole.ToolTipBase, surface)
        pal.setColor(QPalette.ColorRole.ToolTipText, text)
        pal.setColor(QPalette.ColorRole.Highlight, primary)
        pal.setColor(QPalette.ColorRole.HighlightedText, on_primary)
        pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled)
        pal.setColor(QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled)
        app.setPalette(pal)

    def _hook_system_changes(self) -> None:
        """시스템 colorScheme 변경 구독(1회). auto 모드면 자동 재적용."""
        if self._system_hooked:
            return
        app = QApplication.instance()
        if app is None:
            return
        try:
            app.styleHints().colorSchemeChanged.connect(self._on_system_changed)
            self._system_hooked = True
        except Exception:
            pass

    def _on_system_changed(self, _scheme) -> None:
        if self._mode == MODE_AUTO:
            self.apply()


# 모듈 싱글턴 — qce.view.* 어디서든 import해 공유한다.
theme_manager = ThemeManager()
