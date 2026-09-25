"""
LLM prompt templates for NyayaSetu.
Enforces: strict grounding, plain language, legal advice refusal, HIGH/MEDIUM/LOW confidence,
and verifiable section/clause citations.
"""

# ============================================================
# SYSTEM PROMPT (All Calls)
# ============================================================

SYSTEM_PROMPT = """You are NyayaSetu (न्याय सेतु), an AI assistant that helps people understand legal documents.
You provide information and explanations — you do NOT provide legal advice.

CRITICAL RULES:
1. Always base your analysis on the specific document provided.
   Never fabricate clauses or terms not present in the document.
2. If the document does not address a question, say so clearly.
3. Never state that something is "legally binding" or make definitive legal judgments.
   Use phrases like "this clause appears to," "based on the document's language," and
   "a licensed attorney could confirm whether."
4. When you identify risks or obligations, flag them clearly but frame them as observations,
   not legal conclusions.
5. If asked for jurisdiction-specific legal advice, decline and recommend consulting a local attorney.
6. Assign a confidence level to every output:
   - HIGH: clear, unambiguous language in the document
   - MEDIUM: reasonable interpretation but some ambiguity
   - LOW: significant ambiguity or missing context
7. Always cite the specific section, clause, or line numbers that support your analysis.
8. Respond in valid JSON matching the requested structure."""


# ============================================================
# SUMMARY PROMPTS
# ============================================================

def summary_user(document_text: str, doc_type: str = "generic", summary_type: str = "brief") -> str:
    """Prompt for generating brief or detailed document summary."""
    instructions = (
        """Provide a concise summary (3–5 sentences) covering:
- Who are the parties and what is the document's purpose?
- What are the most important obligations and conditions?
- What is the term/duration?
- Are there any notable risks or unusual provisions?"""
        if summary_type == "brief"
        else """Provide a section-by-section breakdown covering:
- Parties and purpose
- Each major section's obligations, rights, and conditions
- Key dates, deadlines, and financial terms
- Termination conditions
- Notable risks or unusual provisions
- Any missing standard provisions that users should be aware of"""
    )

    return f"""Analyze the following legal document and produce a plain-language summary.

DOCUMENT TYPE: {doc_type}
SUMMARY DEPTH: {summary_type}

DOCUMENT TEXT:
---
{document_text}
---

{instructions}

Respond in this JSON structure:
{{
  "parties": [{{"name": "string", "role": "string"}}],
  "purpose": "string",
  "sections": [
    {{
      "heading": "string",
      "summary": "string",
      "source_ref": "string",
      "confidence": "HIGH|MEDIUM|LOW"
    }}
  ],
  "key_dates": [{{"description": "string", "date_or_trigger": "string"}}],
  "risks": [{{"description": "string", "severity": "HIGH|MEDIUM|LOW", "source_ref": "string"}}],
  "overall_confidence": "HIGH|MEDIUM|LOW",
  "missing_provisions": ["string"]
}}"""


# ============================================================
# CLAUSE ANALYSIS
# ============================================================

def clause_user(clause_text: str, doc_type: str = "generic", surrounding_context: str = "") -> str:
    """Prompt for analyzing a specific clause."""
    return f"""Analyze the following clause extracted from a {doc_type}.

CLAUSE TEXT:
---
{clause_text}
---

SURROUNDING CONTEXT:
---
{surrounding_context}
---

Provide:
1. clause_type: one of [obligation, right, condition, definition, risk, boilerplate]
2. plain_language: a clear, jargon-free explanation of what this clause means for someone who is not a lawyer
3. risk_level: LOW / MEDIUM / HIGH with a one-sentence justification
4. obligations: who owes what to whom, and any deadlines or triggers
5. options: practical observations about what the reader might want to discuss with an attorney (e.g., negotiation points)
6. legal_terms: any legal terminology used, with plain definitions

Respond in JSON format:
{{
  "clause_type": "obligation|right|condition|definition|risk|boilerplate",
  "plain_language": "string",
  "risk_level": "LOW|MEDIUM|HIGH",
  "risk_justification": "string",
  "obligations": [{{"who": "string", "what": "string", "to_whom": "string", "deadline_or_trigger": "string"}}],
  "options": ["string"],
  "legal_terms": [{{"term": "string", "plain_definition": "string"}}],
  "confidence": "HIGH|MEDIUM|LOW",
  "source_excerpt": "string"
}}"""


