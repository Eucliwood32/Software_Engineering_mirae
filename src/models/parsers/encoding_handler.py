"""NFR-3.1 EncodingHandler: UTF-8 → CP949 순 인코딩 자동 감지."""
from __future__ import annotations

_REJECT_FAMILIES = frozenset({
    "cp932", "shift_jis", "shiftjis", "sjis",
    "iso2022jp", "euc_jp", "eucjp",
    "iso2022kr",
    "gb2312", "gbk", "gb18030",
    "iso88591", "windows1252",
    "ascii",
})


def _normalize(enc: str) -> str:
    return enc.lower().replace("-", "").replace("_", "")


class EncodingHandler:
    """NFR-3.1 — UTF-8 → CP949 순 시도. 비지원 인코딩은 사전 거부."""

    def read_text(self, path: str) -> str | dict[str, str]:
        """UTF-8 → CP949 순 시도. 실패 시 {"error": "encoding_failed", "path": path}."""
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
