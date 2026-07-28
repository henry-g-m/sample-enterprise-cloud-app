# Codebase Documentation for Claude

## Project Overview

**Enterprise Demo Cloud App** - A simple REST API demonstrating enterprise best practices for cloud deployment on Azure. The application provides health check endpoints and application metadata, with a foundation for scaling to more complex features in future iterations.

## Architecture & Key Concepts

### Layered Architecture
```
API Layer (FastAPI routes)
    ↓
Service Layer (business logic)
    ↓
Domain Layer (domain models)
    ↓
Infrastructure Layer (external services, cache, DB)
```

### Technology Stack
- **Framework**: FastAPI (async REST API framework)
- **Python**: 3.11+ (with type hints)
- **Containerization**: Docker (multi-stage builds)
- **Orchestration**: Azure Container Apps
- **Caching**: Redis (Azure Cache for Redis)
- **Observability**: OpenTelemetry + Application Insights
- **Testing**: pytest + testcontainers
- **Code Quality**: black, ruff, mypy

## Project Structure

### Core Directories

**`src/`** - Application source code
- `app.py` - FastAPI application factory with lifespan management
- `config/` - Settings and configuration management
- `api/` - API routes organized by version (v1, v2, etc.)
- `core/` - Core utilities (middleware, exceptions, security)
- `domain/` - Business logic and domain models
- `infrastructure/` - External service integrations (cache, observability)
- `services/` - Application service layer
- `utils/` - Utility functions and helpers

**`tests/`** - Test suite following testing pyramid
- `unit/` - Unit tests (service methods, utilities)
- `integration/` - Integration tests (API endpoints, external services)
- `e2e/` - End-to-end tests (deployment validation)
- `conftest.py` - Pytest fixtures and configuration

**`infrastructure/`** - Infrastructure as Code
- `terraform/` - Terraform modules (Azure + AWS options)
- `docker/` - Docker-related files
- `scripts/` - Deployment and operational scripts

**`docs/`** - Documentation
- `DEVELOPMENT.md` - Local development setup guide
- `ARCHITECTURE.md` - Detailed architecture decisions
- `API.md` - API endpoint documentation
- `adr/` - Architecture Decision Records

### Configuration Files

- `pyproject.toml` - Python project config (dependencies, tool settings)
- `requirements.txt` - Runtime dependencies (pinned versions)
- `requirements-dev.txt` - Development dependencies
- `pytest.ini` - Pytest configuration
- `.env.example` - Environment variables template
- `Dockerfile` - Multi-stage Docker build
- `docker-compose.yml` - Local development services
- `Makefile` - Common development tasks

## Current Phase: Foundation Setup (Phase 1)

### Completed
✅ Project structure initialized
✅ Configuration system (settings, logging)
✅ FastAPI application factory with middleware
✅ API v1 routes and endpoints
✅ Health check endpoints (liveness, readiness, startup)
✅ `/about` endpoint with application metadata
✅ Docker multi-stage build
✅ Docker Compose for local development
✅ GitHub Actions CI pipeline
✅ Comprehensive testing framework
✅ Code quality tooling (black, ruff, mypy, pylint)

### In Progress
🔄 First test implementations
🔄 Local environment validation

### Planned (Phases 2-3)
- [ ] Service layer implementation
- [ ] Redis caching layer with health checks
- [ ] Structured logging and OpenTelemetry integration
- [ ] Azure deployment (Terraform)
- [ ] Event ticket sales domain
- [ ] Web UI (React)

## Key Files & Their Purpose

### Application Entry Points
- `src/app.py` - FastAPI app initialization and middleware setup
- `src/api/v1/routes.py` - Main router aggregating v1 endpoints

### Configuration
- `src/config/settings.py` - Pydantic BaseSettings with environment loading
- `src/config/logging_config.py` - Structured logging setup (structlog + JSON)

