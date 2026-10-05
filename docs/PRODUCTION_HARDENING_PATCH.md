# Production Hardening Patch

This file contains the full patch content for the four architectural layers discussed earlier.

## 1) app/config.py

```python
from pydantic_settings import BaseSettings
import os


class Settings(BaseSettings):
    app_name: str = "Legare123 Mission of Prosperity - De Jure Mission API"
    environment: str = os.getenv("ENVIRONMENT", "development")
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./legare.db")
    postgres_url: str = os.getenv("POSTGRES_URL", "postgresql://postgres:postgres@db:5432/legare")
    api_prefix: str = "/api/v1"
    jwt_secret: str = os.getenv("JWT_SECRET", "change-me-in-production")
    jwt_algorithm: str = os.getenv("JWT_ALGORITHM", "HS256")
    access_token_expire_minutes: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))
    cors_origins: str = os.getenv("CORS_ORIGINS", "*")

    # Production observability
    log_level: str = os.getenv("LOG_LEVEL", "INFO")
    enable_json_logging: bool = os.getenv("ENABLE_JSON_LOGGING", "true").lower() == "true"

    # Celery / Redis
    celery_broker_url: str = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
    celery_result_backend: str = os.getenv("CELERY_RESULT_BACKEND", "redis://localhost:6379/1")

    class Config:
        env_file = ".env"


settings = Settings()
```

## 2) app/bootstrap.py

```python
import logging
from fastapi import FastAPI, Request

from app.config import settings
from app.logging.json_logger import setup_json_logging
from app.metrics.prometheus import setup_metrics
from app.middleware.correlation_id import CorrelationIDMiddleware
from app.middleware.error_handlers import add_exception_handlers


logger = logging.getLogger("legare_api")


def configure_app(app: FastAPI) -> FastAPI:
    setup_json_logging()
    add_exception_handlers(app)
    app.add_middleware(CorrelationIDMiddleware)

    @app.middleware("http")
    async def add_security_headers_and_logging(request: Request, call_next):
        correlation_id = getattr(getattr(request, "state", None), "correlation_id", None)

        if correlation_id is not None:
            logger.info(
                "request_received",
                extra={
                    "correlation_id": correlation_id,
                    "path": request.url.path,
                    "method": request.method,
                },
            )

        response = await call_next(request)

        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["Content-Security-Policy"] = "default-src 'self'; frame-ancestors 'none';"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"

        if correlation_id is not None:
            response.headers["X-Correlation-ID"] = correlation_id

        return response

    app.state.enable_json_logging = settings.enable_json_logging
    setup_metrics(app)
    return app
```

## 3) app/middleware/correlation_id.py

```python
import uuid
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request


class CorrelationIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        correlation_id = request.headers.get("X-Correlation-ID") or str(uuid.uuid4())
        request.state.correlation_id = correlation_id
        response = await call_next(request)
        response.headers["X-Correlation-ID"] = correlation_id
        return response
```

## 4) app/middleware/error_handlers.py

```python
import logging
from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError


def add_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(IntegrityError)
    async def integrity_error_handler(request: Request, exc: IntegrityError):
        correlation_id = getattr(getattr(request, "state", None), "correlation_id", None)
        return JSONResponse(
            status_code=400,
            content={
                "detail": "Database integrity violation",
                "error": "integrity_error",
                "correlation_id": correlation_id,
            },
        )

    @app.exception_handler(Exception)
    async def general_exception_handler(request: Request, exc: Exception):
        correlation_id = getattr(getattr(request, "state", None), "correlation_id", None)
        logging.getLogger("legare_api").exception(
            "Unhandled exception",
            extra={"correlation_id": correlation_id},
        )
        return JSONResponse(
            status_code=500,
            content={
                "detail": "Internal server error",
                "error": "internal_error",
                "correlation_id": correlation_id,
            },
        )
```

## 5) app/logging/json_logger.py

```python
import logging
from pythonjsonlogger import jsonlogger

from app.config import settings


class CustomJsonFormatter(jsonlogger.JsonFormatter):
    def add_fields(self, log_record, record, message_dict):
        super().add_fields(log_record, record, message_dict)
        log_record.setdefault("environment", settings.environment)
        log_record.setdefault("service", settings.app_name)
        correlation_id = getattr(record, "correlation_id", None)
        if correlation_id is not None:
            log_record["correlation_id"] = correlation_id


def setup_json_logging() -> None:
    if not settings.enable_json_logging:
        return

    logger = logging.getLogger("legare_api")
    logger.setLevel(getattr(logging, settings.log_level.upper(), logging.INFO))
    logger.propagate = False

    if not logger.handlers:
        handler = logging.StreamHandler()
        handler.setFormatter(CustomJsonFormatter())
        logger.addHandler(handler)
```

## 6) app/metrics/prometheus.py

```python
from prometheus_fastapi_instrumentator import Instrumentator


def setup_metrics(app):
    Instrumentator().instrument(app).expose(app, endpoint="/metrics")
    return app
```

