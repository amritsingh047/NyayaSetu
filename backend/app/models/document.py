"""SQLAlchemy ORM models for the LexAI data model."""
import uuid
from datetime import datetime, timezone
from typing import Optional

from pgvector.sqlalchemy import Vector
from sqlalchemy import (
    ARRAY,
    Boolean,
    DateTime,
    Enum,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.database import Base


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Document(Base):
    """Represents an uploaded legal document."""
    __tablename__ = "documents"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True, index=True)
    title: Mapped[str] = mapped_column(String(500))
    file_name: Mapped[str] = mapped_column(String(500))
    storage_uri: Mapped[Optional[str]] = mapped_column(String(2000), nullable=True)
    doc_type: Mapped[str] = mapped_column(
        Enum("lease", "nda", "employment", "tos", "privacy_policy", "generic", name="doc_type_enum"),
        default="generic",
    )
    jurisdiction: Mapped[str] = mapped_column(String(100), default="general")
    status: Mapped[str] = mapped_column(
        Enum("uploading", "processing", "ready", "error", name="doc_status_enum"),
        default="uploading",
    )
    page_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    processing_mode: Mapped[str] = mapped_column(
        Enum("cloud", "local", name="processing_mode_enum"), default="cloud"
    )
    uploaded_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)
    expires_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)
    deleted_at: Mapped[Optional[datetime]] = mapped_column(DateTime(timezone=True), nullable=True)

    # Relationships
    clauses: Mapped[list["Clause"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    summaries: Mapped[list["Summary"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    qnas: Mapped[list["QnA"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    glossary_terms: Mapped[list["GlossaryTerm"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    tags: Mapped[list["Tag"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    chunks: Mapped[list["DocumentChunk"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class DocumentChunk(Base):
    """A semantic chunk of a document with its embedding for RAG."""
    __tablename__ = "document_chunks"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    chunk_index: Mapped[int] = mapped_column(Integer)
    text: Mapped[str] = mapped_column(Text)
    page_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    char_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    # 768-dim embedding for text-embedding-004
    embedding: Mapped[Optional[list[float]]] = mapped_column(Vector(768), nullable=True)

    document: Mapped["Document"] = relationship(back_populates="chunks")

    __table_args__ = (UniqueConstraint("document_id", "chunk_index"),)


class Clause(Base):
    """A specific clause extracted and analyzed from a document."""
    __tablename__ = "clauses"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    page_num: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position_start: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    position_end: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    text: Mapped[str] = mapped_column(Text)
    clause_type: Mapped[str] = mapped_column(
        Enum(
            "obligation", "risk", "termination", "payment", "liability",
            "confidentiality", "definition", "boilerplate", "other",
            name="clause_type_enum",
        ),
        default="other",
    )
    risk_level: Mapped[str] = mapped_column(
        Enum("low", "medium", "high", name="risk_level_enum"), default="low"
    )
    explanation: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    source_excerpt: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    party_affected: Mapped[Optional[str]] = mapped_column(String(200), nullable=True)
    key_obligations: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="clauses")
    tags: Mapped[list["Tag"]] = relationship(back_populates="clause")


class Summary(Base):
    """An LLM-generated summary of a document."""
    __tablename__ = "summaries"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    summary_type: Mapped[str] = mapped_column(
        Enum("plain_language", "key_points", "action_items", "checklist", name="summary_type_enum")
    )
    content: Mapped[dict] = mapped_column(JSONB)  # Structured output
    word_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    model_version: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    reading_level: Mapped[str] = mapped_column(String(20), default="standard")
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    document: Mapped["Document"] = relationship(back_populates="summaries")


class QnA(Base):
    """A question-answer pair grounded in a document."""
    __tablename__ = "qnas"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    question: Mapped[str] = mapped_column(Text)
    answer: Mapped[str] = mapped_column(Text)
    source_excerpts: Mapped[Optional[dict]] = mapped_column(JSONB, nullable=True)
    confidence: Mapped[Optional[float]] = mapped_column(Float, nullable=True)
    is_out_of_scope: Mapped[bool] = mapped_column(Boolean, default=False)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)

    document: Mapped["Document"] = relationship(back_populates="qnas")


class GlossaryTerm(Base):
    """A legal term extracted and defined from a document."""
    __tablename__ = "glossary_terms"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    term: Mapped[str] = mapped_column(String(500))
    definition: Mapped[str] = mapped_column(Text)
    legal_context: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    document: Mapped["Document"] = relationship(back_populates="glossary_terms")


class Comparison(Base):
    """A clause-level diff comparison between two documents."""
    __tablename__ = "comparisons"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    doc_a_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    doc_b_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    diff_json: Mapped[dict] = mapped_column(JSONB)
    summary: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=utcnow)


class Tag(Base):
    """A label/category tag applied to a clause."""
    __tablename__ = "tags"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id", ondelete="CASCADE"))
    clause_id: Mapped[Optional[uuid.UUID]] = mapped_column(UUID(as_uuid=True), ForeignKey("clauses.id", ondelete="SET NULL"), nullable=True)
    label: Mapped[str] = mapped_column(String(200))
    category: Mapped[str] = mapped_column(
        Enum("risk", "obligation", "definition", "penalty", "other", name="tag_category_enum")
    )

    document: Mapped["Document"] = relationship(back_populates="tags")
    clause: Mapped[Optional["Clause"]] = relationship(back_populates="tags")
