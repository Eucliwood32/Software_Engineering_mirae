"""
그림자 효과 헬퍼 (qce-design-guide §5.2). QSS는 box-shadow를 지원하지 않으므로
카드·메인 패널에 한해 ``QGraphicsDropShadowEffect``를 코드로 부착한다.

> 절제된 그림자 원칙: 그림자는 카드·메인 패널 전용. 단일 그림자 토큰만 쓴다.
  버튼·텍스트·헤더·테두리에는 적용하지 않는다.
> 기능 무영향: 시각 효과만 부착한다. 위젯 동작·신호와 무관하다.

INV-V1: model/controller/common import 금지.
"""
from __future__ import annotations

from PyQt6.QtGui import QColor
from PyQt6.QtWidgets import QGraphicsDropShadowEffect, QWidget

from qce.view.style import tokens as T


def apply_card_shadow(widget: QWidget) -> QGraphicsDropShadowEffect:
    """카드/패널에 단일 그림자 토큰(SHADOW_CARD)을 부착한다.

    오프셋 (0, 2), blur 12 — qce-design-guide §5.2 SHADOW_CARD와 동일.
    alpha는 활성 팔레트(라이트 0.10 / 다크 0.40)를 따른다.
    """
    shadow = QGraphicsDropShadowEffect(widget)
    shadow.setOffset(0, 2)
    shadow.setBlurRadius(12)
    alpha = int(getattr(T, "SHADOW_CARD_ALPHA", 26))
    shadow.setColor(QColor(0, 0, 0, alpha))
    widget.setGraphicsEffect(shadow)
    return shadow
