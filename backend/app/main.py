"""LexAI FastAPI application entry point."""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.database import engine
from app.core.logging import configure_logging

configure_logging()
log = structlog.get_logger()


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    log.info("NyayaSetu starting up", env=settings.APP_ENV)
    try:
        async with engine.begin() as conn:
            await conn.execute(__import__('sqlalchemy').text("CREATE EXTENSION IF NOT EXISTS vector"))
        log.info("Database ready")
    except Exception as e:
        log.warning(
            "PostgreSQL database connection skipped or not yet running; "
            "statutory corpus and deterministic analysis routes remain fully functional.",
            error=str(e),
        )
    yield
    log.info("NyayaSetu shutting down")
    try:
        await engine.dispose()
    except Exception:
        pass


app = FastAPI(
    title="NyayaSetu API",
    description="GenAI-powered Indian legal document assistance. Not legal advice.",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/api/docs" if settings.APP_ENV == "development" else None,
    redoc_url="/api/redoc" if settings.APP_ENV == "development" else None,
)

# --- Middleware ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if settings.APP_ENV == "production":
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=[settings.FRONTEND_URL])

# --- Routers ---
app.include_router(api_v1_router, prefix="/api/v1")


@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "nyayasetu-api"}
