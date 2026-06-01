"""
ScatterChartWidget — 가용 데이터 수 기반 동적 산점도 (view-design §7.4, FR-5.1c).

데이터 개수에 따라 표시 방식이 변한다:
(1개) 회색 텍스트 "자료가 한 종류인 경우 산점도가 계산되지 않습니다."
(2개) Y축 첫 번째/X축 두 번째 소스
(3개) Y축 첫 번째/X축 두 번째 소스 + 점 색상(채도) 세 번째 소스 비례.
십자선(해당 축 평균), 동적 툴팁, 라벨 겹침 4방향 해소, fade-in 애니메이션,
하위 이상치 점 경고 ⚠. 점 클릭 시 member_selected(author) 발행(결정 B).
"""
from __future__ import annotations

import math

from matplotlib.colors import LinearSegmentedColormap, to_rgba
from matplotlib.cm import ScalarMappable
from PyQt6.QtCore import pyqtSignal

from qce.view.charts.base_chart import BaseChartWidget
from qce.view.contract import (
    K_ANOMALY,
    K_AUTHOR,
    K_DOC,
    K_GIT,
    K_MSG,
    K_RAW_ADD,
    K_RAW_CHAR,
    K_RAW_MSG,
    SRC_DOC,
    SRC_GIT,
    SRC_MSG,
)
from qce.view.style import tokens as T

_MIN_LABEL_DIST = 30.0   # px (FR-5.1c 라벨 최소거리)

# 가용 소스 우선순위 및 레이블 매핑 (Git -> 문서 -> 메신저)
_SRC_KEYS = [K_GIT, K_DOC, K_MSG]
_SRC_LABELS = {
    K_GIT: ("Git", K_RAW_ADD, "추가 라인"),
    K_DOC: ("문서", K_RAW_CHAR, "글자수"),
    K_MSG: ("메신저", K_RAW_MSG, "발화 수"),
}
_SRC_IDENTIFIERS = {
    K_GIT: SRC_GIT,
    K_DOC: SRC_DOC,
    K_MSG: SRC_MSG,
}

# 컨트롤러가 전달하는 missing set의 한국어 명칭과 테스트용 영어 명칭 모두 대응
_MISSING_ALIASES = {
    K_GIT: {SRC_GIT, "Git", "git"},
    K_DOC: {SRC_DOC, "문서", "doc"},
    K_MSG: {SRC_MSG, "메신저", "messenger"},
}

