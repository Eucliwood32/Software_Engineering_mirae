"""
NFR-3.1 인코딩 자동 감지 단위 테스트 (L1)
TC-NFR-3.1-01 ~ TC-NFR-3.1-04
"""
from qce.model.parsing.encoding_handler import EncodingHandler


def test_utf8_korean(tmp_path):                      # TC-NFR-3.1-01
    p = tmp_path / "u.txt"
    p.write_bytes("안녕하세요".encode("utf-8"))
    result = EncodingHandler().read_text(str(p))
    assert result == "안녕하세요"


def test_cp949_korean(tmp_path):                     # TC-NFR-3.1-02
    p = tmp_path / "c.txt"
    p.write_bytes("한글테스트".encode("cp949"))
    assert EncodingHandler().read_text(str(p)) == "한글테스트"


def test_unsupported_encoding_returns_error(tmp_path):  # TC-NFR-3.1-03
    p = tmp_path / "s.txt"
    p.write_bytes("テスト".encode("shift_jis"))
    out = EncodingHandler().read_text(str(p))
    assert isinstance(out, dict)
    assert out["error"] == "encoding_failed"
    assert out["path"] == str(p)


def test_subsequent_call_after_failure(tmp_path):    # TC-NFR-3.1-04
    bad = tmp_path / "bad.txt"
    bad.write_bytes("テスト".encode("shift_jis"))
    good = tmp_path / "good.txt"
    good.write_bytes("정상".encode("utf-8"))

    handler = EncodingHandler()
    out_bad = handler.read_text(str(bad))
    assert isinstance(out_bad, dict)           # 실패 반환
    out_good = handler.read_text(str(good))
    assert out_good == "정상"                  # 이후 호출 정상
