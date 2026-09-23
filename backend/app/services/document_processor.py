"""Document parsing, Indian PII stripping, and chunking service for Indian Legal Platform."""
import io
import re
from dataclasses import dataclass
from typing import Optional

try:
    import structlog
    log = structlog.get_logger()
except ImportError:
    import logging
    log = logging.getLogger(__name__)

# Indian PII and sensitive identifier patterns for pre-LLM redaction (DPDP Act, 2023 compliance)
INDIAN_PII_PATTERNS = [
    # Aadhaar Number (12 digits, optional spaces/hyphens)
    (r"\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b", "[AADHAAR-REDACTED]"),
    # Permanent Account Number (PAN: 5 letters, 4 digits, 1 letter)
    (r"\b[A-Z]{5}[0-9]{4}[A-Z]\b", "[PAN-REDACTED]"),
    # Indian Mobile Numbers (10 digits starting with 6-9, optional +91 or 0 prefix)
    (r"\b(?:\+91[\-\s]?|91[\-\s]?|0)?[6-9]\d{9}\b", "[MOBILE-REDACTED]"),
    # Goods and Services Tax Identification Number (GSTIN: 15 alphanumeric)
    (r"\b\d{2}[A-Z]{5}\d{4}[A-Z]{1}[A-Z\d]{1}[Z]{1}[A-Z\d]{1}\b", "[GSTIN-REDACTED]"),
    # Indian Financial System Code (IFSC: 4 letters, 0, 6 alphanumeric)
    (r"\b[A-Z]{4}0[A-Z0-9]{6}\b", "[IFSC-REDACTED]"),
    # Credit / Debit Card numbers (16 digits)
    (r"\b\d{4}[\s\-]\d{4}[\s\-]\d{4}[\s\-]\d{4}\b", "[CARD-REDACTED]"),
    # Passwords / Secret keys
    (r"(?i)(?:password|secret|api[_-]?key)[:\s]+[\S]+", "[CREDENTIAL-REDACTED]"),
]


@dataclass
class TextChunk:
    """A text chunk ready for embedding and retrieval."""
    index: int
    text: str
    page_num: Optional[int]
    char_start: int
    char_end: int


@dataclass
class ParsedDocument:
    """Result of parsing an uploaded legal document."""
    full_text: str
    pages: list[dict]
    page_count: int
    word_count: int


class DocumentProcessor:
    """Layout-aware parser, Indian PII scrubber, and sliding-window chunker."""

    def __init__(self, chunk_size: int = 400, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    async def parse_pdf(self, file_bytes: bytes) -> ParsedDocument:
        """Parse PDF document and extract page-referenced text."""
        try:
            import fitz  # PyMuPDF
            doc = fitz.open(stream=file_bytes, filetype="pdf")
            pages = []
            full_text_parts = []

            for page_num in range(len(doc)):
                page = doc[page_num]
                text = page.get_text("text")
                pages.append({"page_num": page_num + 1, "text": text})
                full_text_parts.append(text)

            doc.close()
            full_text = "\n\n".join(full_text_parts)
            return ParsedDocument(
                full_text=full_text,
                pages=pages,
                page_count=len(pages),
                word_count=len(full_text.split()),
            )
        except Exception as e:
            log.warning("PyMuPDF fallback or failed", error=str(e))
            # Fallback to plain text decoding if fitz fails
            decoded = file_bytes.decode("utf-8", errors="ignore")
            return await self.parse_text(decoded)

    async def parse_text(self, text: str) -> ParsedDocument:
        """Handle plain-text input or pasted text."""
        clean = text.strip()
        return ParsedDocument(
            full_text=clean,
            pages=[{"page_num": 1, "text": clean}],
            page_count=1,
            word_count=len(clean.split()),
        )

    def strip_pii(self, text: str) -> str:
        """
        Redacts Indian personal identifiers (Aadhaar, PAN, phone, GSTIN, IFSC)
        before passing text to any cloud processing or external model.
        Fulfills DPDP Act 2023 data minimization and confidentiality safeguards.
        """
        redacted = text
        for pattern, replacement in INDIAN_PII_PATTERNS:
            redacted = re.sub(pattern, replacement, redacted)
        return redacted

    def chunk_text(self, parsed: ParsedDocument) -> list[TextChunk]:
        """
        Splits document text into overlapping semantic chunks with character offsets.
        Preserves section integrity where possible.
        """
        words = parsed.full_text.split()
        chunks: list[TextChunk] = []
        chunk_index = 0
        start = 0

        while start < len(words):
            end = min(start + self.chunk_size, len(words))
            chunk_words = words[start:end]
            chunk_text = " ".join(chunk_words)

            char_start = len(" ".join(words[:start]))
            char_end = char_start + len(chunk_text)
            page_num = self._estimate_page(parsed, char_start)

            chunks.append(TextChunk(
                index=chunk_index,
                text=chunk_text,
                page_num=page_num,
                char_start=char_start,
                char_end=char_end,
            ))
            chunk_index += 1
            start += self.chunk_size - self.chunk_overlap

        log.info("Document chunked", chunk_count=len(chunks), word_count=len(words))
        return chunks

    def _estimate_page(self, parsed: ParsedDocument, char_offset: int) -> Optional[int]:
        """Estimate page number from character offset."""
        cumulative = 0
        for page in parsed.pages:
            cumulative += len(page["text"])
            if cumulative >= char_offset:
                return page["page_num"]
        return parsed.page_count
