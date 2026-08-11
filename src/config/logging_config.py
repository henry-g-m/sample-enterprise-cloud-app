"""Structured logging configuration."""

import logging
import logging.config
import sys
from typing import Any, cast

import structlog
from opentelemetry import trace
from pythonjsonlogger.json import JsonFormatter

from src.config.settings import Settings


def add_trace_context(
    logger: Any, method_name: str, event_dict: structlog.typing.EventDict
) -> structlog.typing.EventDict:
    """Inject the active OpenTelemetry trace_id/span_id into the log event, if any."""
    span_context = trace.get_current_span().get_span_context()
    if span_context.is_valid:
        event_dict["trace_id"] = format(span_context.trace_id, "032x")
        event_dict["span_id"] = format(span_context.span_id, "016x")
    return event_dict


def setup_logging() -> None:
    """Configure structured logging with structlog."""
    settings = Settings()

    # Configure standard library logging
    logging_config = {
        "version": 1,
        "disable_existing_loggers": False,
        "formatters": {
            "json": {
                "()": JsonFormatter,
                "format": "%(timestamp)s %(name)s %(levelname)s %(message)s",
            },
            "standard": {
                "format": "%(asctime)s [%(name)s] %(levelname)s: %(message)s",
            },
        },
        "handlers": {
            "console": {
                "class": "logging.StreamHandler",
                "level": settings.log_level,
                "formatter": "json" if settings.environment == "production" else "standard",
                "stream": sys.stdout,
            },
        },
        "loggers": {
            "": {
                "handlers": ["console"],
                "level": settings.log_level,
                "propagate": True,
            },
        },
    }

    logging.config.dictConfig(logging_config)

    # Configure structlog
    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.stdlib.filter_by_level,
            structlog.stdlib.add_logger_name,
            structlog.stdlib.add_log_level,
            structlog.stdlib.PositionalArgumentsFormatter(),
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.processors.format_exc_info,
            structlog.processors.UnicodeDecoder(),
            add_trace_context,
            structlog.processors.JSONRenderer(),
        ],
        context_class=dict,
        logger_factory=structlog.stdlib.LoggerFactory(),
        cache_logger_on_first_use=True,
    )


def get_logger(name: str) -> structlog.typing.FilteringBoundLogger:
    """Get a named logger instance."""
    return cast(structlog.typing.FilteringBoundLogger, structlog.get_logger(name))
