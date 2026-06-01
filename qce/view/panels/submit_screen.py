"""
SubmitScreen — 메인(제출) 화면 (view-design §6.9, FR-5.5).

큼직한 로고 + 프로그램 설명 + 멀티포맷 드래그앤드롭 존 + Git 저장소 진입점 +
가중치 패널(AnalysisPanel, FR-4.4) + [분석 시작]을 배치한다. 드롭 이벤트를
확장자로 분기해 Signal로 올린다(기존 MainWindow의 드롭 로직 이동).

INV-V1/V2: model/controller import 금지. Signal은 발행만, connect는 Controller.
"""
from __future__ import annotations

import html
import os

from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap
from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QVBoxLayout,
    QWidget,
    QScrollArea,
)

from qce.view.panels.analysis_panel import AnalysisPanel
from qce.view.style import tokens as T

DOC_EXTS = {".pptx", ".docx", ".hwpx"}
MSG_EXTS = {".txt"}

_LOGO_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "assets", "logo.png")
_DESCRIPTION = "Git · 문서 · 메신저 기여를 한 번에 정량 분석합니다.\n과제물(또는 폴더)을 아래 영역에 끌어다 놓으세요."
_DROP_HINT = (
    "여기에 문서(.pptx/.docx/.hwpx)·카카오톡(.txt)·폴더·Git 저장소를 끌어다 놓으세요\n"
    "(폴더를 통째로 끌면 내부의 문서·대화·Git 저장소를 자동으로 찾아 적재합니다)"
)

# 적재 항목 종류별 아이콘 (드롭존 목록 표시용, view-design §6.9 v1.6)
_ICON_DOC = "📄"
_ICON_MSG = "💬"
_ICON_GIT = "🗂"


