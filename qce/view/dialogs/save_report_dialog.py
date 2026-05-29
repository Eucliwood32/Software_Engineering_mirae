"""
SaveReportDialog — 리포트 저장 경로·형식 선택 (view-design §6.4, FR-5.2).

QFileDialog.getSaveFileName으로 경로·형식(.md/.csv)을 받는다. 실제 직렬화는
Model(ReportExporter)이 수행하고, 본 다이얼로그는 경로·형식만 Signal로 올린다.
"""
from __future__ import annotations

import os

from PyQt6.QtCore import QObject, pyqtSignal
from PyQt6.QtWidgets import QFileDialog

_FILTER = "Markdown (*.md);;CSV (*.csv)"


class SaveReportDialog(QObject):
    path_chosen = pyqtSignal(str, str)              # (path, "md" | "csv")

    def prompt(self, parent=None) -> None:
        """확장자 필터로 저장 경로를 묻고, 선택 시 path_chosen 발행."""
        path, selected_filter = QFileDialog.getSaveFileName(
            parent, "리포트 저장", "", _FILTER
        )
        if path:
            self._handle_result(path, selected_filter)

    def _handle_result(self, path: str, selected_filter: str) -> None:
        fmt = self._fmt_for(path, selected_filter)
        self.path_chosen.emit(path, fmt)

    @staticmethod
    def _fmt_for(path: str, selected_filter: str = "") -> str:
        """경로 확장자 우선, 없으면 선택 필터로 형식 결정. 기본 'md'."""
        ext = os.path.splitext(path)[1].lower()
        if ext == ".csv":
            return "csv"
        if ext == ".md":
            return "md"
        if "csv" in selected_filter.lower():
            return "csv"
        return "md"
