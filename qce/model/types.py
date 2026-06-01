"""
공유 데이터 타입 정의. 모든 레이어가 참조하며, 역방향 의존 없음.
"""
from __future__ import annotations
from dataclasses import dataclass, field


@dataclass
class CommitStats:
    commits: int
    additions: int
    deletions: int
    commits_list: list = field(default_factory=list)  # FR-4.2b 빈도 탐지용


@dataclass
class MessengerRecord:
    author: str
    timestamp: str
    message: str


@dataclass
class ParseResult:
    records: list[MessengerRecord]
    skipped_lines: int


@dataclass
class MemberScore:
    author: str
    git_score: float
    doc_score: float
    msg_score: float
    total_score: float
    raw_additions: int
    raw_chars: int
    raw_messages: int
    capping_applied: bool
    signals: list[str] = field(default_factory=list)
    # FR-4.2/4.2b/4.2d 신호 카드용 구조화 상세(작성자·해시·작성일·변경라인 등).
    # signals(문자열 라벨)와 병행 유지(하위호환). 카드 표시·예외처리(FR-4.2c)에 사용.
    signal_details: list[dict] = field(default_factory=list)
    # 커밋 발생 일자(YYYY-MM-DD) 목록. 타임라인 차트·상세 드릴다운용. Git 없으면 빈 목록.
    commit_dates: list[str] = field(default_factory=list)
    # v1.7 레이더 세부 축 점수. 가용 소스별 3개 세부 지표를 0~1 정규화. 표시 전용(STR-7).
    # 키 예: git_commits/git_additions/git_deletions, doc_chars/doc_count/doc_blocks,
    # msg_count/msg_chars/msg_hours. 결측 소스 키는 미포함 → 가용 소스 1·2·3개에 3·6·9키.
    dimensions: dict[str, float] = field(default_factory=dict)
