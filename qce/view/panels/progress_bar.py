"""
ProgressBar — 분석 진행률 표시 (view-design §6.8, NFR-1.1).

분석 시작 시 출현(0%), 진행 중 갱신, 완료/오류 시 소멸. Controller가 Worker의
progress Signal을 받아 set_value로 전달한다(Worker가 직접 호출하지 않음, INV-V3).
"""
from __future__ import annotations

from PyQt6.QtWidgets import QProgressBar, QVBoxLayout, QWidget


class ProgressBar(QWidget):
    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._bar = QProgressBar()
        self._bar.setRange(0, 100)
        self._bar.setValue(0)
        layout.addWidget(self._bar)
        self.setVisible(False)

    def start(self) -> None:
        self._bar.setValue(0)
        self.setVisible(True)

    def set_value(self, pct: int) -> None:
        self._bar.setValue(max(0, min(100, int(pct))))

    def finish(self) -> None:
        self.setVisible(False)

    # --- 테스트 접근자 ---
    def value(self) -> int:
        return self._bar.value()

    def is_running(self) -> bool:
        return self.isVisible()
