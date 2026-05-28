"""
FR-4.2 Capping + 로그 스케일 단위 테스트 (L1)
TC-FR-4.2-01 ~ TC-FR-4.2-06
"""
import math
import pytest
from qce.model.business.capping_scaler import CappingScaler


def test_cap_above_threshold():          # TC-FR-4.2-01
    assert CappingScaler().cap(5000) == (1000, True)


def test_cap_below_threshold():          # TC-FR-4.2-02
    assert CappingScaler().cap(999) == (999, False)


def test_cap_at_boundary():              # TC-FR-4.2-03  경계: > 만 cap
    assert CappingScaler().cap(1000) == (1000, False)


def test_cap_just_above_boundary():      # TC-FR-4.2-04
    assert CappingScaler().cap(1001) == (1000, True)


def test_log_scale_zero():               # TC-FR-4.2-05
    assert CappingScaler().log_scale(0) == 0.0


def test_log_scale_positive():
    scaler = CappingScaler()
    assert abs(scaler.log_scale(999) - math.log1p(999)) < 1e-9


def test_capping_threshold_constant():
    assert CappingScaler.CAPPING_THRESHOLD == 1000
