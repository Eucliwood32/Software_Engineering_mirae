"""
L3 UI 테스트 공통 픽스처.

View는 plain dict만 소비하므로(view-design 결정 A), 차트 테스트는 §5.3 스키마를
만족하는 list[dict]를 주입한다. 실제 Controller가 push하는 형태와 동일하게
dataclasses.asdict(MemberScore)로 생성해 계약 정합성도 함께 검증한다.
"""
from __future__ import annotations

import dataclasses

import pytest

from tests.fixtures.factories import sample_scores


@pytest.fixture
def score_dicts():
    """기본 4팀원 점수 dict 목록(§5.3 스키마)."""
    return [dataclasses.asdict(s) for s in sample_scores(4)]
