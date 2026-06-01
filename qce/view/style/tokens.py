"""
색상·폰트·치수 토큰 (view-design §10). UI(QSS)와 matplotlib 차트가 동일
토큰을 참조해 일관성을 유지한다. 단일 출처.

[v2.0] 색상은 라이트/다크 두 팔레트로 분리한다. 색상 상수는 모듈 전역으로
노출되되, 활성 팔레트(라이트/다크)에 따라 값이 달라진다. ``apply_palette(dark)``
가 활성 팔레트의 값으로 모듈 전역을 재바인딩한다. 차트·QSS는 모두
``tokens.COLOR_X`` 속성 접근으로 읽으므로(import-time 캡처 아님) 재바인딩 직후
다음 렌더·QSS 생성에 새 색이 반영된다. 치수·폰트는 테마 무관 상수다.

INV-V1: model/controller/common import 금지.
"""
from __future__ import annotations

# --- 라이트 팔레트 (기본) ---
_LIGHT: dict[str, object] = {
    "COLOR_BG": "#ffffff",           # 창/차트 figure 배경
    "COLOR_SURFACE": "#ffffff",      # 차트 axes 배경
    "COLOR_TEXT": "#202124",
    "COLOR_MUTED": "#80868b",        # placeholder 문구 등
    "COLOR_GRID": "#dadce0",
    "COLOR_PRIMARY": "#4285f4",      # 1위 강조 막대 등
    "COLOR_BAR_DEFAULT": "#9aa0a6",  # 기본 막대
    "COLOR_AVG_LINE": "#5f6368",     # 평균선·십자선
    "COLOR_WARNING_BG": "#fff8e1",   # WarningBanner 노란 배경
    "COLOR_WARNING_FG": "#5f4300",   # WarningBanner 텍스트
    "COLOR_ANOMALY": "#d93025",      # 하위 이상치 점 (FR-5.1c)
    # 산점도 사분면 배경색 (FR-5.1c)
    "QUADRANT_COLORS": {
        "올라운더": "#e6f4ea",
        "개발 집중": "#e8f0fe",
        "문서 집중": "#fef0e3",
        "저참여": "#f1f3f4",
    },
}

# --- 다크 팔레트 (v2.0) ---
_DARK: dict[str, object] = {
    "COLOR_BG": "#1e1e1e",
    "COLOR_SURFACE": "#2b2b2b",
    "COLOR_TEXT": "#e8eaed",
    "COLOR_MUTED": "#9aa0a6",
    "COLOR_GRID": "#3c4043",
    "COLOR_PRIMARY": "#8ab4f8",
    "COLOR_BAR_DEFAULT": "#5f6368",
    "COLOR_AVG_LINE": "#9aa0a6",
    "COLOR_WARNING_BG": "#3a3320",
    "COLOR_WARNING_FG": "#ffe082",
    "COLOR_ANOMALY": "#f28b82",
    "QUADRANT_COLORS": {
        "올라운더": "#1e3325",
        "개발 집중": "#1f2a3d",
        "문서 집중": "#3a2e1e",
        "저참여": "#2a2c2e",
    },
}

# --- 폰트 (테마 무관) ---
FONT_FAMILY = "Malgun Gothic"    # Windows 한글(C-5)
FONT_SIZE_BASE = 10
FONT_SIZE_TITLE = 13

# --- 치수 (테마 무관) ---
GRID_STEP = 0.2                  # 차트 그리드 간격
DOT_MIN = 40.0                   # 산점도 점 최소 크기(pt)
DOT_MAX = 200.0                  # 산점도 점 최대 크기(pt)
DOT_MISSING = 80.0               # 메신저 결측 시 고정 크기(pt)


def apply_palette(dark: bool) -> None:
    """활성 팔레트 값으로 모듈 전역 색상 상수를 재바인딩한다(view-design §10.1)."""
    globals().update(_DARK if dark else _LIGHT)


# import 시 라이트 팔레트를 기본값으로 적용 (테스트·미초기화 시 일관성)
apply_palette(False)

# 정적 분석·IDE 보조용 선언(런타임 값은 apply_palette가 채운다).
COLOR_BG: str
COLOR_SURFACE: str
COLOR_TEXT: str
COLOR_MUTED: str
COLOR_GRID: str
COLOR_PRIMARY: str
COLOR_BAR_DEFAULT: str
COLOR_AVG_LINE: str
COLOR_WARNING_BG: str
COLOR_WARNING_FG: str
COLOR_ANOMALY: str
QUADRANT_COLORS: dict[str, str]
