"""Analysis endpoints for NyayaSetu: summary, clause extraction, contextual Q&A, statutory corpus, checklist, and comparison."""
import uuid
from datetime import datetime, timezone
from typing import Optional

import structlog
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.core.database import get_db
from app.core.security import AuthenticatedUser, get_current_user
from app.models.document import Clause, Document, DocumentChunk, QnA, Summary
from app.schemas.document import (
    ChecklistRequest,
    ChecklistResponse,
    ClauseResponse,
    ComparisonRequest,
    ComparisonResponse,
    QnARequest,
    QnAResponse,
    SummaryRequest,
    SummaryResponse,
)
from app.services.llm_orchestrator import LLMOrchestrator
from app.services.indian_legal_corpus import indian_legal_service

log = structlog.get_logger()
router = APIRouter()


async def _get_document_text(document_id: uuid.UUID, db: AsyncSession) -> tuple[Document, str]:
    """Load a document and assemble its text from chunks."""
    result = await db.execute(select(Document).where(Document.id == document_id))
    doc = result.scalar_one_or_none()
    if doc is None or doc.deleted_at is not None:
        raise HTTPException(status_code=404, detail="Document not found")
    if doc.status != "ready":
        raise HTTPException(status_code=409, detail=f"Document is not ready (status: {doc.status})")

    chunks_result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == document_id)
        .order_by(DocumentChunk.chunk_index)
    )
    chunks = chunks_result.scalars().all()
    full_text = " ".join(c.text for c in chunks)
    return doc, full_text


@router.get("/statutes")
async def search_statutes(
    q: str = Query(..., min_length=2, description="Statutory query or keyword e.g. 'GST ITC', 'Section 27 non compete', 'FSSAI license'"),
    domain: Optional[str] = Query("all", description="tax_gst, dpdp_privacy, food_safety, textiles, contract, consumer, constitution"),
    top_k: int = Query(3, ge=1, le=10),
):
    """
    Search official Indian statutory and regulatory corpus.
    Provides verifiable citations, official source URLs, and plain-English summaries.
    """
    results = indian_legal_service.search(query=q, domain=domain, top_k=top_k)
    return {
        "query": q,
        "domain": domain,
        "total_matches": len(results),
        "results": results,
        "disclaimer": "Statutory references are for general informational purposes only under Indian law.",
    }


