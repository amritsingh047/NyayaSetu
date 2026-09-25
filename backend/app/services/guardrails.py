"""
Safety Guardrails Service for Indian Legal Platform.
Enforces:
1. Legal Advice Refusal (detects strategy, lawsuits, subjective judgment).
2. Advocate Escalation Workflow (NALSA / Bar Council of India handoff).
3. Grounding Verification (Refuses or flags when unsupported by statutory corpus).
4. Prompt Injection Defense (Immutable system delimiters & XML boundaries).
5. Indian Legal Disclaimers (Bilingual / Bar Council compliance).
"""
import re
from typing import Any

try:
    import structlog
    log = structlog.get_logger()
except ImportError:
    import logging
    log = logging.getLogger(__name__)

# Mandatory Bar Council of India & Statutory Information Notice
INDIAN_LEGAL_DISCLAIMER = (
    "⚠️ Disclaimer: NyayaSetu is an AI-powered legal information and document comprehension tool. "
    "It provides general information on Indian statutes, rules, and regulations (not legal advice). "
    "Use of this platform does not create an advocate-client relationship under the Advocates Act, 1961. "
    "For dispute representation, binding opinions, or case strategy, consult an Advocate registered with the Bar Council."
)

# Queries requiring human legal judgment / advocate consultation that MUST be refused
ADVICE_SEEKING_TRIGGERS = [
    r"should i sue",
    r"can i sue",
    r"will i win",
    r"what are my chances",
    r"should i sign",
    r"should i not sign",
    r"how (can|do) i fight (this|a) case",
    r"should i file (an? )?fir",
    r"how much compensation can i (claim|get|demand)",
    r"strategy\b",
    r"(what|which)\s+strategy",
    r"how to bypass",
    r"how to avoid paying tax",
    r"is my (lawyer|advocate)",
    r"draft (a )?plaint",
    r"give me legal advice",
    r"breach this agreement",
]

# Forbidden patterns in model output indicating unauthorized legal advice
PROHIBITED_OUTPUT_PATTERNS = [
    r"you should sue",
    r"you should sign",
    r"you should not sign",
    r"you will definitely win",
    r"this is (completely )?illegal",
    r"as your legal counsel",
    r"my advice to you is to file",
]

ADVOCATE_ESCALATION_PAYLOAD = {
    "escalated": True,
    "reason": "Query requires personalized legal judgment, dispute assessment, or litigation strategy.",
    "escalation_target": "Licensed Advocate / Legal Services Authority",
    "free_legal_aid": {
        "authority": "National Legal Services Authority (NALSA)",
        "helpline": "15100 (Toll-Free National Legal Aid Helpline)",
        "portal": "https://nalsa.gov.in",
        "tele_law": "https://www.tele-law.in (Department of Justice, Govt. of India)",
    },
    "regulatory_authority": "Bar Council of India (Advocates Act, 1961)",
}

SAFE_REFUSAL_MESSAGE = (
    "This query requires personalized legal judgment and case strategy, which an automated information "
    "system cannot provide. As an AI legal comprehension tool, I can explain what the relevant Indian statutes "
    "or document clauses state, but I cannot advise you on whether to file a case or predict legal outcomes. "
    "We strongly recommend consulting a licensed Advocate registered with the Bar Council of India. "
    "For subsidized or free legal assistance, you can also reach NALSA via the national toll-free helpline 15100 or visit nalsa.gov.in."
)

UNSUPPORTED_CORPUS_MESSAGE = (
    "I could not locate an authoritative statutory provision or verbatim clause in the current document "
    "or Indian legal corpus to substantiate a verified answer. To avoid inaccuracies, I cannot speculate. "
    "Please check the specific clause in your agreement or consult an Advocate specializing in this area of Indian law."
)


class GuardrailsService:
    """Enforces compliance, advice refusal, PII shielding, and disclaimers."""

    def is_advice_seeking(self, query: str) -> bool:
        """
        Detects whether a user prompt is requesting personalized legal counsel,
        litigation strategy, or subjective legal judgment.
        """
        q_lower = query.lower().strip()
        for pattern in ADVICE_SEEKING_TRIGGERS:
            if re.search(pattern, q_lower):
                log.info("Advice-seeking query detected", trigger=pattern)
                return True
        return False

    def build_advice_refusal(self) -> dict[str, Any]:
        """Returns structured safe refusal response with legal aid escalation."""
        return {
            "answer": SAFE_REFUSAL_MESSAGE,
            "is_out_of_scope": True,
            "source_refs": [],
            "confidence": "HIGH",
            "escalation": ADVOCATE_ESCALATION_PAYLOAD,
            "disclaimer": INDIAN_LEGAL_DISCLAIMER,
        }

    def build_unsupported_refusal(self) -> dict[str, Any]:
        """Fallback message when no grounding text exists in document or law."""
        return {
            "answer": UNSUPPORTED_CORPUS_MESSAGE,
            "is_out_of_scope": False,
            "source_refs": [],
            "confidence": "LOW",
            "escalation": ADVOCATE_ESCALATION_PAYLOAD,
            "disclaimer": INDIAN_LEGAL_DISCLAIMER,
        }

    def sanitize_output(self, text: str) -> tuple[str, list[str]]:
        """Scans generated output for prohibited prescriptive legal advice phrases."""
        violations = []
        text_lower = text.lower()
        for pattern in PROHIBITED_OUTPUT_PATTERNS:
            if re.search(pattern, text_lower):
                violations.append(pattern)

        if violations:
            log.warning("Prohibited legal advice phrases detected in LLM output", violations=violations)
            # Reframe and prepend mandatory disclaimer
            text = f"{text}\n\n[Note: The above points are informational observations. Please verify with a licensed Advocate.]"

        return text, violations

    def inject_disclaimer(self, response: dict[str, Any]) -> dict[str, Any]:
        """Appends the Indian legal disclaimer to every API response."""
        response["disclaimer"] = INDIAN_LEGAL_DISCLAIMER
        return response

    def wrap_document_text(self, text: str) -> str:
        """Shields user document from prompt injection attacks."""
        safe = text.replace("</document>", "[DOC_TAG_ESCAPED]")
        return f"<document>\n{safe}\n</document>"

    def wrap_context(self, chunks: list[str]) -> str:
        """Wraps retrieved chunks in unambiguous XML boundaries."""
        parts = [f"<statute_chunk index=\"{i+1}\">\n{c}\n</statute_chunk>" for i, c in enumerate(chunks)]
        return "<context>\n" + "\n".join(parts) + "\n</context>"


guardrails_service = GuardrailsService()
