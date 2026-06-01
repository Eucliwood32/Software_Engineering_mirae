"""
MainWindow — 앱 셸 (view-design §6.1, FR-5.4).

QStackedWidget으로 제출(SubmitScreen) → 로딩(LoadingScreen) → 결과(ResultScreen)
3화면을 보유·전환한다. 상단 메뉴(리포트 저장)·하단 상태바를 레이아웃하고,
GitMissingDialog·SaveReportDialog를 셸 모달로 합성한다.

INV-V1/V2: model/controller/common import 금지. Signal은 발행만 하고 connect와
화면 전환 호출(show_*)은 Controller가 수행한다. 도메인 로직은 보유하지 않는다.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QStackedWidget, QToolButton

from qce.view.dialogs.settings_dialog import SettingsDialog
from qce.view.panels.loading_screen import LoadingScreen
from qce.view.panels.result_screen import ResultScreen
from qce.view.panels.submit_screen import SubmitScreen
from qce.view.style.qss import app_stylesheet
from qce.view.style.theme import theme_manager


from PyQt6.QtGui import QIcon

class MainWindow(QMainWindow):
    save_report_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QCE — 부탁해 꼬마선장")
        self.setWindowIcon(QIcon("assets/logo.png"))
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
        menu = self.menuBar().addMenu("파일")
        self._act_save = menu.addAction("리포트 저장…")
        self._act_save.triggered.connect(self.save_report_requested.emit)
        self._act_save.setEnabled(False)  # 초기 비활성(제출·로딩 화면)

        # [v2.0] 우측 상단 끝 설정 버튼(코너 위젯, FR-5.8)
        self.settings_btn = QToolButton()
        self.settings_btn.setText("⚙")
        self.settings_btn.setToolTip("설정")
        self.settings_btn.setAutoRaise(True)
        self.settings_btn.clicked.connect(self._open_settings)
        self.menuBar().setCornerWidget(self.settings_btn, Qt.Corner.TopRightCorner)

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