class SubmitScreen(QWidget):
    documents_dropped = pyqtSignal(list)     # .pptx/.docx/.hwpx
    git_repo_chosen = pyqtSignal(str)
    messenger_dropped = pyqtSignal(str)      # .txt

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setAcceptDrops(True)
        self._doc_paths: list[str] = []
        self._msg_paths: list[str] = []
        self._git_paths: list[str] = []

        root = QVBoxLayout(self)
        root.setContentsMargins(
            T.SPACING_XL, T.SPACING_SECTION, T.SPACING_XL, T.SPACING_XL
        )
        root.setSpacing(T.SPACING_XL)

        # 로고 (assets/logo.png, 없으면 텍스트 폴백) — 캔버스 위 헤드라인
        logo = QLabel()
        logo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        pix = QPixmap(_LOGO_PATH)
        if not pix.isNull():
            logo.setPixmap(pix.scaledToHeight(48, Qt.TransformationMode.SmoothTransformation))
        else:
            logo.setText("QCE — 부탁해 꼬마선장")
            logo.setObjectName("logoText")
        root.addWidget(logo)

        desc = QLabel(_DESCRIPTION)
        desc.setObjectName("placeholder")
        desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        desc.setWordWrap(True)
        root.addWidget(desc)

        # 드롭존: 빈 상태는 안내 문구, 1개 이상 적재 시 아이콘+파일명+삭제 버튼 목록 (§6.9 v1.7).
        # 점선 컨테이너 스타일은 QSS #dropzone가 담당(라이트/다크·드래그 강조 일원화).
        self._dropzone_scroll = QScrollArea()
        self._dropzone_scroll.setWidgetResizable(True)
        self._dropzone_scroll.setObjectName("dropzone")
        self._dropzone_scroll.setMinimumHeight(T.DROPZONE_MIN_H)

        self._dropzone_container = QWidget()
        self._dropzone_layout = QVBoxLayout(self._dropzone_container)
        self._dropzone_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self._dropzone_layout.setContentsMargins(
            T.SPACING_LG, T.SPACING_MD, T.SPACING_LG, T.SPACING_MD
        )
        self._dropzone_layout.setSpacing(T.SPACING_XS)

        self._dropzone_scroll.setWidget(self._dropzone_container)
        root.addWidget(self._dropzone_scroll, stretch=1)

        # 적재 피드백 + Git 선택
        row = QHBoxLayout()
        row.setSpacing(T.SPACING_SM)
        self._loaded_label = QLabel("")
        self._loaded_label.setObjectName("placeholder")
        row.addWidget(self._loaded_label, stretch=1)
        self._git_btn = QPushButton("Git 저장소 선택…")
        self._git_btn.setObjectName("secondary")
        self._git_btn.clicked.connect(self.choose_git_repo)
        row.addWidget(self._git_btn)
        root.addLayout(row)

        # 가중치 패널 (FR-4.4) — analyze_clicked는 이 패널이 발행
        self.analysis_panel = AnalysisPanel()
        root.addWidget(self.analysis_panel)

        self._refresh_dropzone()

    # ------------------------------------------------------------------ #
    # Drag & Drop
    # ------------------------------------------------------------------ #
    def dragEnterEvent(self, e) -> None:
        if e.mimeData().hasUrls():
            self._set_drag_active(True)        # 드래그 진입 시 드롭존 테두리 강조(시각 전용)
            e.acceptProposedAction()
        else:
            e.ignore()

    def dragLeaveEvent(self, e) -> None:
        self._set_drag_active(False)
        super().dragLeaveEvent(e)

    def dropEvent(self, e) -> None:
        self._set_drag_active(False)
        paths = [u.toLocalFile() for u in e.mimeData().urls() if u.isLocalFile()]
        self._handle_dropped_paths(paths)
        e.acceptProposedAction()

    def _set_drag_active(self, active: bool) -> None:
        """드롭존 테두리 강조 토글(QSS #dropzone[drag_active]). 동작·신호 무영향."""
        self._dropzone_scroll.setProperty("drag_active", "true" if active else "false")
        style = self._dropzone_scroll.style()
        style.unpolish(self._dropzone_scroll)
        style.polish(self._dropzone_scroll)

    def _handle_dropped_paths(self, paths: list[str]) -> None:
        """드롭 경로 처리: 폴더는 내부 파일로 펼치고, `.git`을 가진 폴더는 Git 저장소로
        인식한다. 이후 확장자 분기로 문서→documents_dropped(list),
        카톡 .txt→messenger_dropped(str), Git 저장소→git_repo_chosen(str)을 올린다."""
        files, git_repos = self._expand_paths(paths)
        docs, messengers = self._classify_paths(files)
        if docs:
            for d in docs:
                if d not in self._doc_paths:
                    self._doc_paths.append(d)
            self.documents_dropped.emit(self._doc_paths)
        for m in messengers:
            if m not in self._msg_paths:
                self._msg_paths.append(m)
            self.messenger_dropped.emit(m)
        for repo in git_repos:
            if repo not in self._git_paths:
                self._git_paths.append(repo)
            self.git_repo_chosen.emit(repo)
        self._refresh_loaded_label()
        self._refresh_dropzone()

    @staticmethod
    def _classify_paths(paths: list[str]) -> tuple[list[str], list[str]]:
        docs, messengers = [], []
        for p in paths:
            ext = os.path.splitext(p)[1].lower()
            if ext in DOC_EXTS:
                docs.append(p)
            elif ext in MSG_EXTS:
                messengers.append(p)
        return docs, messengers

    @staticmethod
    def _is_git_repo(path: str) -> bool:
        """`.git` 하위 디렉터리를 가지면 Git 작업 트리로 간주."""
        return os.path.isdir(os.path.join(path, ".git"))

    @classmethod
    def _expand_paths(cls, paths: list[str]) -> tuple[list[str], list[str]]:
        """드롭 경로를 (파일목록, Git저장소목록)으로 정규화한다.
        - 파일/미존재 경로: 그대로 파일목록에 둔다(확장자 분류는 호출측 책임).
        - Git 저장소 폴더(.git 보유): 내부를 훑지 않고 저장소로 수집.
        - 그 외 폴더: 내부를 순회해 파일을 모으되, 중첩 Git 저장소는 수집 후 제외한다.
        """
        files: list[str] = []
        git_repos: list[str] = []
        for p in paths:
            if not os.path.isdir(p):
                files.append(p)                       # 파일 또는 미존재 → 그대로 통과
                continue
            if cls._is_git_repo(p):
                git_repos.append(p)
                continue
            for root, dirs, names in os.walk(p):
                kept: list[str] = []
                for d in dirs:
                    if d == ".git":
                        continue                      # 내부 메타는 무시
                    full = os.path.join(root, d)
                    if cls._is_git_repo(full):
                        git_repos.append(full)        # 중첩 저장소: 수집 후 비탐색
                    else:
                        kept.append(d)
                dirs[:] = kept
                files.extend(os.path.join(root, n) for n in names)
        return files, git_repos

    def choose_git_repo(self) -> None:
        path = QFileDialog.getExistingDirectory(self, "Git 저장소 선택")
        if path:
            if path not in self._git_paths:
                self._git_paths.append(path)
            self.git_repo_chosen.emit(path)
            self._refresh_loaded_label()
            self._refresh_dropzone()

    def _refresh_loaded_label(self) -> None:
        if not self._doc_paths and not self._msg_paths and not self._git_paths:
            self._loaded_label.setText("")
            return
        git_txt = f" · Git 저장소 {len(self._git_paths)}개" if self._git_paths else ""
        self._loaded_label.setText(
            f"문서 {len(self._doc_paths)}개 · 메신저 {len(self._msg_paths)}개{git_txt} 적재됨"
        )

    def _refresh_dropzone(self) -> None:
        """적재 항목이 있으면 아이콘+파일명+삭제버튼 목록을, 없으면 안내 문구를 드롭존에 렌더(§6.9 v1.7)."""
        while self._dropzone_layout.count():
            item = self._dropzone_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        if not self._doc_paths and not self._msg_paths and not self._git_paths:
            hint = QLabel(_DROP_HINT)
            hint.setObjectName("placeholder")
            hint.setAlignment(Qt.AlignmentFlag.AlignCenter)
            hint.setTextFormat(Qt.TextFormat.RichText)
            hint.setWordWrap(True)
            self._dropzone_layout.addWidget(hint)
            return

        for p in self._doc_paths:
            self._add_item_widget(_ICON_DOC, p, "doc")
        for p in self._msg_paths:
            self._add_item_widget(_ICON_MSG, p, "msg")
        for p in self._git_paths:
            self._add_item_widget(_ICON_GIT, p, "git")

    def _add_item_widget(self, icon: str, path: str, item_type: str) -> None:
        row = QWidget()
        lyt = QHBoxLayout(row)
        lyt.setContentsMargins(0, T.SPACING_XXS, 0, T.SPACING_XXS)
        lyt.setSpacing(T.SPACING_XS)

        lbl = QLabel(f"{icon} {html.escape(os.path.basename(path))}" + (" (Git 저장소)" if item_type == "git" else ""))
        lbl.setStyleSheet(f"font-size: {T.FONT_BODY}px;")
        lyt.addWidget(lbl, stretch=1)

        # [X] 삭제 — 유틸 액션. 호버 시 이상색(remove) 강조. 시각 전용.
        btn = QPushButton("✕")
        btn.setFixedSize(24, 24)
        btn.setStyleSheet(
            "QPushButton { border: none; background: transparent; font-weight: 600;"
            f" color: {T.COLOR_TEXT_MUTED}; font-size: {T.FONT_CAPTION}px; }}"
            f" QPushButton:hover {{ color: {T.COLOR_ANOMALY}; }}"
        )
        btn.clicked.connect(lambda _, t=item_type, p=path: self._remove_item(t, p))
        lyt.addWidget(btn)

        self._dropzone_layout.addWidget(row)

    def _remove_item(self, item_type: str, path: str) -> None:
        if item_type == "doc" and path in self._doc_paths:
            self._doc_paths.remove(path)
            self.documents_dropped.emit(self._doc_paths)
        elif item_type == "msg" and path in self._msg_paths:
            self._msg_paths.remove(path)
            self.messenger_dropped.emit(self._msg_paths[-1] if self._msg_paths else "")
        elif item_type == "git" and path in self._git_paths:
            self._git_paths.remove(path)
            self.git_repo_chosen.emit(self._git_paths[-1] if self._git_paths else "")
        self._refresh_loaded_label()
        self._refresh_dropzone()

    def reset(self) -> None:
        """이전 분석 입력값(문서, 메신저, Git 상태 등)을 초기화한다."""
        self._doc_paths.clear()
        self._msg_paths.clear()
        self._git_paths.clear()
        self._refresh_loaded_label()
        self._refresh_dropzone()

    # --- 테스트 접근자 ---
    def loaded_summary(self) -> str:
        return self._loaded_label.text()

    def loaded_files(self) -> list[str]:
        """드롭존에 표시 중인 적재 파일명 목록(문서→메신저→Git 순)."""
        doc_names = [os.path.basename(p) for p in self._doc_paths]
        msg_names = [os.path.basename(p) for p in self._msg_paths]
        git_names = [os.path.basename(p) for p in self._git_paths]
        return [*doc_names, *msg_names, *git_names]
