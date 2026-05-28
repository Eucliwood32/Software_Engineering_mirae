"""
FR-4.3 데이터 소스 결측 → 동적 가중치 재조정 단위 테스트 (L1)
TC-FR-4.3-01 ~ TC-FR-4.3-06
"""
import pytest
from qce.model.business.weight_rebalancer import WeightRebalancer

BASE = {"git": 0.4, "doc": 0.4, "msg": 0.2}


def test_rebalance_missing_msg():        # TC-FR-4.3-01
    out = WeightRebalancer().rebalance(BASE, available={"git", "doc"})
    assert abs(out["git"] - 0.5) < 1e-4
    assert abs(out["doc"] - 0.5) < 1e-4
    assert out["msg"] == 0.0
    assert abs(sum(out.values()) - 1.0) < 1e-4


def test_rebalance_missing_git():        # TC-FR-4.3-02
    out = WeightRebalancer().rebalance(BASE, available={"doc", "msg"})
    assert out["git"] == 0.0
    assert abs(sum(out.values()) - 1.0) < 1e-4
    # 상대 비율 유지: doc/msg = 0.4/0.2 = 2
    assert abs(out["doc"] / out["msg"] - 2.0) < 1e-4


def test_rebalance_missing_doc():        # TC-FR-4.3-03
    out = WeightRebalancer().rebalance(BASE, available={"git", "msg"})
    assert out["doc"] == 0.0
    assert abs(sum(out.values()) - 1.0) < 1e-4


def test_rebalance_single_source():      # TC-FR-4.3-04
    out = WeightRebalancer().rebalance(BASE, available={"git"})
    assert abs(out["git"] - 1.0) < 1e-4
    assert out["doc"] == 0.0
    assert out["msg"] == 0.0


def test_rebalance_deterministic():      # TC-FR-4.3-06
    rb = WeightRebalancer()
    r1 = rb.rebalance(BASE, available={"git", "doc"})
    r2 = rb.rebalance(BASE, available={"git", "doc"})
    assert r1 == r2
