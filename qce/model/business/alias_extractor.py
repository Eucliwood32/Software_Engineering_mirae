"""FR-1.3 AliasExtractor: 세 소스의 식별자를 수집하고, 결정론적 군집화로
N:1 매핑 후보 그룹을 자동 제안한다.

AliasMapper(주어진 매핑 합산)와 달리, 본 모듈은 *사용자가 확정하기 전 단계*에서
유사 식별자를 묶어 초기 추천 매핑을 만든다. 자동 병합을 강제하지 않으며
(서로 다른 미매핑 식별자 임의 병합 금지, FR-1.3), 어디까지나 다이얼로그의
기본값 제안용이다. 동일 입력 → 동일 출력(NFR-1.3 결정론).

INV: model 레이어이므로 view/controller를 import하지 않는다.
"""
from __future__ import annotations

import re
from typing import Optional

from qce.model.types import CommitStats

# contract.py의 식별자 dict 키와 동일 문자열(뷰 의존 없이 값만 맞춘다).
K_RAW_ID = "raw_id"
K_SOURCE = "source"
K_ACTIVITY = "activity"

SRC_GIT = "git"
SRC_DOC = "doc"
SRC_MSG = "messenger"

_SEP_RE = re.compile(r"[\s._\-]+")
_HANGUL_RE = re.compile(r"[가-힣]")
# 식별자가 아닌 분류 라벨(FR-1.2): 자동 그룹 대상에서 제외한다.
_NON_IDENTIFIERS = frozenset({"Unknown", "unknown", ""})


class AliasExtractor:
    @staticmethod
    def normalize_key(alias: str) -> str:
        """비교용 정규화 키: 이메일 로컬파트만 취하고, 공백·`. _ -` 제거 후 소문자."""
        a = (alias or "").strip()
        if "@" in a:
            a = a.split("@", 1)[0]
        a = _SEP_RE.sub("", a)
        return a.lower()

    def extract_identifiers(
        self,
        git: Optional[dict[str, CommitStats]] = None,
        docs: Optional[dict[str, int]] = None,
        msgs: Optional[dict[str, int]] = None,
    ) -> list[dict]:
        """세 소스에서 (raw_id, source, activity) 식별자 목록을 만든다.
        동일 raw_id가 여러 소스에 있으면 소스별로 각각 행을 만든다.
        결정론을 위해 (raw_id, source) 기준 정렬해 반환한다.
        """
        rows: list[dict] = []
        if git:
            for rid, stats in git.items():
                act = stats.additions if isinstance(stats, CommitStats) else int(stats)
                rows.append({K_RAW_ID: rid, K_SOURCE: SRC_GIT, K_ACTIVITY: int(act)})
        if docs:
            for rid, chars in docs.items():
                rows.append({K_RAW_ID: rid, K_SOURCE: SRC_DOC, K_ACTIVITY: int(chars)})
        if msgs:
            for rid, count in msgs.items():
                rows.append({K_RAW_ID: rid, K_SOURCE: SRC_MSG, K_ACTIVITY: int(count)})
        rows.sort(key=lambda r: (r[K_RAW_ID], r[K_SOURCE]))
        return rows

    def unique_aliases(self, identifiers: list[dict]) -> list[str]:
        """식별자 목록에서 분류 라벨을 제외한 고유 raw_id 정렬 목록."""
        seen: dict[str, None] = {}
        for ident in identifiers:
            rid = ident.get(K_RAW_ID, "")
            if rid in _NON_IDENTIFIERS:
                continue
            seen.setdefault(rid, None)
        return sorted(seen.keys())

    def suggest_groups(self, aliases: list[str]) -> dict[str, list[str]]:
        """정규화 키가 같은 alias끼리 묶어 {대표명: [alias...]} 반환.
        대표명은 그룹 내에서 (한글 포함 우선, 길이 큰 순, 사전순) 1순위를 택한다.
        """
        buckets: dict[str, list[str]] = {}
        for alias in aliases:
            if alias in _NON_IDENTIFIERS:
                continue
            key = self.normalize_key(alias)
            if not key:
                continue
            buckets.setdefault(key, [])
            if alias not in buckets[key]:
                buckets[key].append(alias)

        groups: dict[str, list[str]] = {}
        for members in buckets.values():
            rep = self._pick_representative(members)
            groups[rep] = sorted(members)
        return groups

    def suggest_mapping(self, identifiers: list[dict]) -> dict[str, str]:
        """식별자 목록 → 추천 초기 매핑 {raw_id: 대표명}. 다이얼로그 기본값용."""
        aliases = self.unique_aliases(identifiers)
        groups = self.suggest_groups(aliases)
        mapping: dict[str, str] = {}
        for rep, members in groups.items():
            for alias in members:
                mapping[alias] = rep
        return mapping

    @staticmethod
    def _pick_representative(members: list[str]) -> str:
        """대표명 선택: 한글 포함 > 길이 큰 순 > 사전순. (결정론)"""
        def rank(name: str) -> tuple[int, int, str]:
            has_hangul = 1 if _HANGUL_RE.search(name) else 0
            return (-has_hangul, -len(name), name)

        return sorted(members, key=rank)[0]
