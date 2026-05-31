"""
SubmitScreen — 메인(제출) 화면 (view-design §6.9, FR-5.5).

큼직한 로고 + 프로그램 설명 + 멀티포맷 드래그앤드롭 존 + Git 저장소 진입점 +
가중치 패널(AnalysisPanel, FR-4.4) + [분석 시작]을 배치한다. 드롭 이벤트를
확장자로 분기해 Signal로 올린다(기존 MainWindow의 드롭 로직 이동).

INV-V1/V2: model/controller import 금지. Signal은 발행만, connect는 Controller.
"""
from __future__ import annotations

import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
)

from qce.view.panels.analysis_panel import AnalysisPanel

DOC_EXTS = {".pptx", ".docx", ".hwpx"}
MSG_EXTS = {".txt"}

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
_DESCRIPTION = "Git · 문서 · 메신저 기여를 한 번에 정량 분석합니다.\n과제물을 아래 영역에 끌어다 놓으세요."
_DROP_HINT = "여기에 문서(.pptx/.docx/.hwpx)와 카카오톡(.txt)을 끌어다 놓으세요"


class SubmitScreen(QWidget):
    documents_dropped = pyqtSignal(list)     # .pptx/.docx/.hwpx
    git_repo_chosen = pyqtSignal(str)
    messenger_dropped = pyqtSignal(str)      # .txt

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._doc_count = 0
        self._msg_count = 0

        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        # 로고 (assets/logo.png, 없으면 텍스트 폴백)
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(_LOGO_PATH)
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(96, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("QCE — 부탁해 꼬마선장")
            logo.setObjectName("logoText")
            logo.setStyleSheet("font-size: 22pt; font-weight: bold;")
        root.addWidget(logo)

        desc = QLabel(_DESCRIPTION)
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        root.addWidget(desc)

        # 드롭존
        self._dropzone = QLabel(_DROP_HINT)
        self._dropzone.setObjectName("dropzone")
        self._dropzone.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._dropzone.setMinimumHeight(140)
        self._dropzone.setStyleSheet(
            "QLabel#dropzone { border: 2px dashed #9aa0a6; border-radius: 8px; color: #80868b; }"
        )
        root.addWidget(self._dropzone, stretch=1)

        # 적재 피드백 + Git 선택
        row = QHBoxLayout()
        self._loaded_label = QLabel("")
        row.addWidget(self._loaded_label, stretch=1)
        self._git_btn = QPushButton("Git 저장소 선택…")
        self._git_btn.clicked.connect(self.choose_git_repo)
        row.addWidget(self._git_btn)
        root.addLayout(row)

        # 가중치 패널 (FR-4.4) — analyze_clicked는 이 패널이 발행
        self.analysis_panel = AnalysisPanel()
        root.addWidget(self.analysis_panel)

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
        """확장자 분기: 문서→documents_dropped(list), 카톡 .txt→messenger_dropped(str)."""
        docs, messengers = self._classify_paths(paths)
        if docs:
            self._doc_count += len(docs)
            self.documents_dropped.emit(docs)
        for m in messengers:
            self._msg_count += 1
            self.messenger_dropped.emit(m)
        self._refresh_loaded_label()

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

    def choose_git_repo(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Git 저장소 선택")
        if path:
            self.git_repo_chosen.emit(path)

    def _refresh_loaded_label(self) -> None:
        self._loaded_label.setText(f"문서 {self._doc_count}개 · 메신저 {self._msg_count}개 적재됨")

    def reset(self) -> None:
        """이전 분석 입력값(문서, 메신저 개수 등)을 초기화한다."""
        self._doc_count = 0
        self._msg_count = 0
        self._loaded_label.setText("")

    # --- 테스트 접근자 ---
    def loaded_summary(self) -> str:
        return self._loaded_label.text()
