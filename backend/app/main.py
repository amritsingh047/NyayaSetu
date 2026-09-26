"""LexAI FastAPI application entry point."""
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1 import router as api_v1_router
from app.core.config import settings
from app.core.database import engine, Base
import app.models  # Loads the models so the database knows what tables to create
from app.core.logging import configure_logging

configure_logging()
log = structlog.get_logger()

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events."""
    log.info("LexAI starting up", env=settings.APP_ENV)
    
    # Auto-create the database tables when the server turns on
    try:
        async with engine.begin() as conn:
            await conn.execute(__import__('sqlalchemy').text("CREATE EXTENSION IF NOT EXISTS vector"))
            await conn.run_sync(Base.metadata.create_all)
        log.info("Database ready")
    except Exception as e:
        log.error("Database connection failed", error=str(e))
        
    yield
    log.info("LexAI shutting down")
    await engine.dispose()

app = FastAPI(
    title="LexAI API",
    description="GenAI-powered legal document assistance. Not legal advice.",
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

# --- Routers ---
app.include_router(api_v1_router, prefix="/api/v1")

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok", "service": "lexai-api"}
