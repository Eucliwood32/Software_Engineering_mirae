"""
공통 pytest 픽스처 (test-plan §5).
"""
import os
import pytest
from tests.fixtures import factories


@pytest.fixture
def tmp_docx(tmp_path):
    return lambda author, text, name="d.docx": factories.make_docx(
        str(tmp_path / name), author, text)


@pytest.fixture
def tmp_pptx(tmp_path):
    return lambda last_modified_by, slides, name="s.pptx": factories.make_pptx(
        str(tmp_path / name), last_modified_by, slides)


@pytest.fixture
def git_repo(tmp_path):
    return lambda commits, name="repo": factories.make_git_repo(
        str(tmp_path / name), commits)


@pytest.fixture
def katalk(tmp_path):
    return lambda lines, enc="utf-8", name="chat.txt": factories.make_katalk(
        str(tmp_path / name), lines, enc)


@pytest.fixture(autouse=True)
def _no_network(monkeypatch):
    """모든 테스트에서 네트워크 연결 시도 시 즉시 실패(NFR-2.2 런타임 보강)."""
    import socket

    def deny(*a, **k):
        raise RuntimeError("Network access attempted (NFR-2.2 violation)")

    monkeypatch.setattr(socket.socket, "connect", deny)
