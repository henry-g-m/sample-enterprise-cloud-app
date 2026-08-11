"""Async Redis client wrapper with connection pooling."""

import json
from typing import Any

import structlog
from redis.asyncio import ConnectionPool, Redis
from redis.asyncio.connection import Connection, SSLConnection
from redis.exceptions import RedisError

from src.config.settings import Settings

logger = structlog.get_logger(__name__)


class RedisClient:
    """Async wrapper around redis-py with a shared connection pool.

    All read/write operations fail open: a Redis outage logs a warning and
    behaves like a cache miss rather than raising, since the cache is a
    performance optimization, not a source of truth.
    """

    def __init__(self, settings: Settings) -> None:
        self._pool: ConnectionPool = ConnectionPool(
            connection_class=SSLConnection if settings.redis_ssl else Connection,
            host=settings.redis_host,
            port=settings.redis_port,
            db=settings.redis_db,
            password=settings.redis_password,
            decode_responses=True,
            max_connections=20,
            # Fail fast: an unreachable Redis should degrade requests by
            # milliseconds, not hang them for however long the OS takes to
            # give up on the socket.
            socket_connect_timeout=2,
            socket_timeout=2,
        )
        self._client: Redis = Redis(connection_pool=self._pool)

    async def ping(self) -> bool:
        """Check Redis connectivity."""
        try:
            return bool(await self._client.ping())
        except RedisError:
            logger.warning("redis_ping_failed")
            return False

    async def get(self, key: str) -> Any | None:
        """Get a JSON-deserialized value by key, or None if missing or on error."""
        try:
            raw = await self._client.get(key)
        except RedisError:
            logger.warning("redis_get_failed", key=key)
            return None
        return json.loads(raw) if raw is not None else None

    async def set(self, key: str, value: Any, *, ttl_seconds: int | None = None) -> None:
        """Set a JSON-serialized value, optionally with a TTL."""
        try:
            await self._client.set(key, json.dumps(value), ex=ttl_seconds)
        except RedisError:
            logger.warning("redis_set_failed", key=key)

    async def delete(self, *keys: str) -> int:
        """Delete one or more keys. Returns the number of keys actually removed."""
        if not keys:
            return 0
        try:
            return int(await self._client.delete(*keys))
        except RedisError:
            logger.warning("redis_delete_failed", keys=keys)
            return 0

    async def delete_pattern(self, pattern: str) -> int:
        """Delete all keys matching a glob pattern. Returns the number of keys deleted."""
        deleted = 0
        try:
            async for key in self._client.scan_iter(match=pattern):
                deleted += await self.delete(key)
        except RedisError:
            logger.warning("redis_delete_pattern_failed", pattern=pattern)
        return deleted

    async def close(self) -> None:
        """Close the underlying connection pool."""
        await self._client.aclose()


_redis_client: RedisClient | None = None


def get_redis_client(settings: Settings | None = None) -> RedisClient:
    """Return the process-wide RedisClient singleton, creating it on first use."""
    global _redis_client
    if _redis_client is None:
        _redis_client = RedisClient(settings or Settings())
    return _redis_client


async def close_redis_client() -> None:
    """Close and clear the singleton RedisClient, if one exists."""
    global _redis_client
    if _redis_client is not None:
        await _redis_client.close()
        _redis_client = None
