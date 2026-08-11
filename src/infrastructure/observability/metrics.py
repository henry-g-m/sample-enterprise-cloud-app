"""Custom OpenTelemetry metrics for business events."""

import threading
from dataclasses import dataclass

from opentelemetry import metrics
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import Counter, Histogram, Meter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    ConsoleMetricExporter,
    MetricReader,
    PeriodicExportingMetricReader,
)
from opentelemetry.sdk.resources import Resource

from src.config.settings import Settings

_METER_NAME = "sample-enterprise-cloud-app"


@dataclass(frozen=True)
class AppMetrics:
    """Business-event instruments shared across the app."""

    http_requests_total: Counter
    http_request_duration_seconds: Histogram
    cache_hits_total: Counter
    cache_misses_total: Counter


def configure_local_metrics(settings: Settings, resource: Resource) -> None:
    """Set up a local MeterProvider.

    Used when Application Insights export is disabled. `PrometheusMetricReader`
    is always attached so `/metrics` has something to serve; the console
    exporter is additionally attached in debug mode for quick local viewing
    without standing up Prometheus.
    """
    readers: list[MetricReader] = [PrometheusMetricReader()]
    if settings.debug:
        readers.append(
            PeriodicExportingMetricReader(ConsoleMetricExporter(), export_interval_millis=30_000)
        )
    metrics.set_meter_provider(MeterProvider(resource=resource, metric_readers=readers))


def _create_metrics(meter: Meter) -> AppMetrics:
    return AppMetrics(
        http_requests_total=meter.create_counter(
            "http.requests.total", unit="1", description="Total HTTP requests processed"
        ),
        http_request_duration_seconds=meter.create_histogram(
            "http.request.duration", unit="s", description="HTTP request duration in seconds"
        ),
        cache_hits_total=meter.create_counter(
            "cache.hits.total", unit="1", description="Cache read hits"
        ),
        cache_misses_total=meter.create_counter(
            "cache.misses.total", unit="1", description="Cache read misses"
        ),
    )


_app_metrics: AppMetrics | None = None
_app_metrics_lock = threading.Lock()


def get_metrics() -> AppMetrics:
    """Return the process-wide AppMetrics singleton, creating it on first use.

    Binds to whichever MeterProvider is globally active at that point, so
    this must be called after tracing/metrics setup has run (it is, in
    practice, only ever called from request-handling code that runs after
    application startup).

    Thread-safety: uses double-checked locking with a module-level lock to
    ensure the AppMetrics singleton is created only once across threads.
    """
    global _app_metrics
    # Fast path: avoid acquiring the lock if already initialized.
    if _app_metrics is None:
        with _app_metrics_lock:
            if _app_metrics is None:
                _app_metrics = _create_metrics(metrics.get_meter(_METER_NAME))
    return _app_metrics


def reset_metrics() -> None:
    """Clear the AppMetrics singleton, forcing recreation on next access.

    Primarily for tests that reconfigure the MeterProvider between cases.
    Acquires the same lock to avoid races with concurrent initialisation.
    """
    global _app_metrics
    with _app_metrics_lock:
        _app_metrics = None
