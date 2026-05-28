"""FR-1.3 신원 매핑: 여러 alias → 단일 팀원명으로 N:1 합산."""
from __future__ import annotations


class AliasMapper:
    def merge(self, raw: dict[str, dict], mapping: dict[str, str]) -> dict[str, dict]:
        """raw = {alias: {지표...}}, mapping = {alias: 팀원명}.
        매핑된 alias들의 지표를 팀원 단위로 합산(N:1).
        mapping에 없는 alias는 결과에서 제외."""
        result: dict[str, dict] = {}
        for alias, metrics in raw.items():
            team_member = mapping.get(alias)
            if team_member is None:
                continue
            if team_member not in result:
                result[team_member] = {}
            for key, val in metrics.items():
                result[team_member][key] = result[team_member].get(key, 0) + val
        return result
