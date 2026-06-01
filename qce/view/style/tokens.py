"""
색상·폰트·치수 토큰 (view-design §10, qce-design-guide §2·§9). UI(QSS)와 matplotlib
차트가 동일 토큰을 참조해 일관성을 유지한다. 단일 출처.

[v3.0 — Product-First Minimalism] qce-design-guide.md(v1.0)의 디자인 양식을 토큰으로
구현한다. 흑백 계조 + 단일 액센트 블루, 8px 간격 그리드, 3종 반경 문법(6/12/pill),
단일 그림자 토큰. 색상은 라이트/다크 두 팔레트로 분리하며, 색상 상수는 모듈 전역으로
노출되되 활성 팔레트에 따라 값이 달라진다. ``apply_palette(dark)``가 활성 팔레트 값으로
모듈 전역을 재바인딩한다. 차트·QSS는 모두 ``tokens.COLOR_X`` 속성 접근으로 읽으므로
(import-time 캡처 아님) 재바인딩 직후 다음 렌더·QSS 생성에 새 색이 반영된다.
치수·폰트·반경·간격은 테마 무관 상수다.

> 기능 무영향: 본 모듈은 색·치수 값만 정의한다. 신호·슬롯·계산 로직과 무관하다.
  하위 호환을 위해 기존 토큰명(``COLOR_BG``·``COLOR_MUTED`` 등)을 신규 토큰의
  별칭으로 함께 노출해 기존 차트·테스트 코드가 변경 없이 동작한다.

INV-V1: model/controller/common import 금지.
"""
from __future__ import annotations

# --- 라이트 팔레트 (기본, qce-design-guide §2.1) ---
_LIGHT: dict[str, object] = {
    # 표면 계조
    "COLOR_CANVAS": "#ffffff",        # 앱 전체 배경(메인 캔버스)
    "COLOR_SURFACE": "#f5f5f7",       # 카드·패널·드롭존 배경(parchment)
    "COLOR_SURFACE_2": "#fafafc",     # 세컨더리 버튼 배경(pearl)
    # 텍스트 계조
    "COLOR_TEXT": "#1d1d1f",          # 본문·헤드라인(near-black)
    "COLOR_TEXT_MUTED": "#6e6e73",    # 보조 텍스트·캡션·비활성 라벨
    "COLOR_TEXT_DISABLED": "#aeaeb2", # 비활성 버튼 텍스트·placeholder
    # 단일 액센트
    "COLOR_PRIMARY": "#0066cc",       # 유일 액센트 — 버튼·링크·포커스·강조
    "COLOR_PRIMARY_FOCUS": "#0071e3", # 포커스 링·hover 강조
    # 선·구분
    "COLOR_HAIRLINE": "#e0e0e0",      # 카드 테두리·구분선 1px
    "COLOR_DIVIDER_SOFT": "rgba(0,0,0,0.06)",  # 세컨더리 버튼 테두리·부드러운 구분선
    # 의미색
    "COLOR_WARNING_BG": "#fff8e1",    # WarningBanner 배경
    "COLOR_WARNING_FG": "#5f4300",    # WarningBanner 텍스트
    "COLOR_ANOMALY": "#cc0000",       # 이상 신호 카드·산점도 이상 점
    # 차트 전용 (qce-design-guide §2.3)
    "COLOR_BAR_TOP": "#0066cc",       # 막대 1위 강조(= PRIMARY)
    "COLOR_BAR_DEFAULT": "#adb5bd",   # 막대 기본색
    "COLOR_AVG_LINE": "#5f6368",      # 평균선·십자선
    "COLOR_GRID": "#e0e0e0",          # 차트 그리드
    # 산점도 사분면 배경(채도를 낮춰 데이터 점이 묻히지 않게)
    "QUADRANT_COLORS": {
        "올라운더": "#e8f4fd",
        "개발 집중": "#e8f0fe",
        "문서 집중": "#fef0e3",
        "저참여": "#f1f3f4",
    },
    # 그림자(단일 토큰, 카드·패널 전용)
    "SHADOW_CARD": "0 2px 12px rgba(0,0,0,0.10)",
    "SHADOW_CARD_ALPHA": 26,          # QGraphicsDropShadowEffect용 alpha(0~255)
    # --- 하위 호환 별칭(기존 코드/테스트 보존) ---
    "COLOR_BG": "#ffffff",            # = COLOR_CANVAS (차트 figure 배경)
    "COLOR_MUTED": "#6e6e73",         # = COLOR_TEXT_MUTED
}

