"""Reusable decorators, including Redis-backed response caching."""

import functools
import hashlib
import json
from collections.abc import Awaitable, Callable
from typing import Any, ParamSpec, TypeVar, cast

from src.infrastructure.cache.redis_client import get_redis_client

P = ParamSpec("P")
R = TypeVar("R")


def _build_cache_key(
    prefix: str, func: Callable[..., Any], args: tuple[Any, ...], kwargs: dict[str, Any]
) -> str:
    payload = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
    digest = hashlib.sha256(payload.encode()).hexdigest()
    return f"{prefix}:{func.__module__}.{func.__qualname__}:{digest}"


def cache_response(
    *, ttl_seconds: int = 60, prefix: str = "cache"
) -> Callable[[Callable[P, Awaitable[R]]], Callable[P, Awaitable[R]]]:
    """Cache an async function's JSON-serializable return value in Redis.

    Falls back to calling the wrapped function directly when the arguments
    aren't JSON-serializable (e.g. a FastAPI Request) or Redis is unreachable,
    since RedisClient itself fails open on connection errors.
    """

    def decorator(func: Callable[P, Awaitable[R]]) -> Callable[P, Awaitable[R]]:
        @functools.wraps(func)
        async def wrapper(*args: P.args, **kwargs: P.kwargs) -> R:
            try:
                key = _build_cache_key(prefix, func, args, kwargs)
            except TypeError:
                return await func(*args, **kwargs)

            client = get_redis_client()
            cached = await client.get(key)
            if cached is not None:
                return cast(R, cached)

            result = await func(*args, **kwargs)
            await client.set(key, result, ttl_seconds=ttl_seconds)
            return result

        return wrapper

    return decorator
