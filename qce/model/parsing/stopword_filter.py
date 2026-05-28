"""FR-3.3 StopwordFilter: 자동 불용어 제외 후 유효 메시지 수 집계.
결정론 보장, 사용자 편집 API 미제공."""
from __future__ import annotations
import re
from qce.model.types import MessengerRecord

# 미디어 태그: (이모티콘), (사진), (동영상), (파일) 등 괄호 태그
_MEDIA_RE = re.compile(r"^\([^)]+\)$")

# 단순 리액션: 자음/모음 반복 (ㅇㅇ, ㅋㅋ, ㅎㅎ, ㄱㄱ, ㄴㄴ, ㄷㄷ, ㅠㅠ 등)
_REACTION_RE = re.compile(r"^[ㄱ-ㅎㅏ-ㅣ]+$")

# 1글자 단순 응답 목록 (사용자 편집 불가)
_ONE_WORD_STOPWORDS = frozenset({"네", "예", "응", "굳", "ㅇ", "오", "어", "음"})


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
    def count_valid_messages(
        self, records: list[MessengerRecord]
    ) -> dict[str, int]:
        """자동 불용어 제외 후 {author: 유효 메시지 수}. 결정론 보장."""
        counts: dict[str, int] = {}
        for rec in records:
            if not _is_stopword(rec.message):
                counts[rec.author] = counts.get(rec.author, 0) + 1
        return counts