class ScatterChartWidget(BaseChartWidget):
    member_selected = pyqtSignal(str)
    DOT_SIZE = 80.0

    def _render_static(self) -> None:
        self.ax.clear()
        self._style_axes(self.ax)

        # 기존 컬러바 제거 (반복 렌더링 시 중첩 방지)
        if hasattr(self, "_cbar") and self._cbar is not None:
            try:
                self._cbar.remove()
            except Exception:
                pass
            self._cbar = None

        # 가용 소스 판별
        self._available_keys = []
        for k in _SRC_KEYS:
            # missing set에 컨트롤러 방식("Git")이나 테스트 방식(SRC_GIT)이 들어있으면 누락 처리
            if not (_MISSING_ALIASES[k] & self._missing):
                self._available_keys.append(k)

        if len(self._available_keys) < 2:
            self.ax.set_facecolor(T.COLOR_CANVAS)
            self.ax.set_axis_off()
            self.ax.text(
                0.5, 0.5, "자료가 한 종류인 경우 산점도가 계산되지 않습니다.",
                ha="center", va="center", color=T.COLOR_TEXT_MUTED,
                transform=self.ax.transAxes,
            )
            self._label_positions = []
            self._final_colors: list[tuple[float, float, float, float]] = []
            self._mean_x = 0.5
            self._mean_y = 0.5
            self._final_saturations: dict[str, float] = {}
            return

        self.ax.set_axis_on()
        self.ax.set_xlim(0.0, 1.0)
        self.ax.set_ylim(0.0, 1.0)

        # 2개 이상일 경우 매핑 (Y: 0, X: 1, Saturation: 2)
        y_key = self._available_keys[0]
        x_key = self._available_keys[1]
        self.ax.set_ylabel(f"{_SRC_LABELS[y_key][0]} 점수")
        self.ax.set_xlabel(f"{_SRC_LABELS[x_key][0]} 점수")

        x_vals = [float(m[x_key]) for m in self._scores]
        y_vals = [float(m[y_key]) for m in self._scores]

        self._mean_x = sum(x_vals) / len(x_vals) if x_vals else 0.5
        self._mean_y = sum(y_vals) / len(y_vals) if y_vals else 0.5

        # 십자선 (axvline/axhline 사용)
        self.ax.axvline(x=self._mean_x, color=T.COLOR_AVG_LINE, linestyle="--", linewidth=1.0, zorder=1)
        self.ax.axhline(y=self._mean_y, color=T.COLOR_AVG_LINE, linestyle="--", linewidth=1.0, zorder=1)
        self.ax.plot(self._mean_x, self._mean_y, marker="+", color=T.COLOR_AVG_LINE, markersize=10, zorder=1)

        # 색상 및 불투명도 계산
        self._final_colors = []
        self._final_saturations: dict[str, float] = {}

        if len(self._available_keys) >= 3:
            s_key = self._available_keys[2]
            
            # 컬러맵 및 컬러바 생성 (알파 투명도 대신 두 색상의 보간으로 그라데이션)
            c_min = to_rgba("#fbbc04")  # 노란색 (최소)
            c_max = to_rgba("#9c27b0")  # 보라색 (최대)
            
            def mix_colors(c1, c2, ratio):
                # ratio 0.0 -> c2 (min), ratio 1.0 -> c1 (max)
                return (
                    c1[0] * ratio + c2[0] * (1 - ratio),
                    c1[1] * ratio + c2[1] * (1 - ratio),
                    c1[2] * ratio + c2[2] * (1 - ratio),
                    1.0
                )
            
            cmap = LinearSegmentedColormap.from_list("gradient_cmap", [c_min, c_max])
            sm = ScalarMappable(cmap=cmap)
            sm.set_array([])
            self._cbar = self.figure.colorbar(sm, ax=self.ax)
            self._cbar.set_label(f"{_SRC_LABELS[s_key][0]} 점수")
            self._cbar.ax.yaxis.label.set_color(T.COLOR_TEXT)
            self._cbar.ax.tick_params(colors=T.COLOR_TEXT)

            for m in self._scores:
                val = float(m[s_key])
                color = mix_colors(c_max, c_min, val)
                self._final_colors.append(color)
                self._final_saturations[m[K_AUTHOR]] = val
        else:
            for m in self._scores:
                # 2개 소스인 경우 기존처럼 붉은색 이상치 표시 허용 (통일 안 함)
                c_str = T.COLOR_ANOMALY if m.get(K_ANOMALY) else T.COLOR_PRIMARY
                self._final_colors.append(to_rgba(c_str))
                self._final_saturations[m[K_AUTHOR]] = 1.0

        # 초기에는 완전 투명하게 생성하고 테두리 색상도 _draw_frame에서 관리 (fade-in 애니메이션용)
        self._scatter = self.ax.scatter(
            x_vals, y_vals, s=[self.DOT_SIZE] * len(self._scores), 
            facecolors=[(0, 0, 0, 0)] * len(self._scores), 
            edgecolors=[(0, 0, 0, 0)] * len(self._scores), 
            zorder=3, picker=True
        )

        self._resolve_label_overlap(x_vals, y_vals)
        self._draw_labels()

    def _resolve_label_overlap(self, x_vals: list[float], y_vals: list[float]) -> None:
        self.canvas.draw()
        disp = [
            list(self.ax.transData.transform((x, y)))
            for x, y in zip(x_vals, y_vals)
        ]
        labels = [[x + 8.0, y + 8.0] for x, y in disp]

        for _ in range(300):
            moved = False
            for i in range(len(labels)):
                for j in range(i + 1, len(labels)):
                    dx = labels[j][0] - labels[i][0]
                    dy = labels[j][1] - labels[i][1]
                    dist = math.hypot(dx, dy)
                    if dist < _MIN_LABEL_DIST:
                        if dist == 0.0:
                            dx, dy, dist = 1.0, 0.0, 1.0
                        push = (_MIN_LABEL_DIST - dist) / 2 + 0.5
                        ux, uy = dx / dist, dy / dist
                        labels[i][0] -= ux * push
                        labels[i][1] -= uy * push
                        labels[j][0] += ux * push
                        labels[j][1] += uy * push
                        moved = True
            if not moved:
                break
        self._label_positions = labels

    def _draw_labels(self) -> None:
        inv = self.ax.transData.inverted()
        self._name_texts = []
        for (px, py), m in zip(self._label_positions, self._scores):
            dx, dy = inv.transform((px, py))
            text_str = m[K_AUTHOR]
            if m.get(K_ANOMALY):
                text_str += " ⚠"
            t = self.ax.text(dx, dy, text_str, fontsize=8, zorder=4, color=T.COLOR_TEXT)
            self._name_texts.append(t)

    def _draw_frame(self, progress: float) -> None:
        if not hasattr(self, "_final_colors") or not self._final_colors:
            return
        
        # progress에 비례해서 최종 컬러의 alpha(불투명도)를 점진적으로 높여 fade-in 처리
        current_colors = [(r, g, b, a * progress) for r, g, b, a in self._final_colors]
        
        self._scatter.set_facecolors(current_colors)
        self._scatter.set_edgecolors(current_colors)
        self.canvas.draw_idle()

    def _on_pick(self, event) -> None:
        if self._animating:
            return
        if event.ind is not None and len(event.ind):
            self.member_selected.emit(self._scores[event.ind[0]][K_AUTHOR])

    def _connect_hover(self) -> None:
        self._pick_cid = self.canvas.mpl_connect("pick_event", self._on_pick)

    def _disconnect_hover(self) -> None:
        cid = getattr(self, "_pick_cid", None)
        if cid is not None:
            self.canvas.mpl_disconnect(cid)
            self._pick_cid = None

    def _build_tooltip(self, m: dict) -> str:
        lines = [f"{m[K_AUTHOR]}"]
        for k in _SRC_KEYS:
            if not (_MISSING_ALIASES[k] & self._missing):
                name, raw_key, raw_label = _SRC_LABELS[k]
                lines.append(f"{name} 정규화 {float(m[k]):.2f}")
                lines.append(f"{name} 원시 {m.get(raw_key, 0)} {raw_label}")
        lines.append(f"Capping {'발동' if m.get(K_ANOMALY) else '미발동'}")
        lines.append(f"종합 {float(m.get('total_score', 0.0)):.2f}")
        return "\n".join(lines)

    # ------------------------------------------------------------------ #
    # 테스트 접근자
    # ------------------------------------------------------------------ #
    def dot_color_saturation(self, author: str) -> float:
        return getattr(self, "_final_saturations", {}).get(author, 0.0)

    @property
    def crosshair_xy(self) -> tuple[float, float]:
        return (getattr(self, "_mean_x", 0.5), getattr(self, "_mean_y", 0.5))

    def min_label_distance(self) -> float:
        pts = getattr(self, "_label_positions", [])
        if len(pts) < 2:
            return float("inf")
        return min(
            math.hypot(pts[i][0] - pts[j][0], pts[i][1] - pts[j][1])
            for i in range(len(pts))
            for j in range(i + 1, len(pts))
        )

    def simulate_point_click(self, index: int) -> None:
        if self._animating:
            return
        if not hasattr(self, "_available_keys") or len(self._available_keys) < 2:
            return
        self.member_selected.emit(self._scores[index][K_AUTHOR])
