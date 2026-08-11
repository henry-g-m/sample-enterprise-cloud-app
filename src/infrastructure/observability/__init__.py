"""Observability infrastructure (logging, tracing, metrics).

setup_observability() is the single entry point: it decides once, up front,
whether telemetry is exported to Azure Application Insights or kept local,
and configures tracing + metrics accordingly.
"""

import structlog
from azure.monitor.opentelemetry import configure_azure_monitor
from fastapi import FastAPI

from src.config.settings import Settings
from src.infrastructure.observability.metrics import configure_local_metrics
from src.infrastructure.observability.tracing import (
    build_resource,
    configure_local_tracing,
    instrument_app,
)

logger = structlog.get_logger(__name__)


def setup_observability(app: FastAPI, settings: Settings) -> None:
    """Configure tracing and metrics, then instrument this app instance."""
    resource = build_resource(settings)

    if settings.enable_app_insights and settings.app_insights_connection_string:
        # We instrument FastAPI ourselves below, so disable Azure Monitor's
        # own auto-instrumentation for it to avoid double-instrumenting.
        configure_azure_monitor(
            connection_string=settings.app_insights_connection_string,
            resource=resource,
            instrumentation_options={"fastapi": {"enabled": False}},
        )
        logger.info("observability_configured", backend="azure_monitor")
    else:
        configure_local_tracing(settings, resource)
        configure_local_metrics(settings, resource)
        logger.info("observability_configured", backend="local")

    instrument_app(app)
