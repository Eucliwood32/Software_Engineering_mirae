"""NFR-3.1 인코딩 자동 감지: UTF-8 → CP949 순.
charset-normalizer 로 일본어/기타 비지원 인코딩을 사전 거부한다."""
from __future__ import annotations

# charset-normalizer 가 이 인코딩 계열로 판정하면 즉시 거부
_REJECT_FAMILIES = frozenset({
    "cp932", "shift_jis", "shiftjis", "sjis",
    "iso2022jp", "euc_jp", "eucjp",
    "iso2022kr",                       # EUC-KR 아닌 일본어 변형
    "gb2312", "gbk", "gb18030",        # 중국어
    "iso88591", "windows1252",         # 서유럽
    "ascii",                           # 순수 ASCII(텍스트 픽스처 외 가능성 없음)
})


def _normalize(enc: str) -> str:
    return enc.lower().replace("-", "").replace("_", "")


class EncodingHandler:
    def read_text(self, path: str) -> str | dict[str, str]:
        """UTF-8 → CP949 순 시도.
        charset-normalizer 가 비지원 인코딩으로 판정하면
        {"error":"encoding_failed","path":path} 반환."""
        with open(path, "rb") as f:
            raw = f.read()

        detected_norm: str | None = None
        try:
            from charset_normalizer import from_bytes
            best = from_bytes(raw).best()
            if best is not None:
                detected_norm = _normalize(best.encoding)
        except Exception:
            pass

        if detected_norm is not None and detected_norm in _REJECT_FAMILIES:
            return {"error": "encoding_failed", "path": path}

        for enc in ("utf-8", "cp949"):
            try:
                return raw.decode(enc, errors="strict")
            except (UnicodeDecodeError, LookupError):
                continue

        return {"error": "encoding_failed", "path": path}
