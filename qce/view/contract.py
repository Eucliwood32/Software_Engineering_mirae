"""
View가 기대하는 dict 키 상수. View 소유, 매직 스트링 방지(view-design §5.3).

Controller가 push하는 dict는 이 키 집합을 만족해야 한다. 키 이름은 실제
``MemberScore``(common/dto) 필드명과 일치하므로 Controller의
``dataclasses.asdict()`` 변환이 키 재매핑 없이 무손실이 된다.

INV-V1: 이 모듈은 model/controller/common 어떤 것도 import하지 않는다.
"""
from __future__ import annotations

# --- 점수 dict 키 (DashboardView.render 의 scores 원소) ---
K_AUTHOR = "author"
K_GIT = "git_score"
K_DOC = "doc_score"
K_MSG = "msg_score"
K_TOTAL = "total_score"
K_RAW_ADD = "raw_additions"
K_RAW_CHAR = "raw_chars"
K_RAW_MSG = "raw_messages"
K_CAPPING = "capping_applied"
K_ANOMALY = "signals"
K_SIGNAL_DETAILS = "signal_details"      # FR-4.2 카드용 구조화 상세 목록
K_COMMIT_DATES = "commit_dates"          # 커밋 일자(YYYY-MM-DD) 목록 — 타임라인/드릴다운
K_DIMENSIONS = "dimensions"              # v1.7 레이더 세부 축 점수(가용 소스별 3키)

# --- 식별자 dict 키 (AliasMappingDialog.populate 의 원소, FR-1.3) ---
K_RAW_ID = "raw_id"
K_SOURCE = "source"
K_ACTIVITY = "activity"

# --- 결측 소스명 (missing 집합 원소) ---
SRC_GIT = "git"
SRC_DOC = "doc"
SRC_MSG = "messenger"

# --- v1.7 레이더 세부 축 사양 ---
# 소스 → [(dimensions 키, 표시 라벨)] ×3. 레이더 축 표시 순서는 DIM_SOURCE_ORDER를 따른다.
# RadarChartWidget·ContributionAggregator가 이 매핑을 단일 출처로 공유한다.
DIM_SOURCE_ORDER = (SRC_GIT, SRC_DOC, SRC_MSG)
DIM_AXES: dict[str, list[tuple[str, str]]] = {
    SRC_GIT: [("git_commits", "커밋 수"), ("git_additions", "코드 추가"), ("git_deletions", "코드 정리")],
    SRC_DOC: [("doc_chars", "문서 분량"), ("doc_count", "문서 수"), ("doc_blocks", "구성 요소")],
    SRC_MSG: [("msg_count", "발화 수"), ("msg_chars", "발화량"), ("msg_hours", "활동 시간대")],
}

# 점수 dict가 가져야 하는 키 전체 집합 (계약 검증용).
SCORE_KEYS: frozenset[str] = frozenset(
    {
        K_AUTHOR,
        K_GIT,
        K_DOC,
        K_MSG,
        K_TOTAL,
        K_RAW_ADD,
        K_RAW_CHAR,
        K_RAW_MSG,
        K_CAPPING,
        K_ANOMALY,
        K_SIGNAL_DETAILS,
        K_COMMIT_DATES,
        K_DIMENSIONS,
    }
)

# 식별자 dict가 가져야 하는 키 전체 집합.
IDENTIFIER_KEYS: frozenset[str] = frozenset({K_RAW_ID, K_SOURCE, K_ACTIVITY})
