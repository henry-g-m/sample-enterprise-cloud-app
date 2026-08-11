"""Health check endpoints for liveness and readiness probes."""

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

from src.infrastructure.cache.redis_client import get_redis_client

logger = structlog.get_logger(__name__)

health_router = APIRouter()


class HealthResponse(BaseModel):
    """Health check response model."""

    status: str
    timestamp: str
    version: str


class ReadinessResponse(BaseModel):
    """Readiness probe response model."""

    ready: bool
    timestamp: str
    dependencies: dict[str, str]


@health_router.get("/live", response_model=HealthResponse)
async def liveness() -> dict[str, Any]:
    """Liveness probe endpoint.

    Used by Kubernetes/container orchestration to detect if pod is alive.
    """
    logger.info("liveness_check")
    return {
        "status": "alive",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }


@health_router.get("/ready", response_model=ReadinessResponse)
async def readiness() -> dict[str, Any]:
    """Readiness probe endpoint.

    Used by Kubernetes/container orchestration to detect if pod is ready to serve traffic.
    """
    logger.info("readiness_check")

    cache_healthy = await get_redis_client().ping()
    dependencies = {
        "database": "not_configured",
        "cache": "healthy" if cache_healthy else "unhealthy",
    }

    return {
        "ready": True,
        "timestamp": datetime.utcnow().isoformat(),
        "dependencies": dependencies,
    }


@health_router.get("/startup", response_model=HealthResponse)
async def startup() -> dict[str, Any]:
    """Startup probe endpoint.

    Used by Kubernetes/container orchestration to detect if pod has successfully started.
    """
    logger.info("startup_check")
    return {
        "status": "started",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
    }
