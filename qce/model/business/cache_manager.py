"""NFR-2.3, NFR-2.4, C-8 CacheManager: 원자적 JSON 캐싱 (pickle 금지)."""
from __future__ import annotations
import json
import os


class CacheManager:
    """tmp 쓰기 → fsync → os.replace 원자적 커밋. json 전용."""

    CACHE_FILE = ".qce_cache"
    TMP_FILE = ".qce_cache.tmp"

    def save(self, data: dict) -> None:
        """원자적 저장. 실패 시 tmp 삭제 후 예외 전파."""
        try:
            with open(self.TMP_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(self.TMP_FILE, self.CACHE_FILE)
        except Exception:
            if os.path.exists(self.TMP_FILE):
                os.remove(self.TMP_FILE)
            raise

    def load(self) -> dict:
        """JSONDecodeError/KeyError → 캐시 삭제 후 빈 dict 반환."""
        if not os.path.exists(self.CACHE_FILE):
            return {}
        try:
            with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
            if os.path.exists(self.CACHE_FILE):
                os.remove(self.CACHE_FILE)
            return {}