@router.post("/summary", response_model=SummaryResponse)
async def generate_summary(
    request: SummaryRequest,
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Generate a plain-language summary (brief or detailed) of an Indian legal document."""
    doc, full_text = await _get_document_text(request.document_id, db)

    llm = LLMOrchestrator(processing_mode=doc.processing_mode)
    result = await llm.summarize(
        document_text=full_text,
        doc_type=doc.doc_type,
        jurisdiction=doc.jurisdiction,
        reading_level=request.reading_level,
    )

    summary = Summary(
        document_id=doc.id,
        summary_type="plain_language",
        content=result,
        confidence=0.9 if result.get("overall_confidence") == "HIGH" else 0.75,
        model_version=settings.VERTEX_AI_LLM_MODEL,
        reading_level=request.reading_level,
    )
    db.add(summary)
    await db.commit()
    await db.refresh(summary)

    key_points = []
    for sec in result.get("sections", []):
        key_points.append({
            "point": f"{sec.get('heading', '')}: {sec.get('summary', '')}",
            "source_excerpt": sec.get("source_ref", ""),
            "confidence": 0.95 if sec.get("confidence") == "HIGH" else 0.80,
        })

    return SummaryResponse(
        id=summary.id,
        document_id=doc.id,
        overview=result.get("purpose", result.get("overview", "")),
        key_points=key_points or result.get("key_points", []),
        document_type_detected=result.get("document_type_detected", doc.doc_type),
        notable_concerns=[r.get("description", str(r)) for r in result.get("risks", [])],
        reading_level_applied=request.reading_level,
        confidence=summary.confidence or 0.85,
        generated_at=summary.generated_at,
    )


@router.post("/qa", response_model=QnAResponse)
async def answer_question(
    request: QnARequest,
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Answer a question grounded in the uploaded document and Indian statutory knowledge base.
    Actively refuses personalized legal advice queries and triggers Advocate / NALSA escalation.
    """
    doc, _ = await _get_document_text(request.document_id, db)

    chunks_result = await db.execute(
        select(DocumentChunk)
        .where(DocumentChunk.document_id == request.document_id)
        .order_by(DocumentChunk.chunk_index)
        .limit(settings.TOP_K_CHUNKS)
    )
    chunks = [c.text for c in chunks_result.scalars().all()]

    llm = LLMOrchestrator(processing_mode=doc.processing_mode)
    result = await llm.answer_question(request.question, retrieved_chunks=chunks)

    conf_map = {"HIGH": 0.95, "MEDIUM": 0.75, "LOW": 0.5}
    raw_conf = result.get("confidence", "MEDIUM")
    confidence_val = conf_map.get(raw_conf, 0.75) if isinstance(raw_conf, str) else float(raw_conf)

    qna = QnA(
        document_id=doc.id,
        question=request.question,
        answer=result.get("answer", ""),
        source_excerpts={"excerpts": result.get("source_refs", [])},
        confidence=confidence_val,
        is_out_of_scope=result.get("is_out_of_scope", False),
    )
    db.add(qna)
    await db.commit()
    await db.refresh(qna)

    sources = [
        s.get("excerpt", str(s)) if isinstance(s, dict) else str(s)
        for s in (result.get("source_refs") or result.get("source_excerpts") or [])
    ]

    return QnAResponse(
        id=qna.id,
        document_id=doc.id,
        question=request.question,
        answer=result.get("answer", ""),
        source_excerpts=sources,
        confidence=confidence_val,
        is_out_of_scope=result.get("is_out_of_scope", False),
        generated_at=qna.generated_at,
    )


@router.post("/checklist", response_model=ChecklistResponse)
async def generate_checklist(
    request: ChecklistRequest,
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Extract action items, statutory compliance tasks, and 'Tasks before consulting an Advocate'."""
    doc, full_text = await _get_document_text(request.document_id, db)

    llm = LLMOrchestrator(processing_mode=doc.processing_mode)
    result = await llm.generate_checklist(document_text=full_text)

    return ChecklistResponse(
        document_id=doc.id,
        deadlines=result.get("deadlines", []),
        required_actions=result.get("required_actions", []),
        optional_decisions=result.get("optional_decisions", []),
        red_flags=result.get("red_flags", []),
        generated_at=datetime.now(timezone.utc),
    )


@router.get("/clauses/{document_id}", response_model=list[ClauseResponse])
async def get_clauses(
    document_id: uuid.UUID,
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get all extracted and categorized clauses for a document with risk classifications."""
    result = await db.execute(select(Clause).where(Clause.document_id == document_id))
    clauses = result.scalars().all()

    if not clauses:
        doc, full_text = await _get_document_text(document_id, db)
        chunks_result = await db.execute(
            select(DocumentChunk)
            .where(DocumentChunk.document_id == document_id)
            .order_by(DocumentChunk.chunk_index)
            .limit(10)
        )
        chunks = chunks_result.scalars().all()
        created = []
        for i, c in enumerate(chunks[:6]):
            clause_type = "obligation"
            risk_level = "low"
            explanation = "Standard contract provision."

            c_lower = c.text.lower()
            if "indemn" in c_lower:
                clause_type = "risk"
                risk_level = "high"
                explanation = "Indemnity clause: shifts financial responsibility to cover losses. Confirm liability cap."
            elif "non-compete" in c_lower or "restrain" in c_lower:
                clause_type = "risk"
                risk_level = "high"
                explanation = "Non-compete clause: Section 27 of Indian Contract Act 1872 renders restraints of trade void."
            elif "terminat" in c_lower:
                clause_type = "condition"
                risk_level = "medium"
                explanation = "Termination clause: specifies notice duration and exit conditions."
            elif "arbitrat" in c_lower or "dispute" in c_lower:
                clause_type = "right"
                risk_level = "low"
                explanation = "Dispute resolution: specifies arbitration under Arbitration & Conciliation Act 1996."

            clause = Clause(
                document_id=doc.id,
                page_num=c.page_num or 1,
                position_start=c.char_start,
                position_end=c.char_end,
                text=c.text[:400] + ("..." if len(c.text) > 400 else ""),
                clause_type=clause_type,
                risk_level=risk_level,
                explanation=explanation,
                confidence=0.90,
                source_excerpt=c.text[:120],
                party_affected="Executing Party",
                key_obligations={"items": ["Adhere to specified operational covenants"]},
            )
            db.add(clause)
            created.append(clause)
        await db.commit()
        clauses = created

    return [
        ClauseResponse(
            id=c.id,
            document_id=c.document_id,
            page_num=c.page_num,
            position_start=c.position_start,
            position_end=c.position_end,
            text=c.text,
            clause_type=c.clause_type,
            risk_level=c.risk_level,
            explanation=c.explanation,
            confidence=c.confidence,
            source_excerpt=c.source_excerpt,
            party_affected=c.party_affected,
            key_obligations=c.key_obligations.get("items") if c.key_obligations else None,
        )
        for c in clauses
    ]


@router.post("/compare", response_model=ComparisonResponse)
async def compare_documents(
    request: ComparisonRequest,
    user: Optional[AuthenticatedUser] = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Side-by-side contract comparison and deviation analysis."""
    doc_a, text_a = await _get_document_text(request.doc_a_id, db)
    doc_b, text_b = await _get_document_text(request.doc_b_id, db)

    llm = LLMOrchestrator(processing_mode=doc_a.processing_mode)
    result = await llm.compare_documents(
        doc_a_text=text_a,
        doc_b_text=text_b,
        doc_a_label=doc_a.title,
        doc_b_label=doc_b.title,
    )

    diffs = [
        {
            "clause_type": d.get("section", "Clause"),
            "change_description": f"[{d.get('type', 'change').upper()}] {d.get('summary', '')} (Impact: {d.get('impact', '')})",
            "doc_a_text": f"Version A: {d.get('summary', '')}",
            "doc_b_text": f"Version B (Risk: {d.get('risk_delta', 'neutral')})",
        }
        for d in result.get("differences", [])
    ]

    return ComparisonResponse(
        id=uuid.uuid4(),
        doc_a_id=request.doc_a_id,
        doc_b_id=request.doc_b_id,
        added_clauses=[d["summary"] for d in result.get("differences", []) if d.get("type") == "added"],
        removed_clauses=[d["summary"] for d in result.get("differences", []) if d.get("type") == "removed"],
        modified_clauses=diffs,
        risk_delta="Review Required",
        summary=result.get("overall_summary", "Comparison completed successfully."),
        generated_at=datetime.now(timezone.utc),
    )
