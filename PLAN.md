# Enterprise Demo Cloud App - Implementation Plan

## Table of Contents
1. [Architecture Overview](#architecture-overview)
2. [Technology Stack](#technology-stack)
3. [Project Structure](#project-structure)
4. [Development Phases](#development-phases)
5. [Critical Path](#critical-path)
6. [Iterations Preview](#iterations-preview)

---

## Architecture Overview

### High-Level Architecture (Iteration 1)

```
┌─────────────────────────────────────────────────────────────┐
│                     CLIENT LAYER                             │
│  (Future: Web UI - Iteration 3)                             │
└───────────────────┬─────────────────────────────────────────┘
                    │
┌───────────────────v─────────────────────────────────────────┐
│          AZURE API MANAGEMENT (APIM)                         │
│  - Rate limiting, throttling, versioning                    │
│  - Authentication/Authorization enforcement                 │
│  - OpenAPI documentation                                    │
│  - Analytics & developer portal                             │
└───────────────────┬─────────────────────────────────────────┘
                    │
        ┌───────────┴────────────┐
        │                        │
┌───────v─────┐        ┌────────v────────┐
│  Primary    │        │  Secondary      │
│  Region     │        │  Region (HA)    │
│  (East US)  │        │  (West US)      │
└───────┬─────┘        └────────┬────────┘
        │                       │
   ┌────v────────────────────────v────┐
   │  Azure Container Apps (ACA)       │
   │  - Multi-instance deployment      │
   │  - Auto-scaling based on load     │
   │  - Managed Kubernetes abstraction │
   └────┬─────────────────────────────┘
        │
   ┌────v──────────────────────┐
   │  Python REST API Service   │
   │  ├── Health checks         │
   │  ├── /about endpoint       │
   │  ├── API versioning        │
   │  └── Graceful shutdown     │
   └────┬──────────────────────┘
        │
   ┌────v──────────────────────┐
   │  Redis Cache (Azure)       │
   │  - Response caching        │
   │  - Session data (future)   │
   │  - Rate limit counters     │
   └────────────────────────────┘

Observability Layer (All Components):
├── Azure Application Insights
├── Azure Monitor
├── Structured Logging
└── Distributed Tracing (OpenTelemetry)
```

### Design Patterns

| Pattern | Purpose | Implementation |
|---------|---------|-----------------|
| **Layered Architecture** | Separation of concerns | Controller → Service → Domain → Repository |
| **Dependency Injection** | Loose coupling | Factory patterns, constructor injection |
| **Repository Pattern** | Data abstraction | Interface-based repository layer |
| **DTO** | API contract clarity | Separate request/response models |
| **Health Checks** | Liveness/readiness probes | Structured health endpoint |
| **Caching Strategy** | Performance optimization | Redis for distributed caching |
| **Event-Driven** | Future event processing | Queue patterns for ticket events |

---

## Technology Stack

### Primary Stack (Azure + Python)

| Component | Technology | Rationale |
|-----------|-----------|-----------|
| **Framework** | FastAPI | Modern, async-first, auto-docs, high performance |
| **Python Version** | 3.14+ | Latest stable release, type hints maturity |
| **Web Server** | Uvicorn (ASGI) | High performance, async-native |
| **Testing** | pytest | Industry standard, excellent plugins |
| **Type Checking** | mypy | Static type safety, early error detection |
| **Linting** | ruff + pylint | Fast, comprehensive |
| **Code Formatting** | black | Opinionated, consistent |
| **Logging** | structlog + python-json-logger | Structured logging for observability |
| **Caching** | redis | Distributed, industry standard |
| **Monitoring** | OpenTelemetry + Azure SDK | Standards-compliant, vendor-agnostic |
| **Containerization** | Docker | Multi-stage builds, minimal image size |
| **Orchestration** | Azure Container Apps | Serverless containers, auto-scaling |

### Azure Services

| Service | Purpose |
|---------|---------|
| **Container Apps** | Application hosting (serverless containers) |
| **API Management** | API gateway, rate limiting, versioning |
| **Application Insights** | APM (Application Performance Monitoring) |
| **Azure Monitor** | Infrastructure monitoring, alerts |
| **Cache for Redis** | Distributed caching |
| **Key Vault** | Secrets management |
| **Container Registry** | Private image registry |
| **Application Gateway** | Load balancing |
| **Virtual Networks** | Network isolation |
| **Log Analytics** | Log aggregation |

### Alternative Stack (AWS + Java/Spring Boot)

| Component | Technology |
|-----------|-----------|
| **Framework** | Spring Boot 3.x |
| **Java Version** | 21 LTS |
| **Testing** | JUnit 5 + Testcontainers |
| **Container Orchestration** | ECS Fargate |
| **API Gateway** | AWS API Gateway |
| **Monitoring** | CloudWatch + X-Ray |
| **Caching** | ElastiCache Redis |
| **Resilience** | Resilience4j |

---

## Project Structure

```
sample-enterprise-cloud-app/
├── .github/
│   └── workflows/
│       ├── ci-python.yml          # Build, lint, test
│       ├── cd-azure.yml           # Deploy to Azure
│       └── security-scanning.yml  # SAST, dependency checks
│
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf               # Primary infrastructure
│   │   ├── variables.tf           # Input variables
│   │   ├── outputs.tf             # Output values
│   │   ├── azure/
│   │   │   ├── container-apps.tf
│   │   │   ├── api-management.tf
│   │   │   ├── redis.tf
│   │   │   ├── monitor.tf
│   │   │   └── networking.tf
│   │   └── aws/
│   │       ├── ecs.tf
│   │       ├── api-gateway.tf
│   │       └── elasticache.tf
│   ├── docker/
│   │   └── Dockerfile
│   └── scripts/
│       ├── deploy.sh
│       ├── health-check.sh
│       └── rollback.sh
│
├── src/
│   ├── app.py                    # Application entry point
│   ├── config/
│   │   ├── settings.py           # Configuration management
│   │   ├── logging_config.py     # Structured logging
│   │   └── feature_flags.py      # Feature flags
│   ├── api/
│   │   ├── v1/
│   │   │   ├── routes.py         # Route definitions
│   │   │   ├── health.py         # Health endpoints
│   │   │   └── about.py          # /about endpoint
│   │   └── v2/                   # Future versions
│   ├── core/
│   │   ├── exceptions.py         # Custom exceptions
│   │   ├── middleware.py         # Request/response middleware
│   │   ├── security.py           # Security utilities
│   │   └── constants.py          # App constants
│   ├── domain/
│   │   ├── events/               # Event definitions
│   │   ├── models.py             # Domain models
│   │   └── services.py           # Business services
│   ├── infrastructure/
│   │   ├── cache/
│   │   │   └── redis_client.py   # Redis wrapper
│   │   ├── observability/
│   │   │   ├── logging.py        # Structured logging
│   │   │   ├── tracing.py        # Distributed tracing
│   │   │   └── metrics.py        # Custom metrics
│   │   └── external/
│   │       └── azure_services.py # Azure SDK integration
│   ├── services/
│   │   ├── health_service.py     # Health check logic
│   │   └── about_service.py      # About endpoint logic
│   └── utils/
│       ├── decorators.py         # Custom decorators
│       ├── validators.py         # Data validation
│       └── helpers.py            # Utility functions
│
├── tests/
│   ├── conftest.py               # Pytest fixtures
│   ├── unit/
│   │   ├── test_about_service.py
│   │   ├── test_health_service.py
│   │   └── test_cache.py
│   ├── integration/
│   │   ├── test_api_endpoints.py
│   │   └── test_redis_integration.py
│   └── e2e/
│       └── test_deployment.py
│
├── docs/
│   ├── README.md                 # Project overview
│   ├── ARCHITECTURE.md           # Architecture decisions
│   ├── API.md                    # API documentation
│   ├── DEPLOYMENT.md             # Deployment guide
│   ├── DEVELOPMENT.md            # Dev environment setup
│   └── adr/                      # Architecture Decision Records
│
├── Dockerfile                    # Multi-stage build
├── docker-compose.yml            # Local development
├── pyproject.toml               # Python project config
├── requirements.txt             # Runtime dependencies
├── requirements-dev.txt         # Development dependencies
├── pytest.ini                   # Pytest configuration
├── Makefile                     # Development tasks
├── PLAN.md                      # This file
├── LICENSE                      # Apache 2.0 or MIT
└── CHANGELOG.md                 # Version history
```

---

## Development Phases

### Phase 1: Foundation Setup (Week 1) ✅ COMPLETED

**Objectives**: Project skeleton, CI/CD pipeline, local development environment

**Deliverables**:
- [x] Python project structure with Poetry/pip-tools
- [x] FastAPI application skeleton
- [x] Docker multi-stage Dockerfile
- [x] docker-compose.yml for local development
- [x] GitHub Actions CI pipeline (build, lint, test)
- [x] Code quality gates (Black, ruff, mypy, pytest)
- [x] CLAUDE.md with project documentation

**Key Milestones**:
- Repository initialized with base structure
- Development environment working locally
- CI pipeline running on every push
- Code quality standards enforced

---

### Phase 2: Core API Development (Week 2) ✅ COMPLETED

**Objectives**: Implement REST API with health checks and /about endpoint

**Deliverables**:
- [x] FastAPI route structure (v1 namespace)
- [x] Health check endpoints (liveness, readiness, startup)
- [x] /about endpoint with version and metadata
- [x] Structured logging with structlog
- [x] Request/response middleware
- [x] Exception handling and error responses
- [x] Unit tests (80%+ coverage)

---

### Phase 3: Caching & Performance (Week 2-3) ✅ COMPLETED

**Objectives**: Implement Redis caching layer with health checks

**Deliverables**:
- [x] Redis client wrapper with connection pooling
- [x] Cache decorators for response caching
- [x] Cache invalidation strategies
- [x] Health checks for Redis connectivity
- [x] Integration tests with Redis container

---

### Phase 4: Observability Implementation (Week 3) ✅ COMPLETED

**Objectives**: Structured logging, distributed tracing, custom metrics

**Deliverables**:
- [x] OpenTelemetry integration
- [x] Structured logging with JSON output
- [x] Custom metrics for business events
- [x] Application Insights SDK integration
- [x] Correlation ID propagation

---

### Phase 5: Docker & Local Testing (Week 3-4)

**Objectives**: Multi-stage Docker build, local deployment simulation

**Deliverables**:
- [x] Multi-stage Dockerfile
- [x] Docker image security scanning (Trivy scan added to CI `build` job)
- [x] docker-compose.yml with all services
- [x] Image size optimization
- [x] Health check configurations (Dockerfile `HEALTHCHECK` + compose `app`/`redis` healthchecks, verified against a running container)

---

### Phase 6: Azure Deployment Setup (Week 4) ✅ DEPLOYED

**Objectives**: Terraform configuration for Azure resources

**Deliverables**:
- [x] Terraform modules for Container Apps (workload-profile environment, VNet-integrated, liveness/readiness/startup probes wired to the app's health endpoints)
- [x] API Management configuration (External VNet mode, gateway routes to the container app) — gated behind `enable_apim` (default `false`) to skip its hourly Developer-SKU billing until an auth/rate-limit policy justifies turning it on
- [x] Azure Container Registry (Basic SKU, admin disabled) + user-assigned managed identity + `AcrPull` role assignment, so the container app pulls images without a shared password
- [x] Redis cache setup (TLS-only, wired into the container app via secrets/env vars)
- [x] Application Insights resource (workspace-based, connection string wired into the container app)
- [x] Networking (VNet, subnets, NSGs) — separate delegated subnet for Container Apps and un-delegated subnet for APIM, each with NSG rules sourced from Microsoft's documented minimums

Applied to a real Azure subscription (`terraform apply`, resource group `rg-entdemo-dev`, `eastus`). Along the way: the subscription needed `Microsoft.App` resource-provider registration (`az provider register -n Microsoft.App`), and the app crash-looped on first deploy because Terraform sent `ENVIRONMENT=dev` while `src/config/settings.py`'s `Settings.environment` only accepts `development|staging|production` — fixed by translating the value in a `locals` block in `container-apps.tf` rather than renaming the `environment` Terraform variable (which drives resource naming and would have forced recreating everything). The real app image is built and pushed via `az acr build` (see Phase 7) and running healthy at the container app's FQDN.

---

### Phase 7: CI/CD Pipeline Enhancement (Week 4)

**Objectives**: Full deployment pipeline with testing gates

**Deliverables**:
- [x] GitHub Actions workflow for Docker build/push — `.github/workflows/cd-azure.yml`, `build-and-push` job runs `az acr build` against `acrentdemodev.azurecr.io`, tagged with the git SHA
- [x] Registry push to Azure Container Registry (ACR) — now automated in CI (was previously manual, see Phase 6 notes)
- [x] Terraform plan/apply in CI/CD — remote state backend (`sttfstateentdemo` storage account in `rg-entdemo-tfstate`, `use_azuread_auth`), OIDC federated login (no stored credentials), `terraform-plan-pr` job plans read-only on PRs touching `infrastructure/terraform/**`, `terraform-apply-infra` + `deploy-image` jobs apply on push to `master`
- [x] Deployment approval gates — GitHub Environment `production` requires manual approval (reviewer: repo owner) before any job that can create/modify/destroy Azure resources runs
- [x] Smoke tests post-deployment — `smoke-test` job polls `/api/v1/health/live`, `/api/v1/health/ready`, `/api/v1/about` on the deployed container app FQDN, retrying for ~100s before failing the run

Bootstrapped this session (one-time, outside Terraform since it can't create its own backend): resource group `rg-entdemo-tfstate` + storage account `sttfstateentdemo` for remote state; Azure AD app registration `gh-actions-entdemo` with OIDC federated credentials scoped to the `master` branch, the `production` GitHub Environment, and `pull_request` (no client secret stored anywhere); `Contributor` on `rg-entdemo-dev` + `Storage Blob Data Contributor` on the state storage account, both scoped to just those resource groups. Local dev now points at the same backend via `infrastructure/terraform/backend.hcl` (gitignored; see `backend.hcl.example`).

Not yet done: the live Azure resources were destroyed after the Phase 6 demo/load-test session to stop hourly billing (Redis Standard C1), so the next push to `master` (or manual `workflow_dispatch`) will recreate everything from scratch through the new pipeline — that first real run, with its approval gate, is still pending.

---

### Phase 8: Testing Strategy & QA (Week 4-5)

**Objectives**: Comprehensive testing coverage and validation

**Deliverables**:
- [ ] Unit tests (80%+ coverage)
- [ ] Integration tests with containers
- [ ] E2E tests in staging environment
- [ ] Performance/load testing strategy
- [ ] Security scanning (dependency, container)

---

### Phase 9: Documentation & Knowledge Transfer (Week 5)

**Objectives**: Comprehensive documentation for operations and developers

**Deliverables**:
- [ ] API documentation (OpenAPI/Swagger)
- [ ] Deployment guide
- [ ] Architecture Decision Records (ADRs)
- [ ] Development setup guide
- [ ] Troubleshooting guide

---

## Critical Path

```
Phase 1 (Foundation)
    └─→ Phase 2 (Core API)
            └─→ Phase 3 (Caching)
                    └─→ Phase 4 (Observability)
                            └─→ Phase 5 (Docker)
                                    └─→ Phase 6 (Terraform)
                                            └─→ Phase 7 (CI/CD)
                                                    └─→ Phase 8 (Testing)
                                                            └─→ Phase 9 (Documentation)
```

**Critical Path Duration**: ~5 weeks

### Parallel Work Streams

**Stream A (Application)**:
- Phase 1 → Phase 2 → Phase 3 → Phase 4 → Phase 5

**Stream B (Infrastructure)**:
- Phase 6 (can start after Phase 2)

**Stream C (CI/CD)**:
- Phase 7 (requires Phase 5 + Phase 6)

**Stream D (Testing & QA)**:
- Phase 8 (can start during Phase 5)

**Stream E (Documentation)**:
- Phase 9 (final phase)

---

## Iterations Preview

### Iteration 2: Event Ticket Sales Application

**Features**:
- Venue definition (layout, seat count, pricing)
- Inventory/seat availability
- Shopping cart functionality
- Inventory holds (temporary reservations)
- Ticket assignment
- PostgreSQL database
- Event-driven architecture
- Azure Service Bus for event processing

**Technology Additions**:
- SQLAlchemy ORM
- Pydantic models
- Event processing
- Payment integration

---

### Iteration 3: Web UI & Advanced Patterns

**Features**:
- Web UI for ticket browsing
- User authentication (OAuth2/OIDC)
- Advanced resilience patterns
- Circuit breakers, retries, timeouts
- Terraform Infrastructure as Code

**Technology Stack**:
- React 18+ (TypeScript)
- TailwindCSS
- Azure Static Web Apps
- Resilience4j patterns

---

## Key Decisions & Rationale

### Why FastAPI?
- Modern, async-first framework
- Automatic OpenAPI documentation
- Native async/await support
- High performance (comparable to Node.js)
- Excellent for microservices

### Why Azure Container Apps?
- Simpler than Kubernetes/AKS
- Serverless containers with autoscaling
- Built-in traffic management
- Native Azure service integration
- Cost-effective for this scale

### Why Terraform?
- Multi-cloud support (Azure, AWS, GCP)
- State management for tracking changes
- Modular, reusable code
- Version control friendly
- Widely adopted in enterprises

### Why Docker Multi-Stage Builds?
- Separation of build and runtime environments
- Reduced image size (security, speed)
- Layer caching optimization
- Production best practice
- Target: <100MB image size

---

## Getting Started

See [DEVELOPMENT.md](docs/DEVELOPMENT.md) for:
- Local environment setup
- Running the application locally
- Running tests
- Development workflows

See [ARCHITECTURE.md](docs/ARCHITECTURE.md) for:
- Detailed architectural decisions
- Data flow diagrams
- Component interactions

See [DEPLOYMENT.md](docs/DEPLOYMENT.md) for:
- Azure setup prerequisites
- Deploying to staging/production
- Monitoring and alerting
- Troubleshooting deployment issues

---

## Status

- **Iteration**: 1 (MVP)
- **Phase**: 7 - CI/CD Pipeline Enhancement (pipeline built; first automated deploy run pending)
- **Target Launch**: 5 weeks
- **Status**: Phase 1 through Phase 6 complete. Phase 7's CI/CD pipeline (`.github/workflows/cd-azure.yml`) is now in place: OIDC-authenticated Terraform plan/apply, ACR build/push, an approval-gated `production` GitHub Environment, and post-deploy smoke tests. Live Azure resources were torn down after the Phase 6 demo to avoid idle billing, so they don't exist right now — the next push to `master` (or a manual `workflow_dispatch` run) will recreate them via the new pipeline instead of the old manual `az acr build` + local `terraform apply` steps.

Last Updated: 2026-08-26
