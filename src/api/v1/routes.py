"""API v1 routes and endpoint definitions."""

from fastapi import APIRouter

from src.api.v1.health import health_router
from src.api.v1.about import about_router

router = APIRouter()

# Include sub-routers
router.include_router(health_router, prefix="/health", tags=["health"])
router.include_router(about_router, prefix="/about", tags=["about"])
