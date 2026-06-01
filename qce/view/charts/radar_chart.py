"""
RadarChartWidget — 가변 세부 축 레이더 (view-design §7.3, FR-5.1b).

[v1.7] 가용 소스마다 3개 세부 지표 축(소스 1·2·3개 → 3·6·9축). dimensions가
없으면 레거시 3축(Git/문서/메신저)으로 폴백.

[v2.0]
- 각 세부 축이 Git/문서/메신저 중 어디에 속하는지 눈금 라벨에 2줄로 명시.
- 범례를 전용 axes(_legend_ax)로 분리해 폴리곤과 겹치지 않게 수평 배치.
- 한 figure에 종합 레이더(전체 팀원+팀 평균)와 인원별 개인 레이더를 한 행으로
  나란히 배치: [종합 | 범례 | 개인1 | 개인2 | …].

토글·하이라이트·결측 접근자는 모두 '종합 레이더'의 폴리곤(_member_lines)을 대상으로
유지해 기존 테스트 회귀를 막는다(view-design §7.3 테스트 표면 보존).
"""
from __future__ import annotations

import math

from PyQt6.QtCore import QTimer

from qce.view.charts.base_chart import PLACEHOLDER_TEXT, BaseChartWidget
from qce.view.contract import (
    K_AUTHOR,
    K_DOC,
    K_GIT,
    K_MSG,
    K_DIMENSIONS,
    DIM_AXES,
    DIM_SOURCE_ORDER,
    SRC_DOC,
    SRC_GIT,
    SRC_MSG,
    K_RAW_ADD,
    K_RAW_CHAR,
    K_RAW_MSG,
)
from qce.view.style import tokens as T

# 레거시(폴백) 축 순서: Git / 문서 / 메신저 (점수 dict 키와 결측 소스명 매핑)
_AXIS_SPEC = [
    ("Git", K_GIT, SRC_GIT),
    ("문서", K_DOC, SRC_DOC),
    ("메신저", K_MSG, SRC_MSG),
]

# dimensions 세부 키 → 소속 소스 (축 소스 명시용 역인덱스, v2.0)
_KEY_SOURCE: dict[str, str] = {
    key: src for src, specs in DIM_AXES.items() for key, _label in specs
}


