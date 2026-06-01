"""
QSS 스타일시트 문자열 (view-design §10, qce-design-guide §6). tokens.py 값을 보간해
생성한다. Product-First Minimalism: 흑백 계조 + 단일 액센트 블루, 8px 간격, 3종 반경,
절제된 그림자(그림자는 카드/패널에만 QGraphicsDropShadowEffect로 별도 적용).

> 기능 무영향: 색·여백·반경 등 표현 속성만 정의한다. 위젯 objectName 계약은
  기존과 동일하게 유지한다(primary·warningBanner·placeholder·weightWarning·
  signalCard·dismissSignal·signalPanelTitle·signalEmpty·logoText). 신규 objectName
  (secondary·preset·dropzone·weight 슬라이더·analysis 진행률·signalSection)을 추가한다.

INV-V1: model/controller/common import 금지.
"""
from __future__ import annotations

from qce.view.style import tokens as T

# UI 폰트 스택 (한글 Malgun Gothic → 영문 Segoe UI → sans-serif 폴백).
# 공백 포함 패밀리명은 따옴표로 감싼다.
_FONT_STACK = '"Malgun Gothic", "Segoe UI", sans-serif'


def app_stylesheet() -> str:
    """애플리케이션 전역 QSS. MainWindow.setStyleSheet에 적용."""
    return f"""
    /* ── 기본 (전 위젯) ───────────────────────────────────── */
    QWidget {{
        font-family: {_FONT_STACK};
        font-size: {T.FONT_BODY}px;
        color: {T.COLOR_TEXT};
        background: transparent;
    }}
    QMainWindow, QStackedWidget, QDialog {{
        background: {T.COLOR_CANVAS};
    }}

    /* ── 메뉴바·설정 버튼 ─────────────────────────────────── */
    QMenuBar {{
        background: {T.COLOR_CANVAS};
        color: {T.COLOR_TEXT};
        border-bottom: 1px solid {T.COLOR_HAIRLINE};
        padding: {T.SPACING_XXS}px {T.SPACING_XS}px;
    }}
    QMenuBar::item {{
        background: transparent;
        padding: {T.SPACING_XXS}px {T.SPACING_SM}px;
        border-radius: {T.RADIUS_SM}px;
    }}
    QMenuBar::item:selected {{ background: {T.COLOR_SURFACE}; }}
    QMenu {{
        background: {T.COLOR_SURFACE};
        border: 1px solid {T.COLOR_HAIRLINE};
        border-radius: {T.RADIUS_SM}px;
        padding: {T.SPACING_XXS}px;
    }}
    QMenu::item {{ padding: {T.SPACING_XS}px {T.SPACING_MD}px; border-radius: {T.RADIUS_SM}px; }}
    QMenu::item:selected {{ background: {T.COLOR_PRIMARY}; color: #ffffff; }}
    QToolButton {{
        background: transparent;
        color: {T.COLOR_TEXT};
        border: none;
        border-radius: {T.RADIUS_SM}px;
        padding: {T.SPACING_XXS}px {T.SPACING_XS}px;
        font-size: {T.FONT_SUBTITLE}px;
    }}
    QToolButton:hover {{ background: {T.COLOR_SURFACE}; color: {T.COLOR_PRIMARY}; }}

    /* ── 주 액션 버튼 (완전 캡슐) ─────────────────────────── */
    QPushButton#primary {{
        background: {T.COLOR_PRIMARY};
        color: #ffffff;
        border: none;
        border-radius: {T.RADIUS_PILL}px;
        padding: {T.BTN_PAD_PRIMARY[0]}px {T.BTN_PAD_PRIMARY[1]}px;
        font-size: {T.FONT_BUTTON_PRIMARY}px;
        font-weight: 400;
        min-height: {T.TOUCH_TARGET_MIN}px;
    }}
    QPushButton#primary:hover    {{ background: {T.COLOR_PRIMARY_FOCUS}; }}
    QPushButton#primary:pressed  {{ background: {T.COLOR_PRIMARY_FOCUS}; }}
    QPushButton#primary:disabled {{
        background: {T.COLOR_SURFACE_2};
        color: {T.COLOR_TEXT_DISABLED};
    }}

    /* ── 세컨더리/유틸 버튼 (6px) ─────────────────────────── */
    QPushButton#secondary {{
        background: {T.COLOR_SURFACE_2};
        color: {T.COLOR_TEXT};
        border: 1px solid {T.COLOR_HAIRLINE};
        border-radius: {T.RADIUS_SM}px;
        padding: {T.BTN_PAD_SECONDARY[0]}px {T.BTN_PAD_SECONDARY[1]}px;
        font-size: {T.FONT_BUTTON_UTILITY}px;
        min-height: {T.TOUCH_TARGET_MIN}px;
    }}
    QPushButton#secondary:hover    {{ background: {T.COLOR_SURFACE}; border-color: {T.COLOR_PRIMARY}; }}
    QPushButton#secondary:disabled {{ color: {T.COLOR_TEXT_DISABLED}; border-color: {T.COLOR_DIVIDER_SOFT}; }}

    /* 기본(objectName 없는) 버튼도 세컨더리 톤으로 — 다이얼로그 OK/취소 등 */
    QPushButton {{
        background: {T.COLOR_SURFACE_2};
        color: {T.COLOR_TEXT};
        border: 1px solid {T.COLOR_HAIRLINE};
        border-radius: {T.RADIUS_SM}px;
        padding: {T.BTN_PAD_SECONDARY[0]}px {T.BTN_PAD_SECONDARY[1]}px;
        font-size: {T.FONT_BUTTON_UTILITY}px;
    }}
    QPushButton:hover    {{ border-color: {T.COLOR_PRIMARY}; }}
    QPushButton:disabled {{ color: {T.COLOR_TEXT_DISABLED}; border-color: {T.COLOR_DIVIDER_SOFT}; }}

    /* ── 프리셋 칩 (완전 캡슐) ────────────────────────────── */
    QPushButton#preset {{
        background: {T.COLOR_SURFACE_2};
        color: {T.COLOR_TEXT};
        border: 1px solid {T.COLOR_HAIRLINE};
        border-radius: {T.RADIUS_PILL}px;
        padding: {T.BTN_PAD_SMALL[0]}px 14px;
        font-size: {T.FONT_CAPTION_STRONG}px;
        font-weight: 600;
    }}
    QPushButton#preset:hover            {{ border-color: {T.COLOR_PRIMARY}; color: {T.COLOR_PRIMARY}; }}
    QPushButton#preset[selected="true"] {{ background: {T.COLOR_PRIMARY}; color: #ffffff; border-color: {T.COLOR_PRIMARY}; }}

    /* ── 카드 패널 ────────────────────────────────────────── */
    QFrame#card {{
        background: {T.COLOR_SURFACE};
        border: 1px solid {T.COLOR_HAIRLINE};
        border-radius: {T.RADIUS_LG}px;
    }}

    /* ── 드롭존 (점선 컨테이너) ───────────────────────────── */
    #dropzone {{
        background: {T.COLOR_SURFACE};
        border: 2px dashed {T.COLOR_HAIRLINE};
        border-radius: {T.RADIUS_LG}px;
    }}
    #dropzone[drag_active="true"] {{
        border-color: {T.COLOR_PRIMARY};
    }}

    /* ── WarningBanner ────────────────────────────────────── */
    QLabel#warningBanner {{
        background: {T.COLOR_WARNING_BG};
        color: {T.COLOR_WARNING_FG};
        padding: 10px {T.SPACING_MD}px;
        border-radius: {T.RADIUS_SM}px;
        font-size: {T.FONT_CAPTION}px;
    }}

    /* ── 보조 라벨 ────────────────────────────────────────── */
    QLabel#placeholder    {{ color: {T.COLOR_TEXT_MUTED}; font-size: {T.FONT_CAPTION}px; }}
    QLabel#weightWarning  {{ color: {T.COLOR_ANOMALY}; font-size: {T.FONT_CAPTION}px; }}
    QLabel#logoText       {{ color: {T.COLOR_TEXT}; font-size: {T.FONT_HERO}px; font-weight: 600; }}
    QLabel#cornerLogo     {{ color: {T.COLOR_TEXT}; font-size: {T.FONT_SUBTITLE}px; font-weight: 600; padding: 0 {T.SPACING_XS}px; }}

    /* ── 페이지·섹션 타이틀 (결과 화면 등) ────────────────── */
    QLabel#pageTitle    {{ color: {T.COLOR_TEXT}; font-size: {T.FONT_HERO}px; font-weight: 600; }}
    QLabel#sectionTitle {{ color: {T.COLOR_TEXT}; font-size: {T.FONT_TITLE}px; font-weight: 600; }}
    QLabel#sectionHint  {{ color: {T.COLOR_TEXT_MUTED}; font-size: {T.FONT_CAPTION}px; }}

    /* ── 이상 신호 카드 ───────────────────────────────────── */
    QFrame#signalCard {{
        background: {T.COLOR_SURFACE};
        border: none;
        border-left: 3px solid {T.COLOR_ANOMALY};
        border-radius: {T.RADIUS_SM}px;
    }}
    QLabel#signalPanelTitle {{ font-size: {T.FONT_SUBTITLE}px; font-weight: 600; color: {T.COLOR_TEXT}; }}
    QLabel#signalSection    {{ color: {T.COLOR_ANOMALY}; font-weight: 600; font-size: {T.FONT_CAPTION_STRONG}px; }}
    QLabel#signalEmpty      {{ color: {T.COLOR_TEXT_MUTED}; font-size: {T.FONT_CAPTION}px; }}
    QPushButton#dismissSignal {{
        background: {T.COLOR_SURFACE_2};
        color: {T.COLOR_TEXT_MUTED};
        border: 1px solid {T.COLOR_DIVIDER_SOFT};
        border-radius: {T.RADIUS_SM}px;
        padding: {T.BTN_PAD_SMALL[0]}px {T.BTN_PAD_SMALL[1]}px;
        font-size: {T.FONT_BUTTON_UTILITY}px;
    }}
    QPushButton#dismissSignal:hover {{ border-color: {T.COLOR_PRIMARY}; color: {T.COLOR_PRIMARY}; }}

    /* ── 진행률 ───────────────────────────────────────────── */
    QProgressBar#analysis {{
        background: {T.COLOR_SURFACE};
        border: none;
        border-radius: 3px;
        max-height: {T.PROGRESS_H}px;
        min-height: {T.PROGRESS_H}px;
        text-align: center;
        color: transparent;
    }}
    QProgressBar#analysis::chunk {{ background: {T.COLOR_PRIMARY}; border-radius: 3px; }}

    /* ── 가중치 슬라이더 ──────────────────────────────────── */
    QSlider#weight::groove:horizontal {{
        background: {T.COLOR_HAIRLINE}; height: 4px; border-radius: 2px;
    }}
    QSlider#weight::sub-page:horizontal {{
        background: {T.COLOR_PRIMARY}; border-radius: 2px;
    }}
    QSlider#weight::handle:horizontal {{
        background: {T.COLOR_PRIMARY};
        width: 14px; height: 18px; margin: -7px 0; border-radius: 3px;   /* 깔끔한 사각형 핸들 */
    }}
    QSlider#weight::handle:horizontal:hover {{ background: {T.COLOR_PRIMARY_FOCUS}; }}

    /* ── 입력 위젯 (콤보·체크박스) ────────────────────────── */
    QComboBox {{
        background: {T.COLOR_SURFACE_2};
        color: {T.COLOR_TEXT};
        border: 1px solid {T.COLOR_HAIRLINE};
        border-radius: {T.RADIUS_SM}px;
        padding: {T.SPACING_XXS}px {T.SPACING_XS}px;
        min-height: 28px;
    }}
    QComboBox:hover {{ border-color: {T.COLOR_PRIMARY}; }}
    QComboBox QAbstractItemView {{
        background: {T.COLOR_SURFACE};
        border: 1px solid {T.COLOR_HAIRLINE};
        selection-background-color: {T.COLOR_PRIMARY};
        selection-color: #ffffff;
    }}
    QCheckBox {{ spacing: {T.SPACING_XS}px; }}

    /* ── 스크롤바 (미니멀) ────────────────────────────────── */
    QScrollBar:vertical {{ background: transparent; width: 10px; margin: 0; }}
    QScrollBar::handle:vertical {{ background: {T.COLOR_HAIRLINE}; border-radius: 5px; min-height: 24px; }}
    QScrollBar::handle:vertical:hover {{ background: {T.COLOR_TEXT_MUTED}; }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
    QScrollBar:horizontal {{ background: transparent; height: 10px; margin: 0; }}
    QScrollBar::handle:horizontal {{ background: {T.COLOR_HAIRLINE}; border-radius: 5px; min-width: 24px; }}
    QScrollBar::handle:horizontal:hover {{ background: {T.COLOR_TEXT_MUTED}; }}
    QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal {{ width: 0; }}

    /* ── 상태바 ───────────────────────────────────────────── */
    QStatusBar {{
        background: {T.COLOR_SURFACE};
        color: {T.COLOR_TEXT_MUTED};
        font-size: {T.FONT_CAPTION}px;
        border-top: 1px solid {T.COLOR_HAIRLINE};
        padding: {T.SPACING_XXS}px {T.SPACING_SM}px;
    }}
    """
