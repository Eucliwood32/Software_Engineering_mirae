"""Track C — 헤드리스 CLI(qce.cli) 통합 테스트."""
from __future__ import annotations

import pytest

from qce import cli
from qce.model.types import MemberScore


# ── 가중치 파싱 ──────────────────────────────────────────────────────────

def test_parse_weights_default():
    assert cli.parse_weights(None) == {"git": 0.4, "doc": 0.4, "msg": 0.2}


def test_parse_weights_preset_name():
    assert cli.parse_weights("개발 중심") == {"git": 0.60, "doc": 0.25, "msg": 0.15}


def test_parse_weights_triplet():
    assert cli.parse_weights("0.5,0.3,0.2") == {"git": 0.5, "doc": 0.3, "msg": 0.2}


def test_parse_weights_normalizes_when_sum_off():
    out = cli.parse_weights("2,1,1")
    assert abs(sum(out.values()) - 1.0) < 1e-9
    assert out["git"] == 0.5


def test_parse_weights_bad_count_raises():
    with pytest.raises(ValueError):
        cli.parse_weights("0.5,0.5")


# ── 결측 판정 ────────────────────────────────────────────────────────────

def test_detect_missing_reports_absent_sources():
    assert cli.detect_missing("", [], "") == {"Git", "문서", "메신저"}
    assert cli.detect_missing("repo", ["a.docx"], "") == {"메신저"}


# ── 텍스트 표 ────────────────────────────────────────────────────────────

def test_render_text_table_sorts_desc():
    scores = [
        MemberScore("Low", 0.1, 0.1, 0.1, 0.1, 0, 0, 0, False, []),
        MemberScore("High", 0.9, 0.9, 0.9, 0.9, 0, 0, 0, False, ["ZSCORE"]),
    ]
    table = cli.render_text_table(scores)
    assert table.index("High") < table.index("Low")
    assert "ZSCORE" in table


def test_render_text_table_empty():
    assert cli.render_text_table([]) == "(분석 결과 없음)"


# ── main 엔드투엔드 (Git 저장소 실분석) ───────────────────────────────────

def test_main_requires_input(capsys):
    rc = cli.main([])
    assert rc == 2
    assert "최소 하나" in capsys.readouterr().err


def test_main_runs_on_git_repo_and_saves_md(tmp_path):
    from tests.fixtures.factories import make_git_repo

    repo = make_git_repo(str(tmp_path / "repo"), [
        {"email": "alice@t.com", "date": "2024-01-01 10:00:00", "add": 50, "del": 0},
        {"email": "bob@t.com", "date": "2024-01-02 10:00:00", "add": 30, "del": 0},
    ])
    out = tmp_path / "report.md"
    rc = cli.main(["--git", repo, "--out", str(out)])
    assert rc == 0
    assert out.exists()
    text = out.read_text(encoding="utf-8")
    assert "종합 지표" in text


def test_main_format_override_changes_extension(tmp_path):
    from tests.fixtures.factories import make_git_repo

    repo = make_git_repo(str(tmp_path / "repo"), [
        {"email": "a@t.com", "date": "2024-01-01 10:00:00", "add": 10, "del": 0},
    ])
    out = tmp_path / "report.md"
    rc = cli.main(["--git", repo, "--out", str(out), "--format", "csv"])
    assert rc == 0
    assert (tmp_path / "report.csv").exists()
