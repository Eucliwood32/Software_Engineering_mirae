"""
FR-2.1 GitAnalyzer 단위 테스트 (L1)
TC-FR-2.1-01 ~ 04, 06
"""
import pytest
from qce.model.parsing.git_analyzer import GitAnalyzer
from qce.model.types import CommitStats


def test_git_exact_stats(git_repo):                   # TC-FR-2.1-01
    repo = git_repo([
        {"email": "base@x.com",        "date": "2024-01-01 00:00:00", "add": 100, "del": 0},
        {"email": "alice@test.com",    "date": "2024-01-02 00:00:00", "add": 10,  "del": 5},
    ])
    stats = GitAnalyzer().analyze(repo)
    a = stats["alice@test.com"]
    assert (a.commits, a.additions, a.deletions) == (1, 10, 5)


def test_git_bad_path_returns_empty():                # TC-FR-2.1-02
    assert GitAnalyzer().analyze("/no/such/repo/xyz_abc") == {}


def test_git_non_git_dir_returns_empty(tmp_path):     # TC-FR-2.1-03
    empty = tmp_path / "notgit"
    empty.mkdir()
    assert GitAnalyzer().analyze(str(empty)) == {}


def test_git_two_authors(git_repo):                   # TC-FR-2.1-04
    repo = git_repo([
        {"email": "alice@x.com", "date": "2024-01-01 00:00:00", "add": 10, "del": 2},
        {"email": "bob@x.com",   "date": "2024-01-02 00:00:00", "add": 7,  "del": 3},
    ])
    stats = GitAnalyzer().analyze(repo)
    assert "alice@x.com" in stats
    assert "bob@x.com"   in stats
    assert stats["alice@x.com"].additions == 10
    assert stats["bob@x.com"].additions   == 7


def test_git_timeout(monkeypatch):                    # TC-FR-2.1-06
    import subprocess
    def boom(*a, **k):
        raise subprocess.TimeoutExpired(cmd="git", timeout=30)
    monkeypatch.setattr(subprocess, "run", boom)
    assert GitAnalyzer().analyze(".") == {}
