"""Pydantic schemas for document-related API endpoints."""
from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


# ---- Request Schemas ----

class DocumentCreateRequest(BaseModel):
    title: str = Field(..., max_length=500)
    doc_type: str = Field(default="generic")
    jurisdiction: str = Field(default="general", max_length=100)
    processing_mode: str = Field(default="cloud")  # "cloud" | "local"


class SummaryRequest(BaseModel):
    document_id: UUID
    reading_level: str = Field(default="standard")  # simple | standard | detailed


class QnARequest(BaseModel):
    document_id: UUID
    question: str = Field(..., min_length=3, max_length=2000)


class ChecklistRequest(BaseModel):
    document_id: UUID


class ComparisonRequest(BaseModel):
    doc_a_id: UUID
    doc_b_id: UUID


# ---- Response Schemas ----

class KeyPoint(BaseModel):
    point: str
    source_excerpt: str
    confidence: float


class SummaryResponse(BaseModel):
    id: UUID
    document_id: UUID
    overview: str
    key_points: list[KeyPoint]
    document_type_detected: str
    notable_concerns: list[str]
    reading_level_applied: str
    confidence: float
    disclaimer: str = "⚠️ This is informational only and does not constitute legal advice. Consult a licensed attorney for binding guidance."
    generated_at: datetime


class ClauseResponse(BaseModel):
    id: UUID
    document_id: UUID
    page_num: Optional[int]
    position_start: Optional[int]
    position_end: Optional[int]
    text: str
    clause_type: str
    risk_level: str
    explanation: Optional[str]
    confidence: Optional[float]
    source_excerpt: Optional[str]
    party_affected: Optional[str]
    key_obligations: Optional[list[str]]


class ChecklistItem(BaseModel):
    item: str
    date_mentioned: Optional[str] = None
    party: Optional[str] = None
    severity: Optional[str] = None
    source_excerpt: str


class ChecklistResponse(BaseModel):
    document_id: UUID
    deadlines: list[ChecklistItem]
    required_actions: list[ChecklistItem]
    optional_decisions: list[ChecklistItem]
    red_flags: list[ChecklistItem]
    disclaimer: str = "⚠️ This checklist is informational only and does not constitute legal advice."
    generated_at: datetime


class QnAResponse(BaseModel):
    id: UUID
    document_id: UUID
    question: str
    answer: str
    source_excerpts: list[str]
    confidence: float
    is_out_of_scope: bool
    disclaimer: str = "⚠️ This answer is informational only and does not constitute legal advice."
    generated_at: datetime


class DocumentResponse(BaseModel):
    id: UUID
    user_id: Optional[str]
    title: str
    file_name: str
    doc_type: str
    jurisdiction: str
    status: str
    page_count: Optional[int]
    word_count: Optional[int]
    processing_mode: str
    uploaded_at: datetime
    expires_at: Optional[datetime]

    class Config:
        from_attributes = True


class ComparisonDiff(BaseModel):
    clause_type: str
    change_description: str
    doc_a_text: str
    doc_b_text: str


class ComparisonResponse(BaseModel):
    id: UUID
    doc_a_id: UUID
    doc_b_id: UUID
    added_clauses: list[str]
    removed_clauses: list[str]
    modified_clauses: list[ComparisonDiff]
    risk_delta: str
    summary: str
    disclaimer: str = "⚠️ This comparison is informational only and does not constitute legal advice."
    generated_at: datetime
