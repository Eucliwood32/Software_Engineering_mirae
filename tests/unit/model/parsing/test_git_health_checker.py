"""
FR-2.2 GitHealthChecker 로직 단위 테스트 (L1)
TC-FR-2.2-01 ~ 04
"""
import subprocess
import pytest
from qce.model.parsing.git_health_checker import GitHealthChecker


def test_health_missing(monkeypatch):                 # TC-FR-2.2-01
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: (_ for _ in ()).throw(FileNotFoundError()),
    )
    assert GitHealthChecker().is_available() is False


def test_health_nonzero_returncode(monkeypatch):      # TC-FR-2.2-02
    class FakeResult:
        returncode = 1
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())
    assert GitHealthChecker().is_available() is False


def test_health_ok(monkeypatch):                      # TC-FR-2.2-03
    class FakeResult:
        returncode = 0
        stdout = "git version 2.x"
    monkeypatch.setattr(subprocess, "run", lambda *a, **k: FakeResult())
    assert GitHealthChecker().is_available() is True


def test_health_timeout(monkeypatch):                 # TC-FR-2.2-04
    monkeypatch.setattr(
        subprocess, "run",
        lambda *a, **k: (_ for _ in ()).throw(
            subprocess.TimeoutExpired(cmd="git", timeout=5)
        ),
    )
    assert GitHealthChecker().is_available() is False
