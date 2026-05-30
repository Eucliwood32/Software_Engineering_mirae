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
