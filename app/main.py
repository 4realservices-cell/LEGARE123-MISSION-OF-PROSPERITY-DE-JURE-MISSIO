from fastapi import FastAPI, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.bootstrap import configure_app
from app.config import settings
from app.database import get_db, engine
from app.routers.domain import router as sentinel_domain_router

# Ensure global model discovery for Alembic/SQLAlchemy context
import app.models  # noqa: F401

app = FastAPI(
    title=settings.app_name,
    description="A human-in-the-loop multi-agent evidence orchestration framework based on 'Proof Before Claim'.",
    version="1.2.0",
)


def _parse_cors_origins(raw: str):
    if not raw:
        return []
    raw = raw.strip()
    if raw == "*":
        return ["*"]
    return [part.strip() for part in raw.split(",") if part.strip()]


app.add_middleware(
    CORSMiddleware,
    allow_origins=_parse_cors_origins(settings.cors_origins),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

configure_app(app)
app.include_router(sentinel_domain_router)


@app.on_event("startup")
def startup_event():
    """
    Production Readiness:
    Remove schema auto-creation (`create_all`). Migrations are managed via Alembic.
    Instead, execute a lightweight connection pool ping to guarantee database readiness.
    """
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
        app.state.db_connected = True
    except Exception as e:
        app.state.db_connected = False
        raise RuntimeError(f"Database initialization health check failed: {str(e)}")


@app.get("/health/readiness", status_code=status.HTTP_200_OK)
def database_readiness_probe(db: Session = Depends(get_db)):
    """Kubernetes / Cloud Run readiness probe verifying live DB connection."""
    try:
        db.execute(text("SELECT 1"))
        return {"status": "ready", "database": "connected"}
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={"status": "unhealthy", "database": "disconnected", "error": str(e)},
        )
