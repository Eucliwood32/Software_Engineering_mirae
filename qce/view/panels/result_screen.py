"""
ResultScreen — 결과 화면 (view-design §6.11, FR-5.7).

DashboardView(3차트+신호)와 WarningBanner, 계정 병합 컨트롤(AliasMappingDialog
재사용)과 [새 분석] 버튼을 배치한다. 병합 컨트롤에서 복수 인물을 1인으로 합치면
merge_requested(분석-후 N:1)를 올리고, Controller가 재집계·재정규화 후 render로
갱신한다(결정: 재집계+재정규화). View는 merge_requested만 발행한다(INV-V1).
"""
from __future__ import annotations

import os
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import QHBoxLayout, QLabel, QPushButton, QVBoxLayout, QWidget

from qce.view.contract import (
    K_AUTHOR,
    K_RAW_ADD,
    K_RAW_CHAR,
    K_RAW_MSG,
)
from qce.view.dialogs.alias_mapping_dialog import AliasMappingDialog
from qce.view.panels.dashboard_view import DashboardView
from qce.view.panels.warning_banner import WarningBanner

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")

class ResultScreen(QWidget):
    merge_requested = pyqtSignal(dict)            # {alias→member} 병합 그룹
    new_analysis_requested = pyqtSignal()
    signal_dismissed = pyqtSignal(str, str, str)  # (author, type, ref) — FR-4.2c 중계

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.dashboard = DashboardView()
        self.banner = WarningBanner()
        self.merge = AliasMappingDialog()         # 결과 화면 임베드(FR-5.7)
        # 병합 확정 → merge_requested로 중계 (재집계는 Controller 책임)
        self.merge.mapping_confirmed.connect(self.merge_requested)
        # 신호 예외 처리(FR-4.2c) → Controller로 중계
        self.dashboard.signal_dismissed.connect(self.signal_dismissed)

        root = QVBoxLayout(self)

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

        root.addWidget(self.banner)
        root.addWidget(self.dashboard, stretch=1)
        root.addWidget(self.merge)

        bottom = QHBoxLayout()
        bottom.addStretch(1)
        self._new_btn = QPushButton("새 분석")
        self._new_btn.clicked.connect(self.new_analysis_requested.emit)
        bottom.addWidget(self._new_btn)
        root.addLayout(bottom)

    def render(self, scores: list[dict], missing: set[str]) -> None:
        """대시보드·배너 갱신 + 병합 후보 목록 채움."""
        self.dashboard.render(scores, missing)
        self.banner.show_missing(missing)
        self.populate_merge(scores)

    def set_suggested_mapping(self, suggested: dict[str, str]) -> None:
        """Controller가 계산한 추천 별칭 매핑을 병합 컨트롤에 미리 채운다(FR-1.3)."""
        self.merge.apply_suggested(suggested)

    def populate_merge(self, scores: list[dict]) -> None:
        """결과 인물(author)을 병합 컨트롤 후보로 채운다. 후보=대표 지정 대상 팀원."""
        authors = [s[K_AUTHOR] for s in scores]
        self.merge.set_members(authors)
        identifiers = [
            {
                "raw_id": s[K_AUTHOR],
                "source": "result",
                "activity": int(s.get(K_RAW_ADD, 0))
                + int(s.get(K_RAW_CHAR, 0))
                + int(s.get(K_RAW_MSG, 0)),
            }
            for s in scores
        ]
        self.merge.populate(identifiers)
