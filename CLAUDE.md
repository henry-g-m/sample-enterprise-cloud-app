# Codebase Documentation for Claude

## Project Overview

**Enterprise Demo Cloud App** - A simple REST API demonstrating enterprise best practices for cloud deployment on Azure. The application provides health check endpoints and application metadata, with a foundation for scaling to more complex features in future iterations.

### Iteration 2: Event Ticket Sales (Prototype)

Iteration 2 adds a ticket sales system for a **single venue, multiple events**.
This is explicitly a **learning prototype, not a production system** — the
goal is for the user to learn how the technologies involved (database,
multiple Docker services, a simple UI, and how they integrate with the
Phase 1-7 foundation) actually work together, not to build something
enterprise-grade. When designing or implementing this iteration:

- **Favor simple, readable, and easy to understand over robust/scalable.**
  Skip patterns whose only justification is "a real production system would
  need this" (e.g. don't reach for CQRS, saga orchestration, or heavy
  abstraction layers unless the user asks).
- It's fine to make simplifying assumptions (single venue, no auth beyond
  what's already trivial, no payment processor integration) rather than
  modeling the general case.
- Prefer fewer moving parts and less configuration over flexibility that
  isn't needed yet.
- This still runs as multiple Docker services with a real database, so the
  simplicity guidance is about design/code complexity, not about skipping
  the multi-service setup itself — that's part of what the user wants to
  learn.

Detailed design (data model, concurrency approach, API surface, service
boundaries, and why we're using a shared database instead of a
per-service one) is in
[docs/ITERATION2_DESIGN.md](docs/ITERATION2_DESIGN.md). PLAN.md's
"Iteration 2: Event Ticket Sales Application" section has the original
high-level sketch and points here for the real design. Not yet
implemented — design work happens collaboratively in conversation before
code is written.

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
- **Python**: 3.14+ (with type hints)
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
- `terraform/` - Terraform for Azure (root module + `azure/` submodule: Container Apps, ACR, Redis, networking, monitoring, budget). Remote state in Azure Blob Storage (`rg-entdemo-tfstate` / `sttfstateentdemo`), auth via Azure AD (no storage keys). `backend.hcl.example` + `terraform.tfvars.example` show the local dev setup (both real files are gitignored).
- `docker/` - Docker-related files
- `scripts/` - Deployment and operational scripts

**`.github/workflows/`** - CI/CD
- `ci-python.yml` - lint, type-check, test, security scan, Docker build + Trivy vulnerability scan (runs on every push/PR)
- `cd-azure.yml` - Terraform plan (PRs)/apply, ACR build & push, image rollout, post-deploy smoke tests (runs on push to `master`). Azure auth is OIDC-only (no stored credentials); Azure-touching jobs are gated behind the `production` GitHub Environment's required-reviewer approval.

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

## Current Phase: Phase 8 - Testing Strategy & QA

Phases 1-7 are complete: FastAPI app with health/about endpoints, Redis
caching, OpenTelemetry + Application Insights observability, multi-stage
Docker build, Azure infrastructure via Terraform, and a full CI/CD pipeline.
The app is live and deployed. See [PLAN.md](PLAN.md) for the authoritative,
detailed phase-by-phase status (this file only tracks the high-level shape).

### Live deployment

- **Endpoint**: `https://ca-entdemo-dev.ambitiouswater-d567181b.eastus.azurecontainerapps.io`
- **Azure resource group**: `rg-entdemo-dev` (`eastus`) — Container Apps, ACR, Redis, App Insights/Log Analytics, VNet, budget alert. APIM exists in Terraform but is gated off (`enable_apim = false`) to avoid its hourly billing.
- **Logs**: `az containerapp logs show --name ca-entdemo-dev --resource-group rg-entdemo-dev --follow` for live tail; Application Insights (`appi-entdemo-dev`) in the Portal for traces; Log Analytics (`law-entdemo-dev`) for queryable console/system logs.

### Planned (Phase 8+)
- [ ] Higher unit/integration/e2e test coverage
- [ ] Performance/load testing strategy (a Locust load test already exists at `tests/load/locustfile.py`)
- [ ] API documentation (OpenAPI/Swagger), deployment guide, ADRs (Phase 9)
- [ ] Event ticket sales domain, Web UI (Iteration 2-3, see PLAN.md)

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

### Infrastructure (Terraform / Azure)

```bash
cd infrastructure/terraform
terraform init -backend-config=backend.hcl   # local dev; CI passes backend config via -backend-config flags instead
terraform plan                                # uses terraform.tfvars automatically
terraform apply
terraform output -raw container_app_fqdn      # read a value from remote state, e.g. the live URL

az containerapp logs show --name ca-entdemo-dev --resource-group rg-entdemo-dev --follow  # tail live logs
```

## Next Steps for Development

1. **Phase 8**: Expand test coverage (unit/integration/e2e), formalize load-testing strategy
2. **Phase 9**: API docs (OpenAPI/Swagger), deployment guide, ADRs
3. **Iteration 2**: Event ticket sales domain (PostgreSQL, Service Bus, SQLAlchemy)
4. **Iteration 3**: Web UI (React), OAuth2/OIDC auth, resilience patterns

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
