"""L2 통합: 파서 3종 출력 → ContributionAggregator → MemberScore 전 구간.

실제 픽스처(.docx / git repo / 카카오톡 .txt)를 실제 파서로 파싱하고,
그 출력을 비즈니스 로직 파이프라인에 주입해 최종 MemberScore까지 검증한다.
파싱·집계 레이어가 인터페이스 정합성을 유지하며 하나로 연결되는지 확인한다.
"""
from __future__ import annotations

from qce.model.parsing.document_parser import DocumentParser
from qce.model.parsing.git_analyzer import GitAnalyzer
from qce.model.parsing.messenger_parser import MessengerParser
from qce.model.parsing.stopword_filter import StopwordFilter
from qce.model.business.contribution_aggregator import ContributionAggregator


def _run_pipeline(doc_path, git_path, kakao_path, weights=None):
    """worker_thread/orchestrator가 수행하는 파이프라인을 동기로 재현."""
    # 1. 문서 (FR-1.1)
    docs = DocumentParser().parse(doc_path)

    # 2. Git (FR-2.1)
    git = GitAnalyzer().analyze(git_path)

    # 3. 메신저 + 불용어 (FR-3.1, FR-3.3)
    parsed = MessengerParser().parse(kakao_path)
    msgs = StopwordFilter().count_valid_messages(parsed.records)

    # 4. 집계 (FR-4.*)
    return ContributionAggregator().aggregate(
        git=git, docs=docs, msgs=msgs,
        weights=weights or {"git": 0.4, "doc": 0.4, "msg": 0.2},
    )


def test_full_pipeline_produces_memberscores(tmp_docx, git_repo, katalk):
    """세 소스 모두 가용 → 각 소스 식별자별 MemberScore 생성."""
    doc = tmp_docx("Alice", "가" * 200)
    repo = git_repo([
        {"email": "alice@test.com", "date": "2024-01-01 10:00:00", "add": 50, "del": 5},
        {"email": "bob@test.com", "date": "2024-01-02 10:00:00", "add": 30, "del": 2},
    ])
    chat = katalk([("Alice", "안녕하세요 회의 정리합니다"),
                   ("Bob", "넵 확인했습니다"),
                   ("Alice", "ㅋㅋ"),                 # 불용어 → 제외
                   ("Bob", "오늘 일정 공유드려요")])

    scores = _run_pipeline(doc, repo, chat)

    assert scores, "MemberScore가 비어 있으면 안 됨"
    # 모든 점수는 0.0~1.0, total은 가중합
    for s in scores:
        assert 0.0 <= s.git_score <= 1.0
        assert 0.0 <= s.doc_score <= 1.0
        assert 0.0 <= s.msg_score <= 1.0
        assert 0.0 <= s.total_score <= 1.0

    # 각 소스의 식별자가 결과에 반영됨
    authors = {s.author for s in scores}
    assert "alice@test.com" in authors        # git 이메일
    assert "bob@test.com" in authors
    assert "Alice" in authors                  # 문서 작성자
    assert "Alice" in authors and "Bob" in authors  # 카톡 발화자


def test_pipeline_stopword_filtering_reduces_msg_count(tmp_docx, git_repo, katalk):
    """불용어(ㅋㅋ/넵 등)는 유효 발화 집계에서 제외되어야 한다 (FR-3.3)."""
    doc = tmp_docx("Alice", "가" * 10)
    repo = git_repo([{"email": "a@t.com", "date": "2024-01-01 10:00:00", "add": 1, "del": 0}])
    chat = katalk([("Carol", "의미있는 메시지 하나"),
                   ("Carol", "ㅋㅋㅋ"),
                   ("Carol", "ㅇㅇ"),
                   ("Carol", "네")])

    parsed = MessengerParser().parse(chat)
    valid = StopwordFilter().count_valid_messages(parsed.records)

    # 4개 발화 중 의미있는 것 1개만 집계
    assert valid.get("Carol", 0) == 1


def test_pipeline_deterministic(tmp_docx, git_repo, katalk):
    """동일 입력 2회 실행 → 종합 점수 완전 일치 (NFR-1.3 결정론)."""
    doc = tmp_docx("Alice", "가" * 120)
    repo = git_repo([
        {"email": "alice@test.com", "date": "2024-01-01 10:00:00", "add": 40, "del": 1},
        {"email": "bob@test.com", "date": "2024-01-02 10:00:00", "add": 60, "del": 3},
    ])
    chat = katalk([("Alice", "정리 자료입니다"), ("Bob", "확인 부탁드려요")])

    first = _run_pipeline(doc, repo, chat)
    second = _run_pipeline(doc, repo, chat)

    f = {s.author: s.total_score for s in first}
    g = {s.author: s.total_score for s in second}
    assert f == g