# --- 다크 팔레트 (qce-design-guide §2.2) ---
_DARK: dict[str, object] = {
    "COLOR_CANVAS": "#1c1c1e",
    "COLOR_SURFACE": "#2c2c2e",
    "COLOR_SURFACE_2": "#3a3a3c",
    "COLOR_TEXT": "#f5f5f7",
    "COLOR_TEXT_MUTED": "#aeaeb2",
    "COLOR_TEXT_DISABLED": "#636366",
    "COLOR_PRIMARY": "#2997ff",       # 다크 서피스용 — 밝아야 가시성 확보
    "COLOR_PRIMARY_FOCUS": "#409cff",
    "COLOR_HAIRLINE": "#3a3a3c",
    "COLOR_DIVIDER_SOFT": "rgba(255,255,255,0.08)",
    "COLOR_WARNING_BG": "#3a2f00",
    "COLOR_WARNING_FG": "#ffd60a",
    "COLOR_ANOMALY": "#ff6b6b",
    "COLOR_BAR_TOP": "#2997ff",
    "COLOR_BAR_DEFAULT": "#636366",
    "COLOR_AVG_LINE": "#9aa0a6",
    "COLOR_GRID": "#3c3c3e",
    "QUADRANT_COLORS": {
        "올라운더": "#1a2e3d",
        "개발 집중": "#1a2340",
        "문서 집중": "#2d2010",
        "저참여": "#252526",
    },
    "SHADOW_CARD": "0 2px 12px rgba(0,0,0,0.40)",
    "SHADOW_CARD_ALPHA": 102,         # rgba(0,0,0,0.40)
    # --- 하위 호환 별칭 ---
    "COLOR_BG": "#1c1c1e",            # = COLOR_CANVAS
    "COLOR_MUTED": "#aeaeb2",         # = COLOR_TEXT_MUTED
}

# --- 폰트 (테마 무관, qce-design-guide §3) ---
FONT_FAMILY = "Malgun Gothic, Segoe UI, sans-serif"  # UI(QSS)용 폰트 스택
FONT_FAMILY_CHART = "Malgun Gothic"                  # matplotlib rcParams용(C-5)

# 타이포 계층 (px). 굵기 사다리는 400/600 두 단계만.
FONT_HERO = 28            # 앱 타이틀·헤드라인
FONT_TITLE = 20           # 화면 섹션 타이틀
FONT_SUBTITLE = 17        # 카드 이름·강조 본문
FONT_BODY = 15            # 기본 본문·드롭존 안내·툴팁
FONT_CAPTION = 13         # 캡션·부가 설명·상태바
FONT_CAPTION_STRONG = 13  # 강조 캡션·프리셋 라벨(weight 600)
FONT_BUTTON_PRIMARY = 15  # 주 액션 버튼
FONT_BUTTON_UTILITY = 13  # 유틸리티 버튼·탭
FONT_FINE_PRINT = 11      # Staff Credit·법적 고지

# 하위 호환(기존 QSS·차트가 pt 단위로 참조하던 토큰)
FONT_SIZE_BASE = 10       # (legacy) 기본 pt
FONT_SIZE_TITLE = 13      # (legacy) 타이틀 pt

# --- 간격·치수 (테마 무관, 8px 배수 그리드, qce-design-guide §4) ---
SPACING_XXS = 4
SPACING_XS = 8
SPACING_SM = 12
SPACING_MD = 16
SPACING_LG = 24
SPACING_XL = 32
SPACING_SECTION = 48

BTN_PAD_PRIMARY = (10, 22)
BTN_PAD_SECONDARY = (8, 16)
BTN_PAD_SMALL = (6, 12)
TOUCH_TARGET_MIN = 44
CARD_PADDING = SPACING_LG
DROPZONE_MIN_H = 160
PROGRESS_H = 6
PROGRESS_W = 280          # 로딩 화면 진행률 너비

# --- 반경 문법 (이 세 값 외 사용 금지, qce-design-guide §5.1) ---
RADIUS_SM = 6             # 유틸리티 버튼·칩·인라인 태그
RADIUS_LG = 12            # 카드·드롭존·다이얼로그
RADIUS_PILL = 9999        # 주 버튼·프리셋·검색창 — 완전 캡슐

# --- 차트 치수 (테마 무관) ---
GRID_STEP = 0.2           # 차트 그리드 간격
DOT_MIN = 40.0            # 산점도 점 최소 크기(pt)
DOT_MAX = 200.0           # 산점도 점 최대 크기(pt)
DOT_MISSING = 80.0        # 메신저 결측 시 고정 크기(pt)
CHART_ANIM_FRAMES = 20
CHART_ANIM_MS = 30


def apply_palette(dark: bool) -> None:
    """활성 팔레트 값으로 모듈 전역 색상 상수를 재바인딩한다(view-design §10.1)."""
    globals().update(_DARK if dark else _LIGHT)


# import 시 라이트 팔레트를 기본값으로 적용 (테스트·미초기화 시 일관성)
apply_palette(False)

# 정적 분석·IDE 보조용 선언(런타임 값은 apply_palette가 채운다).
COLOR_CANVAS: str
COLOR_SURFACE: str
COLOR_SURFACE_2: str
COLOR_TEXT: str
COLOR_TEXT_MUTED: str
COLOR_TEXT_DISABLED: str
COLOR_PRIMARY: str
COLOR_PRIMARY_FOCUS: str
COLOR_HAIRLINE: str
COLOR_DIVIDER_SOFT: str
COLOR_WARNING_BG: str
COLOR_WARNING_FG: str
COLOR_ANOMALY: str
COLOR_BAR_TOP: str
COLOR_BAR_DEFAULT: str
COLOR_AVG_LINE: str
COLOR_GRID: str
QUADRANT_COLORS: dict[str, str]
SHADOW_CARD: str
SHADOW_CARD_ALPHA: int
# 하위 호환 별칭
COLOR_BG: str
COLOR_MUTED: str
