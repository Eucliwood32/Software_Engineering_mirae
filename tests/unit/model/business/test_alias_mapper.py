"""
FR-1.3 신원 매핑 (AliasMapper) 단위 테스트 (L1)
TC-FR-1.3-01 ~ TC-FR-1.3-04
"""
from qce.model.business.alias_mapper import AliasMapper


def test_n_to_1_merge():                             # TC-FR-1.3-01
    raw = {
        "dh-lee":    {"add": 10},
        "daehan.lee":{"add": 5},
        "이대한":     {"add": 3},
    }
    mapping = {"dh-lee": "이대한", "daehan.lee": "이대한", "이대한": "이대한"}
    out = AliasMapper().merge(raw, mapping)
    assert out["이대한"]["add"] == 18
    assert len(out) == 1


def test_unmapped_excluded():                        # TC-FR-1.3-02
    raw = {"a": {"add": 1}, "ghost1": {"add": 9}}
    out = AliasMapper().merge(raw, {"a": "Alice"})
    assert "Alice" in out
    assert "ghost1" not in out


def test_two_unmapped_not_merged():                  # TC-FR-1.3-03
    raw = {"a": {"add": 1}, "ghost1": {"add": 9}, "ghost2": {"add": 7}}
    out = AliasMapper().merge(raw, {"a": "Alice"})
    assert "ghost1" not in out
    assert "ghost2" not in out
    assert len(out) == 1                             # Alice 하나만


def test_unknown_not_merged_with_unmapped():         # TC-FR-1.3-04
    raw = {
        "Unknown":  {"add": 10},
        "ghost":    {"add": 5},
        "alice":    {"add": 3},
    }
    mapping = {"alice": "Alice"}
    out = AliasMapper().merge(raw, mapping)
    # Unknown과 ghost 모두 제외, Alice만 남음
    assert "Alice" in out
    assert "Unknown" not in out
    assert "ghost" not in out


def test_multiple_keys_summed():
    raw = {
        "a1": {"add": 10, "del": 2},
        "a2": {"add": 5,  "del": 1},
        "b1": {"add": 7,  "del": 3},
    }
    mapping = {"a1": "Alice", "a2": "Alice", "b1": "Bob"}
    out = AliasMapper().merge(raw, mapping)
    assert out["Alice"]["add"] == 15
    assert out["Alice"]["del"] == 3
    assert out["Bob"]["add"] == 7
