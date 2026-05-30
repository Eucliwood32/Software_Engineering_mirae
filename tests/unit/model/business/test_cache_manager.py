"""NFR-2.3/2.4 CacheManager 단위 테스트 (원자적 JSON 캐시)."""
from __future__ import annotations

import pytest

from qce.model.business.cache_manager import CacheManager


@pytest.fixture
def cache(tmp_path, monkeypatch):
    """캐시 파일 경로를 tmp_path로 격리."""
    cm = CacheManager()
    monkeypatch.setattr(cm, "CACHE_FILE", str(tmp_path / ".qce_cache"))
    monkeypatch.setattr(cm, "TMP_FILE", str(tmp_path / ".qce_cache.tmp"))
    return cm


def test_save_load_roundtrip(cache):
    data = {"scores": [{"author": "Alice", "total_score": 0.5}]}
    cache.save(data)
    assert cache.load() == data


def test_load_missing_returns_empty(cache):
    assert cache.load() == {}


def test_load_corrupt_deletes_and_returns_empty(cache, tmp_path):
    # 손상된 JSON 기록
    with open(cache.CACHE_FILE, "w", encoding="utf-8") as f:
        f.write("{ this is not valid json ")
    assert cache.load() == {}                       # 빈 dict 반환
    import os
    assert not os.path.exists(cache.CACHE_FILE)     # 손상 캐시 삭제됨


def test_save_no_tmp_left_behind(cache):
    import os
    cache.save({"k": "v"})
    assert not os.path.exists(cache.TMP_FILE)       # tmp 잔존 없음 (원자적 커밋)


def test_save_korean_preserved(cache):
    data = {"author": "조원희", "msg": "한글 보존"}
    cache.save(data)
    assert cache.load()["author"] == "조원희"
