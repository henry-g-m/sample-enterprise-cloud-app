"""FastAPI application factory and configuration."""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.api.metrics import metrics_router
from src.api.v1.routes import router as v1_router
from src.config.logging_config import setup_logging
from src.config.settings import Settings
from src.core.exceptions import register_exception_handlers
from src.core.middleware import add_request_logging_middleware
from src.infrastructure.cache.redis_client import close_redis_client
from src.infrastructure.observability import setup_observability


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Application startup and shutdown events."""
    # Startup
    setup_logging()
    print("✓ Application started")
    yield
    # Shutdown
    await close_redis_client()
    print("✓ Application shutdown")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    settings = Settings()

    app = FastAPI(
        title=settings.app_title,
        description=settings.app_description,
        version=settings.app_version,
        lifespan=lifespan,
    )

    setup_observability(app, settings)

    # Add middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    add_request_logging_middleware(app)
    register_exception_handlers(app)

    # Include routers
    app.include_router(v1_router, prefix="/api/v1")
    app.include_router(metrics_router)

    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src.app:app",
        host="localhost",
        port=8000,
        reload=True,
        log_level="info",
    )

# Home
# http://localhost:8000/api/v1/about