# ============================================================
# CONTEXTUAL Q&A
# ============================================================

def qa_user(question: str, chunks: list[dict], doc_type: str = "generic", history: list[dict] = None) -> str:
    """Prompt for answering grounded questions with conversation history and citations."""
    history_str = ""
    if history:
        for turn in history:
            history_str += f"  Q: {turn.get('question', '')}\n  A: {turn.get('answer', '')}\n"

    chunks_str = ""
    for c in chunks:
        chunks_str += f"[Section: {c.get('section_ref', 'Doc Excerpt')} | Relevance: {c.get('score', 1.0)}]\n{c.get('text', '')}\n\n"

    return f"""Answer the user's question based ONLY on the provided document excerpts.

DOCUMENT TYPE: {doc_type}
USER QUESTION: {question}

CONVERSATION HISTORY:
{history_str if history_str else "None"}

RELEVANT DOCUMENT EXCERPTS (ranked by relevance):
{chunks_str}

INSTRUCTIONS:
- Answer based solely on the excerpts above.
- If the excerpts do not contain enough information to answer, say "I couldn't find a clear answer to this in the document" and suggest which sections the user might want to review.
- If the question asks for jurisdiction-specific legal advice, respond: "This question goes beyond document comprehension into legal advice territory. I'd recommend discussing this with a licensed attorney in your jurisdiction."
- Cite specific sections for every claim.
- Rate your confidence: HIGH, MEDIUM, or LOW.

Respond in JSON:
{{
  "answer": "string",
  "source_refs": [{{"section": "string", "excerpt": "string", "relevance": 0.95}}],
  "confidence": "HIGH|MEDIUM|LOW",
  "guardrail_triggered": false,
  "follow_up_suggestions": ["string"]
}}"""


# ============================================================
# ACTION ITEMS & CHECKLIST
# ============================================================

def action_items_user(document_text: str, user_role: str = "Signer / Recipient") -> str:
    """Prompt for extracting actionable obligations, deadlines, and conditions."""
    return f"""Extract all actionable items, obligations, deadlines, and conditions from the following document that the reader ({user_role}) needs to be aware of.

DOCUMENT TEXT:
---
{document_text}
---

For each action item, provide:
- description: what needs to be done, in plain language
- who: which party is responsible
- deadline: specific date, relative timeframe, or triggering event
- priority: HIGH (financial/legal consequence for missing), MEDIUM (important but flexible), LOW (administrative/routine)
- source_ref: the clause or section number
- category: one of [financial, notice, compliance, deliverable, reporting, renewal, termination]

Respond as a JSON array sorted by priority (HIGH first):
[
  {{
    "description": "string",
    "who": "string",
    "deadline": "string",
    "priority": "HIGH|MEDIUM|LOW",
    "source_ref": "string",
    "category": "financial|notice|compliance|deliverable|reporting|renewal|termination"
  }}
]"""


# ============================================================
# CONTRACT COMPARISON (Phase 2)
# ============================================================

def comparison_user(doc_a_text: str, doc_b_text: str, label_a: str = "Document A", label_b: str = "Document B", doc_type: str = "contract") -> str:
    """Prompt for side-by-side contract comparison."""
    return f"""Compare these two versions of a {doc_type} and identify all meaningful differences.

DOCUMENT A ({label_a}):
---
{doc_a_text}
---

DOCUMENT B ({label_b}):
---
{doc_b_text}
---

For each difference:
- section: which section/clause changed
- type: added | removed | modified | moved
- summary: plain-language description of the change
- impact: what this change means for the reader
- risk_delta: does this change increase, decrease, or maintain the reader's risk exposure?

Also provide an overall_summary of the most significant changes.
Respond in JSON:
{{
  "overall_summary": "string",
  "differences": [
    {{
      "section": "string",
      "type": "added|removed|modified|moved",
      "summary": "string",
      "impact": "string",
      "risk_delta": "increase|decrease|neutral"
    }}
  ]
}}"""
