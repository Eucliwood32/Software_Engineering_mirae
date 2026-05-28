"""FR-3.1/3.2 MessengerParser: 카카오톡 .txt 파싱."""
from __future__ import annotations
import re
from qce.model.types import MessengerRecord, ParseResult
from qce.model.parsing.encoding_handler import EncodingHandler

# 발화줄 패턴 (test-plan §4.3)
_MSG_RE = re.compile(
    r"^\[(?P<author>.+?)\] \[(?P<ap>오전|오후) (?P<h>\d{1,2}):(?P<m>\d{2})\] (?P<msg>.*)$"
)
# 날짜 구분줄 패턴
_DATE_RE = re.compile(r"^\d{4}년 \d{1,2}월 \d{1,2}일")


class MessengerParser:
    def parse(self, path: str) -> ParseResult:
        """카톡 .txt → ParseResult(records, skipped_lines).
        오염 줄 skip + 카운트. 인코딩은 EncodingHandler 경유."""
        raw = EncodingHandler().read_text(path)
        if isinstance(raw, dict):
            return ParseResult(records=[], skipped_lines=0)

        records: list[MessengerRecord] = []
        skipped = 0

        for line in raw.splitlines():
            line = line.strip()
            if not line:
                continue
            if _DATE_RE.match(line):
                continue                         # 날짜 구분줄 — record 아님
            m = _MSG_RE.match(line)
            if m:
                ap, h, mn = m.group("ap"), int(m.group("h")), int(m.group("m"))
                if ap == "오후" and h != 12:
                    h += 12
                elif ap == "오전" and h == 12:
                    h = 0
                timestamp = f"{h:02d}:{mn:02d}"
                records.append(MessengerRecord(
                    author=m.group("author"),
                    timestamp=timestamp,
                    message=m.group("msg"),
                ))
            else:
                skipped += 1

        return ParseResult(records=records, skipped_lines=skipped)
