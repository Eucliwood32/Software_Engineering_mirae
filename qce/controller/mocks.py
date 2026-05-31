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
        # 매핑 여부에 따라 결과를 다르게 반환하여 L2 통합 테스트 지원
        if mapping:
            return {"MergedPerson": 100}
        else:
            return {"Alice": 100}

class ContributionAggregator:
    def aggregate(self, git, docs, msgs, weights) -> List[MemberScore]:
        if docs and "MergedPerson" in docs:
            return [MemberScore(author="MergedPerson", total_score=0.99)]
        return [MemberScore(author="Alice", total_score=0.9)]

class CacheManager:
    def save(self, data: dict) -> None:
        pass

# === Mocks for View layer ===

class ResultScreen:
    def __init__(self):
        self.rendered_scores = []
        self.missing = set()
    def render(self, scores: list[dict], missing: set):
        self.rendered_scores = scores
        self.missing = missing

class MainWindow:
    def __init__(self):
        self.current_screen = None
        self.result_screen = ResultScreen()
    def show_submit(self):
        self.current_screen = "submit"
    def show_loading(self):
        self.current_screen = "loading"
    def show_result(self):
        self.current_screen = "result"
