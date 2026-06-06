"""
MainWindow — 앱 셸 (view-design §6.1, FR-5.4).

QStackedWidget으로 제출(SubmitScreen) → 로딩(LoadingScreen) → 결과(ResultScreen)
3화면을 보유·전환한다. 상단 메뉴(리포트 저장)·하단 상태바를 레이아웃하고,
GitMissingDialog·SaveReportDialog를 셸 모달로 합성한다.

INV-V1/V2: model/controller/common import 금지. Signal은 발행만 하고 connect와
화면 전환 호출(show_*)은 Controller가 수행한다. 도메인 로직은 보유하지 않는다.
"""
from __future__ import annotations

import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QLabel, QMainWindow, QStackedWidget, QToolButton

from qce.view.dialogs.settings_dialog import SettingsDialog
from qce.view.panels.loading_screen import LoadingScreen
from qce.view.panels.result_screen import ResultScreen
from qce.view.panels.submit_screen import SubmitScreen
from qce.view.style.qss import app_stylesheet
from qce.view.style.theme import theme_manager


from PyQt6.QtGui import QIcon, QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QWidget, QMenu

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "QCE_Logo.png")

# 자주 쓰는 대표 세로(portrait) 해상도 — QCE는 세로로 길게 펼칠 때 가장 보기 좋다.
# (width, height) 오름차순. 사용자 화면에 가장 잘 맞는 항목만 '권장' 표시한다.
_RESOLUTION_PRESETS: list[tuple[int, int]] = [
    (600, 960),
    (720, 1280),
    (810, 1440),
    (900, 1600),
    (1080, 1920),
]


