"""
FR-4.1 Min-Max 정규화 단위 테스트 (L1)
TC-FR-4.1-01 ~ TC-FR-4.1-06
"""
import pytest
from qce.model.business.normalizer import Normalizer


@pytest.mark.parametrize("inp,exp", [
    ([0, 50, 100], [0.0, 0.5, 1.0]),         # TC-FR-4.1-01 기본
    ([75, 75, 75], [0.5, 0.5, 0.5]),          # TC-FR-4.1-02 분산 0
])
def test_normalize_basic(inp, exp):
    assert Normalizer().normalize(inp) == exp


def test_normalize_zero_variance_no_exception():  # TC-FR-4.1-02
    result = Normalizer().normalize([42, 42, 42])
    assert result == [0.5, 0.5, 0.5]


def test_normalize_range():                        # TC-FR-4.1-03
    import random
    random.seed(0)
    vals = [random.uniform(0.1, 100) for _ in range(20)]
    result = Normalizer().normalize(vals)
    assert all(0.0 <= v <= 1.0 for v in result)


def test_normalize_two_elements():                 # TC-FR-4.1-04
    assert Normalizer().normalize([1, 2]) == [0.0, 1.0]


def test_normalize_rounding():                     # TC-FR-4.1-05
    result = Normalizer().normalize([10, 20, 30, 40])
    for v in result:
        # 소수점 4자리 이하는 0 (반올림 결과가 4자리 범위 내)
        assert round(v, 4) == v


def test_normalize_empty():                        # TC-FR-4.1-06
    result = Normalizer().normalize([])
    assert result == []
