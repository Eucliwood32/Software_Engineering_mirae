"""CacheManager — NFR-2.3/2.4/C-8 원자적 JSON 캐싱."""
import json
import os


class CacheManager:
    CACHE_FILE = ".qce_cache"
    TMP_FILE = ".qce_cache.tmp"

    def save(self, data: dict) -> None:
        try:
            with open(self.TMP_FILE, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
                f.flush()
                os.fsync(f.fileno())
            os.replace(self.TMP_FILE, self.CACHE_FILE)
        except Exception as e:
            if os.path.exists(self.TMP_FILE):
                os.remove(self.TMP_FILE)
            raise e

    def load(self) -> dict:
        if not os.path.exists(self.CACHE_FILE):
            return {}
        try:
            with open(self.CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, KeyError, UnicodeDecodeError):
            if os.path.exists(self.CACHE_FILE):
                os.remove(self.CACHE_FILE)
            return {}


__all__ = ["CacheManager"]
