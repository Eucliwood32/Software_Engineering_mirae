"""
QSS 스타일시트 문자열 (view-design §10). tokens.py 값을 보간해 생성한다.

INV-V1: model/controller/common import 금지.
"""
from __future__ import annotations

from qce.view.style import tokens as T


def app_stylesheet() -> str:
    """애플리케이션 전역 QSS. MainWindow.setStyleSheet에 적용."""
    return f"""
    QWidget {{
        font-family: "{T.FONT_FAMILY}";
        font-size: {T.FONT_SIZE_BASE}pt;
        color: {T.COLOR_TEXT};
    }}
    QLabel#warningBanner {{
        background-color: {T.COLOR_WARNING_BG};
        color: {T.COLOR_WARNING_FG};
        padding: 8px 12px;
        border-radius: 4px;
    }}
    QPushButton#primary {{
        background-color: {T.COLOR_PRIMARY};
        color: white;
        padding: 6px 16px;
        border-radius: 4px;
    }}
    QPushButton#primary:disabled {{
        background-color: {T.COLOR_BAR_DEFAULT};
    }}
    QLabel#placeholder {{
        color: {T.COLOR_MUTED};
    }}
    QLabel#weightWarning {{
        color: {T.COLOR_ANOMALY};
    }}
    """
