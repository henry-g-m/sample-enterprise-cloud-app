"""Prometheus scrape endpoint.

Deliberately unversioned and outside `/api/v1` - `/metrics` is a Prometheus
convention, not a product API surface.
"""

from fastapi import APIRouter
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

metrics_router = APIRouter()


@metrics_router.get("/metrics", include_in_schema=False)
async def get_metrics() -> Response:
    """Expose current metrics in Prometheus text exposition format."""
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
