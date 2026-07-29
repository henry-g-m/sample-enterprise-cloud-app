# Development Guide

## Prerequisites

- Python 3.14+
- Docker and Docker Compose
- Git
- Make (optional, for using Makefile commands)

## Environment Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd sample-enterprise-cloud-app
```

### 2. Create Virtual Environment

```bash
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Setup Environment Variables

```bash
cp .env.example .env
# Edit .env if needed for your development environment
```

## Running the Application

### Option 1: Local Development (No Docker)

```bash
# Install dependencies
pip install -r requirements-dev.txt

# Run development server
make dev
# or
uvicorn src.app:app --reload --host localhost --port 8000
```

The API will be available at `http://localhost:8000`

### Option 2: Docker Compose (Recommended)

```bash
# Start all services
make docker-up
# or
docker-compose up -d

# View logs
make docker-logs
# or
docker-compose logs -f app

# Stop services
make docker-down
# or
docker-compose down
```

The API will be available at `http://localhost:8000`

## Testing

### Run All Tests

```bash
make test
# or
pytest tests/ -v
```

### Run Specific Test Categories

```bash
# Unit tests only
make test-unit
pytest tests/unit/ -v

# Integration tests only
make test-integration
pytest tests/integration/ -v

# With coverage report
make test-cov
pytest tests/ --cov=src --cov-report=html --cov-report=term
```

### View Coverage Report

After running tests with coverage:

```bash
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## Code Quality

### Format Code

```bash
make format
# or
black src/ tests/
isort src/ tests/
```

### Check Formatting

```bash
make format-check
# or
black --check src/ tests/
isort --check-only src/ tests/
```

### Lint Code

```bash
make lint
# or
ruff check src/ tests/
```

### Type Checking

```bash
make type-check
# or
mypy src/ --strict
```

### Run All Checks

```bash
make all
# Runs: clean, install, lint, type-check, test
```

## API Endpoints

### Health Checks

- **Liveness**: `GET /api/v1/health/live`
  - Used by Kubernetes/container orchestration
  - Returns: `{status: "alive", timestamp, version}`

- **Readiness**: `GET /api/v1/health/ready`
  - Checks if service is ready to handle traffic
  - Returns: `{ready: boolean, timestamp, dependencies}`

- **Startup**: `GET /api/v1/health/startup`
  - Checks if service has successfully started
  - Returns: `{status: "started", timestamp, version}`

### Application Info

- **About**: `GET /api/v1/about`
  - Returns: `{name, version, description, timestamp, environment}`

## Project Structure

```
sample-enterprise-cloud-app/
├── src/                          # Source code
│   ├── app.py                   # FastAPI app factory
│   ├── config/                  # Configuration
│   ├── api/v1/                  # API routes
│   ├── core/                    # Core utilities
│   ├── domain/                  # Business logic
│   ├── infrastructure/          # External services
│   ├── services/                # Application services
│   └── utils/                   # Utilities
├── tests/                        # Test suite
│   ├── unit/                    # Unit tests
│   ├── integration/             # Integration tests
│   └── e2e/                     # End-to-end tests
├── docs/                         # Documentation
├── infrastructure/               # Infrastructure as Code
├── Dockerfile                   # Multi-stage Docker build
├── docker-compose.yml           # Local development services
├── pyproject.toml              # Project configuration
├── requirements.txt            # Runtime dependencies
├── requirements-dev.txt        # Development dependencies
├── Makefile                    # Development tasks
└── pytest.ini                  # Pytest configuration
```

## Useful Make Commands

```bash
make install         # Install dependencies
make dev            # Start development server
make test           # Run all tests
make test-unit      # Run unit tests
make test-cov       # Run tests with coverage
make lint           # Run linting
make format         # Format code
make type-check     # Run type checking
make clean          # Clean build artifacts
make docker-build   # Build Docker image
make docker-up      # Start docker-compose services
make docker-down    # Stop docker-compose services
make all            # Run all checks and tests
```

## Debugging

### Enable Debug Logging

Set environment variable:

```bash
LOG_LEVEL=DEBUG
```

### VSCode Debug Configuration

Add to `.vscode/launch.json`:

```json
{
  "version": "0.2.0",
  "configurations": [
    {
      "name": "Python: FastAPI",
      "type": "python",
      "request": "launch",
      "module": "uvicorn",
      "args": [
        "src.app:app",
        "--reload",
        "--host",
        "0.0.0.0",
        "--port",
        "8000"
      ],
      "jinja": true,
      "justMyCode": true
    }
  ]
}
```

## Common Issues

### Port Already in Use

If port 8000 is already in use:

```bash
# Change port in .env or command line
uvicorn src.app:app --port 8001
```

### Redis Connection Error

If Redis is not running:

```bash
# Start Redis with Docker
docker run -d -p 6379:6379 redis:7-alpine
# or use docker-compose
docker-compose up -d redis
```

### Import Errors

Ensure you're using the correct Python path:

```bash
export PYTHONPATH=/path/to/sample-enterprise-cloud-app
```

## Getting Help

- Check [PLAN.md](../PLAN.md) for architecture and implementation plan
- Check [ARCHITECTURE.md](ARCHITECTURE.md) for technical decisions
- Check [API.md](API.md) for API documentation
- See individual module docstrings for implementation details

## Next Steps

After getting the development environment working:

1. Create a feature branch: `git checkout -b feature/your-feature`
2. Make your changes
3. Run tests and linting: `make all`
4. Commit with clear messages
5. Push and create a pull request

For more details, see [PLAN.md](../PLAN.md)
