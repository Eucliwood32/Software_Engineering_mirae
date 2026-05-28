"""
FR-3.3 자동 불용어 처리 단위 테스트 (L1)
TC-FR-3.3-01 ~ 06
"""
import pytest
from qce.model.parsing.stopword_filter import StopwordFilter
from qce.model.types import MessengerRecord


def _rec(author: str, msg: str) -> MessengerRecord:
    return MessengerRecord(author, "t", msg)


def test_reaction_excluded():                         # TC-FR-3.3-01
    recs = [_rec("A", "회의 시작합니다"), _rec("A", "ㅇㅇ"), _rec("A", "ㅋㅋ")]
    assert StopwordFilter().count_valid_messages(recs)["A"] == 1


def test_media_tag_excluded():                        # TC-FR-3.3-02
    recs = [_rec("B", "(이모티콘)"), _rec("B", "(사진)"), _rec("B", "의견 정리했어요")]
    assert StopwordFilter().count_valid_messages(recs)["B"] == 1


def test_single_char_excluded():                      # TC-FR-3.3-03
    recs = [_rec("C", "네"), _rec("C", "응"), _rec("C", "굳"),
            _rec("C", "구체적 피드백 드릴게요")]
    assert StopwordFilter().count_valid_messages(recs)["C"] == 1


def test_deterministic():                             # TC-FR-3.3-04
    recs = [_rec("A", "ㅋㅋ"), _rec("A", "제안서 검토함")]
    f = StopwordFilter()
    assert f.count_valid_messages(recs) == f.count_valid_messages(recs)


def test_meaningful_sentence_kept():                  # TC-FR-3.3-05
    recs = [_rec("A", "오늘 회의 내용 정리해서 공유드리겠습니다")]
    assert StopwordFilter().count_valid_messages(recs)["A"] == 1


def test_no_edit_api():                               # TC-FR-3.3-06
    f = StopwordFilter()
    assert not hasattr(f, "set_stopwords")
    assert not hasattr(f, "add_stopword")
