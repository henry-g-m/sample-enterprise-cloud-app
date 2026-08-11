# Multi-stage Dockerfile for enterprise demo cloud app

# ============================================================================
# Stage 1: Builder
# ============================================================================
FROM python:3.14-slim AS builder

WORKDIR /build

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
COPY requirements-dev.txt .

# Create wheels
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /build/wheels -r requirements-dev.txt


# ============================================================================
# Stage 2: Runtime
# ============================================================================
FROM python:3.14-slim

# Create non-root user
RUN useradd -m -u 1000 appuser

WORKDIR /app

# Install runtime dependencies only
RUN apt-get update && apt-get install -y --no-install-recommends \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy wheels from builder
COPY --from=builder /build/wheels /wheels
COPY --from=builder /build/requirements.txt .
COPY --from=builder /build/requirements-dev.txt .

# Install Python dependencies from wheels
RUN pip install --no-cache /wheels/*

# Copy application code
COPY --chown=appuser:appuser src/ ./src/

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/api/v1/health/live')" || exit 1

# Expose port
EXPOSE 8000

# Run application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
