"""
ResultScreen — 결과 화면 (view-design §6.11, FR-5.7).

세로 스크롤 페이지로 결과를 한 항목씩 읽어 내려가도록 구성한다(웹 문서 느낌, 넉넉한
좌우 패딩). 순서: 페이지 타이틀("프로젝트 분석 결과") → 결측 배너 → 막대 → 산점도 →
레이더 → 이상 신호 → 인원 합치기(AliasMappingDialog 재사용) → 하단 [새 분석]·[리포트 저장].
각 그래프에는 의미를 알려주는 섹션 타이틀이 붙는다(타이틀·간격은 DashboardView가 부여).

병합 컨트롤에서 복수 인물을 1인으로 합치면 merge_requested(분석-후 N:1)를 올리고,
Controller가 재집계·재정규화 후 render로 갱신한다. [리포트 저장]은 save_report_requested를
발행만 하며 실제 저장은 Controller(ReportExporter)가 수행한다(INV-V1).
"""
from __future__ import annotations

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtWidgets import (
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QVBoxLayout,
    QWidget,
)

from qce.view.contract import (
    K_AUTHOR,
    K_RAW_ADD,
    K_RAW_CHAR,
    K_RAW_MSG,
)
from qce.view.dialogs.alias_mapping_dialog import AliasMappingDialog
from qce.view.panels.dashboard_view import DashboardView
from qce.view.panels.warning_banner import WarningBanner
from qce.view.style import tokens as T


class ResultScreen(QWidget):
    merge_requested = pyqtSignal(dict)            # {alias→member} 병합 그룹
    new_analysis_requested = pyqtSignal()
    signal_dismissed = pyqtSignal(str, str, str)  # (author, type, ref) — FR-4.2c 중계
    save_report_requested = pyqtSignal()          # [리포트 저장] — Controller가 저장 수행

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.dashboard = DashboardView()
        self.banner = WarningBanner()
        self.merge = AliasMappingDialog()         # 결과 화면 임베드(FR-5.7)
        # 병합 확정 → merge_requested로 중계 (재집계는 Controller 책임)
        self.merge.mapping_confirmed.connect(self.merge_requested)
        # 신호 예외 처리(FR-4.2c) → Controller로 중계
        self.dashboard.signal_dismissed.connect(self.signal_dismissed)

        # ── 세로 스크롤 페이지 (요구사항 3: 넉넉한 패딩 + 스크롤로 천천히 읽기) ──
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setObjectName("resultScroll")
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QScrollArea.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        page = QWidget()
        page_lyt = QVBoxLayout(page)
        # 웹사이트 느낌의 넉넉한 좌우 패딩 + 섹션 간 넓은 간격
        page_lyt.setContentsMargins(
            T.SPACING_SECTION, T.SPACING_XL, T.SPACING_SECTION, T.SPACING_XL
        )
        page_lyt.setSpacing(T.SPACING_SECTION)
        page_lyt.setAlignment(Qt.AlignmentFlag.AlignTop)

        # 페이지 타이틀
        title = QLabel("프로젝트 분석 결과")
        title.setObjectName("pageTitle")
        page_lyt.addWidget(title)

        page_lyt.addWidget(self.banner)
        # 막대 → 산점도 → 레이더 → 이상 신호 (각 섹션 타이틀은 DashboardView가 부여)
        page_lyt.addWidget(self.dashboard)

        # 인원 합치기 섹션
        merge_title = QLabel("인원 합치기")
        merge_title.setObjectName("sectionTitle")
        page_lyt.addWidget(merge_title)
        merge_hint = QLabel("여러 계정으로 잡힌 한 사람을 골라 하나로 합치면 결과가 다시 집계됩니다.")
        merge_hint.setObjectName("sectionHint")
        merge_hint.setWordWrap(True)
        page_lyt.addWidget(merge_hint)
        page_lyt.addWidget(self.merge)

        # 하단 액션: [새 분석] · [리포트 저장] 나란히 (요구사항 3-2)
        bottom = QHBoxLayout()
        bottom.setSpacing(T.SPACING_SM)
        bottom.addStretch(1)
        self._new_btn = QPushButton("새 분석")
        self._new_btn.setObjectName("secondary")
        self._new_btn.clicked.connect(self.new_analysis_requested.emit)
        bottom.addWidget(self._new_btn)
        self._save_btn = QPushButton("리포트 저장")
        self._save_btn.setObjectName("primary")
        self._save_btn.clicked.connect(self.save_report_requested.emit)
        bottom.addWidget(self._save_btn)
        page_lyt.addLayout(bottom)

        scroll.setWidget(page)
        outer.addWidget(scroll)

    def render(self, scores: list[dict], missing: set[str]) -> None:
        """대시보드·배너 갱신 + 병합 후보 목록 채움."""
        self.dashboard.render(scores, missing)
        self.banner.show_missing(missing)
        self.populate_merge(scores)

    def set_suggested_mapping(self, suggested: dict[str, str]) -> None:
        """Controller가 계산한 추천 별칭 매핑을 병합 컨트롤에 미리 채운다(FR-1.3)."""
        self.merge.apply_suggested(suggested)

    def populate_merge(self, scores: list[dict]) -> None:
        """결과 인물(author)을 병합 컨트롤 후보로 채운다. 후보=대표 지정 대상 팀원."""
        authors = [s[K_AUTHOR] for s in scores]
        self.merge.set_members(authors)
        identifiers = [
            {
                "raw_id": s[K_AUTHOR],
                "source": "result",
                "activity": int(s.get(K_RAW_ADD, 0))
                + int(s.get(K_RAW_CHAR, 0))
                + int(s.get(K_RAW_MSG, 0)),
            }
            for s in scores
        ]
        self.merge.populate(identifiers)
