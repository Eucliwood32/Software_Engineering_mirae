# 디자인 가이드 (Design Guide)
## QCE — 부탁해 꼬마선장 (Quantitative Contribution Evaluator)

| 항목 | 내용 |
| --- | --- |
| 문서 버전 | v1.0 |
| 작성일 | 2026-06-02 |
| 대상 | View 레이어 (PyQt6 + matplotlib), `style/tokens.py`·`style/qss.py` |
| 디자인 철학 | Product-First Minimalism — 데이터가 전면에, UI 크롬은 후면으로 |
| 적용 대상 | SubmitScreen · LoadingScreen · ResultScreen 3화면 및 전 위젯 |
| 작성 주체 | QCE 개발팀 (View 담당 20247142 이대한) |

---

## 1. 개요

QCE의 비주얼 언어는 **제품(=데이터)을 주인공으로 두고, UI 크롬은 최대한 물러나게 하는** 미니멀리즘을 따른다. 차트와 점수가 화면의 주인공이며, 버튼·패널·네비게이션은 존재감을 낮춘다. 색은 흑백 계조 위에 **단 하나의 액센트 블루**만 얹고, 그림자는 극도로 절제하며, 계층은 선이 아니라 여백과 배경색 전환으로 만든다.

이 가이드는 데스크톱 분석 도구라는 QCE의 성격에 맞춰 정보 밀도와 가독성의 균형점을 잡았다. Windows 10/11 네이티브 데스크톱 앱(PyQt6) 환경을 전제로 한다.

### 핵심 5원칙

| # | 원칙 | 의미 |
| :-- | :-- | :-- |
| 1 | **데이터 우선** | 차트·점수가 주인공. UI 크롬(버튼·패널·테두리)은 최소한의 존재감만. |
| 2 | **단일 액센트** | 모든 인터랙티브 요소(버튼·링크·포커스·강조)는 단 하나의 블루를 쓴다. 두 번째 브랜드 색은 없다. |
| 3 | **절제된 그림자** | 그림자는 카드·메인 패널에만 드물게. 동일한 단일 그림자 토큰만 허용. 버튼·텍스트·헤더에는 금지. |
| 4 | **여백이 계층이다** | 섹션 경계는 선이 아니라 여백(48px)과 배경색 전환으로 표현. 모든 간격은 8px 배수. |
| 5 | **반경 문법** | 주 버튼=완전 캡슐(pill), 유틸 버튼=6px, 카드=12px. 이 세 값 외 중간값 금지. |

---

## 2. 색상 (Colors)

흑백 계조 + 단일 블루 액센트. 모든 색상은 라이트/다크 두 팔레트로 정의하며, `tokens.apply_palette(dark)`가 활성 팔레트로 전역 상수를 재바인딩한다.

### 2.1 라이트 팔레트

