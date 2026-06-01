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
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QVBoxLayout, QWidget

from qce.view.panels.progress_bar import ProgressBar
from qce.view.style import tokens as T

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

class LoadingScreen(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(
            T.SPACING_SECTION, T.SPACING_SECTION, T.SPACING_SECTION, T.SPACING_SECTION
        )
        root.setSpacing(T.SPACING_LG)

        # 로고: 수직 중앙보다 약간 위(상단 40%) — qce-design-guide §8
        root.addStretch(2)

        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(_LOGO_PATH)
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(48, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("QCE")
            logo.setObjectName("logoText")
        root.addWidget(logo)

        # 진행률: 로고 아래 SPACING_LG 간격, 너비 280px 중앙 정렬
        self.progress = ProgressBar()
        self.progress.setVisible(True)        # 로딩 화면에선 항상 진행바 영역 표시
        self.progress.setMaximumWidth(T.PROGRESS_W)
        prog_row = QHBoxLayout()
        prog_row.addStretch(1)
        prog_row.addWidget(self.progress)
        prog_row.addStretch(1)
        root.addLayout(prog_row)

        # 부드러운 안내 — 보조 텍스트(muted caption)
        title = QLabel("분석 중입니다…")
        title.setObjectName("placeholder")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        root.addWidget(title)

        root.addStretch(3)

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
