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
        self._apply_app_palette(dark)
        self._hook_system_changes()
        self.changed.emit()

    def _apply_app_palette(self, dark: bool) -> None:
        """Fusion 스타일 네이티브 위젯(메뉴·다이얼로그 등)을 위한 QPalette 설정."""
        app = QApplication.instance()
        if app is None:
            return
        pal = QPalette()
        if dark:
            bg = QColor("#1e1e1e")
            base = QColor("#2b2b2b")
            text = QColor("#e8eaed")
            disabled = QColor("#6e6e6e")
            pal.setColor(QPalette.ColorRole.Window, bg)
            pal.setColor(QPalette.ColorRole.WindowText, text)
            pal.setColor(QPalette.ColorRole.Base, base)
            pal.setColor(QPalette.ColorRole.AlternateBase, bg)
            pal.setColor(QPalette.ColorRole.Text, text)
            pal.setColor(QPalette.ColorRole.Button, base)
            pal.setColor(QPalette.ColorRole.ButtonText, text)
            pal.setColor(QPalette.ColorRole.ToolTipBase, base)
            pal.setColor(QPalette.ColorRole.ToolTipText, text)
            pal.setColor(QPalette.ColorRole.Highlight, QColor("#8ab4f8"))
            pal.setColor(QPalette.ColorRole.HighlightedText, QColor("#202124"))
            pal.setColor(
                QPalette.ColorGroup.Disabled, QPalette.ColorRole.Text, disabled
            )
            pal.setColor(
                QPalette.ColorGroup.Disabled, QPalette.ColorRole.ButtonText, disabled
            )
        # 라이트는 기본 QPalette(시스템 표준)로 복원
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
