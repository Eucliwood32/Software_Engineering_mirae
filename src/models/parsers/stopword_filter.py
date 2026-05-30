"""FR-3.3 StopwordFilter: 자동 불용어 제외 후 유효 메시지 수 집계.
결정론 보장, 사용자 편집 API 미제공."""
from __future__ import annotations
import re
from src.models.types import MessengerRecord

_MEDIA_RE = re.compile(r"^\([^)]+\)$")
_REACTION_RE = re.compile(r"^[ㄱ-ㅎㅏ-ㅣ]+$")

_ONE_WORD_STOPWORDS = frozenset({
    "네", "넵", "넹", "넴",
    "예", "옙",
    "응", "웅", "엉",
    "어",
    "음", "오",
    "굳", "굿",
})


def _is_stopword(msg: str) -> bool:
    stripped = msg.strip()
    if not stripped:
        return True
    if _MEDIA_RE.match(stripped):
        return True
    if _REACTION_RE.match(stripped):
        return True
    if stripped in _ONE_WORD_STOPWORDS:
        return True
    return False


class StopwordFilter:
    """FR-3.3 — 자동 불용어 제외 후 {author: 유효 메시지 수}. 결정론 보장."""

    def count_valid_messages(
        self, records: list[MessengerRecord]
    ) -> dict[str, int]:
        counts: dict[str, int] = {}
        for rec in records:
            if not _is_stopword(rec.message):
                counts[rec.author] = counts.get(rec.author, 0) + 1
        return counts