class MainWindow(QMainWindow):
    save_report_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QCE — 부탁해 꼬마선장")
        self.setWindowIcon(QIcon(_LOGO_PATH))
        self.setStyleSheet(app_stylesheet())

        self.stack = QStackedWidget()
        self.submit = SubmitScreen()
        self.loading = LoadingScreen()
        self.result = ResultScreen()
        self.stack.addWidget(self.submit)     # index 0
        self.stack.addWidget(self.loading)    # index 1
        self.stack.addWidget(self.result)     # index 2
        self.setCentralWidget(self.stack)

        self._build_menu()
        # [v2.0] 테마 변경 시 앱 전역 QSS 재적용(차트 재채색은 각 차트가 직접 구독)
        theme_manager.changed.connect(self._reapply_theme)
        self.show_submit()

    def _build_menu(self) -> None:
        # 모든 화면에서 항상 노출되는 좌측 상단 작은 로고 (셸 크롬, 요구사항 1)
        left_widget = QWidget()
        left_layout = QHBoxLayout(left_widget)
        left_layout.setContentsMargins(12, 0, 0, 0)
        left_layout.setSpacing(12)

        self.corner_logo = QLabel()
        pix = QPixmap(_LOGO_PATH)
        if not pix.isNull():
            self.corner_logo.setPixmap(
                pix.scaledToHeight(20, Qt.TransformationMode.SmoothTransformation)
            )
        else:
            self.corner_logo.setText("QCE")
            self.corner_logo.setObjectName("cornerLogo")
        left_layout.addWidget(self.corner_logo)
        
        self.file_btn = QToolButton()
        self.file_btn.setText("파일")
        self.file_btn.setObjectName("secondary")
        self.file_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        file_menu = QMenu(self.file_btn)
        self._act_save = file_menu.addAction("리포트 저장…")
        self._act_save.triggered.connect(self.save_report_requested.emit)
        self._act_save.setEnabled(False)
        self.file_btn.setMenu(file_menu)
        left_layout.addWidget(self.file_btn)

        # '파일' 버튼과 똑같이 생긴 '화면' 버튼 — 세로 해상도 프리셋 선택(FR-5.8 인접 기능)
        self.screen_btn = QToolButton()
        self.screen_btn.setText("화면")
        self.screen_btn.setObjectName("secondary")
        self.screen_btn.setPopupMode(QToolButton.ToolButtonPopupMode.InstantPopup)
        self._screen_menu = QMenu(self.screen_btn)
        # 메뉴를 펼칠 때마다 현재 화면 기준으로 '권장' 표시를 다시 계산한다(모니터 이동 대응)
        self._screen_menu.aboutToShow.connect(self._rebuild_screen_menu)
        self.screen_btn.setMenu(self._screen_menu)
        self._rebuild_screen_menu()
        left_layout.addWidget(self.screen_btn)

        self.menuBar().setCornerWidget(left_widget, Qt.Corner.TopLeftCorner)

        # [v2.0] 우측 상단 끝 설정 버튼(코너 위젯, FR-5.8)
        self.settings_btn = QToolButton()
        self.settings_btn.setText("⚙")
        self.settings_btn.setToolTip("설정")
        self.settings_btn.setAutoRaise(True)
        self.settings_btn.clicked.connect(self._open_settings)
        self.menuBar().setCornerWidget(self.settings_btn, Qt.Corner.TopRightCorner)

    # ------------------------------------------------------------------ #
    # 화면(해상도) 메뉴 — 세로 프리셋 + 사용자 화면 맞춤 '권장' 표시
    # ------------------------------------------------------------------ #
    def _recommended_resolution(self) -> tuple[int, int] | None:
        """현재 화면에 가장 잘 어울리는 세로 프리셋을 고른다.

        작업표시줄을 제외한 가용 영역(availableGeometry)과 창 프레임(타이틀바 등)을
        고려해, '들어가는 것 중 가장 큰' 세로 해상도를 권장한다. 세로로 길수록 보기
        좋은 앱이므로 높이를 최대화하는 쪽을 고른다. 하나도 안 들어가면 가장 작은 것.
        """
        screen = self.screen()
        if screen is None:
            return None
        avail = screen.availableGeometry()
        frame = self.frameGeometry().size() - self.size()  # 타이틀바·테두리 여백
        max_w = avail.width() - max(frame.width(), 0)
        max_h = avail.height() - max(frame.height(), 0)
        fitting = [(w, h) for (w, h) in _RESOLUTION_PRESETS if w <= max_w and h <= max_h]
        if fitting:
            return max(fitting, key=lambda wh: wh[1])  # 들어가는 것 중 가장 높이가 큰 것
        return _RESOLUTION_PRESETS[0]

    def _rebuild_screen_menu(self) -> None:
        """세로 해상도 액션을 (재)구성한다. 권장 항목에만 '(권장)' 꼬리표를 단다."""
        self._screen_menu.clear()
        recommended = self._recommended_resolution()
        for w, h in _RESOLUTION_PRESETS:
            label = f"{w} × {h}"
            if (w, h) == recommended:
                label += "  (권장)"
            act = self._screen_menu.addAction(label)
            act.triggered.connect(lambda _checked=False, w=w, h=h: self._apply_resolution(w, h))

    def _apply_resolution(self, w: int, h: int) -> None:
        """창 크기를 프리셋으로 바꾸고 화면 중앙에 다시 배치한다."""
        self.showNormal()  # 최대화 상태였다면 해제해야 resize가 반영된다
        self.resize(w, h)
        screen = self.screen()
        if screen is not None:
            center = screen.availableGeometry().center()
            geo = self.frameGeometry()
            geo.moveCenter(center)
            self.move(geo.topLeft())
        self.flash_status(f"화면 해상도를 {w} × {h}(으)로 변경했습니다.", 3000)

    def set_save_enabled(self, enabled: bool) -> None:
        """리포트 저장 메뉴 활성/비활성. 결과 화면+결과 존재 시에만 True."""
        self._act_save.setEnabled(enabled)

    def _open_settings(self) -> None:
        dlg = SettingsDialog(self)
        dlg.exec()

    def _reapply_theme(self) -> None:
        self.setStyleSheet(app_stylesheet())

    # ------------------------------------------------------------------ #
    # 화면 전환 (FR-5.4) — Controller가 생명주기에 맞춰 호출
    # ------------------------------------------------------------------ #
    def show_submit(self) -> None:
        self.stack.setCurrentWidget(self.submit)

    def show_loading(self) -> None:
        self.stack.setCurrentWidget(self.loading)

    def show_result(self) -> None:
        self.stack.setCurrentWidget(self.result)

    # ------------------------------------------------------------------ #
    # 상태바
    # ------------------------------------------------------------------ #
    def flash_status(self, msg: str, msec: int = 3000) -> None:
        self.statusBar().showMessage(msg, msec)

    # --- 테스트 접근자 ---
    def current_screen(self):
        return self.stack.currentWidget()
