"""Integration tests for the Redis client wrapper against a real Redis instance."""

import os
from collections.abc import AsyncIterator

import pytest

from src.config.settings import Settings
from src.infrastructure.cache.redis_client import RedisClient

pytestmark = pytest.mark.integration


@pytest.fixture
async def redis_client() -> AsyncIterator[RedisClient]:
    settings = Settings(_env_file=None, redis_host=os.environ.get("REDIS_HOST", "localhost"))
    client = RedisClient(settings)
    if not await client.ping():
        pytest.skip("Redis is not reachable")
    yield client
    await client.delete_pattern("integration:*")
    await client.close()


class TestRedisClientIntegration:
    """Exercise RedisClient against a live Redis container."""

    async def test_ping(self, redis_client: RedisClient) -> None:
        assert await redis_client.ping() is True

    async def test_set_and_get_roundtrip(self, redis_client: RedisClient) -> None:
        await redis_client.set("integration:key", {"hello": "world"}, ttl_seconds=5)

        assert await redis_client.get("integration:key") == {"hello": "world"}

    async def test_get_missing_key_returns_none(self, redis_client: RedisClient) -> None:
        assert await redis_client.get("integration:does-not-exist") is None

    async def test_delete_removes_key(self, redis_client: RedisClient) -> None:
        await redis_client.set("integration:to-delete", "value")

        deleted = await redis_client.delete("integration:to-delete")

        assert deleted == 1
        assert await redis_client.get("integration:to-delete") is None

    async def test_delete_pattern_removes_matching_keys(self, redis_client: RedisClient) -> None:
        await redis_client.set("integration:pattern:1", 1)
        await redis_client.set("integration:pattern:2", 2)

        deleted = await redis_client.delete_pattern("integration:pattern:*")

        assert deleted == 2
        assert await redis_client.get("integration:pattern:1") is None
