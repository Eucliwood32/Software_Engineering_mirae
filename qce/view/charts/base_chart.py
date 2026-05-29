"""
BaseChartWidget — 차트 3종의 추상 기반 (view-design §7.1).

matplotlib FigureCanvasQTAgg를 QWidget에 임베딩하고, placeholder·진입 애니메이션
타이머 골격·툴팁 골격을 끌어올린다. 하위 클래스는 "한 프레임에서 무엇을 그릴지"
(_render_static / _draw_frame)와 툴팁(_build_tooltip)만 구현한다.

INV-V1: model/controller/common import 금지 — 입력은 plain dict(list[dict]).
INV-V3: 애니메이션은 메인 스레드 QTimer로만 구동.
INV-V5: 애니메이션 진행 중 hover 툴팁 비활성.
"""
from __future__ import annotations

import matplotlib
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as Canvas
from matplotlib.figure import Figure
from PyQt6.QtCore import QTimer
from PyQt6.QtWidgets import QVBoxLayout, QWidget

from qce.view.style import tokens as T

# 한글 폰트·음수 부호 깨짐 방지 (view-design §10, C-5)
matplotlib.rcParams["font.family"] = T.FONT_FAMILY
matplotlib.rcParams["axes.unicode_minus"] = False

PLACEHOLDER_TEXT = "분석을 실행하면 결과가 표시됩니다."


class BaseChartWidget(QWidget):
    ANIM_FRAMES = 20          # FR-5.1a/b/c 공통
    ANIM_INTERVAL = 30        # ms

    def __init__(self) -> None:
        super().__init__()
        self.figure = Figure(figsize=(6.0, 4.5), tight_layout=True)
        self.canvas = Canvas(self.figure)
        self._create_axes()

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(self.canvas)

        self._scores: list[dict] = []
        self._missing: set[str] = set()

        self._anim_timer = QTimer(self)          # 메인 스레드 타이머 (INV-V3)
        self._anim_timer.setInterval(self.ANIM_INTERVAL)
        self._anim_timer.timeout.connect(self._on_anim_tick)
        self._frame = 0
        self._progress = 0.0
        self._animating = False                  # True 동안 hover 비활성 (INV-V5)

        self.show_placeholder()

    # ------------------------------------------------------------------ #
    # 공개 API
    # ------------------------------------------------------------------ #
    def render(self, scores: list[dict], missing: set[str]) -> None:
        """세 차트 공통 진입점. 데이터 세팅 → 정적 요소 렌더 → 애니메이션 시작."""
        self._scores = list(scores)
        self._missing = set(missing or set())
        if not self._scores:
            self.show_placeholder()
            return
        self._render_static()
        self._start_animation()

    def show_placeholder(self) -> None:
        """축 숨기고 중앙에 안내 문구."""
        self.ax.clear()
        self.ax.set_axis_off()
        self.ax.text(
            0.5, 0.5, PLACEHOLDER_TEXT,
            ha="center", va="center", color=T.COLOR_MUTED,
            transform=self.ax.transAxes,
        )
        self.canvas.draw_idle()

    def clear(self) -> None:
        self._scores = []
        self._missing = set()
        self.ax.clear()
        self.canvas.draw_idle()

    # ------------------------------------------------------------------ #
    # 애니메이션 골격 (결정 D)
    # ------------------------------------------------------------------ #
    def _start_animation(self) -> None:
        self._disconnect_hover()
        self._animating = True
        self._frame = 0
        self._progress = 0.0
        self._draw_frame(0.0)
        self._anim_timer.start()

    def _on_anim_tick(self) -> None:
        self._frame += 1
        self._progress = min(self._frame / self.ANIM_FRAMES, 1.0)
        self._draw_frame(self._progress)
        if self._frame >= self.ANIM_FRAMES:
            self._anim_timer.stop()
            self._progress = 1.0
            self._animating = False
            self._connect_hover()        # 종료 후 hover 활성 (INV-V5)

    def finish_animation(self) -> None:
        """테스트·즉시완료용: 남은 프레임을 동기적으로 전진(타이머 대기 없음)."""
        while self._animating:
            self._on_anim_tick()

    # ------------------------------------------------------------------ #
    # 하위 클래스 구현 지점
    # ------------------------------------------------------------------ #
    def _create_axes(self) -> None:
        self.ax = self.figure.add_subplot(111)

    def _render_static(self) -> None:           # 추상: 축·그리드 등 비애니 요소
        raise NotImplementedError

    def _draw_frame(self, progress: float) -> None:  # 추상: 프레임별 렌더
        raise NotImplementedError

    def _build_tooltip(self, member: dict) -> str:    # 추상
        return ""

    # 기본 hover 훅(하위에서 override). 기본은 무동작.
    def _connect_hover(self) -> None:
        pass

    def _disconnect_hover(self) -> None:
        pass

    # ------------------------------------------------------------------ #
    # 테스트 접근자
    # ------------------------------------------------------------------ #
    @property
    def is_animating(self) -> bool:
        return self._animating

    @property
    def animation_done(self) -> bool:
        return bool(self._scores) and not self._animating