## 7) app/tasks/celery_app.py

```python
from celery import Celery

from app.config import settings

celery_app = Celery(
    "legare123",
    broker=settings.celery_broker_url,
    backend=settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
)
```

## 8) app/tasks/evidence_tasks.py

```python
import hashlib

from app.tasks.celery_app import celery_app


@celery_app.task(name="app.tasks.hash_payload")
def hash_payload(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


@celery_app.task(name="app.tasks.verify_evidence_batch")
def verify_evidence_batch(evidence_ids: list[str]) -> dict:
    results = []
    for evidence_id in evidence_ids:
        results.append({"evidence_id": evidence_id, "status": "queued_for_verification"})
    return {"status": "queued", "items": results}
```

## 9) requirements.txt

```txt
fastapi==0.110.0
uvicorn==0.28.0
pydantic==2.6.4
pydantic-settings==2.2.1
sqlalchemy==2.0.23
python-jose[cryptography]==3.3.0
passlib[bcrypt]==1.7.4
psycopg2-binary==2.9.9
alembic==1.13.2
pytest==8.1.1
httpx==0.27.0
python-json-logger==2.0.7
prometheus-fastapi-instrumentator==6.1.0
celery==5.3.4
redis==5.0.1
```

## 10) docker-compose.yml

```yaml
version: '3.9'
services:
  api:
    build: .
    ports:
      - "8000:8000"
    environment:
      ENVIRONMENT: development
      DATABASE_URL: sqlite:///./legare.db
      JWT_SECRET: change-me-in-production
      JWT_ALGORITHM: HS256
      ACCESS_TOKEN_EXPIRE_MINUTES: 60
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    volumes:
      - .:/app
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
    depends_on:
      - db
      - redis

  db:
    image: postgres:16-alpine
    environment:
      POSTGRES_DB: legare
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: postgres
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

  celery_worker:
    build: .
    command: celery -A app.tasks.celery_app worker --loglevel=info
    environment:
      ENVIRONMENT: development
      DATABASE_URL: sqlite:///./legare.db
      CELERY_BROKER_URL: redis://redis:6379/0
      CELERY_RESULT_BACKEND: redis://redis:6379/1
    depends_on:
      - redis
      - db

volumes:
  postgres_data:
```

## 11) .github/workflows/ci.yml

```yaml
name: CI

on:
  pull_request:
    branches: [main, v1.0.0]
  push:
    branches: [main, v1.0.0]

jobs:
  test:
    runs-on: ubuntu-latest

    services:
      postgres:
        image: postgres:16-alpine
        env:
          POSTGRES_DB: legare_test
          POSTGRES_USER: postgres
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
        ports:
          - 5432:5432

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt
          pip install flake8 ruff pytest-cov

      - name: Lint with flake8
        run: |
          flake8 app --count --select=E9,F63,F7,F82 --show-source --statistics

      - name: Lint with ruff
        run: ruff check app

      - name: Run pytest
        run: pytest tests/ -v --cov=app --cov-report=xml
        env:
          DATABASE_URL: postgresql://postgres:postgres@localhost:5432/legare_test

      - name: Upload coverage
        if: always()
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.xml
```

## 12) app/main.py — initialization update

```python
from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.bootstrap import configure_app
from app.config import settings
from app.database import get_db, SessionLocal, Base, engine
from app.database.seeder import seed_database
from app.models import (
    AgentRegistration,
    AgentUpdate,
    EvidenceItem,
    EvidenceUpdate,
    ClaimEvaluationRequest,
    ClaimEvaluationResponse,
    AgentStatus,
    EvidenceStatus,
    ClaimStatus,
    UserCreate,
    UserLogin,
    Token,
)
from app.services.agent_registry import AgentRegistryService
from app.services.evidence_service import EvidenceService
from app.services.claim_evaluation import ClaimEvaluationService
from app.services.workflow_service import WorkflowService
from app.services.audit_service import audit_service
from app.services.user_service import UserService
from app.auth import authenticate_user, create_access_token, get_current_user, require_roles, get_password_hash

app = FastAPI(
    title=settings.app_name,
    description="A human-in-the-loop multi-agent evidence orchestration framework based on 'Proof Before Claim'.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins.split(",") if settings.cors_origins != "*" else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_app(app)

Base.metadata.create_all(bind=engine)
```

## 13) Create directories

```bash
mkdir -p app/middleware app/logging app/metrics app/tasks
```

## 14) Optional .gitignore additions

```gitignore
.env
.venv/
__pycache__/
.pytest_cache/
```

## 15) Quick validation

```bash
pip install -r requirements.txt
pytest tests/ -q
```

This gives you:
- request correlation IDs
- global structured error handling
- security headers
- JSON logging
- Prometheus /metrics endpoint
- Redis/Celery scaffolding
- GitHub Actions CI for lint + tests
- Docker Compose updates for worker support

