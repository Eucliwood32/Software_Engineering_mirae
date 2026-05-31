"""
MainWindow — 앱 셸 (view-design §6.1, FR-5.4).

QStackedWidget으로 제출(SubmitScreen) → 로딩(LoadingScreen) → 결과(ResultScreen)
3화면을 보유·전환한다. 상단 메뉴(리포트 저장)·하단 상태바를 레이아웃하고,
GitMissingDialog·SaveReportDialog를 셸 모달로 합성한다.

INV-V1/V2: model/controller/common import 금지. Signal은 발행만 하고 connect와
화면 전환 호출(show_*)은 Controller가 수행한다. 도메인 로직은 보유하지 않는다.
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QMainWindow, QStackedWidget

from qce.view.panels.loading_screen import LoadingScreen
from qce.view.panels.result_screen import ResultScreen
from qce.view.panels.submit_screen import SubmitScreen
from qce.view.style.qss import app_stylesheet


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
        self.show_submit()

    def _build_menu(self) -> None:
        menu = self.menuBar().addMenu("파일")
        act_save = menu.addAction("리포트 저장…")
        act_save.triggered.connect(self.save_report_requested.emit)

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
