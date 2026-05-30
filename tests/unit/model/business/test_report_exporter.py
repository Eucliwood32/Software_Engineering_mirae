"""FR-5.2/5.3 ReportExporter 단위 테스트."""
from __future__ import annotations

from qce.model.types import MemberScore
from qce.model.business.report_exporter import ReportExporter


def _scores():
    return [
        MemberScore("Alice", 0.8, 0.6, 0.4, 0.66, 800, 1500, 30, False, []),
        MemberScore("Bob", 0.2, 0.1, 0.9, 0.34, 200, 300, 90, True, ["CAPPING"]),
    ]


def test_markdown_table_has_header_and_rows():
    md = ReportExporter().to_markdown(_scores())
    assert "종합 지표" in md          # STR-7: 판정 금지 용어
    assert "최종 평가" not in md
    assert "| Alice |" in md
    assert "| Bob |" in md


def test_markdown_sorted_by_total_desc():
    md = ReportExporter().to_markdown(_scores())
    assert md.index("Alice") < md.index("Bob")   # 0.66 > 0.34


def test_markdown_missing_warning_blockquote():
    md = ReportExporter().to_markdown(_scores(), missing={"메신저"})
    assert "> ⚠" in md
    assert "메신저" in md


def test_csv_has_utf8_bom():
    data = ReportExporter().to_csv(_scores())
    assert data.startswith(b"\xef\xbb\xbf")        # Excel 한글 호환 BOM


def test_csv_missing_warning_row():
    data = ReportExporter().to_csv(_scores(), missing={"Git"})
    text = data.decode("utf-8-sig")
    assert "WARNING" in text
    assert "Git" in text


def test_save_md_roundtrip(tmp_path):
    path = str(tmp_path / "report.md")
    ReportExporter().save(path, _scores())
    content = (tmp_path / "report.md").read_text(encoding="utf-8")
    assert "| Alice |" in content


def test_save_csv_roundtrip(tmp_path):
    path = str(tmp_path / "report.csv")
    ReportExporter().save(path, _scores(), missing={"문서"})
    raw = (tmp_path / "report.csv").read_bytes()
    assert raw.startswith(b"\xef\xbb\xbf")
    assert "WARNING" in raw.decode("utf-8-sig")
