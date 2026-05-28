"""
FR-1.1/1.2 DocumentParser 단위 테스트 (L1)
TC-FR-1.1-01 ~ 07, TC-FR-1.2-01 ~ 04
"""
import os
import pytest
from tests.fixtures.factories import (
    make_docx, make_pptx, make_hwpx, make_corrupted, make_empty_docx,
)
from qce.model.parsing.document_parser import DocumentParser


# ── FR-1.1 글자수·도형 추출 ──────────────────────────────────────────────

def test_docx_200_chars(tmp_path):                   # TC-FR-1.1-01
    p = make_docx(str(tmp_path / "d.docx"), "Alice", "가" * 200)
    assert sum(DocumentParser().parse(p).values()) == 200


def test_pptx_chars_and_shapes(tmp_path):            # TC-FR-1.1-02
    p = make_pptx(str(tmp_path / "s.pptx"), "Bob", [["가" * 50, "나" * 50]] * 3)
    dp = DocumentParser()
    assert sum(dp.parse(p).values()) == 300
    assert dp.count_shapes(p) == 6


def test_hwpx_200_chars(tmp_path):                   # TC-FR-1.1-03
    p = make_hwpx(str(tmp_path / "h.hwpx"), "A", "다" * 200)
    assert sum(DocumentParser().parse(p).values()) == 200


def test_mixed_formats(tmp_path):                    # TC-FR-1.1-04
    dp = DocumentParser()
    pd = make_docx(str(tmp_path / "a.docx"), "A", "가" * 10)
    pp = make_pptx(str(tmp_path / "b.pptx"), "B", [["나" * 10]])
    ph = make_hwpx(str(tmp_path / "c.hwpx"), "C", "다" * 10)
    assert sum(dp.parse(pd).values()) == 10
    assert sum(dp.parse(pp).values()) == 10
    assert sum(dp.parse(ph).values()) == 10


def test_empty_docx(tmp_path):                       # TC-FR-1.1-05
    p = make_empty_docx(str(tmp_path / "e.docx"))
    dp = DocumentParser()
    result = dp.parse(p)
    assert sum(result.values()) == 0
    assert dp.count_shapes(p) == 0


def test_corrupted_is_skipped(tmp_path):             # TC-FR-1.1-06
    p = make_corrupted(str(tmp_path / "bad.docx"))
    result = DocumentParser().parse(p)   # must not raise
    assert isinstance(result, dict)


def test_spaces_excluded(tmp_path):                  # TC-FR-1.1-07
    p = make_docx(str(tmp_path / "sp.docx"), "A", "가 나\n다")
    assert sum(DocumentParser().parse(p).values()) == 3


# ── FR-1.2 작성자별 집계 ─────────────────────────────────────────────────

def test_two_docx_authors(tmp_path):                 # TC-FR-1.2-01
    dp = DocumentParser()
    p1 = make_docx(str(tmp_path / "a.docx"), "Alice", "가" * 100)
    p2 = make_docx(str(tmp_path / "b.docx"), "Bob",   "나" * 150)
    r1, r2 = dp.parse(p1), dp.parse(p2)
    merged = {}
    for d in (r1, r2):
        for k, v in d.items():
            merged[k] = merged.get(k, 0) + v
    assert merged == {"Alice": 100, "Bob": 150}


def test_missing_author_is_unknown(tmp_path):        # TC-FR-1.2-02
    p = make_docx(str(tmp_path / "u.docx"), None, "x" * 30)
    result = DocumentParser().parse(p)
    assert "Unknown" in result
    assert sum(result.values()) == 30


def test_pptx_last_modified_by(tmp_path):            # TC-FR-1.2-03
    p = make_pptx(str(tmp_path / "c.pptx"), "Carol", [["가" * 20]])
    result = DocumentParser().parse(p)
    assert "Carol" in result


def test_input_not_modified(tmp_path):               # TC-NFR-2.1-01 (런타임)
    p = make_docx(str(tmp_path / "r.docx"), "A", "x" * 100)
    before = os.path.getmtime(p)
    DocumentParser().parse(p)
    assert os.path.getmtime(p) == before
