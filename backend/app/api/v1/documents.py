"""Document upload, retrieval, and deletion endpoints for LegalLens."""
import uuid
from datetime import datetime, timedelta, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import AuthenticatedUser, get_current_user
from app.models.document import Document, DocumentChunk
from app.schemas.document import DocumentResponse
from app.services.document_processor import DocumentProcessor

log = structlog.get_logger()
router = APIRouter()
processor = DocumentProcessor(
    chunk_size=settings.CHUNK_SIZE_TOKENS,
    chunk_overlap=settings.CHUNK_OVERLAP_TOKENS,
)


@router.post("/upload", response_model=DocumentResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: Optional[UploadFile] = File(None),
    text_content: Optional[str] = Form(None),
    title: str = Form(...),
    doc_type: str = Form(default="generic"),
    jurisdiction: str = Form(default="general"),
    processing_mode: str = Form(default="cloud"),
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Upload a legal document (PDF/DOCX file or plain text paste).
    Supports up to 25MB (configurable up to 50MB).
    """
    if file is None and not text_content:
        raise HTTPException(status_code=400, detail="Either a file or text_content is required")

    # Parse document
    if file:
        contents = await file.read()
        if len(contents) > settings.max_upload_size_bytes:
            raise HTTPException(
                status_code=413,
                detail=f"File exceeds maximum upload size of {settings.MAX_UPLOAD_SIZE_MB}MB",
            )

        if file.content_type == "application/pdf" or (file.filename or "").endswith(".pdf"):
            parsed = await processor.parse_pdf(contents)
        else:
            text = contents.decode("utf-8", errors="ignore")
            parsed = await processor.parse_text(text)
        file_name = file.filename or "document.txt"
    else:
        parsed = await processor.parse_text(text_content or "")
        file_name = "pasted-text.txt"

    # Create document entity
    doc = Document(
        user_id=user.uid if user else None,
        title=title,
        file_name=file_name,
        doc_type=doc_type,
        jurisdiction=jurisdiction,
        processing_mode=processing_mode,
        status="processing",
        page_count=parsed.page_count,
        word_count=parsed.word_count,
        expires_at=datetime.now(timezone.utc) + timedelta(days=settings.DOCUMENT_TTL_DAYS),
    )
    db.add(doc)
    await db.flush()

    # Chunk text and store
    chunks = processor.chunk_text(parsed)
    for chunk in chunks:
        db_chunk = DocumentChunk(
            document_id=doc.id,
            chunk_index=chunk.index,
            text=chunk.text,
            page_num=chunk.page_num,
            char_start=chunk.char_start,
            char_end=chunk.char_end,
        )
        db.add(db_chunk)

    doc.status = "ready"
    await db.commit()
    await db.refresh(doc)

    log.info("Document uploaded & processed", doc_id=str(doc.id), chunks=len(chunks))
    return doc


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: uuid.UUID,
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Retrieve document metadata."""
    doc = await _get_owned_document(document_id, user, db)
    return doc


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: uuid.UUID,
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a document and cascade-delete all derived data (chunks, clauses, summaries, Q&A).
    Ensures complete data minimization and right-to-erasure compliance.
    """
    doc = await _get_owned_document(document_id, user, db)
    doc.deleted_at = datetime.now(timezone.utc)
    doc.status = "error"
    await db.delete(doc)
    await db.commit()
    log.info("Document and derived data purged", doc_id=str(document_id))


async def _get_owned_document(
    document_id: uuid.UUID,
    user: Optional[AuthenticatedUser],
    db: AsyncSession,
) -> Document:
    """Verify document existence and user access."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc is None or doc.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Document not found")
    if user and doc.user_id and doc.user_id != user.uid:
        raise HTTPException(status_code=403, detail="Access denied")
    return doc
