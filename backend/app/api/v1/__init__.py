"""API v1 router aggregator."""
from fastapi import APIRouter

from app.api.v1.documents import router as documents_router
from app.api.v1.analysis import router as analysis_router

router = APIRouter()
router.include_router(documents_router, prefix="/documents", tags=["Documents"])
router.include_router(analysis_router, prefix="/analysis", tags=["Analysis"])
