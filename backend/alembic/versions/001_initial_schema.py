"""Initial schema: documents, clauses, summaries, qnas, glossary, comparisons, tags, chunks.

Revision ID: 001
Revises:
Create Date: 2026-09-24
"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Enums
    doc_type_enum = sa.Enum(
        "lease", "nda", "employment", "tos", "privacy_policy", "generic",
        name="doc_type_enum",
    )
    doc_status_enum = sa.Enum("uploading", "processing", "ready", "error", name="doc_status_enum")
    processing_mode_enum = sa.Enum("cloud", "local", name="processing_mode_enum")
    clause_type_enum = sa.Enum(
        "obligation", "risk", "termination", "payment", "liability",
        "confidentiality", "definition", "boilerplate", "other",
        name="clause_type_enum",
    )
    risk_level_enum = sa.Enum("low", "medium", "high", name="risk_level_enum")
    summary_type_enum = sa.Enum(
        "plain_language", "key_points", "action_items", "checklist",
        name="summary_type_enum",
    )
    tag_category_enum = sa.Enum(
        "risk", "obligation", "definition", "penalty", "other",
        name="tag_category_enum",
    )

    # documents
    op.create_table(
        "documents",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=True, index=True),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("file_name", sa.String(500), nullable=False),
        sa.Column("storage_uri", sa.String(2000), nullable=True),
        sa.Column("doc_type", doc_type_enum, nullable=False, server_default="generic"),
        sa.Column("jurisdiction", sa.String(100), nullable=False, server_default="general"),
        sa.Column("status", doc_status_enum, nullable=False, server_default="uploading"),
        sa.Column("page_count", sa.Integer, nullable=True),
        sa.Column("word_count", sa.Integer, nullable=True),
        sa.Column("processing_mode", processing_mode_enum, nullable=False, server_default="cloud"),
        sa.Column("uploaded_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # document_chunks
    op.create_table(
        "document_chunks",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("page_num", sa.Integer, nullable=True),
        sa.Column("char_start", sa.Integer, nullable=True),
        sa.Column("char_end", sa.Integer, nullable=True),
        sa.Column("embedding", Vector(768), nullable=True),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_chunk_doc_idx"),
    )
    op.create_index("ix_chunks_document_id", "document_chunks", ["document_id"])

    # clauses
    op.create_table(
        "clauses",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("page_num", sa.Integer, nullable=True),
        sa.Column("position_start", sa.Integer, nullable=True),
        sa.Column("position_end", sa.Integer, nullable=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("clause_type", clause_type_enum, nullable=False, server_default="other"),
        sa.Column("risk_level", risk_level_enum, nullable=False, server_default="low"),
        sa.Column("explanation", sa.Text, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("source_excerpt", sa.Text, nullable=True),
        sa.Column("party_affected", sa.String(200), nullable=True),
        sa.Column("key_obligations", sa.dialects.postgresql.JSONB, nullable=True),
    )
    op.create_index("ix_clauses_document_id", "clauses", ["document_id"])

    # summaries
    op.create_table(
        "summaries",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("summary_type", summary_type_enum, nullable=False),
        sa.Column("content", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column("word_count", sa.Integer, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("model_version", sa.String(100), nullable=True),
        sa.Column("reading_level", sa.String(20), nullable=False, server_default="standard"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # qnas
    op.create_table(
        "qnas",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("question", sa.Text, nullable=False),
        sa.Column("answer", sa.Text, nullable=False),
        sa.Column("source_excerpts", sa.dialects.postgresql.JSONB, nullable=True),
        sa.Column("confidence", sa.Float, nullable=True),
        sa.Column("is_out_of_scope", sa.Boolean, nullable=False, server_default="false"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # glossary_terms
    op.create_table(
        "glossary_terms",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("term", sa.String(500), nullable=False),
        sa.Column("definition", sa.Text, nullable=False),
        sa.Column("legal_context", sa.Text, nullable=True),
    )

    # comparisons
    op.create_table(
        "comparisons",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("user_id", sa.String(128), nullable=True),
        sa.Column("doc_a_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("doc_b_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("diff_json", sa.dialects.postgresql.JSONB, nullable=False),
        sa.Column("summary", sa.Text, nullable=True),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=False),
    )

    # tags
    op.create_table(
        "tags",
        sa.Column("id", sa.UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", sa.UUID(as_uuid=True), sa.ForeignKey("documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("clause_id", sa.UUID(as_uuid=True), sa.ForeignKey("clauses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("label", sa.String(200), nullable=False),
        sa.Column("category", tag_category_enum, nullable=False),
    )


def downgrade() -> None:
    op.drop_table("tags")
    op.drop_table("comparisons")
    op.drop_table("glossary_terms")
    op.drop_table("qnas")
    op.drop_table("summaries")
    op.drop_table("clauses")
    op.drop_table("document_chunks")
    op.drop_table("documents")

    for enum_name in [
        "doc_type_enum", "doc_status_enum", "processing_mode_enum",
        "clause_type_enum", "risk_level_enum", "summary_type_enum", "tag_category_enum",
    ]:
        sa.Enum(name=enum_name).drop(op.get_bind(), checkfirst=True)
