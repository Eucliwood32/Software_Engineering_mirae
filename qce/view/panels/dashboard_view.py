"""
DashboardView — 3차트 컨테이너 + 차트간 Signal 중재자 (view-design §6.6, FR-5.1).

세 차트를 합성하고, 산점도 클릭(member_selected)을 레이더(highlight_member)로
중재한다(결정 B; INV-V4 — 차트는 서로를 직접 참조하지 않는다). AnomalySignalDetector
출력(표시 전용 신호 목록)을 가벼운 라벨로 노출한다.
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QGridLayout, QLabel, QVBoxLayout, QWidget

from qce.view.charts.bar_chart import BarChartWidget
from qce.view.charts.radar_chart import RadarChartWidget
from qce.view.charts.scatter_chart import ScatterChartWidget
from qce.view.contract import K_ANOMALY, K_AUTHOR
from qce.view.panels.anomaly_signal_panel import AnomalySignalPanel


class DashboardView(QWidget):
    signal_dismissed = pyqtSignal(str, str, str)     # (author, type, ref) 중계

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.bar = BarChartWidget()
        self.radar = RadarChartWidget()
        self.scatter = ScatterChartWidget()

        # 차트간 연동 중재 (INV-V4): scatter는 radar를 모른다.
        self.scatter.member_selected.connect(self.radar.highlight_member)

        self._signal_label = QLabel("")
        self._signal_label.setWordWrap(True)

        # 이상 신호 카드 패널(FR-4.2/4.2b/4.2d). dismiss는 상위로 중계만 한다(INV-V1).
        self.signals_panel = AnomalySignalPanel()
        self.signals_panel.signal_dismissed.connect(self.signal_dismissed)

        grid = QGridLayout()
        grid.addWidget(self.bar, 0, 0)
        grid.addWidget(self.radar, 0, 1)
        grid.addWidget(self.scatter, 1, 0, 1, 2)

        root = QVBoxLayout(self)
        root.addLayout(grid)
        root.addWidget(self._signal_label)
        root.addWidget(self.signals_panel)

    def render(self, scores: list[dict], missing: set[str]) -> None:
        """세 차트 동시 갱신. 각 차트에 동일 scores·missing 전달."""
        self.bar.render(scores, missing)
        self.radar.render(scores, missing)
        self.scatter.render(scores, missing)
        self._update_signal_label(scores)
        self.signals_panel.render(scores)

    def show_placeholder(self) -> None:
        self.bar.show_placeholder()
        self.radar.show_placeholder()
        self.scatter.show_placeholder()
        self._signal_label.setText("")
        self.signals_panel.render([])

    def _update_signal_label(self, scores: list[dict]) -> None:
        items = []
        for m in scores:
            flags = m.get(K_ANOMALY) or []
            if flags:
                items.append(f"{m[K_AUTHOR]}: {', '.join(flags)}")
        self._signal_label.setText("  |  ".join(items))

    # --- 테스트 접근자 ---
    def signal_text(self) -> str:
        return self._signal_label.text()
