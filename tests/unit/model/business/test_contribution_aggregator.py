"""
FR-5.1b v1.7 — ContributionAggregator 레이더 세부 축(dimensions) 단위 테스트 (L1).

가용 소스마다 3개 세부 지표를 0~1 정규화하여 MemberScore.dimensions에 담는다.
가용 소스 1·2·3개 → 3·6·9키. 세부 축은 표시 전용으로 total_score에 비반영(STR-7).
"""
from qce.model.business.BusinessLogic import ContributionAggregator, CommitStats

WEIGHTS = {"git": 0.4, "doc": 0.4, "msg": 0.2}
DOC_DETAILS = {
    "A": {"chars": 300, "docs": 2, "blocks": 12},
    "B": {"chars": 600, "docs": 1, "blocks": 20},
}
MSG_DETAILS = {
    "A": {"count": 20, "chars": 180, "hours": 4},
    "B": {"count": 10, "chars": 90, "hours": 2},
}
GIT_KEYS = {"git_commits", "git_additions", "git_deletions"}
DOC_KEYS = {"doc_chars", "doc_count", "doc_blocks"}
MSG_KEYS = {"msg_count", "msg_chars", "msg_hours"}


def _agg():
    return ContributionAggregator()


def test_git_only_has_three_keys():
    git = {"A": CommitStats(3, 100, 10), "B": CommitStats(5, 200, 20)}
    result = _agg().aggregate(git=git, docs=None, msgs=None, weights=WEIGHTS)
    for s in result:
        assert set(s.dimensions) == GIT_KEYS
        assert all(0.0 <= v <= 1.0 for v in s.dimensions.values())


def test_two_sources_has_six_keys():
    docs = {"A": 300, "B": 600}
    msgs = {"A": 20, "B": 10}
    result = _agg().aggregate(git=None, docs=docs, msgs=msgs, weights=WEIGHTS,
                              doc_details=DOC_DETAILS, msg_details=MSG_DETAILS)
    for s in result:
        assert set(s.dimensions) == DOC_KEYS | MSG_KEYS
        assert not (GIT_KEYS & set(s.dimensions))


def test_three_sources_has_nine_keys():
    git = {"A": CommitStats(5, 500, 50), "B": CommitStats(3, 100, 10)}
    docs = {"A": 300, "B": 600}
    msgs = {"A": 20, "B": 10}
    result = _agg().aggregate(git, docs, msgs, WEIGHTS,
                              doc_details=DOC_DETAILS, msg_details=MSG_DETAILS)
    for s in result:
        assert set(s.dimensions) == GIT_KEYS | DOC_KEYS | MSG_KEYS


def test_doc_details_absent_omits_doc_keys():
    """문서 세부 데이터가 없으면 문서 세부 축은 생성하지 않는다(축 미생성)."""
    git = {"A": CommitStats(5, 500, 50), "B": CommitStats(3, 100, 10)}
    docs = {"A": 300, "B": 600}
    result = _agg().aggregate(git, docs, None, WEIGHTS)   # doc_details 미전달
    for s in result:
        assert set(s.dimensions) == GIT_KEYS
        assert not (DOC_KEYS & set(s.dimensions))


def test_single_member_dimensions_are_max():
    """팀원 1명이면 Max 정규화 결과가 1.0 (자신의 값이 최대값이므로)."""
    git = {"A": CommitStats(3, 100, 10)}
    result = _agg().aggregate(git=git, docs=None, msgs=None, weights=WEIGHTS)
    assert result[0].dimensions == {
        "git_commits": 1.0, "git_additions": 1.0, "git_deletions": 1.0,
    }


def test_dimensions_do_not_affect_total_score():
    """세부 축은 표시 전용 — total_score는 기존 git/doc score 가중합의 비율과 동일(STR-7)."""
    git = {"A": CommitStats(5, 500, 50), "B": CommitStats(3, 100, 10)}
    docs = {"A": 300, "B": 600}
    result = _agg().aggregate(git, docs, None, {"git": 0.5, "doc": 0.5, "msg": 0.0})
    raw_totals = [s.git_score * 0.5 + s.doc_score * 0.5 for s in result]
    sum_raw = sum(raw_totals)
    
    for i, s in enumerate(result):
        expected = round(raw_totals[i] / sum_raw, 4) if sum_raw > 0 else 0.5
        assert abs(s.total_score - expected) < 1e-4

def test_total_score_sum_is_one():
    """팀원들의 total_score 합계는 항상 1.0(100%)이어야 한다."""
    git = {"A": CommitStats(5, 500, 50), "B": CommitStats(3, 100, 10), "C": CommitStats(10, 1000, 100)}
    docs = {"A": 300, "B": 600, "C": 100}
    msgs = {"A": 20, "B": 10, "C": 50}
    result = _agg().aggregate(git, docs, msgs, WEIGHTS)
    
    total_sum = sum(s.total_score for s in result)
    assert abs(total_sum - 1.0) < 1e-4
