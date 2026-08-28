"""OpenTelemetry distributed tracing setup."""

import structlog
from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.instrumentation.redis import RedisInstrumentor
from opentelemetry.sdk.resources import Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter

from src.config.settings import Settings

logger = structlog.get_logger(__name__)


def build_resource(settings: Settings) -> Resource:
    """Build the OpenTelemetry Resource describing this service instance."""
    return Resource.create(
        {
            "service.name": settings.app_title,
            "service.version": settings.app_version,
            "deployment.environment": settings.environment,
        }
    )


def configure_local_tracing(settings: Settings, resource: Resource) -> None:
    """Set up a local TracerProvider.

    Used when Application Insights export is disabled. A console exporter is
    only attached in debug mode to avoid flooding production-like logs with
    span output; spans are still created (and available for log correlation)
    even without an exporter attached.
    """
    provider = TracerProvider(resource=resource)
    if settings.debug:
        provider.add_span_processor(BatchSpanProcessor(ConsoleSpanExporter()))
    trace.set_tracer_provider(provider)


def instrument_app(app: FastAPI) -> None:
    """Instrument this specific FastAPI instance and stdlib logging.

    Called explicitly (rather than relying on auto-instrumentation) because
    the app module imports `FastAPI` at module load time, before any
    monkey-patch-based auto-instrumentation could take effect.
    """
    FastAPIInstrumentor.instrument_app(app)
    LoggingInstrumentor().instrument(set_logging_format=False)
    RedisInstrumentor().instrument()