class RadarChartWidget(BaseChartWidget):
    AXIS_LABELS = ["Git", "문서", "메신저"]
    SRC_DISPLAY = {SRC_GIT: "Git", SRC_DOC: "문서", SRC_MSG: "메신저"}
    HIGHLIGHT_MS = 1500

    # ------------------------------------------------------------------ #
    # 축 구성
    # ------------------------------------------------------------------ #
    def _resolve_axes(self) -> list[tuple[str, str]] | None:
        """[v1.7] 점수 dict의 dimensions 기반 가변 세부 축. 가용 소스마다 DIM_AXES 순서로
        (축 키, 라벨) 3개를 누적해 3/6/9축을 만든다. dimensions가 없으면 None(레거시 3축)."""
        if not any(m.get(K_DIMENSIONS) for m in self._scores):
            return None
        present: set[str] = set()
        for m in self._scores:
            present |= set((m.get(K_DIMENSIONS) or {}).keys())
        axes: list[tuple[str, str]] = []
        for src in DIM_SOURCE_ORDER:
            spec = DIM_AXES[src]
            if spec[0][0] in present:        # 소스의 첫 세부 키 존재 = 해당 소스 가용
                axes.extend(spec)
        return axes or None

    def _radii_for(self, m: dict) -> list[float]:
        """현재 축 구성에 맞춰 멤버 m의 축별 반경(점수)을 추출한다."""
        if self._dynamic:
            dims = m.get(K_DIMENSIONS) or {}
            return [float(dims.get(k, 0.0)) for k in (self._axis_keys or [])]
        return [float(m[key]) for _label, key, _src in _AXIS_SPEC]

    def _build_tick_labels(self) -> list[str]:
        """[v2.0] 눈금 라벨 구성. 동적 모드는 '{소스}\\n{세부지표}', 레거시는 결측 축 표기."""
        self._excluded_axis_labels = []
        if self._dynamic:
            labels = []
            for key, label in zip(self._axis_keys or [], self._axis_labels):
                src = _KEY_SOURCE.get(key)
                disp = self.SRC_DISPLAY.get(src, "") if src else ""
                labels.append(f"{disp}\n{label}" if disp else label)
            return labels
        # 레거시 3축: 결측 축은 "(제외됨)" 라벨 표기
        tick_labels = []
        for label, _key, src in _AXIS_SPEC:
            if src in self._missing:
                marked = f"{label} (제외됨)"
                tick_labels.append(marked)
                self._excluded_axis_labels.append(marked)
            else:
                tick_labels.append(label)
        return tick_labels

    # ------------------------------------------------------------------ #
    # 렌더
    # ------------------------------------------------------------------ #
    def _render_static(self) -> None:
        self._apply_canvas_theme()
        self.figure.clear()

        axes = self._resolve_axes()
        self._dynamic = axes is not None
        self._axis_keys: list[str] | None
        if axes is not None:
            self._axis_keys = [k for k, _l in axes]
            self._axis_labels = [label for _k, label in axes]
        else:
            self._axis_keys = None
            self._axis_labels = list(self.AXIS_LABELS)

        tick_labels = self._build_tick_labels()
        n_axes = len(self._axis_labels)
        self._angles = [i / n_axes * 2 * math.pi for i in range(n_axes)]

        n_members = len(self._scores)
        # GridSpec 1행: [종합 | 범례 | 개인×N]. 범례 열에 여백을 둬 폴리곤과 분리(v2.0).
        width_ratios = [1.6, 0.8] + [1.0] * n_members
        gs = self.figure.add_gridspec(1, 2 + n_members, width_ratios=width_ratios, wspace=0.6)

        self.ax = self.figure.add_subplot(gs[0, 0], projection="polar")
        self._legend_ax = self.figure.add_subplot(gs[0, 1])
        self._legend_ax.axis("off")

        # 애니메이션 대상(종합+개인 모든 폴리곤)과 종합 폴리곤(접근자 대상)을 분리 추적.
        self._anim: list = []
        self._member_lines = []
        self._base_radii = []

        # --- 종합 레이더 ---
        self._setup_polar(self.ax, tick_labels, fontsize=8)
        self._avg_line = self._draw_team_average(self.ax)
        for m in self._scores:
            radii = self._radii_for(m)
            line, fill = self._add_polygon(self.ax, n_axes)
            self._member_lines.append((line, fill))
            self._base_radii.append(radii)
            self._anim.append((line, fill, radii))
        self.ax.set_title("종합", fontsize=10)

        # --- 분리 범례(전용 axes) ---
        self._legend_ax.legend(
            handles=[ln for ln, _f in self._member_lines] + [self._avg_line],
            labels=[m[K_AUTHOR] for m in self._scores] + ["팀 평균"],
            loc="center", fontsize=8, frameon=False,
        )

        # --- 인원별 개인 레이더 ---
        self._indiv_axes = []
        for i, m in enumerate(self._scores):
            ax_i = self.figure.add_subplot(gs[0, 2 + i], projection="polar")
            self._setup_polar(ax_i, tick_labels, fontsize=6)
            self._draw_team_average(ax_i, faint=True)
            radii = self._radii_for(m)
            color = self._member_lines[i][0].get_color()
            line, fill = self._add_polygon(ax_i, n_axes, color=color)
            self._anim.append((line, fill, radii))
            ax_i.set_title(m[K_AUTHOR], fontsize=9)
            self._indiv_axes.append(ax_i)

    def _setup_polar(self, ax, tick_labels: list[str], fontsize: int = 8) -> None:
        ax.set_theta_offset(math.pi / 2)
        ax.set_theta_direction(-1)
        ax.set_ylim(0.0, 1.0)
        ax.set_yticks([T.GRID_STEP * k for k in range(1, 6)])  # 0.2 간격 5단계
        ax.set_yticklabels([])
        ax.set_xticks(self._angles)
        ax.set_xticklabels(tick_labels, fontsize=fontsize)
        ax.grid(color=T.COLOR_GRID)
        self._style_axes(ax)

    def _add_polygon(self, ax, n_axes: int, color=None):
        """ax에 0반경 폴리곤(line+fill)을 추가하고 반환(애니메이션으로 확장)."""
        closed_theta = self._angles + [self._angles[0]]
        closed_r = [0.0] * (n_axes + 1)
        (line,) = ax.plot(closed_theta, closed_r, linewidth=1.8, zorder=3, color=color)
        fill = ax.fill(closed_theta, closed_r, alpha=0.08, zorder=2, color=line.get_color())[0]
        return line, fill

    def _draw_team_average(self, ax, faint: bool = False):
        per_member = [self._radii_for(m) for m in self._scores]
        n_axes = len(self._axis_labels)
        avg = []
        for j in range(n_axes):
            vals = [r[j] for r in per_member]
            avg.append(sum(vals) / len(vals) if vals else 0.0)
        closed_theta = self._angles + [self._angles[0]]
        closed_r = avg + [avg[0]]
        (line,) = ax.plot(
            closed_theta, closed_r, linestyle="--", color=T.COLOR_AVG_LINE,
            linewidth=1.0 if faint else 1.5, alpha=0.4 if faint else 1.0, zorder=4,
        )
        return line

    def _draw_frame(self, progress: float) -> None:
        closed_theta = self._angles + [self._angles[0]]
        for line, fill, radii in self._anim:
            scaled = [r * progress for r in radii]
            closed_r = scaled + [scaled[0]]
            line.set_data(closed_theta, closed_r)
            fill.set_xy(list(zip(closed_theta, closed_r)))
        self.canvas.draw_idle()

    # ------------------------------------------------------------------ #
    # placeholder (다중 subplot 잔상 방지 위해 figure 초기화 후 단일 축)
    # ------------------------------------------------------------------ #
    def show_placeholder(self) -> None:
        self._apply_canvas_theme()
        self.figure.clear()
        self.ax = self.figure.add_subplot(111)
        self.ax.set_facecolor(T.COLOR_SURFACE)
        self.ax.set_axis_off()
        self.ax.text(
            0.5, 0.5, PLACEHOLDER_TEXT,
            ha="center", va="center", color=T.COLOR_MUTED,
            transform=self.ax.transAxes,
        )
        self.canvas.draw_idle()

    # ------------------------------------------------------------------ #
    # 상호작용 (종합 레이더 폴리곤 대상)
    # ------------------------------------------------------------------ #
    def toggle_member(self, index: int) -> None:
        """범례 클릭 슬롯. 종합 레이더 해당 폴리곤 visible 토글."""
        line, fill = self._member_lines[index]
        vis = not line.get_visible()
        line.set_visible(vis)
        fill.set_visible(vis)
        self.canvas.draw_idle()

    def highlight_member(self, author: str) -> None:
        """산점도 연동 슬롯(INV-V4). 종합 폴리곤 굵기 2배로 1.5초 강조 후 원복."""
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
        """현재 렌더된 순수 축 라벨(소스 접두 없음). 동적이면 세부 축(3/6/9), 폴백/렌더 전이면 3축."""
        return list(getattr(self, "_axis_labels", self.AXIS_LABELS))

    def is_polygon_visible(self, index: int) -> bool:
        line, _fill = self._member_lines[index]
        return bool(line.get_visible())

    def member_linewidth(self, index: int) -> float:
        line, _fill = self._member_lines[index]
        return float(line.get_linewidth())

    @property
    def excluded_axis_labels(self) -> list[str]:
        return list(getattr(self, "_excluded_axis_labels", []))
