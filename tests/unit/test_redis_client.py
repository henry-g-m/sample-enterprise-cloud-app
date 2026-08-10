"""Unit tests for the Redis client wrapper's fail-open behavior and singleton."""

from src.config.settings import Settings
from src.infrastructure.cache import redis_client as redis_client_module
from src.infrastructure.cache.redis_client import (
    RedisClient,
    close_redis_client,
    get_redis_client,
)


def _unreachable_client() -> RedisClient:
    """Point at a port nothing listens on so calls fail fast (connection refused)."""
    settings = Settings(_env_file=None, redis_host="localhost", redis_port=1)
    return RedisClient(settings)


class TestRedisClientFailOpen:
    """Redis outages should degrade to cache misses, never raise."""

    async def test_ping_returns_false_when_unreachable(self):
        client = _unreachable_client()

        assert await client.ping() is False

        await client.close()

    async def test_get_returns_none_when_unreachable(self):
        client = _unreachable_client()

        assert await client.get("any-key") is None

        await client.close()

    async def test_set_does_not_raise_when_unreachable(self):
        client = _unreachable_client()

        await client.set("any-key", {"a": 1})

        await client.close()

    async def test_delete_returns_zero_when_unreachable(self):
        client = _unreachable_client()

        assert await client.delete("any-key") == 0

        await client.close()

    async def test_delete_with_no_keys_returns_zero(self):
        client = _unreachable_client()

        assert await client.delete() == 0

        await client.close()

    async def test_delete_pattern_returns_zero_when_unreachable(self):
        client = _unreachable_client()

        assert await client.delete_pattern("prefix:*") == 0

        await client.close()


class TestGetRedisClientSingleton:
    """get_redis_client should return one shared instance per process."""

    async def test_returns_same_instance(self):
        redis_client_module._redis_client = None

        first = get_redis_client(Settings(_env_file=None, redis_host="localhost", redis_port=1))
        second = get_redis_client()

        assert first is second

        await close_redis_client()

    async def test_close_resets_singleton(self):
        redis_client_module._redis_client = None
        get_redis_client(Settings(_env_file=None, redis_host="localhost", redis_port=1))

        await close_redis_client()

        assert redis_client_module._redis_client is None
