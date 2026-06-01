"""
AnomalySignalPanel — 이상 신호 카드 패널 (view-design §6.8, FR-4.2/4.2b/4.2d).

ContributionAggregator가 산출한 구조화 신호 상세(signal_details)를 신호 유형별
섹션으로 묶어 카드로 표시한다. 각 카드는 작성자·근거 메타(커밋 해시·작성일·변경
라인 수 등)와 "정상으로 표시" 버튼(FR-4.2c)을 가진다. 버튼 클릭 시
signal_dismissed(author, type, ref)를 발행하며, 재집계 없이 Controller가
NormalizedSignalsTracker로 예외 처리 후 재렌더한다.

신호는 점수에 반영되지 않는 표시 전용 정보다(STR-7). View는 model을 import하지
않으며(C-4), plain dict(signal_details)만 소비한다.
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from qce.view.contract import K_AUTHOR, K_SIGNAL_DETAILS
from qce.view.style import tokens as T

# 신호 유형 → 섹션 제목. 표시 순서도 이 dict 순서를 따른다.
# (색상은 qce-design-guide §6 signal_card 명세에 따라 COLOR_ANOMALY 단일색으로 통일 —
#  카드 좌측 보더·섹션 헤더 모두 QSS objectName(signalCard·signalSection)이 채색한다.)
_TYPE_META: dict[str, str] = {
    "CAPPING": "대량 변경 (Capping 적용)",
    "EW-02": "커밋 빈도 급증 (EW-02)",
    "ZSCORE": "기여 지표 하위 이상치 (Z-Score)",
}
_TYPE_ORDER = list(_TYPE_META.keys())
_DISMISS_LABEL = "정상으로 표시"


def _ref_of(detail: dict) -> str:
    """예외 식별자(ref) 추출. NormalizedSignalsTracker.ref_of와 동일 규칙(뷰측 사본)."""
    t = detail.get("type", "")
    if t == "CAPPING":
        return str(detail.get("hash", ""))
    if t == "EW-02":
        return str(detail.get("date", ""))
    return ""


def _describe(author: str, detail: dict) -> str:
    """카드 본문 문구를 신호 유형별로 구성."""
    t = detail.get("type", "")
    if t == "CAPPING":
        return (
            f"{author}  ·  커밋 {detail.get('hash', '?')}  ·  "
            f"{detail.get('date', '')}  ·  +{detail.get('additions', 0):,}줄"
            f"  (10,000줄 초과 → 캡핑)"
        )
    if t == "EW-02":
        return (
            f"{author}  ·  {detail.get('date', '')}  ·  "
            f"하루 {detail.get('period_commits', 0)}커밋"
            f"  (일평균 {detail.get('baseline_avg', 0)}의 3배 초과)"
        )
    if t == "ZSCORE":
        metrics = ", ".join(detail.get("metrics", []))
        return f"{author}  ·  하위 이상치 지표: {metrics}  (Z-Score ≤ -1.5)"
    return f"{author}  ·  {t}"


class _SignalCard(QFrame):
    """단일 신호 카드: 설명 라벨 + '정상으로 표시' 버튼."""

    dismissed = pyqtSignal(str, str, str)        # (author, type, ref)

    def __init__(self, author: str, detail: dict, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("signalCard")        # QSS: COLOR_ANOMALY 좌측 보더·surface 배경
        self._author = author
        self._type = detail.get("type", "")
        self._ref = _ref_of(detail)

        row = QHBoxLayout(self)
        # qce-design-guide §6 signal_card padding: SPACING_SM / SPACING_MD
        row.setContentsMargins(T.SPACING_MD, T.SPACING_SM, T.SPACING_MD, T.SPACING_SM)
        row.setSpacing(T.SPACING_SM)

        label = QLabel(_describe(author, detail))
        label.setWordWrap(True)
        row.addWidget(label, stretch=1)

        btn = QPushButton(_DISMISS_LABEL)
        btn.setObjectName("dismissSignal")
        btn.clicked.connect(self._emit_dismiss)
        row.addWidget(btn, alignment=Qt.AlignmentFlag.AlignTop)

    def _emit_dismiss(self) -> None:
        self.dismissed.emit(self._author, self._type, self._ref)

    # --- 테스트 접근자 ---
    def ref(self) -> str:
        return self._ref

    def signal_type(self) -> str:
        return self._type


class AnomalySignalPanel(QWidget):
    signal_dismissed = pyqtSignal(str, str, str)     # (author, type, ref)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        root = QVBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(T.SPACING_SM)

        self._title = QLabel("이상 신호")
        self._title.setObjectName("signalPanelTitle")
        root.addWidget(self._title)

        self._empty = QLabel("탐지된 이상 신호가 없습니다.")
        self._empty.setObjectName("signalEmpty")
        root.addWidget(self._empty)

        self._host = QWidget()
        self._host_layout = QVBoxLayout(self._host)
        self._host_layout.setContentsMargins(0, 0, 0, 0)
        self._host_layout.setSpacing(T.SPACING_SM)
        self._host_layout.addStretch(1)
        root.addWidget(self._host, stretch=1)

        self._cards: list[_SignalCard] = []

    def render(self, scores: list[dict]) -> None:
        """점수 dict 목록의 signal_details를 신호 유형별 카드로 갱신."""
        self._clear()

        # 유형별로 (author, detail) 수집
        grouped: dict[str, list[tuple[str, dict]]] = {t: [] for t in _TYPE_ORDER}
        for member in scores:
            author = member.get(K_AUTHOR, "?")
            for detail in member.get(K_SIGNAL_DETAILS, []) or []:
                t = detail.get("type", "")
                grouped.setdefault(t, []).append((author, detail))

        total = 0
        for t in _TYPE_ORDER:
            items = grouped.get(t, [])
            if not items:
                continue
            section_title = _TYPE_META[t]
            header = QLabel(f"● {section_title}  ({len(items)})")
            header.setObjectName("signalSection")     # QSS: COLOR_ANOMALY·weight 600
            self._host_layout.insertWidget(self._host_layout.count() - 1, header)
            for author, detail in items:
                card = _SignalCard(author, detail)
                card.dismissed.connect(self.signal_dismissed)
                self._host_layout.insertWidget(self._host_layout.count() - 1, card)
                self._cards.append(card)
                total += 1

        self._empty.setVisible(total == 0)
        self._title.setText(f"이상 신호 ({total})" if total else "이상 신호")

    def _clear(self) -> None:
        # 위젯(헤더 라벨·카드)만 제거하고 끝의 stretch 스페이서는 보존한다.
        self._cards.clear()
        for i in reversed(range(self._host_layout.count())):
            w = self._host_layout.itemAt(i).widget()
            if w is not None:
                w.setParent(None)
                w.deleteLater()

    # --- 테스트 접근자 ---
    def card_count(self) -> int:
        return len(self._cards)

    def cards_of_type(self, signal_type: str) -> list[_SignalCard]:
        return [c for c in self._cards if c.signal_type() == signal_type]
