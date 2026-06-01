"""
GitMissingDialog — Git 부재 안내 모달 (view-design §6.2, FR-2.2).

고정 문구, 다운로드 링크, PATH 안내 1줄, 확인 버튼. 링크는 앱 내부 HTTP가 아니라
webbrowser.open OS 위임만 사용한다(C-2/NFR-2.2 준수).
"""
from __future__ import annotations

import webbrowser

from PyQt6.QtWidgets import (
    QDialog,
    QDialogButtonBox,
    QLabel,
    QPushButton,
    QVBoxLayout,
)

from qce.view.style import tokens as T


class GitMissingDialog(QDialog):
    DOWNLOAD_URL = "https://git-scm.com/download/win"
    MESSAGE = "Git이 설치되어 있지 않거나 PATH에 등록되지 않았습니다."
    PATH_HINT = "설치 후에도 인식되지 않으면 Git이 시스템 PATH 환경 변수에 등록되어 있는지 확인하세요."

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Git을 찾을 수 없습니다")
        layout = QVBoxLayout(self)
        layout.setContentsMargins(T.SPACING_LG, T.SPACING_LG, T.SPACING_LG, T.SPACING_LG)
        layout.setSpacing(T.SPACING_MD)

        msg = QLabel(self.MESSAGE)
        msg.setWordWrap(True)
        layout.addWidget(msg)
        hint = QLabel(self.PATH_HINT)
        hint.setObjectName("placeholder")
        hint.setWordWrap(True)
        layout.addWidget(hint)

        self.download_button = QPushButton("Git 다운로드 페이지 열기")
        self.download_button.setObjectName("secondary")
        self.download_button.clicked.connect(self._open_download)
        layout.addWidget(self.download_button)

        buttons = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        buttons.accepted.connect(self.accept)
        layout.addWidget(buttons)

    def _open_download(self) -> None:
        """webbrowser.open(DOWNLOAD_URL) — OS 기본 브라우저 위임(C-2 준수)."""
        webbrowser.open(self.DOWNLOAD_URL)
