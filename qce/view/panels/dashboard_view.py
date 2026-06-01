"""
DashboardView — 3차트 컨테이너 + 차트간 Signal 중재자 (view-design §6.6, FR-5.1).

세 차트를 합성하고, 산점도 클릭(member_selected)을 레이더(highlight_member)로
중재한다(결정 B; INV-V4 — 차트는 서로를 직접 참조하지 않는다). AnomalySignalDetector
출력(표시 전용 신호 목록)을 가벼운 라벨로 노출한다.
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from qce.view.charts.bar_chart import BarChartWidget
from qce.view.charts.radar_chart import RadarChartWidget
from qce.view.charts.scatter_chart import ScatterChartWidget
from qce.view.contract import K_ANOMALY, K_AUTHOR
from qce.view.panels.anomaly_signal_panel import AnomalySignalPanel
from qce.view.style import tokens as T


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
        self._signal_label.setObjectName("placeholder")
        self._signal_label.setWordWrap(True)

        # 이상 신호 카드 패널(FR-4.2/4.2b/4.2d). dismiss는 상위로 중계만 한다(INV-V1).
        self.signals_panel = AnomalySignalPanel()
        self.signals_panel.signal_dismissed.connect(self.signal_dismissed)

        # [v3.0] 세로 1열 배치: 막대 → 산점도 → 레이더 → 이상 신호. 각 그래프에 의미
        # 타이틀을 달고(요구사항 3-2), 차트마다 최소 높이를 고정해 데이터 양과 무관하게
        # 화면 내 비율을 유지한다(요구사항 4 — 스크롤로 천천히 읽는 구성).
        self.bar.setMinimumHeight(360)
        self.scatter.setMinimumHeight(420)
        self.radar.setMinimumHeight(440)

        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(T.SPACING_SECTION * 2)

        self._add_chart_section(
            root, "팀원별 종합 기여도",
            "가중치를 반영한 종합 점수를 팀원별 막대로 비교합니다. (1위 강조 · 팀 평균선)",
            self.bar,
        )
        self._add_chart_section(
            root, "기여 성향 분포 (산점도)",
            "두 지표를 축으로, 세 번째 지표를 색으로 나타낸 분포입니다. 점을 누르면 레이더가 강조됩니다.",
            self.scatter,
        )
        self._add_chart_section(
            root, "세부 역량 레이더",
            "Git·문서·메신저 세부 지표를 종합/개인 레이더로 펼쳐 봅니다.",
            self.radar,
        )

        # 이상 신호 섹션 — 타이틀은 패널 자체(signalPanelTitle)가 가지므로 요약 라벨만 함께 둔다.
        signal_box = QVBoxLayout()
        signal_box.setSpacing(T.SPACING_SM)
        signal_box.addWidget(self._signal_label)
        signal_box.addWidget(self.signals_panel)
        root.addLayout(signal_box)

    def _add_chart_section(self, layout, title: str, hint: str, chart) -> None:
        """그래프 위에 섹션 타이틀·설명을 얹어 한 묶음으로 추가(요구사항 3-2)."""
        box = QVBoxLayout()
        box.setSpacing(T.SPACING_SM)
        title_lbl = QLabel(title)
        title_lbl.setObjectName("sectionTitle")
        box.addWidget(title_lbl)
        hint_lbl = QLabel(hint)
        hint_lbl.setObjectName("sectionHint")
        hint_lbl.setWordWrap(True)
        box.addWidget(hint_lbl)
        box.addWidget(chart)
        layout.addLayout(box)

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
