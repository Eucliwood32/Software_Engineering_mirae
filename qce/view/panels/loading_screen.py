"""
LoadingScreen — 분석 로딩 화면 (view-design §6.10, FR-5.6).

전체 화면에 로고/안내 문구와 ProgressBar를 중앙 배치한다. 분석 시작 1초 이내
진입(NFR-1.1), 진행률 갱신, 완료/오류 시 화면 전환은 Controller가 수행한다.
진행률 메서드는 내부 ProgressBar에 위임한다.
"""
from __future__ import annotations

import os
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from qce.view.panels.progress_bar import ProgressBar

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

class LoadingScreen(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 24, 24, 24)

        # 로고 (가운데 상단, 여백 포함 작게 표시)
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo.setContentsMargins(20, 20, 20, 20)
        pix = QPixmap(_LOGO_PATH)
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(48, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("QCE")
            logo.setObjectName("logoText")
            logo.setStyleSheet("font-size: 22pt; font-weight: bold;")
        root.addWidget(logo)

        root.addStretch(1)

        title = QLabel("분석 중입니다…")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setStyleSheet("font-size: 16pt;")
        root.addWidget(title)

        self.progress = ProgressBar()
        self.progress.setVisible(True)        # 로딩 화면에선 항상 진행바 영역 표시
        root.addWidget(self.progress)

        root.addStretch(1)

    def start(self) -> None:
        self.progress.start()

    def set_value(self, pct: int) -> None:
        self.progress.set_value(pct)

    def finish(self) -> None:
        self.progress.finish()

    # --- 테스트 접근자 ---
    def value(self) -> int:
        return self.progress.value()

    def is_running(self) -> bool:
        return self.progress.is_running()
