from dataclasses import dataclass, field
from typing import List, Dict

@dataclass
class MemberScore:
    author: str
    git_score: float = 0.0
    doc_score: float = 0.0
    msg_score: float = 0.0
    total_score: float = 0.0
    raw_additions: int = 0
    raw_char_count: int = 0
    raw_msg_count: int = 0
    capping_applied: bool = False
    anomaly_flags: list = field(default_factory=list)

class ParseResult:
    def __init__(self, records, skipped_lines):
        self.records = records
        self.skipped_lines = skipped_lines

class DocumentParser:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
    def parse(self, path: str) -> Dict[str, int]:
        if self.should_fail:
            raise RuntimeError("Document parse error")
        return {"Alice": 100}
    def count_shapes(self, path: str) -> int:
        return 1

class GitAnalyzer:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
    def analyze(self, path: str) -> Dict[str, dict]:
        if self.should_fail:
            raise RuntimeError("Git analyze error")
        return {"alice@test.com": {"commits": 1, "additions": 10, "deletions": 5}}

class MessengerParser:
    def __init__(self, should_fail=False):
        self.should_fail = should_fail
    def parse(self, path: str) -> ParseResult:
        if self.should_fail:
            raise RuntimeError("Messenger parse error")
        return ParseResult(["msg1"], 0)

class AliasMapper:
    def merge(self, raw: dict, mapping: dict) -> dict:
        return {"Alice": {"git": {}, "docs": 100, "msg": 1}}

class ContributionAggregator:
    def aggregate(self, git, docs, msgs, weights) -> List[MemberScore]:
        return [MemberScore(author="Alice", total_score=0.9)]

class CacheManager:
    def save(self, data: dict) -> None:
        pass
