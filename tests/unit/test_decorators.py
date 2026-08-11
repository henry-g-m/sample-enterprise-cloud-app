"""Unit tests for the cache_response decorator."""

from typing import Any

import pytest

from src.utils import decorators as decorators_module
from src.utils.decorators import cache_response


class _FakeRedisClient:
    """In-memory stand-in for RedisClient, tracking get/set calls."""

    def __init__(self) -> None:
        self.store: dict[str, Any] = {}

    async def get(self, key: str) -> Any | None:
        return self.store.get(key)

    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        self.store[key] = value


@pytest.fixture
def fake_client(monkeypatch: pytest.MonkeyPatch) -> _FakeRedisClient:
    client = _FakeRedisClient()
    monkeypatch.setattr(decorators_module, "get_redis_client", lambda: client)
    return client


class TestCacheResponse:
    """Test the cache_response decorator against a fake in-memory client."""

    async def test_caches_return_value(self, fake_client: _FakeRedisClient) -> None:
        calls = 0

        @cache_response(ttl_seconds=60)
        async def compute() -> dict[str, int]:
            nonlocal calls
            calls += 1
            return {"value": calls}

        first = await compute()
        second = await compute()

        assert first == {"value": 1}
        assert second == {"value": 1}
        assert calls == 1

    async def test_different_args_get_different_cache_keys(
        self, fake_client: _FakeRedisClient
    ) -> None:
        @cache_response(ttl_seconds=60)
        async def compute(x: int) -> int:
            return x * 2

        assert await compute(1) == 2
        assert await compute(2) == 4
        assert len(fake_client.store) == 2

    async def test_falls_back_when_args_not_serializable(
        self, fake_client: _FakeRedisClient
    ) -> None:
        calls = 0

        class Unserializable:
            pass

        @cache_response(ttl_seconds=60)
        async def compute(obj: Any) -> str:
            nonlocal calls
            calls += 1
            return "ok"

        await compute(Unserializable())
        await compute(Unserializable())

        assert calls == 2
        assert fake_client.store == {}
