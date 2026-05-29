"""
MainWindow — 앱 셸 (view-design §6.1).

좌측 입력/가중치 패널, 우측 DashboardView, 상단 메뉴, 결측 배너·진행률, 상태바를
레이아웃한다. Drag&Drop 이벤트를 확장자로 분기해 Signal로 올린다.

INV-V1/V2: model/controller/common import 금지. Signal은 발행만 하고 connect는
Controller가 수행한다. 헬스체크·분석 트리거 등 도메인 로직은 보유하지 않는다.
"""
from __future__ import annotations

import os

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QMainWindow,
    QVBoxLayout,
    QWidget,
)

from qce.view.panels.analysis_panel import AnalysisPanel
from qce.view.panels.dashboard_view import DashboardView
from qce.view.panels.progress_bar import ProgressBar
from qce.view.panels.warning_banner import WarningBanner
from qce.view.style.qss import app_stylesheet

DOC_EXTS = {".pptx", ".docx", ".hwpx"}
MSG_EXTS = {".txt"}


class MainWindow(QMainWindow):
    documents_dropped = pyqtSignal(list)
    git_repo_chosen = pyqtSignal(str)
    messenger_dropped = pyqtSignal(str)
    alias_mapping_requested = pyqtSignal()
    save_report_requested = pyqtSignal()

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("QCE — 부탁해 꼬마선장")
        self.setAcceptDrops(True)
        self.setStyleSheet(app_stylesheet())

        self.analysis_panel = AnalysisPanel()
        self.dashboard = DashboardView()
        self.warning_banner = WarningBanner()
        self.progress_bar = ProgressBar()

        central = QWidget()
        root = QVBoxLayout(central)
        root.addWidget(self.warning_banner)

        body = QHBoxLayout()
        body.addWidget(self.analysis_panel, 1)
        body.addWidget(self.dashboard, 3)
        root.addLayout(body)
        root.addWidget(self.progress_bar)

        self.setCentralWidget(central)
        self._build_menu()
        self.dashboard.show_placeholder()

    def _build_menu(self) -> None:
        menu = self.menuBar().addMenu("파일")
        act_git = menu.addAction("Git 저장소 선택…")
        act_git.triggered.connect(self._choose_git_repo)
        act_map = menu.addAction("팀원 매핑…")
        act_map.triggered.connect(self.alias_mapping_requested.emit)
        act_save = menu.addAction("리포트 저장…")
        act_save.triggered.connect(self.save_report_requested.emit)

    # ------------------------------------------------------------------ #
    # 상태바
    # ------------------------------------------------------------------ #
    def flash_status(self, msg: str, msec: int = 3000) -> None:
        self.statusBar().showMessage(msg, msec)

    # ------------------------------------------------------------------ #
    # Drag & Drop
    # ------------------------------------------------------------------ #
    def dragEnterEvent(self, e) -> None:
        if e.mimeData().hasUrls():
            e.acceptProposedAction()
        else:
            e.ignore()

    def dropEvent(self, e) -> None:
        paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        self._handle_dropped_paths(paths)
        e.acceptProposedAction()

    def _handle_dropped_paths(self, paths: list[str]) -> None:
        """확장자 분기: 문서는 documents_dropped(list), 카톡 .txt는 messenger_dropped(str)."""
        docs, messengers = self._classify_paths(paths)
        if docs:
            self.documents_dropped.emit(docs)
        for m in messengers:
            self.messenger_dropped.emit(m)

    @staticmethod
    def _classify_paths(paths: list[str]) -> tuple[list[str], list[str]]:
        docs, messengers = [], []
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if ext in DOC_EXTS:
                docs.append(p)
            elif ext in MSG_EXTS:
                messengers.append(p)
        return docs, messengers

    # ------------------------------------------------------------------ #
    def _choose_git_repo(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Git 저장소 선택")
        if path:
            self.git_repo_chosen.emit(path)
