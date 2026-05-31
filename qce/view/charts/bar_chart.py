"""
BarChartWidget — 팀원별 종합 기여 지표 막대 (view-design §7.2, FR-5.1a).

Y축 0.0~1.0 고정, 그리드 0.2, 1위 강조색, 평균선, 수치 레이블, 6항목 툴팁,
하단→최종 높이 상승 애니메이션.
"""
from __future__ import annotations

from matplotlib.ticker import MultipleLocator

from qce.view.charts.base_chart import BaseChartWidget
from qce.view.contract import (
    K_AUTHOR,
    K_CAPPING,
    K_DOC,
    K_GIT,
    K_MSG,
    K_TOTAL,
    K_RAW_ADD,
    K_RAW_CHAR,
    K_RAW_MSG,
)
from qce.view.style import tokens as T


class BarChartWidget(BaseChartWidget):
    def _render_static(self) -> None:
        self.ax.clear()
        self.ax.set_axis_on()

        authors = [m[K_AUTHOR] for m in self._scores]
        totals = [float(m[K_TOTAL]) for m in self._scores]
        xs = list(range(len(authors)))

        self.ax.set_ylim(0.0, 1.0)              # Y 0.0~1.0 고정
        self.ax.set_xticks(xs)
        self.ax.set_xticklabels(authors)
        self.ax.yaxis.set_major_locator(MultipleLocator(T.GRID_STEP))  # 그리드 0.2
        self.ax.grid(axis="y", color=T.COLOR_GRID, linewidth=0.6, zorder=0)

        # 1위 강조색 + 나머지 기본색
        top_idx = max(xs, key=lambda i: totals[i]) if totals else -1
        colors = [T.COLOR_PRIMARY if i == top_idx else T.COLOR_BAR_DEFAULT for i in xs]

        self._bars = self.ax.bar(xs, [0.0] * len(authors), color=colors, zorder=3)
        self._totals: dict[str, float] = dict(zip(authors, totals))
        self._avg = (sum(totals) / len(totals)) if totals else 0.0
        self._value_texts: list = []

        self._draw_average_line()

    def _draw_average_line(self) -> None:
        self.ax.axhline(self._avg, linestyle="--", color=T.COLOR_AVG_LINE, linewidth=1.2)
        self.ax.text(
            len(self._scores) - 0.4, self._avg + 0.02,
            f"팀 평균: {self._avg:.2f}",
            color=T.COLOR_AVG_LINE, ha="right", va="bottom", fontsize=9,
        )

    def _draw_frame(self, progress: float) -> None:
        for text in self._value_texts:
            text.remove()
        self._value_texts = []

        for bar, m in zip(self._bars, self._scores):
            h = float(m[K_TOTAL]) * progress
            bar.set_height(h)
            # 막대 상단 수치 레이블(소수점 2자리)
            t = self.ax.text(
                bar.get_x() + bar.get_width() / 2, h + 0.01,
                f"{float(m[K_TOTAL]):.2f}",
                ha="center", va="bottom", fontsize=9,
            )
            self._value_texts.append(t)

        self.canvas.draw_idle()

    def _build_tooltip(self, m: dict) -> str:
        return "\n".join(self._tooltip_fields(m))

    @staticmethod
    def _tooltip_fields(m: dict) -> list[str]:
        return [
            f"{m[K_AUTHOR]}",
            f"Git {float(m[K_GIT]):.2f} (코드 양: {m.get(K_RAW_ADD, 0)})",
            f"문서 {float(m[K_DOC]):.2f} (문서 양: {m.get(K_RAW_CHAR, 0)})",
            f"메신저 {float(m[K_MSG]):.2f} (대화 수: {m.get(K_RAW_MSG, 0)})",
            f"종합 {float(m[K_TOTAL]):.2f}",
            f"Capping {'발동' if m[K_CAPPING] else '미발동'}",
        ]

    # ------------------------------------------------------------------ #
    # 테스트 접근자
    # ------------------------------------------------------------------ #
    @property
    def average_line_y(self) -> float:
        return self._avg

    def bar_height(self, author: str) -> float:
        return self._totals.get(author, 0.0) * self._progress

    def tooltip_fields(self, author: str) -> list[str]:
        m = next(s for s in self._scores if s[K_AUTHOR] == author)
        return self._tooltip_fields(m)
