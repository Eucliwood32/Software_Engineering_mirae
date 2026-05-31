"""FR-1.3 AliasExtractor 단위 테스트 — 식별자 수집 + 결정론적 후보 그룹 제안."""
from qce.model.business.alias_extractor import AliasExtractor
from qce.model.types import CommitStats


def _ex():
    return AliasExtractor()


def test_normalize_strips_separators_and_case():
    assert _ex().normalize_key("DH-Lee") == "dhlee"
    assert _ex().normalize_key("dh.lee") == "dhlee"
    assert _ex().normalize_key("dh lee") == "dhlee"


def test_normalize_email_local_part():
    assert _ex().normalize_key("daehan.lee@gmail.com") == "daehanlee"


def test_extract_identifiers_from_three_sources():
    git = {"dh-lee": CommitStats(3, 120, 10, [])}
    docs = {"이대한": 800}
    msgs = {"대한": 42}
    rows = _ex().extract_identifiers(git, docs, msgs)
    assert {r["raw_id"] for r in rows} == {"dh-lee", "이대한", "대한"}
    git_row = next(r for r in rows if r["raw_id"] == "dh-lee")
    assert git_row["source"] == "git"
    assert git_row["activity"] == 120


def test_extract_is_deterministic_sorted():
    git = {"b": CommitStats(1, 1, 0, []), "a": CommitStats(1, 1, 0, [])}
    rows1 = _ex().extract_identifiers(git, None, None)
    rows2 = _ex().extract_identifiers(git, None, None)
    assert rows1 == rows2
    assert [r["raw_id"] for r in rows1] == ["a", "b"]


def test_suggest_groups_clusters_similar_aliases():
    groups = _ex().suggest_groups(["dh-lee", "dh.lee", "DH LEE"])
    # 셋 다 같은 정규화 키 → 한 그룹
    assert len(groups) == 1
    rep, members = next(iter(groups.items()))
    assert members == sorted(["dh-lee", "dh.lee", "DH LEE"])


def test_suggest_groups_prefers_hangul_representative():
    groups = _ex().suggest_groups(["이대한", "이대한"])
    assert "이대한" in groups


def test_suggest_groups_keeps_distinct_aliases_separate():
    groups = _ex().suggest_groups(["alice", "bob"])
    assert set(groups.keys()) == {"alice", "bob"}


def test_suggest_groups_excludes_unknown():
    groups = _ex().suggest_groups(["Unknown", "alice"])
    assert "Unknown" not in groups
    assert "alice" in groups


def test_suggest_mapping_maps_each_alias_to_representative():
    git = {"dh-lee": CommitStats(1, 5, 0, [])}
    docs = {"dh.lee": 100}
    mapping = _ex().suggest_mapping(_ex().extract_identifiers(git, docs, None))
    # 동일 인물 → 같은 대표명으로 매핑
    assert mapping["dh-lee"] == mapping["dh.lee"]


def test_suggest_mapping_deterministic():
    git = {"a1": CommitStats(1, 1, 0, []), "a-1": CommitStats(1, 1, 0, [])}
    m1 = _ex().suggest_mapping(_ex().extract_identifiers(git, None, None))
    m2 = _ex().suggest_mapping(_ex().extract_identifiers(git, None, None))
    assert m1 == m2