### API Endpoints
- `src/api/v1/health.py` - Health check endpoints (live, ready, startup)
- `src/api/v1/about.py` - Application information endpoint

### Core Utilities
- `src/core/middleware.py` - Request/response logging middleware

### Testing
- `tests/conftest.py` - Pytest fixtures (app instance, test client)
- Tests organized by type (unit, integration, e2e)

## Development Workflows

### Adding a New Endpoint

1. Create endpoint handler in appropriate module under `src/api/v1/`
2. Add route to `src/api/v1/routes.py`
3. Create tests in `tests/unit/` and `tests/integration/`
4. Run: `make test` to verify
5. Run: `make lint type-check` for code quality

### Adding a New Service

1. Create service class in `src/services/`
2. Use dependency injection (constructor) for dependencies
3. Create corresponding tests in `tests/unit/`
4. Use service in API endpoints

### Running Locally

```bash
# Option 1: Direct Python (reload on changes)
make dev

# Option 2: Docker Compose (full stack)
make docker-up
```

## Code Standards

### Style & Formatting
- **Formatting**: black (line length: 100)
- **Import sorting**: isort with black profile
- **Linting**: ruff (E, W, F, I, C, B, UP)

### Type Safety
- **Type hints**: Required for all functions/methods
- **Checking**: mypy --strict (no untyped defs)
- **Models**: Pydantic for request/response validation

### Testing
- **Framework**: pytest with asyncio support
- **Coverage**: Minimum 80% for src/
- **Categories**: unit (60%), integration (30%), e2e (10%)

### Logging
- **Structured**: JSON format in production, human-readable in dev
- **Context**: Includes trace_id, span_id, timestamp, level
- **Levels**: DEBUG, INFO, WARNING, ERROR, CRITICAL

## Environment Variables

Key environment variables (see `.env.example`):
- `ENVIRONMENT` - development|staging|production
- `DEBUG` - Enable debug mode
- `LOG_LEVEL` - Logging verbosity
- `REDIS_HOST`, `REDIS_PORT` - Redis connection
- `APP_INSIGHTS_CONNECTION_STRING` - Azure Application Insights

## Dependencies Overview

### Runtime (requirements.txt)
- **fastapi** - Web framework
- **uvicorn** - ASGI server
- **pydantic** - Data validation
- **structlog** - Structured logging
- **redis** - Cache client
- **opentelemetry-*** - Observability SDKs
- **python-dotenv** - Environment loading

### Development (requirements-dev.txt)
- **pytest** - Testing framework
- **black** - Code formatter
- **ruff** - Fast linter
- **mypy** - Type checker
- **pre-commit** - Git hooks

## Common Commands

```bash
make dev              # Start development server
make test             # Run all tests
make lint             # Check code quality
make format           # Format code
make type-check       # Run type checking
make docker-up        # Start Docker Compose services
make docker-logs      # View Docker logs
make all              # Run all checks (lint, type-check, test)
```

## Next Steps for Development

1. **Phase 2**: Implement core services and business logic
2. **Phase 3**: Add Redis caching layer
3. **Phase 4**: Integrate OpenTelemetry and Application Insights
4. **Phase 5**: Finalize Docker build and images
5. **Phase 6**: Create Terraform modules for Azure deployment

See [PLAN.md](PLAN.md) for complete development roadmap.

## Documentation References

- **PLAN.md** - High-level implementation roadmap and architecture
- **docs/DEVELOPMENT.md** - Detailed setup and development guide
- **docs/ARCHITECTURE.md** - Architecture decisions and patterns
- **docs/API.md** - API endpoint reference (to be created)
- **docs/adr/** - Architecture Decision Records

## Support & Guidance

For questions or implementation guidance:
1. Check existing code patterns in the repository
2. Review PLAN.md for architectural context
3. Check DEVELOPMENT.md for setup/running issues
4. Refer to docstrings in source modules
5. Review test examples for usage patterns
