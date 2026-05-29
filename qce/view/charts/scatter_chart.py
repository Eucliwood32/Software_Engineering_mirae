"""
ScatterChartWidget — X=Git, Y=문서, 점 크기=메신저 (view-design §7.4, FR-5.1c).

사분면 4색+레이블, 평균 십자선, 라벨 겹침 4방향 해소, fade-in 애니메이션,
하위 이상치 점 붉은색. 점 클릭 시 member_selected(author) 발행(결정 B).
"""
from __future__ import annotations

import math

from PyQt6.QtCore import pyqtSignal

from qce.view.charts.base_chart import BaseChartWidget
from qce.view.contract import (
    K_ANOMALY,
    K_AUTHOR,
    K_DOC,
    K_GIT,
    K_MSG,
    SRC_MSG,
)
from qce.view.style import tokens as T

_QUADRANT_LABELS = ["올라운더", "개발 집중", "문서 집중", "저참여"]
_MIN_LABEL_DIST = 30.0   # px (FR-5.1c 라벨 최소거리)


class ScatterChartWidget(BaseChartWidget):
    member_selected = pyqtSignal(str)
    DOT_MIN = T.DOT_MIN
    DOT_MAX = T.DOT_MAX
    DOT_MISSING = T.DOT_MISSING

    def _render_static(self) -> None:
        self.ax.clear()
        self.ax.set_xlim(0.0, 1.0)
        self.ax.set_ylim(0.0, 1.0)
        self.ax.set_xlabel("Git 점수")
        self.ax.set_ylabel("문서 점수")

        gits = [float(m[K_GIT]) for m in self._scores]
        docs = [float(m[K_DOC]) for m in self._scores]
        self._mean_x = sum(gits) / len(gits) if gits else 0.5
        self._mean_y = sum(docs) / len(docs) if docs else 0.5

        # 점 크기·색상 (최종값; 애니는 progress로 스케일)
        self._final_sizes: dict[str, float] = {}
        self._final_size_list: list[float] = []
        colors: list[str] = []
        for m in self._scores:
            size = self._compute_size(m)
            self._final_sizes[m[K_AUTHOR]] = size
            self._final_size_list.append(size)
            colors.append(T.COLOR_ANOMALY if m[K_ANOMALY] else T.COLOR_PRIMARY)
        self._colors = colors

        self._draw_quadrants()

        # 평균 십자선
        self._mean_x = self._mean_x
        self.ax.axvline(self._mean_x, linestyle="--", color=T.COLOR_AVG_LINE, linewidth=1.0)
        self.ax.axhline(self._mean_y, linestyle="--", color=T.COLOR_AVG_LINE, linewidth=1.0)
        self.ax.plot(self._mean_x, self._mean_y, marker="+", color=T.COLOR_AVG_LINE, markersize=10)

        self._scatter = self.ax.scatter(
            gits, docs, s=[0.0] * len(self._scores), c=colors, zorder=3, picker=True
        )

        self._resolve_label_overlap()
        self._draw_labels()

    def _compute_size(self, m: dict) -> float:
        if SRC_MSG in self._missing:
            return self.DOT_MISSING            # 메신저 결측 시 80pt 고정
        msg = float(m[K_MSG])
        return self.DOT_MIN + (self.DOT_MAX - self.DOT_MIN) * msg

    def _draw_quadrants(self) -> None:
        mx, my = self._mean_x, self._mean_y
        # (좌하/우하/좌상/우상) → 라벨 매핑
        regions = [
            ("올라운더", (mx, 1.0), (my, 1.0)),    # 우상: Git↑ 문서↑
            ("개발 집중", (mx, 1.0), (0.0, my)),    # 우하: Git↑ 문서↓
            ("문서 집중", (0.0, mx), (my, 1.0)),    # 좌상: Git↓ 문서↑
            ("저참여", (0.0, mx), (0.0, my)),       # 좌하: Git↓ 문서↓
        ]
        self._quadrant_texts = []
        for label, (x0, x1), (y0, y1) in regions:
            color = T.QUADRANT_COLORS[label]
            self.ax.add_patch(
                __import__("matplotlib.patches", fromlist=["Rectangle"]).Rectangle(
                    (x0, y0), x1 - x0, y1 - y0, color=color, alpha=0.0, zorder=0
                )
            )
            txt = self.ax.text(
                (x0 + x1) / 2, (y0 + y1) / 2, label,
                ha="center", va="center", color=T.COLOR_MUTED, fontsize=9, zorder=1,
            )
            self._quadrant_texts.append(txt)

    def _resolve_label_overlap(self) -> None:
        """라벨 위치를 display(px) 좌표에서 최소 30px 이상 떨어지도록 분리."""
        self.canvas.draw()      # transData 유효화
        disp = [
            list(self.ax.transData.transform((float(m[K_GIT]), float(m[K_DOC]))))
            for m in self._scores
        ]
        # 점 우측상단으로 약간 오프셋해 시작
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
            t = self.ax.text(dx, dy, m[K_AUTHOR], fontsize=8, zorder=4)
            self._name_texts.append(t)

    def _draw_frame(self, progress: float) -> None:
        sizes = [s * progress for s in self._final_size_list]
        self._scatter.set_sizes(sizes)
        self.canvas.draw_idle()

    def _on_pick(self, event) -> None:
        if self._animating:        # 애니 중 무시 (INV-V5)
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
        # 9항목 (view-design §7.4)
        return "\n".join(
            [
                f"{m[K_AUTHOR]}",
                f"Git 정규화 {float(m[K_GIT]):.2f}",
                f"Git 원시 {m.get('raw_additions', 0)}",
                f"Capping {'발동' if m.get(K_ANOMALY) else '미발동'}",
                f"문서 정규화 {float(m[K_DOC]):.2f}",
                f"문서 원시 {m.get('raw_chars', 0)}",
                f"메신저 정규화 {float(m[K_MSG]):.2f}",
                f"메신저 원시 {m.get('raw_messages', 0)}",
                f"종합 {float(m.get('total_score', 0.0)):.2f}",
            ]
        )

    # ------------------------------------------------------------------ #
    # 테스트 접근자
    # ------------------------------------------------------------------ #
    @property
    def quadrant_labels(self) -> list[str]:
        return list(_QUADRANT_LABELS)

    def dot_size(self, author: str) -> float:
        return self._final_sizes.get(author, 0.0)

    @property
    def crosshair_xy(self) -> tuple[float, float]:
        return (self._mean_x, self._mean_y)

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
        """테스트용 점 클릭 모사 → member_selected 발행(애니 중 무시)."""
        if self._animating:
            return
        self.member_selected.emit(self._scores[index][K_AUTHOR])
