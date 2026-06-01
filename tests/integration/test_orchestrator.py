"""L2 통합: AnalysisOrchestrator 비동기 파이프라인 + NFR-1.2 중복 실행 방지.

Orchestrator는 QThreadPool Worker에서 파서·집계를 실행하고 completed Signal로
결과를 메인 스레드에 넘긴다. qtbot으로 Signal 흐름과 is_analyzing 가드를 검증한다.
"""
from __future__ import annotations

import pytest

from qce.controller.Controller import AnalysisOrchestrator


@pytest.fixture
def orchestrator(qtbot):
    return AnalysisOrchestrator()


def test_start_analysis_emits_completed(orchestrator, qtbot, tmp_docx, git_repo, katalk):
    """start_analysis → Worker 실행 → completed(list[MemberScore]) 발행 (NFR-1.1)."""
    config = {
        "doc_paths": [tmp_docx("Alice", "가" * 150)],
        "git_path": git_repo([
            {"email": "alice@test.com", "date": "2024-01-01 10:00:00", "add": 40, "del": 1},
        ]),
        "msg_path": katalk([("Alice", "회의록 정리했습니다"), ("Bob", "확인했어요")]),
        "weights": {"git": 0.4, "doc": 0.4, "msg": 0.2},
    }

    with qtbot.waitSignal(orchestrator.completed, timeout=30000) as blocker:
        orchestrator.start_analysis(config)

    scores = blocker.args[0]
    assert scores, "completed Signal로 비어있지 않은 점수 목록이 와야 함"
    authors = {s.author for s in scores}
    assert "alice@test.com" in authors
    # 종료 후 is_analyzing 해제 (재실행 가능 상태)
    assert orchestrator.is_analyzing is False


def test_duplicate_run_blocked(orchestrator, qtbot):
    """이미 분석 중이면 추가 start_analysis는 무시된다 (NFR-1.2)."""
    fired = []
    orchestrator.completed.connect(lambda s: fired.append(s))

    # 분석 진행 중 상태를 강제
    orchestrator.is_analyzing = True
    orchestrator.start_analysis({"doc_paths": [], "git_path": "", "msg_path": "",
                                 "weights": {"git": 0.4, "doc": 0.4, "msg": 0.2}})

    # 가드가 즉시 return 했으므로 Worker가 기동되지 않아 completed 미발행
    qtbot.wait(300)
    assert fired == [], "중복 실행 시 새 Worker가 기동되면 안 됨"
    assert orchestrator.is_analyzing is True


def test_partial_source_still_completes(orchestrator, qtbot, git_repo):
    """일부 소스만 제공(git만) → 예외 없이 completed 발행 (NFR-3.2)."""
    config = {
        "doc_paths": [],
        "git_path": git_repo([
            {"email": "solo@test.com", "date": "2024-01-01 10:00:00", "add": 20, "del": 0},
        ]),
        "msg_path": "",
        "weights": {"git": 0.4, "doc": 0.4, "msg": 0.2},
    }

    with qtbot.waitSignal(orchestrator.completed, timeout=30000) as blocker:
        orchestrator.start_analysis(config)

    scores = blocker.args[0]
    assert scores
    # FR-4.1 (v1.6) 비례 정규화에 의해 total_score 합계는 1.0이 된다.
    total_sum = sum(s.total_score for s in scores)
    assert abs(total_sum - 1.0) < 1e-4
    
    for s in scores:
        expected_total = s.git_score / sum(x.git_score for x in scores)
        assert abs(s.total_score - expected_total) < 1e-4


