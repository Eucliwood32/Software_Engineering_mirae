"""
SettingsDialog — 설정 팝업 (view-design §6.13, FR-5.8).

MainWindow 우측 상단 ⚙ 버튼이 띄우는 팝업. 두 가지를 담는다.
1. 다크 모드 스위치 — 기본은 시스템(Windows) 자동 추종이며, 조작 시 명시
   라이트/다크로 고정. 상태 변경은 theme_manager에 위임한다(§10.2).
2. Staff Credit — QCE 개발팀 3인 표기.

INV-V1/V2: model/controller import 금지. 테마 로직은 theme_manager가 소유하고
본 다이얼로그는 스위치 상태 동기화·위임만 한다.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QCheckBox,
    QDialog,
    QFrame,
    QLabel,
    QVBoxLayout,
)

from qce.view.style.theme import theme_manager


class SettingsDialog(QDialog):
    # (이름, 학번) — view-design §6.13 / 문서 작성 주체
    STAFF: list[tuple[str, str]] = [
        ("이대한", "20247142"),
        ("조원희", "20222047"),
        ("김휘중", "20221985"),
    ]

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("설정")
        self.setModal(True)

        root = QVBoxLayout(self)
        root.setContentsMargins(20, 18, 20, 18)
        root.setSpacing(12)

        # --- 다크 모드 스위치 ---
        title = QLabel("화면")
        title.setStyleSheet("font-weight: bold;")
        root.addWidget(title)

        self._dark_switch = QCheckBox("다크 모드")
        self._dark_switch.setChecked(theme_manager.is_dark())   # 현재 테마와 동기화
        self._dark_switch.toggled.connect(theme_manager.set_dark)
        root.addWidget(self._dark_switch)

        hint = QLabel("끄면 라이트 모드로, 켜면 다크 모드로 전환됩니다.\n"
                      "(앱 시작 시에는 Windows 설정을 자동으로 따릅니다.)")
        hint.setObjectName("placeholder")
        hint.setWordWrap(True)
        root.addWidget(hint)

        # --- 구분선 ---
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setFrameShadow(QFrame.Shadow.Sunken)
        root.addWidget(line)

        # --- Staff Credit ---
        staff_title = QLabel("Staff Credit")
        staff_title.setStyleSheet("font-weight: bold;")
        root.addWidget(staff_title)

        for name, sid in self.STAFF:
            row = QLabel(f"{name}  ·  {sid}")
            row.setAlignment(Qt.AlignmentFlag.AlignLeft)
            root.addWidget(row)

        team = QLabel("QCE — 부탁해 꼬마선장 개발팀")
        team.setObjectName("placeholder")
        root.addWidget(team)

    # --- 테스트 접근자 ---
    def is_dark_checked(self) -> bool:
        return self._dark_switch.isChecked()

    def staff_names(self) -> list[str]:
        return [name for name, _sid in self.STAFF]
