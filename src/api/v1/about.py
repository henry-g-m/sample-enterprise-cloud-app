"""About endpoint returning application information."""

from datetime import datetime
from typing import Any

import structlog
from fastapi import APIRouter
from pydantic import BaseModel

from src.utils.decorators import cache_response

logger = structlog.get_logger(__name__)

about_router = APIRouter()


class AboutResponse(BaseModel):
    """About endpoint response model."""

    name: str
    version: str
    description: str
    timestamp: str
    environment: str


@about_router.get("", response_model=AboutResponse)
@cache_response(ttl_seconds=30, prefix="about")
async def get_about() -> dict[str, Any]:
    """Get information about the application.

    Returns application name, version, description, and current environment.
    """
    logger.info("about_endpoint_called")

    return {
        "name": "Enterprise Demo Cloud App",
        "version": "0.1.1",
        "description": "Simple REST API deployed to Azure with enterprise best practices",
        "timestamp": datetime.utcnow().isoformat(),
        "environment": "development",  # TODO: Load from settings
    }
