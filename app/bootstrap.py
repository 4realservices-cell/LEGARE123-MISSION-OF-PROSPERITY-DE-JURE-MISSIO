# app/bootstrap.py
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

logger = logging.getLogger("sentinel.bootstrap")

def configure_app(app: FastAPI) -> None:
    """Configure middleware, logging, and startup settings for Sentinel Ecosystem v1.2.0."""
    logger.info("Initializing Sentinel Ecosystem application configuration...")

    # Avoid duplicate CORS registration if main.py already added it.
    # Starlette stores pending middleware as Middleware objects, so check .cls.
    if not any(getattr(middleware, "cls", None) is CORSMiddleware for middleware in app.user_middleware):
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Explicit dev origins
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

    logger.info("Sentinel application configuration successfully applied.")
