"""
RadarChartWidget — Git/문서/메신저 3축 레이더 (view-design §7.3, FR-5.1b).

팀원 N개 + 팀 평균 1개 = (N+1) 폴리곤, 범례 토글, 결측 축 점선+"(제외됨)",
중심→최종 확장 애니메이션. 산점도 클릭을 받아 폴리곤 1.5초 하이라이트(결정 B).
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QTimer

from qce.view.charts.base_chart import BaseChartWidget
from qce.view.contract import (
    K_AUTHOR,
    K_DOC,
    K_GIT,
    K_MSG,
    SRC_DOC,
    SRC_GIT,
    SRC_MSG,
    K_RAW_ADD,
    K_RAW_CHAR,
    K_RAW_MSG,
)
from qce.view.style import tokens as T

# 축 순서: Git / 문서 / 메신저 (점수 dict 키와 결측 소스명 매핑)
_AXIS_SPEC = [
    ("Git", K_GIT, SRC_GIT),
    ("문서", K_DOC, SRC_DOC),
    ("메신저", K_MSG, SRC_MSG),
]


class RadarChartWidget(BaseChartWidget):
    AXIS_LABELS = ["Git", "문서", "메신저"]
    HIGHLIGHT_MS = 1500

    def _create_axes(self) -> None:
        self.ax = self.figure.add_subplot(111, projection="polar")

    def _render_static(self) -> None:
        self.ax.clear()
        n_axes = len(self.AXIS_LABELS)
        # 각 축 각도 (꼭짓점)
        self._angles = [i / n_axes * 2 * math.pi for i in range(n_axes)]

        self.ax.set_theta_offset(math.pi / 2)
        self.ax.set_theta_direction(-1)
        self.ax.set_ylim(0.0, 1.0)
        self.ax.set_yticks([T.GRID_STEP * k for k in range(1, 6)])  # 0.2 간격 5단계
        self.ax.set_yticklabels([])
        self.ax.set_xticks(self._angles)

        # 결측 축은 "(제외됨)" 라벨 + 점선 표기
        self._excluded_axis_labels: list[str] = []
        tick_labels: list[str] = []
        for label, _key, src in _AXIS_SPEC:
            if src in self._missing:
                marked = f"{label} (제외됨)"
                tick_labels.append(marked)
                self._excluded_axis_labels.append(marked)
            else:
                tick_labels.append(label)
        self.ax.set_xticklabels(tick_labels)

        # 팀 평균 폴리곤(회색 점선) + 팀원 폴리곤
        self._draw_team_average()
        self._member_lines = []      # (line, fill) per member
        self._base_radii = []        # 최종 반경 목록 (애니 스케일 대상)
        for m in self._scores:
            radii = [float(m[key]) for _label, key, _src in _AXIS_SPEC]
            self._base_radii.append(radii)
            closed_theta = self._angles + [self._angles[0]]
            closed_r = [0.0] * (n_axes + 1)
            (line,) = self.ax.plot(closed_theta, closed_r, linewidth=1.8, zorder=3)
            fill = self.ax.fill(closed_theta, closed_r, alpha=0.08, zorder=2)[0]
            self._member_lines.append((line, fill))

        self.ax.legend(
            [ln for ln, _f in self._member_lines] + [self._avg_line],
            [m[K_AUTHOR] for m in self._scores] + ["팀 평균"],
            loc="upper right", bbox_to_anchor=(1.25, 1.1), fontsize=8,
        )

    def _draw_team_average(self) -> None:
        avg = []
        for _label, key, _src in _AXIS_SPEC:
            vals = [float(m[key]) for m in self._scores]
            avg.append(sum(vals) / len(vals) if vals else 0.0)
        closed_theta = self._angles + [self._angles[0]]
        closed_r = avg + [avg[0]]
        (self._avg_line,) = self.ax.plot(
            closed_theta, closed_r, linestyle="--", color=T.COLOR_AVG_LINE,
            linewidth=1.5, zorder=4,
        )

    def _draw_frame(self, progress: float) -> None:
        closed_theta = self._angles + [self._angles[0]]
        for (line, fill), radii in zip(self._member_lines, self._base_radii):
            scaled = [r * progress for r in radii]
            closed_r = scaled + [scaled[0]]
            line.set_data(closed_theta, closed_r)
            fill.set_xy(list(zip(closed_theta, closed_r)))
        self.canvas.draw_idle()

    def toggle_member(self, index: int) -> None:
        """범례 클릭 슬롯. 해당 폴리곤 visible 토글."""
        line, fill = self._member_lines[index]
        vis = not line.get_visible()
        line.set_visible(vis)
        fill.set_visible(vis)
        self.canvas.draw_idle()

    def highlight_member(self, author: str) -> None:
        """산점도 연동 슬롯(INV-V4). 굵기 2배로 1.5초 강조 후 원복."""
        for (line, _fill), m in zip(self._member_lines, self._scores):
            if m[K_AUTHOR] == author:
                orig = line.get_linewidth()
                line.set_linewidth(orig * 2)
                self.canvas.draw_idle()
                QTimer.singleShot(
                    self.HIGHLIGHT_MS, lambda ln=line, w=orig: self._restore_width(ln, w)
                )
                break

    def _restore_width(self, line, width: float) -> None:
        line.set_linewidth(width)
        self.canvas.draw_idle()

    def _build_tooltip(self, m: dict, axis: str = "") -> str:
        base = f"{m[K_AUTHOR]} · {axis}"
        return f"{base}\nGit 코드: {m.get(K_RAW_ADD, 0)}\n문서 양: {m.get(K_RAW_CHAR, 0)}\n메신저 대화: {m.get(K_RAW_MSG, 0)}"

    # ------------------------------------------------------------------ #
    # 테스트 접근자
    # ------------------------------------------------------------------ #
    @property
    def axis_labels(self) -> list[str]:
        return list(self.AXIS_LABELS)

    def is_polygon_visible(self, index: int) -> bool:
        line, _fill = self._member_lines[index]
        return bool(line.get_visible())

    def member_linewidth(self, index: int) -> float:
        line, _fill = self._member_lines[index]
        return float(line.get_linewidth())

    @property
    def excluded_axis_labels(self) -> list[str]:
        return list(getattr(self, "_excluded_axis_labels", []))
