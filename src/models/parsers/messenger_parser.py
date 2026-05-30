"""FR-3.1/3.2 MessengerParser: 카카오톡 .txt 파싱."""
from __future__ import annotations
import os
import re
import typing
from src.models.types import MessengerRecord, ParseResult
from src.models.parsers.encoding_handler import EncodingHandler

def parse_messenger_file(file_path: str) -> typing.Dict[str, typing.Any]:
    """
    FR-3.1, 3.2: 카카오톡 내보내기 파싱, 방어적 예외 처리 (Slack 기능 제외됨)
    """
    if not os.path.exists(file_path):
        return {"error": "file_not_found", "path": file_path}
        
    # NFR-3.1: 인코딩 자동 감지
    encodings = ['utf-8', 'cp949']
    for enc in encodings:
        try:
            with open(file_path, 'r', encoding=enc) as f:
                return _parse_kakao_txt(f)
        except UnicodeDecodeError:
            continue
            
    return {"error": "encoding_failed", "path": file_path}

_DATE_RE = re.compile(r"^\d{4}년 \d{1,2}월 \d{1,2}일")
_MSG_RE = re.compile(
    r"^\[(?P<author>.+?)\] \[(?P<ap>오전|오후) (?P<h>\d{1,2}):(?P<m>\d{2})\] (?P<msg>.*)$"
)

def _parse_kakao_txt(file_obj) -> typing.Dict[str, typing.Any]:
    records = []
    skipped = 0

    for line in file_obj:
        line = line.strip()
        if not line:
            continue

        try:
            if _DATE_RE.match(line):
                continue

            m = _MSG_RE.match(line)
            if m:
                ap, h, mn = m.group("ap"), int(m.group("h")), int(m.group("m"))
                if ap == "오후" and h != 12:
                    h += 12
                elif ap == "오전" and h == 12:
                    h = 0
                records.append({
                    "author": m.group("author"),
                    "timestamp": f"{h:02d}:{mn:02d}",
                    "message": m.group("msg"),
                })
            else:
                skipped += 1
        except Exception:
            skipped += 1

    return {"records": records, "skipped_lines": skipped}


class MessengerParser:
    """FR-3.1, FR-3.2 — 카카오톡 .txt 파싱. 인코딩은 EncodingHandler 경유."""

    def parse(self, path: str) -> ParseResult:
        """카톡 .txt → ParseResult(records, skipped_lines). 오염 줄 skip + 카운트."""
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
                continue
            m = _MSG_RE.match(line)
            if m:
                ap, h, mn = m.group("ap"), int(m.group("h")), int(m.group("m"))
                if ap == "오후" and h != 12:
                    h += 12
                elif ap == "오전" and h == 12:
                    h = 0
                records.append(MessengerRecord(
                    author=m.group("author"),
                    timestamp=f"{h:02d}:{mn:02d}",
                    message=m.group("msg"),
                ))
            else:
                skipped += 1

        return ParseResult(records=records, skipped_lines=skipped)
