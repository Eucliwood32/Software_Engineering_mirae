"""
AnalysisPanel — 가중치 프리셋·슬라이더·합계 검증 표시 (view-design §6.5, FR-4.4).

프리셋 버튼 3개 + 슬라이더 3개(0.00~1.00, step 0.05) + 합계 라벨 + [분석 시작].

합계==1.0 판정 로직은 Model(WeightPresetManager)의 책임이다(§6.5). 본 패널은
슬라이더 변경 시 weights_changed를 발행하고, Controller가 검증 결과를
set_analyze_enabled/set_weight_warning으로 되돌려준다. View는 합계 계산 로직을
보유하지 않는다(합계 라벨은 단순 표시용).
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QSlider,
    QVBoxLayout,
    QWidget,
)

_STEP = 0.05
_TICKS = 20  # 0.00~1.00을 0.05 단위 → 21 포지션(0..20)


class AnalysisPanel(QWidget):
    weights_changed = pyqtSignal(dict)
    preset_chosen = pyqtSignal(str)
    analyze_clicked = pyqtSignal()

    PRESETS: dict[str, tuple[float, float, float]] = {
        "개발 중심": (0.60, 0.25, 0.15),
        "기획 중심": (0.20, 0.60, 0.20),
        "균형 설정": (0.40, 0.40, 0.20),
    }

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)

        # 프리셋 버튼
        preset_row = QHBoxLayout()
        for name in self.PRESETS:
            btn = QPushButton(name)
            btn.clicked.connect(lambda _checked=False, n=name: self.apply_preset(n))
            preset_row.addWidget(btn)
        root.addLayout(preset_row)

        # 슬라이더 3개 (git/doc/msg)
        self._sliders: dict[str, QSlider] = {}
        self._value_labels: dict[str, QLabel] = {}
        for key, label in (("w_git", "Git"), ("w_doc", "문서"), ("w_msg", "메신저")):
            row = QHBoxLayout()
            row.addWidget(QLabel(label))
            s = QSlider(Qt.Orientation.Horizontal)
            s.setRange(0, _TICKS)
            s.setSingleStep(1)
            s.setPageStep(1)
            # valueChanged 대신 사용자 조작인 sliderMoved에 연결
            s.sliderMoved.connect(lambda val, k=key: self._on_slider_dragged(k, val))
            self._sliders[key] = s
            row.addWidget(s)

            v_label = QLabel("0.00")
            v_label.setMinimumWidth(35)
            v_label.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
            self._value_labels[key] = v_label
            row.addWidget(v_label)

            root.addLayout(row)

        self._sum_label = QLabel("")
        root.addWidget(self._sum_label)

        self._warning_label = QLabel("")
        self._warning_label.setObjectName("weightWarning")
        self._warning_label.setVisible(False)
        root.addWidget(self._warning_label)

        self._analyze_btn = QPushButton("분석 시작")
        self._analyze_btn.setObjectName("primary")
        self._analyze_btn.clicked.connect(self.analyze_clicked.emit)
        root.addWidget(self._analyze_btn)

        self._refresh_sum_label()

    # ------------------------------------------------------------------ #
    # 공개 API
    # ------------------------------------------------------------------ #
    def apply_preset(self, name: str) -> None:
        w_git, w_doc, w_msg = self.PRESETS[name]
        self._set_silently("w_git", w_git)
        self._set_silently("w_doc", w_doc)
        self._set_silently("w_msg", w_msg)
        self._refresh_sum_label()
        self.preset_chosen.emit(name)
        self.weights_changed.emit(self.current_weights())

    def current_weights(self) -> dict[str, float]:
        return {key: round(s.value() * _STEP, 2) for key, s in self._sliders.items()}

    def set_analyze_enabled(self, enabled: bool) -> None:
        self._analyze_btn.setEnabled(enabled)

    def set_weight_warning(self, msg: str | None) -> None:
        """msg=None이면 경고 해제."""
        if msg is None:
            self._warning_label.setText("")
            self._warning_label.setVisible(False)
        else:
            self._warning_label.setText(msg)
            self._warning_label.setVisible(True)

    # ------------------------------------------------------------------ #
    # 내부
    # ------------------------------------------------------------------ #
    def _set_silently(self, key: str, value: float) -> None:
        s = self._sliders[key]
        s.blockSignals(True)
        s.setValue(int(round(value / _STEP)))
        s.blockSignals(False)
        if hasattr(self, "_value_labels"):
            self._value_labels[key].setText(f"{value:.2f}")

    def _on_slider_dragged(self, changed_key: str, value: int) -> None:
        new_val = value * _STEP
        current = self.current_weights()
        fixed_val = max(0.0, min(1.0, new_val))
        
        remaining = 1.0 - fixed_val
        other_keys = [k for k in ["w_git", "w_doc", "w_msg"] if k != changed_key]
        other_sum = sum(current.get(k, 0.0) for k in other_keys)
        
        result = {changed_key: fixed_val}
        if other_sum == 0:
            for k in other_keys:
                result[k] = remaining / len(other_keys)
        else:
            for k in other_keys:
                ratio = current.get(k, 0.0) / other_sum
                result[k] = remaining * ratio
                
        # Grid snap
        grid_result = {}
        for k, v in result.items():
            grid_result[k] = round(v / _STEP) * _STEP
            
        # Fix sum error due to grid snap
        grid_sum = sum(grid_result.values())
        diff_steps = round((1.0 - grid_sum) / _STEP)
        if diff_steps != 0:
            last_key = other_keys[-1]
            grid_result[last_key] = max(0.0, grid_result[last_key] + diff_steps * _STEP)
                
        for k, v in grid_result.items():
            self._set_silently(k, v)
            
        self._refresh_sum_label()
        self.weights_changed.emit(self.current_weights())

    def _refresh_sum_label(self) -> None:
        total = sum(self.current_weights().values())
        self._sum_label.setText(f"합계: {total:.2f}")

    # --- 테스트 접근자 ---
    def analyze_enabled(self) -> bool:
        return self._analyze_btn.isEnabled()

    def weight_warning_text(self) -> str:
        return self._warning_label.text()

    @property
    def weight_step(self) -> float:
        return _STEP
