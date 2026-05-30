"""공유 데이터 타입. 모든 레이어가 참조하며 역방향 의존 없음."""
from __future__ import annotations
from dataclasses import dataclass, field
from typing import Any


@dataclass
class CommitStats:                      # FR-2.1
    commits: int
    additions: int
    deletions: int
    commits_list: list[dict[str, Any]] = field(default_factory=list)


@dataclass
class MessengerRecord:                  # FR-3.1
    author: str
    timestamp: str
    message: str


@dataclass
class ParseResult:                      # FR-3.2
    records: list[MessengerRecord]
    skipped_lines: int


@dataclass
class MemberScore:                      # FR-4.* 통합 결과
    author: str
    git_score: float
    doc_score: float
    msg_score: float
    total_score: float
    raw_additions: int
    raw_char_count: int
    raw_msg_count: int
    capping_applied: bool
    anomaly_flags: list[str] = field(default_factory=list)
