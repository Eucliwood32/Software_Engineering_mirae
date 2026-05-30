"""L2 통합: NFR-3.2 데이터 모듈 상호 격리 + FR-4.3 동적 가중치 재조정.

임의의 1~2개 소스만 가용한 상황(나머지 None=결측/실패)에서도 ContributionAggregator가
예외 없이 가용 소스만으로 종합 점수를 산출하고, 가중치가 1.0으로 재정규화되는지 검증한다.
"""
from __future__ import annotations

import pytest

from qce.model.types import CommitStats
from qce.model.business.contribution_aggregator import ContributionAggregator

GIT = {"a@t.com": CommitStats(2, 100, 5, []), "b@t.com": CommitStats(1, 40, 2, [])}
DOCS = {"a@t.com": 300, "b@t.com": 100}
MSGS = {"a@t.com": 10, "b@t.com": 4}
W = {"git": 0.4, "doc": 0.4, "msg": 0.2}


def _agg():
    return ContributionAggregator()


# ── 단일 소스만 가용 (FR-4.3: 가중치 1.0) ────────────────────────────────

@pytest.mark.parametrize("src", ["git", "doc", "msg"])
def test_single_source_available(src):
    """1개 소스만 가용 → 종합 점수 = 해당 소스 정규화 점수 (가중치 1.0)."""
    kwargs = {"git": None, "docs": None, "msgs": None, "weights": W}
    if src == "git":
        kwargs["git"] = GIT
    elif src == "doc":
        kwargs["docs"] = DOCS
    else:
        kwargs["msgs"] = MSGS

    scores = _agg().aggregate(**kwargs)

    assert scores, "가용 소스가 1개라도 있으면 점수가 생성돼야 함"
    for s in scores:
        attr = {"git": "git_score", "doc": "doc_score", "msg": "msg_score"}[src]
        assert abs(s.total_score - getattr(s, attr)) < 1e-6, \
            "단일 소스의 종합 점수는 해당 소스 정규화 점수와 같아야 함"


# ── 2개 소스 가용 (FR-4.3: 상대 비율 유지 재정규화) ──────────────────────

@pytest.mark.parametrize("missing", ["git", "doc", "msg"])
def test_two_sources_available(missing):
    """3개 중 1개 결측 → 나머지 2개로 정상 산출, 예외 없음."""
    kwargs = {"git": GIT, "docs": DOCS, "msgs": MSGS, "weights": W}
    kwargs[{"git": "git", "doc": "docs", "msg": "msgs"}[missing]] = None

    scores = _agg().aggregate(**kwargs)

    assert scores
    for s in scores:
        assert 0.0 <= s.total_score <= 1.0
        # 결측 소스의 정규화 점수는 0.0
        if missing == "git":
            assert s.git_score == 0.0
        elif missing == "doc":
            assert s.doc_score == 0.0
        else:
            assert s.msg_score == 0.0


def test_one_failed_source_does_not_break_others():
    """한 소스가 None(파싱 실패)이어도 나머지 결과가 최종 결과에 정상 포함 (NFR-3.2)."""
    # docs 실패(None)로 간주 → git/msg 결과는 그대로 산출
    scores = _agg().aggregate(git=GIT, docs=None, msgs=MSGS, weights=W)
    authors = {s.author for s in scores}
    assert {"a@t.com", "b@t.com"} <= authors
    # git 활동이 많은 a@t.com 이 b@t.com 보다 종합 점수가 높아야 함
    by_author = {s.author: s.total_score for s in scores}
    assert by_author["a@t.com"] >= by_author["b@t.com"]


def test_all_sources_missing_returns_empty():
    """3개 소스 모두 부재 → 빈 결과(예외 없음). 차단 안내는 Controller 책임(FR-4.3)."""
    scores = _agg().aggregate(git=None, docs=None, msgs=None, weights=W)
    assert scores == []
