"""
색상·폰트·치수 토큰 (view-design §10). UI(QSS)와 matplotlib 차트가 동일
토큰을 참조해 일관성을 유지한다. 단일 출처.

INV-V1: model/controller/common import 금지.
"""
from __future__ import annotations

# --- 색상 ---
COLOR_PRIMARY = "#4285f4"        # 1위 강조 막대 등
COLOR_BAR_DEFAULT = "#9aa0a6"    # 기본 막대
COLOR_AVG_LINE = "#5f6368"       # 평균선·십자선
COLOR_WARNING_BG = "#fff8e1"     # WarningBanner 노란 배경
COLOR_WARNING_FG = "#5f4300"     # WarningBanner 텍스트
COLOR_ANOMALY = "#d93025"        # 하위 이상치 점 (FR-5.1c)
COLOR_TEXT = "#202124"
COLOR_MUTED = "#80868b"          # placeholder 문구 등
COLOR_GRID = "#dadce0"

# 산점도 사분면 배경색 (FR-5.1c)
QUADRANT_COLORS: dict[str, str] = {
    "올라운더": "#e6f4ea",
    "개발 집중": "#e8f0fe",
    "문서 집중": "#fef0e3",
    "저참여": "#f1f3f4",
}

# --- 폰트 ---
FONT_FAMILY = "Malgun Gothic"    # Windows 한글(C-5)
FONT_SIZE_BASE = 10
FONT_SIZE_TITLE = 13

# --- 치수 ---
GRID_STEP = 0.2                  # 차트 그리드 간격
DOT_MIN = 40.0                   # 산점도 점 최소 크기(pt)
DOT_MAX = 200.0                  # 산점도 점 최대 크기(pt)
DOT_MISSING = 80.0               # 메신저 결측 시 고정 크기(pt)