| 토큰 | 값 | 용도 |
| :-- | :-- | :-- |
| `COLOR_CANVAS` | `#ffffff` | 앱 전체 배경 (메인 캔버스) |
| `COLOR_SURFACE` | `#f5f5f7` | 카드·패널·드롭존 배경 (parchment) |
| `COLOR_SURFACE_2` | `#fafafc` | 세컨더리 버튼 배경 (pearl) |
| `COLOR_TEXT` | `#1d1d1f` | 본문·헤드라인 (순수 #000 대신 near-black) |
| `COLOR_TEXT_MUTED` | `#6e6e73` | 보조 텍스트·캡션·비활성 라벨 |
| `COLOR_TEXT_DISABLED` | `#aeaeb2` | 비활성 버튼 텍스트·placeholder |
| **`COLOR_PRIMARY`** | **`#0066cc`** | **유일 액센트** — 버튼·링크·포커스·강조 모두 |
| `COLOR_PRIMARY_FOCUS` | `#0071e3` | 포커스 링·hover 강조 |
| `COLOR_HAIRLINE` | `#e0e0e0` | 카드 테두리·구분선 1px |
| `COLOR_DIVIDER_SOFT` | `rgba(0,0,0,0.06)` | 세컨더리 버튼 테두리·부드러운 구분선 |
| `COLOR_WARNING_BG` | `#fff8e1` | WarningBanner 배경 |
| `COLOR_WARNING_FG` | `#5f4300` | WarningBanner 텍스트 |
| `COLOR_ANOMALY` | `#cc0000` | 이상 신호 카드·산점도 이상 점 |

### 2.2 다크 팔레트

| 토큰 | 값 | 용도 |
| :-- | :-- | :-- |
| `COLOR_CANVAS` | `#1c1c1e` | 앱 배경 (near-black) |
| `COLOR_SURFACE` | `#2c2c2e` | 카드·패널 배경 |
| `COLOR_SURFACE_2` | `#3a3a3c` | 세컨더리 버튼 배경 |
| `COLOR_TEXT` | `#f5f5f7` | 메인 텍스트 (off-white) |
| `COLOR_TEXT_MUTED` | `#aeaeb2` | 보조 텍스트 |
| `COLOR_TEXT_DISABLED` | `#636366` | 비활성 텍스트 |
| **`COLOR_PRIMARY`** | **`#2997ff`** | 다크 서피스용 액센트 (밝아야 가시성 확보) |
| `COLOR_PRIMARY_FOCUS` | `#409cff` | 포커스 링 |
| `COLOR_HAIRLINE` | `#3a3a3c` | 카드 테두리 |
| `COLOR_DIVIDER_SOFT` | `rgba(255,255,255,0.08)` | 부드러운 구분선 |
| `COLOR_WARNING_BG` | `#3a2f00` | WarningBanner 배경 |
| `COLOR_WARNING_FG` | `#ffd60a` | WarningBanner 텍스트 |
| `COLOR_ANOMALY` | `#ff6b6b` | 이상 신호 강조 |

> **핵심 원칙 — 다크 모드의 블루.** 라이트의 `#0066cc`를 다크 배경에 그대로 쓰면 가시성이 떨어진다. 다크에서는 반드시 밝은 `#2997ff`를 쓴다. 같은 `COLOR_PRIMARY` 토큰이지만 팔레트마다 값이 다르다.

### 2.3 차트 전용 색상

| 토큰 | 라이트 | 다크 | 용도 |
| :-- | :-- | :-- | :-- |
| `COLOR_BAR_TOP` | `#0066cc` | `#2997ff` | 막대 1위 강조 (= PRIMARY) |
| `COLOR_BAR_DEFAULT` | `#adb5bd` | `#636366` | 막대 기본색 |
| `COLOR_AVG_LINE` | `#5f6368` | `#9aa0a6` | 평균선·십자선 |
| `COLOR_GRID` | `#e0e0e0` | `#3c3c3e` | 차트 그리드 |

**산점도 사분면 배경** (`QUADRANT_COLORS`) — 채도를 낮춰 데이터 점이 묻히지 않게 한다.

| 사분면 | 라이트 | 다크 |
| :-- | :-- | :-- |
| 올라운더 | `#e8f4fd` | `#1a2e3d` |
| 개발 집중 | `#e8f0fe` | `#1a2340` |
| 문서 집중 | `#fef0e3` | `#2d2010` |
| 저참여 | `#f1f3f4` | `#252526` |

### Do / Don't

| ✅ Do | ❌ Don't |
| :-- | :-- |
| 모든 버튼·링크·포커스에 `COLOR_PRIMARY` 단일 사용 | 두 번째 액센트 색 추가 (`#34a853` 등) |
| 다크 서피스에서 `#2997ff` 사용 | 라이트 `#0066cc`를 다크 배경에 그대로 사용 |
| 카드 테두리에 `COLOR_HAIRLINE` 단일 적용 | 카드에 그림자와 테두리를 동시에 진하게 |
| 경고·이상 신호에 전용 색 사용 | 일반 UI 요소에 `COLOR_ANOMALY` 사용 |

---

## 3. 타이포그래피 (Typography)

Windows 기본 탑재 **Malgun Gothic**(맑은 고딕)을 한글 전용으로, `Segoe UI`를 영문 폴백으로 둔다.

```python
FONT_FAMILY       = "Malgun Gothic, Segoe UI, sans-serif"
FONT_FAMILY_CHART = "Malgun Gothic"   # matplotlib rcParams용
```

### 3.1 계층

| 토큰 | 크기 | 굵기 | 행간 | 용도 |
| :-- | --: | :-- | :-- | :-- |
| `FONT_HERO` | 28px | 600 | 1.10 | 앱 타이틀·SubmitScreen 헤드라인 |
| `FONT_TITLE` | 20px | 600 | 1.15 | 화면 섹션 타이틀 |
| `FONT_SUBTITLE` | 17px | 600 | 1.24 | 카드 이름·강조 본문 |
| `FONT_BODY` | 15px | 400 | 1.47 | 기본 본문·드롭존 안내·툴팁 |
| `FONT_CAPTION` | 13px | 400 | 1.43 | 캡션·부가 설명·상태바 |
| `FONT_CAPTION_STRONG` | 13px | 600 | 1.29 | 강조 캡션·프리셋 라벨 |
| `FONT_BUTTON_PRIMARY` | 15px | 400 | 1.0 | 주 액션 버튼 |
| `FONT_BUTTON_UTILITY` | 13px | 400 | 1.0 | 유틸리티 버튼·탭 |
| `FONT_FINE_PRINT` | 11px | 400 | 1.3 | Staff Credit·법적 고지 |

### 3.2 원칙

- **굵기 사다리는 400 / 600 두 단계만.** `500`은 사용하지 않는다. 중간 강조가 필요하면 600을 쓴다.
- **헤드라인은 600, 700 아님.** 700은 거의 쓰지 않는다.
- **본문 15px.** 데스크톱 분석 도구의 정보 밀도와 가독성 균형점. (참조 원본의 17px는 웹 기준이며, Windows DPI·창 크기를 고려해 15px로 조정)
- **행간은 맥락별로.** 헤드라인은 타이트(1.10~1.24), 본문은 여유(1.47).

---

## 4. 간격·치수 (Spacing & Dimensions)

모든 구조적 간격은 **8px 배수 그리드**를 따른다.

```python
# 8px 기반 간격 그리드
SPACING_XXS     =  4   # 인라인 타이포 미세 조정
SPACING_XS      =  8   # 요소 내 최소 여백
SPACING_SM      = 12
SPACING_MD      = 16   # 기본 내부 패딩
SPACING_LG      = 24   # 카드 패딩
SPACING_XL      = 32   # 섹션 간 여백
SPACING_SECTION = 48   # 화면 상하 여백

# 버튼 패딩 (수직, 수평)
BTN_PAD_PRIMARY   = (10, 22)   # 주 액션 — 넉넉한 터치 영역
BTN_PAD_SECONDARY = ( 8, 16)   # 세컨더리·유틸
BTN_PAD_SMALL     = ( 6, 12)   # 작은 버튼 (X 삭제, 토글)

TOUCH_TARGET_MIN = 44          # 모든 클릭 요소 최소 높이

CARD_PADDING    = 24           # 카드 내부 패딩 (= SPACING_LG)
DROPZONE_MIN_H  = 160          # 드롭존 최소 높이
PROGRESS_H      = 6            # 진행률 표시줄 두께
```

### 여백 철학
- 연속된 섹션은 선이 아니라 **`SPACING_XL`(32px) 이상의 여백 + 배경색 전환**으로 나눈다.
- 차트·드롭존 등 "제품"은 절대 빽빽하게 두지 않는다. 가장 가까운 요소까지 최소 `SPACING_LG`(24px) 확보.

---

## 5. 모서리·그림자 (Shapes & Elevation)

### 5.1 반경 문법 (이 세 값 외 사용 금지)

```python
RADIUS_SM   =  6     # 유틸리티 버튼·칩·인라인 태그
RADIUS_LG   = 12     # 카드·드롭존·다이얼로그
RADIUS_PILL = 9999   # 주 버튼·프리셋·검색창 — 완전 캡슐
# 전체 화면 타일·메인 창은 RADIUS_NONE(0)
```

| 요소 | 반경 | 이유 |
| :-- | :-- | :-- |
| [분석 시작], [새 분석], 주 CTA | `RADIUS_PILL` | 캡슐 = "기본 액션"의 시각 언어 |
| 프리셋 버튼 (개발 중심 등) | `RADIUS_PILL` | 선택 가능한 칩 |
| 유틸리티 버튼 (저장, [X]) | `RADIUS_SM` | 명령 액션 |
| 카드·드롭존·다이얼로그 | `RADIUS_LG` | 컨테이너 |
| 메인 창·전체 화면 영역 | `0` | 엣지-투-엣지 |

### 5.2 그림자

```python
SHADOW_CARD      = "0 2px 12px rgba(0,0,0,0.10)"   # 라이트 카드
SHADOW_CARD_DARK = "0 2px 12px rgba(0,0,0,0.40)"   # 다크 카드
```

- 그림자는 **카드·메인 패널 전용**. 단 하나의 그림자 토큰만 쓴다.
- 버튼·텍스트·헤더·테두리에는 절대 그림자를 쓰지 않는다.
- 계층은 그림자가 아니라 **배경색 전환**(canvas ↔ surface)으로 표현하는 것이 우선.

> **PyQt6 그림자 적용.** QSS는 `box-shadow`를 지원하지 않으므로 `QGraphicsDropShadowEffect`를 코드로 붙인다.
> ```python
> from PyQt6.QtWidgets import QGraphicsDropShadowEffect
> from PyQt6.QtGui import QColor
> shadow = QGraphicsDropShadowEffect()
> shadow.setOffset(0, 2)
> shadow.setBlurRadius(12)
> shadow.setColor(QColor(0, 0, 0, 26))   # rgba(0,0,0,0.10)
> card_widget.setGraphicsEffect(shadow)
> ```

---

## 6. 컴포넌트 QSS 명세 (Components)

`style/qss.py`의 `app_stylesheet()`가 토큰을 보간해 QSS 문자열을 반환한다. `{TOKEN}` 표기는 보간 자리표시자다.

### 주 버튼 `QPushButton#primary`

```css
QPushButton#primary {
    background: {COLOR_PRIMARY};
    color: #ffffff;
    border: none;
    border-radius: {RADIUS_PILL}px;
    padding: 10px 22px;
    font-size: {FONT_BUTTON_PRIMARY}px;
    font-weight: 400;
    min-height: {TOUCH_TARGET_MIN}px;
}
QPushButton#primary:hover    { background: {COLOR_PRIMARY_FOCUS}; }
QPushButton#primary:pressed  { background: {COLOR_PRIMARY_FOCUS};
                               padding: 11px 22px 9px 22px; }
QPushButton#primary:disabled { background: {COLOR_DIVIDER_SOFT};
                               color: {COLOR_TEXT_DISABLED}; }
```

> **포커스 링.** PyQt6는 `outline`을 직접 지원하지 않으므로, `focusInEvent`/`focusOutEvent`에서 `setProperty("focused", True/False)` + QSS `[focused="true"]` 선택자로 2px solid `COLOR_PRIMARY_FOCUS` 테두리를 적용한다.

### 세컨더리 버튼 `QPushButton#secondary`

```css
QPushButton#secondary {
    background: {COLOR_SURFACE_2};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_HAIRLINE};
    border-radius: {RADIUS_SM}px;
    padding: 8px 16px;
    font-size: {FONT_BUTTON_UTILITY}px;
    min-height: {TOUCH_TARGET_MIN}px;
}
QPushButton#secondary:hover    { background: {COLOR_SURFACE};
                                 border-color: {COLOR_PRIMARY}; }
QPushButton#secondary:disabled { color: {COLOR_TEXT_DISABLED};
                                 border-color: {COLOR_DIVIDER_SOFT}; }
```

### 프리셋 칩 `QPushButton#preset`

```css
QPushButton#preset {
    background: {COLOR_SURFACE_2};
    color: {COLOR_TEXT};
    border: 1px solid {COLOR_HAIRLINE};
    border-radius: {RADIUS_PILL}px;
    padding: 6px 14px;
    font-size: {FONT_CAPTION_STRONG}px;
    font-weight: 600;
}
QPushButton#preset:hover            { border-color: {COLOR_PRIMARY};
                                      color: {COLOR_PRIMARY}; }
QPushButton#preset[selected="true"] { background: {COLOR_PRIMARY};
                                      color: #ffffff;
                                      border-color: {COLOR_PRIMARY}; }
```

### 카드 패널 `QFrame#card`

```css
QFrame#card {
    background: {COLOR_SURFACE};
    border: 1px solid {COLOR_HAIRLINE};
    border-radius: {RADIUS_LG}px;
    padding: {CARD_PADDING}px;
}
/* SHADOW_CARD는 QGraphicsDropShadowEffect로 별도 적용 */
```

### 드롭존 `QFrame#dropzone`

```css
QFrame#dropzone {
    background: {COLOR_SURFACE};
    border: 2px dashed {COLOR_HAIRLINE};
    border-radius: {RADIUS_LG}px;
    min-height: {DROPZONE_MIN_H}px;
}
QFrame#dropzone[drag_active="true"] {
    border-color: {COLOR_PRIMARY};
    background: rgba(0,102,204,0.05);   /* PRIMARY at 5% — 드래그 진입 시 */
}
```

### WarningBanner `QFrame#warning`

```css
QFrame#warning {
    background: {COLOR_WARNING_BG};
    border: 1px solid rgba(95,67,0,0.20);
    border-radius: {RADIUS_SM}px;
    padding: 10px {SPACING_MD}px;
}
QLabel#warning_text { color: {COLOR_WARNING_FG};
                      font-size: {FONT_CAPTION}px; }
```

### 진행률 `QProgressBar#analysis`

```css
QProgressBar#analysis {
    background: {COLOR_SURFACE};
    border: none;
    border-radius: 3px;
    max-height: {PROGRESS_H}px;
}
QProgressBar#analysis::chunk { background: {COLOR_PRIMARY};
                               border-radius: 3px; }
```

### 슬라이더 `QSlider#weight`

```css
QSlider#weight::groove:horizontal {
    background: {COLOR_HAIRLINE}; height: 4px; border-radius: 2px;
}
QSlider#weight::sub-page:horizontal {
    background: {COLOR_PRIMARY}; border-radius: 2px;
}
QSlider#weight::handle:horizontal {
    background: {COLOR_PRIMARY};
    width: 18px; height: 18px; margin: -7px 0; border-radius: 9px;
}
QSlider#weight::handle:horizontal:hover { background: {COLOR_PRIMARY_FOCUS}; }
```

### 상태바 `QStatusBar`

```css
QStatusBar {
    background: {COLOR_SURFACE};
    color: {COLOR_TEXT_MUTED};
    font-size: {FONT_CAPTION}px;
    border-top: 1px solid {COLOR_HAIRLINE};
    padding: 4px {SPACING_SM}px;
}
```

### 이상 신호 카드 `QFrame#signal_card`

```css
QFrame#signal_card {
    background: {COLOR_SURFACE};
    border-left: 3px solid {COLOR_ANOMALY};
    border-radius: {RADIUS_SM}px;
    padding: {SPACING_SM}px {SPACING_MD}px;
}
QFrame#signal_card QLabel#signal_type {
    color: {COLOR_ANOMALY};
    font-size: {FONT_CAPTION_STRONG}px;
    font-weight: 600;
}
```

---

## 7. matplotlib 차트 스타일

차트도 동일 토큰을 참조해 라이트/다크 전환 시 UI와 일관되게 재채색한다. BaseChartWidget에 공통 헬퍼를 둔다.

```python
def _style_axes(self, ax) -> None:
    """테마 토큰을 matplotlib axes에 적용 (BaseChartWidget 공통 헬퍼)."""
    ax.set_facecolor(tokens.COLOR_CANVAS)
    ax.figure.patch.set_facecolor(tokens.COLOR_CANVAS)
    for spine in ax.spines.values():
        spine.set_edgecolor(tokens.COLOR_HAIRLINE)
        spine.set_linewidth(0.8)
    ax.tick_params(colors=tokens.COLOR_TEXT_MUTED, labelsize=11)
    ax.xaxis.label.set_color(tokens.COLOR_TEXT)
    ax.yaxis.label.set_color(tokens.COLOR_TEXT)
    ax.title.set_color(tokens.COLOR_TEXT)
    ax.set_axisbelow(True)
    ax.yaxis.grid(True, color=tokens.COLOR_GRID, linewidth=0.6, linestyle="--")
    ax.xaxis.grid(False)
```

### 차트별 색상 매핑

| 차트 | 요소 | 토큰 |
| :-- | :-- | :-- |
| Bar | 막대 (1위) | `COLOR_BAR_TOP` |
| Bar | 막대 (그 외) | `COLOR_BAR_DEFAULT` |
| Bar | 평균선 | `COLOR_AVG_LINE`, lw=1.2, `--` |
| Bar | 수치 라벨 | `COLOR_TEXT` |
| Radar | 폴리곤 선 | `COLOR_PRIMARY` 계열 (팀원별 색조 분리, alpha 0.85) |
| Radar | 동심원 그리드 | `COLOR_GRID` |
| Radar | 축 라벨 | `COLOR_TEXT_MUTED` |
| Scatter | 일반 점 | `COLOR_BAR_DEFAULT` |
| Scatter | 이상 신호 점 | `COLOR_ANOMALY` |
| Scatter | 십자선 | `COLOR_AVG_LINE`, lw=0.8, `:` |
| Scatter | 사분면 배경 | `QUADRANT_COLORS[사분면명]` |

> **한글 폰트.** 차트 생성 시 `rcParams["font.family"] = [tokens.FONT_FAMILY_CHART]`, `rcParams["axes.unicode_minus"] = False` 설정 (Malgun Gothic, 음수 부호 깨짐 방지).

---

## 8. 화면별 레이아웃 리듬

교차 배경색과 풍부한 여백을 3화면에 적용한다.

### SubmitScreen (제출)
- 배경 `COLOR_CANVAS`
- 상단 여백 `SPACING_SECTION`(48px) → 로고 → `SPACING_XL`(32px) → 설명 1~2줄
- 드롭존: `COLOR_SURFACE` 배경 + 점선 테두리 (캔버스 위에 살짝 올라온 느낌)
- AnalysisPanel: `COLOR_SURFACE` 카드로 감싸 드롭존과 구분
- [분석 시작]: 가운데 정렬, pill, `COLOR_PRIMARY` — 화면의 유일한 강조 버튼

### LoadingScreen (로딩)
- 배경 `COLOR_CANVAS`
- 로고: 수직 중앙보다 약간 위(상단 40%)
- 진행률: 로고 아래 `SPACING_LG`(24px) 간격, 너비 280px, 두께 6px
- 텍스트: `COLOR_TEXT_MUTED`, `FONT_CAPTION` — "분석 중..." 부드러운 안내

### ResultScreen (결과)
- 배경 `COLOR_CANVAS`
- 대시보드: 차트가 전체 폭 사용, 좌우 여백 `SPACING_XL`(32px)만
- WarningBanner·신호 패널: `COLOR_SURFACE` 카드 안, 차트 아래 `SPACING_XL` 간격
- 하단 액션(병합·새 분석·저장): `COLOR_SURFACE` 얇은 툴바 스트립, 높이 56px, 우측 정렬

---

## 9. tokens.py 구현 골격

```python
# style/tokens.py — QCE 스타일 토큰 단일 출처

# ── 테마 가변 팔레트 ──────────────────────────────────────
_LIGHT: dict[str, object] = {
    "COLOR_CANVAS": "#ffffff", "COLOR_SURFACE": "#f5f5f7",
    "COLOR_SURFACE_2": "#fafafc", "COLOR_TEXT": "#1d1d1f",
    "COLOR_TEXT_MUTED": "#6e6e73", "COLOR_TEXT_DISABLED": "#aeaeb2",
    "COLOR_PRIMARY": "#0066cc", "COLOR_PRIMARY_FOCUS": "#0071e3",
    "COLOR_HAIRLINE": "#e0e0e0", "COLOR_DIVIDER_SOFT": "rgba(0,0,0,0.06)",
    "COLOR_WARNING_BG": "#fff8e1", "COLOR_WARNING_FG": "#5f4300",
    "COLOR_ANOMALY": "#cc0000", "COLOR_AVG_LINE": "#5f6368",
    "COLOR_GRID": "#e0e0e0", "COLOR_BAR_DEFAULT": "#adb5bd",
    "COLOR_BAR_TOP": "#0066cc",
    "QUADRANT_COLORS": {"올라운더": "#e8f4fd", "개발 집중": "#e8f0fe",
                        "문서 집중": "#fef0e3", "저참여": "#f1f3f4"},
    "SHADOW_CARD": "0 2px 12px rgba(0,0,0,0.10)",
}
_DARK: dict[str, object] = {
    "COLOR_CANVAS": "#1c1c1e", "COLOR_SURFACE": "#2c2c2e",
    "COLOR_SURFACE_2": "#3a3a3c", "COLOR_TEXT": "#f5f5f7",
    "COLOR_TEXT_MUTED": "#aeaeb2", "COLOR_TEXT_DISABLED": "#636366",
    "COLOR_PRIMARY": "#2997ff", "COLOR_PRIMARY_FOCUS": "#409cff",
    "COLOR_HAIRLINE": "#3a3a3c", "COLOR_DIVIDER_SOFT": "rgba(255,255,255,0.08)",
    "COLOR_WARNING_BG": "#3a2f00", "COLOR_WARNING_FG": "#ffd60a",
    "COLOR_ANOMALY": "#ff6b6b", "COLOR_AVG_LINE": "#9aa0a6",
    "COLOR_GRID": "#3c3c3e", "COLOR_BAR_DEFAULT": "#636366",
    "COLOR_BAR_TOP": "#2997ff",
    "QUADRANT_COLORS": {"올라운더": "#1a2e3d", "개발 집중": "#1a2340",
                        "문서 집중": "#2d2010", "저참여": "#252526"},
    "SHADOW_CARD": "0 2px 12px rgba(0,0,0,0.40)",
}

# ── 테마 무관 상수 ────────────────────────────────────────
FONT_FAMILY       = "Malgun Gothic, Segoe UI, sans-serif"
FONT_FAMILY_CHART = "Malgun Gothic"

FONT_HERO = 28; FONT_TITLE = 20; FONT_SUBTITLE = 17
FONT_BODY = 15; FONT_CAPTION = 13; FONT_CAPTION_STRONG = 13
FONT_BUTTON_PRIMARY = 15; FONT_BUTTON_UTILITY = 13; FONT_FINE_PRINT = 11

SPACING_XXS = 4; SPACING_XS = 8; SPACING_SM = 12
SPACING_MD = 16; SPACING_LG = 24; SPACING_XL = 32; SPACING_SECTION = 48

BTN_PAD_PRIMARY = (10, 22); BTN_PAD_SECONDARY = (8, 16); BTN_PAD_SMALL = (6, 12)
TOUCH_TARGET_MIN = 44
CARD_PADDING = SPACING_LG; DROPZONE_MIN_H = 160; PROGRESS_H = 6

RADIUS_SM = 6; RADIUS_LG = 12; RADIUS_PILL = 9999

GRID_STEP = 0.2; CHART_ANIM_FRAMES = 20; CHART_ANIM_MS = 30


def apply_palette(dark: bool) -> None:
    """활성 팔레트 값으로 모듈 전역 색상 상수를 재바인딩한다."""
    globals().update(_DARK if dark else _LIGHT)


apply_palette(False)   # import 시 라이트 기본값
```

> **접근 규칙 (중요).** QSS·차트는 반드시 `tokens.COLOR_PRIMARY`처럼 **속성 접근**으로 읽는다. `from tokens import COLOR_PRIMARY`처럼 import 시점에 값을 캡처하면 `apply_palette` 후에도 갱신되지 않으므로 금지한다.

---

## 10. 적용 체크리스트

새 위젯을 만들거나 기존 위젯을 이 가이드로 교체할 때:

- [ ] 색은 하드코딩 없이 `tokens.*` 속성 접근으로만 참조했는가
- [ ] 인터랙티브 요소는 `COLOR_PRIMARY` 단일 액센트만 쓰는가
- [ ] 반경은 `RADIUS_SM`/`RADIUS_LG`/`RADIUS_PILL` 셋 중 하나인가
- [ ] 간격은 8px 배수(`SPACING_*`)인가
- [ ] 그림자는 카드/패널에만, 단일 토큰으로 적용했는가
- [ ] 클릭 가능 요소 높이가 `TOUCH_TARGET_MIN`(44px) 이상인가
- [ ] 폰트 굵기는 400 또는 600만 썼는가 (500 금지)
- [ ] 라이트·다크 양쪽에서 텍스트 대비가 충분한가
- [ ] 차트가 `_style_axes` 헬퍼를 거쳐 테마 전환에 반응하는가

---

## 11. 문서 변경 이력

| 버전 | 일자 | 변경 | 작성자 |
| :--- | :--- | :--- | :--- |
| v1.0 | 2026-06-02 | 최초 작성. QCE View 레이어 디자인 가이드 정의 — Product-First Minimalism 5원칙, 라이트/다크 색상 팔레트 및 차트 전용 색상, 타이포그래피 계층, 8px 간격 그리드, 반경·그림자 문법, 컴포넌트별 QSS 명세, matplotlib 차트 스타일, 3화면 레이아웃 리듬, `tokens.py` 구현 골격, 적용 체크리스트 수록. | QCE 개발팀 (이대한) |
