"""
AliasMappingDialog — 신원(N:1) 매핑 다이얼로그 (view-design §6.3, FR-1.3).

추출된 모든 식별자를 행으로 나열하고, 각 행에 실제 팀원 드롭다운(N:1)을 둔다.
미매핑 행은 활동 규모와 함께 경고색으로 표시한다. 입력은 식별자 dict 목록(§5.3).

서로 다른 미매핑 식별자를 임의 병합하지 않으며("Unknown"(FR-1.2)과 미매핑은 별개),
미매핑 식별자는 current_mapping에서 제외된다.
"""
from __future__ import annotations

from PyQt6.QtCore import pyqtSignal
from PyQt6.QtWidgets import (
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QGridLayout,
    QLabel,
    QVBoxLayout,
    QWidget,
)

from qce.view.contract import K_ACTIVITY, K_RAW_ID, K_SOURCE

PLACEHOLDER = "(미지정)"
_SOURCE_LABELS = {"git": "Git", "doc": "문서", "messenger": "메신저"}


class AliasMappingDialog(QDialog):
    mapping_confirmed = pyqtSignal(dict)            # {raw_id: member_name}

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setWindowTitle("팀원 신원 매핑")
        self._members: list[str] = []
        self._combos: dict[str, QComboBox] = {}
        self._row_labels: dict[str, QLabel] = {}

        root = QVBoxLayout(self)
        self._rows_host = QWidget()
        self._grid = QGridLayout(self._rows_host)
        root.addWidget(self._rows_host)

        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.accepted.connect(self._confirm)
        buttons.rejected.connect(self._reset_mapping)
        root.addWidget(buttons)

    def set_members(self, members: list[str]) -> None:
        """드롭다운에 들어갈 실제 팀원 목록."""
        self._members = list(members)

    def populate(self, identifiers: list[dict]) -> None:
        """식별자 dict(raw_id/source/activity)를 행으로 생성. 모든 식별자 빠짐없이 표시."""
        # 기존 행 제거
        while self._grid.count():
            item = self._grid.takeAt(0)
            w = item.widget()
            if w is not None:
                w.deleteLater()
        self._combos.clear()
        self._row_labels.clear()

        for r, ident in enumerate(identifiers):
            raw_id = ident[K_RAW_ID]
            src = _SOURCE_LABELS.get(ident.get(K_SOURCE), ident.get(K_SOURCE, ""))
            activity = ident.get(K_ACTIVITY, 0)
            label = QLabel(f"{raw_id}  ·  {src}  ·  활동 {activity}")
            combo = QComboBox()
            combo.addItem(PLACEHOLDER)
            combo.addItems(self._members)
            combo.currentTextChanged.connect(
                lambda _t, rid=raw_id: self._update_row_style(rid)
            )

            self._grid.addWidget(label, r, 0)
            self._grid.addWidget(combo, r, 1)
            self._combos[raw_id] = combo
            self._row_labels[raw_id] = label
            self._update_row_style(raw_id)

    def apply_suggested(self, suggested: dict[str, str]) -> None:
        """Controller가 계산한 추천 매핑({raw_id: 대표명})으로 드롭다운을 미리 선택.

        FR-1.3: 자동 병합을 강제하지 않으므로, 대표명이 raw_id 자신과 다르고
        실제 팀원 목록에 존재할 때만(=명확한 별칭 군집) 미리 채운다. 단일 식별자는
        (미지정) 상태로 둔다.
        """
        for raw_id, member in suggested.items():
            combo = self._combos.get(raw_id)
            if combo is None or member == raw_id or member not in self._members:
                continue
            combo.setCurrentText(member)

    def current_mapping(self) -> dict[str, str]:
        """드롭다운에서 팀원이 선택된 식별자만 {raw_id: member}로 반환."""
        return {
            rid: c.currentText()
            for rid, c in self._combos.items()
            if c.currentText() != PLACEHOLDER
        }

    def unmapped_ids(self) -> list[str]:
        """드롭다운 미선택 식별자(분석 제외 대상)."""
        return [rid for rid, c in self._combos.items() if c.currentText() == PLACEHOLDER]

    # ------------------------------------------------------------------ #
    def _confirm(self) -> None:
        self.mapping_confirmed.emit(self.current_mapping())

    def _reset_mapping(self) -> None:
        """취소 버튼 클릭 시 다이얼로그를 닫지 않고 선택값을 미지정으로 되돌린다."""
        for combo in self._combos.values():
            combo.setCurrentText(PLACEHOLDER)

    def _update_row_style(self, raw_id: str) -> None:
        label = self._row_labels.get(raw_id)
        if label is None:
            return
        unmapped = self._combos[raw_id].currentText() == PLACEHOLDER
        # 미매핑 행은 경고색 강조
        label.setStyleSheet("color: #d93025;" if unmapped else "")

    # --- 테스트 접근자 ---
    def row_count(self) -> int:
        return len(self._combos)

    def combo_for(self, raw_id: str) -> QComboBox:
        return self._combos[raw_id]