def test_merge_reaggregation_after_analysis(orchestrator, qtbot, tmp_docx, git_repo, katalk):
    """1차 분석(전 소스) 완료 후 병합 재집계 → MergeWorker 경로 검증 (FR-1.3)."""
    config = {
        "doc_paths": [tmp_docx("Alice", "가" * 100)],
        "git_path": git_repo([
            {"email": "alice@test.com", "date": "2024-01-01 10:00:00", "add": 30, "del": 1},
        ]),
        "msg_path": katalk([("Alice", "정리 자료입니다"), ("Bob", "확인했어요")]),
        "weights": {"git": 0.4, "doc": 0.4, "msg": 0.2},
    }
    with qtbot.waitSignal(orchestrator.completed, timeout=30000) as b1:
        orchestrator.start_analysis(config)
    first = {s.author for s in b1.args[0]}
    assert "alice@test.com" in first

    # 모든 raw 식별자를 단일 인격으로 N:1 병합
    mapping = {alias: "Alice" for alias in first}
    with qtbot.waitSignal(orchestrator.completed, timeout=30000) as b2:
        orchestrator.start_merge_reaggregation(mapping)

    merged = b2.args[0]
    assert merged, "병합 재집계 결과가 비어있으면 안 됨"
    assert all(s.author == "Alice" for s in merged)   # N:1 병합 결과
    assert orchestrator.is_analyzing is False


def test_katalk_standalone_pipeline(orchestrator, qtbot, katalk):
    """카카오톡만 입력(git·문서 없음)해도 파이프라인이 정상 종료되고
    분석 결과가 반환된다 (TC-FR-3.1-06, FR-3.1 단독 분석 보장)."""
    config = {
        "doc_paths": [],
        "git_path": "",
        "msg_path": katalk([("A", "회의 시작"), ("B", "확인"), ("A", "수고")]),
        "weights": {"git": 0.4, "doc": 0.4, "msg": 0.2},
    }

    with qtbot.waitSignal(orchestrator.completed, timeout=30000) as blocker:
        orchestrator.start_analysis(config)

    scores = blocker.args[0]
    assert scores, "카카오톡 단독 입력에서도 점수 목록이 반환돼야 함"
    authors = {s.author for s in scores}
    assert "A" in authors
    assert "B" in authors
    assert orchestrator.is_analyzing is False


def test_katalk_all_authors_appear_in_scores(orchestrator, qtbot, katalk):
    """불용어만 발화한 팀원도 msg_data에서 누락되지 않아 scores에 포함된다
    (TC-FR-3.1-07 오케스트레이터 레벨, FR-3.1 식별자 누락 방지)."""
    # "ㅇㅇ"은 불용어(_REACTION_RE) → filtered count=0이지만 author는 보존돼야 함
    config = {
        "doc_paths": [],
        "git_path": "",
        "msg_path": katalk([
            ("Alice", "오늘 회의록 정리했습니다"),
            ("Bob", "ㅇㅇ"),
            ("Charlie", "네"),
        ]),
        "weights": {"git": 0.4, "doc": 0.4, "msg": 0.2},
    }

    with qtbot.waitSignal(orchestrator.completed, timeout=30000) as blocker:
        orchestrator.start_analysis(config)

    scores = blocker.args[0]
    authors = {s.author for s in scores}
    assert "Alice" in authors, "유효 발화자가 scores에 없음"
    assert "Bob" in authors, "불용어 전용 발화자가 식별자 목록에서 누락됨"
    assert "Charlie" in authors, "단일 불용어 발화자가 누락됨"


def test_failure_resets_is_analyzing(orchestrator, qtbot, monkeypatch):
    """Worker 내부 예외 발생 시 failed 발행 + is_analyzing 해제 (NFR-1.2 비정상 종료 복원)."""
    import qce.controller.Controller as mod

    def boom(self):
        self.signals.failed.emit("forced failure")

    monkeypatch.setattr(mod.AnalysisWorker, "run", boom)

    config = {"doc_paths": [], "git_path": "x", "msg_path": "",
              "weights": {"git": 0.4, "doc": 0.4, "msg": 0.2}}

    with qtbot.waitSignal(orchestrator.failed, timeout=10000):
        orchestrator.start_analysis(config)

    assert orchestrator.is_analyzing is False
