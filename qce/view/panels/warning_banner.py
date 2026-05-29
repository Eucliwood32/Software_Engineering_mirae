"""
WarningBanner — 데이터 소스 결측 경고 배너 (view-design §6.7, FR-5.3).

노란 배경 배너. 결측 소스 집합을 받아 소스별 문구를 누적 표시한다.
입력 집합 원소는 contract의 소스 코드(git/doc/messenger)이며, 표시용 한글로 매핑한다.
"""
from __future__ import annotations

from PyQt6.QtWidgets import QLabel, QVBoxLayout, QWidget

from qce.view.contract import SRC_DOC, SRC_GIT, SRC_MSG

# 소스 코드 → 표시용 한글 라벨. 이미 한글이면 그대로 사용.
_SOURCE_LABELS = {SRC_GIT: "Git", SRC_DOC: "문서", SRC_MSG: "메신저"}
_DISPLAY_ORDER = [SRC_GIT, SRC_DOC, SRC_MSG]


class WarningBanner(QWidget):
    TEMPLATE = "⚠ {src} 데이터의 형식 불일치 또는 부재로 인해 해당 지표가 평가에서 제외되었습니다."

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self._label = QLabel("")
        self._label.setObjectName("warningBanner")
        self._label.setWordWrap(True)
        layout.addWidget(self._label)
        self.setVisible(False)

    def show_missing(self, missing: set[str]) -> None:
        """missing이 비면 숨김. 복수 결측 시 각 소스별 문구를 모두 표시."""
        if not missing:
            self.clear()
            return
        lines = [self.TEMPLATE.format(src=self._label_for(s)) for s in self._ordered(missing)]
        self._label.setText("\n".join(lines))
        self.setVisible(True)

    def clear(self) -> None:
        self._label.setText("")
        self.setVisible(False)

    @staticmethod
    def _label_for(src: str) -> str:
        return _SOURCE_LABELS.get(src, src)

    @staticmethod
    def _ordered(missing: set[str]) -> list[str]:
        known = [s for s in _DISPLAY_ORDER if s in missing]
        extra = sorted(s for s in missing if s not in _DISPLAY_ORDER)
        return known + extra

    # --- 테스트 접근자 ---
    def current_text(self) -> str:
        return self._label.text()

    def is_banner_visible(self) -> bool:
        return self.isVisible()
