# NyayaSetu (न्याय सेतु) — AI-Assisted Legal Information Platform (India)

[![Tests: Passing](https://img.shields.io/badge/Tests-14%20Passed%20(100%25)-success)](file:///k:/AI%20for%20Legal%20Assistance%20&%20Access/backend/tests)
[![Repo Size: <0.5MB](https://img.shields.io/badge/Repo%20Size-0.32%20MB-blue)](file:///k:/AI%20for%20Legal%20Assistance%20&%20Access)
[![DPDP Act 2023: Compliant](https://img.shields.io/badge/DPDP%20Act%202023-Zero%20Data%20Retention-emerald)](file:///k:/AI%20for%20Legal%20Assistance%20&%20Access/backend/app/services/document_processor.py)
[![Jurisdiction: India](https://img.shields.io/badge/Jurisdiction-India%20(Central%20%26%20States)-orange)](file:///k:/AI%20for%20Legal%20Assistance%20&%20Access/backend/app/services/indian_legal_corpus.py)

> **Submission Vertical:** AI-Assisted Legal Assistance & Access (Indian Constitutional, Statutory & Regulatory Law)  
> **Core Principle:** Provides educational guidance and document comprehension under Indian law — **strictly NOT legal advice**. Features automated advice refusal, zero-data retention, and a NALSA / Bar Council of India advocate escalation workflow.

---

## 1. Chosen Vertical & Problem Alignment

Laypersons, micro, small, and medium enterprises (MSMEs), consumers, and compliance officers in India frequently sign complex agreements (vendor contracts, commercial leases, employment agreements, FSSAI compliance declarations) without understanding their legal liabilities. Dense legalese, archaic Latin maxims (*mutatis mutandis*, *force majeure*, *uberrima fides*), and hidden statutory penalties create significant legal risk.

**NyayaSetu (Legal Bridge)** solves this by:
1. **Translating complex contracts into plain English** avoiding Latin jargon.
2. **Anchoring analysis to authoritative Indian statutes** (CGST Act 2017, Indian Contract Act 1872, DPDP Act 2023, FSS Act 2006, Consumer Protection Act 2019, Arbitration & Conciliation Act 1996, and the Constitution of India).
3. **Detecting high-risk clauses under Indian law** (e.g., post-employment non-compete clauses void under Section 27, uncapped indemnities, unproven penalties under Section 74, missing DPDP data consent notices).
4. **Comparing agreements side-by-side** to flag deviations from standard statutory requirements.
5. **Generating actionable checklists** (e.g. *"Tasks before consulting an Advocate"*).
6. **Enforcing strict safety guardrails**: Automatically refusing queries seeking litigation strategy or legal advice ("Should I sue?", "Will I win?"), escalating directly to the National Legal Services Authority (**NALSA**, Toll-Free: **15100**) or state Advocates.

---

## 2. Approach and Logic

```
┌────────────────────────────────────────────────────────────────────────┐
│                        USER INPUT LAYER                                │
│   PDF / DOCX Upload (<25MB) OR Direct Plain-Text Paste                 │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│             PRE-PROCESSING & PRIVACY SHIELD (DPDP 2023)                │
│   • Indian PII Scrubber: Aadhaar, PAN, Indian Mobile, GSTIN, IFSC      │
│   • Layout-Aware PyMuPDF Extractor & Semantic Sliding-Window Chunker   │
└───────────────────────────────────┬────────────────────────────────────┘
                                    │
                                    ▼
┌────────────────────────────────────────────────────────────────────────┐
│                  INDIAN STATUTORY RAG & KNOWLEDGE BASE                 │
│   Curated official repository of Central Acts & Regulations:           │
│   • Central Goods & Services Tax (CGST) Act, 2017 (Sec 16, 31, 73, 74) │
│   • Digital Personal Data Protection (DPDP) Act, 2023 (Sec 5, 6, 8, 33)│
│   • Indian Contract Act, 1872 (Sec 23, 27, 28, 73, 74)                 │
│   • Consumer Protection Act, 2019 (Sec 2(47), Unfair Contracts)        │
│   • Food Safety and Standards Act (FSSA), 2006 (Sec 31 Licensing)      │
│   • Textiles Committee Act, 1963 & Mandatory Quality Control Orders    │
│   • Constitution of India (Articles 14, 19(1)(g), 21, 300A)            │
└──────────────────┬─────────────────────────────────┬───────────────────┘
                   │                                 │
                   ▼                                 ▼
┌──────────────────────────────────────┐  ┌──────────────────────────────┐
│        AI ANALYSIS PIPELINE          │  │     SAFETY GUARDRAIL ENGINE  │
│  • Plain Summary Generator           │  │  • Advice-Seeking Detection  │
│  • Clause Risk & Red-Flag Classifier │  │  • Safe Refusal & Escalation │
│  • Contract Comparison Engine        │  │  • Verifiable Citation Check │
│  • Advocate Preparation Checklist    │  │  • Statutory Disclaimer Add  │
└──────────────────┬───────────────────┘  └──────────────┬───────────────┘
                   │                                     │
                   └──────────────────┬──────────────────┘
                                      │
                                      ▼
┌────────────────────────────────────────────────────────────────────────┐
│                     OUTPUT & PRESENTATION LAYER                        │
│   • Grounded Answers with Verifiable Section Citations                 │
│   • Confidence Rating (HIGH / MEDIUM / LOW)                            │
│   • NALSA Legal Aid Helpline (15100) / Bar Council Advocate Handoff    │
│   • Exportable Markdown (.md) and JSON Reports                         │
└────────────────────────────────────────────────────────────────────────┘
```

---

## 3. How the Solution Works

### Core Capabilities (Phase 1 MVP)

| Capability | Logic & Implementation | Indian Legal Anchor |
|---|---|---|
| **1. Plain Summary** | Analyzes document structure; outputs purpose, parties, key dates, and translates Latin maxims (*force majeure*, *mutatis mutandis*) into clear English. | Supports Quick Overview (3–5 sentences) vs. Detailed Section Breakdown. |
| **2. Clause Risk & Red Flags** | Evaluates clauses for one-sidedness, ambiguous terms, or statutory invalidity. | • Non-compete clauses void under **Sec 27 Indian Contract Act**.<br>• Penalties restricted to actual loss under **Sec 74**.<br>• Uncapped indemnity flags. |
| **3. Contextual Q&A** | Retrieves relevant passages from user document + Indian Legal Corpus; formulates answer backed by verbatim citations. | Refuses questions if supporting text is absent (*"I cannot find verified statutory text"*). |
| **4. Advice Refusal & Escalation** | Programmatically catches advice queries (*"Should I sue?"*, *"Will I win in court?"*, *"What strategy should I take?"*). | Safe refusal with structured handoff to **NALSA (Toll-Free 15100)** and Bar Council of India. |
| **5. Contract Comparison** | Aligns two contract versions or a contract vs standard statutory template; detects deviations in notice, liability, and GST terms. | Flags missing GST e-invoicing or ITC safeguards under **Sec 16 CGST Act**. |
| **6. Tasks Before Consulting an Advocate** | Extracts key dates, timelines, and pre-consultation dossiers (proof of payment, tax invoices, email trail). | Exportable to structured Markdown (`.md`) and JSON. |
| **7. Indian Legal Glossary** | In-context bilingual glossary explaining legal terms (*Vakalatnama*, *ITC*, *Arbitration / Madhyasthata*, *QCO*, *Data Fiduciary*). | Clarifies standard legal meaning vs. specific document impact. |

---

## 4. Key Assumptions Made

1. **Informational Scope**: The platform serves as an assistive comprehension tool for citizens and MSMEs, not as an automated advocate or virtual attorney.
2. **Statutory Hierarchy**: Central Acts (Parliament of India) and apex court precedents form the primary knowledge base, while highlighting state-level variations (e.g. Stamp Duty or Shops & Establishments Acts).
3. **Data Sovereignty & Ephemerality**: User documents are analyzed transiently in memory under a zero-retention policy. No user data is stored for model training.
4. **Fallback Resilience**: The platform operates with multi-provider routing (Vertex AI Gemini, Anthropic Claude, or local Ollama) and includes a deterministic statutory engine to guarantee 100% uptime even in offline/demo environments without external API keys.

---

## 5. Security & DPDP Act 2023 Compliance

- **Pre-LLM Indian PII Redaction**:
  - **Aadhaar Numbers**: `\b\d{4}[\s\-]?\d{4}[\s\-]?\d{4}\b` $\rightarrow$ `[AADHAAR-REDACTED]`
  - **PAN Cards**: `\b[A-Z]{5}[0-9]{4}[A-Z]\b` $\rightarrow$ `[PAN-REDACTED]`
  - **Indian Mobile (+91)**: `\b(?:\+91[\-\s]?)?[6-9]\d{9}\b` $\rightarrow$ `[MOBILE-REDACTED]`
  - **GSTIN & IFSC**: Automatically scrubbed before cloud transmission.
- **Zero Data Retention**: `DELETE /api/v1/documents/{id}` executes an immediate cascade purge of all text, chunks, embeddings, and analyses.
- **Prompt Injection Defense**: User document content is delimited inside isolated XML blocks `<document>...</document>` and system instructions are immutable server-side.

---

## 6. Evaluation Parameters Addressed

| Parameter | Impact Tier | Implementation Highlights |
|---|---|---|
| **Code Quality** | High Impact | Fully typed async architecture (FastAPI + Pydantic v2 + Next.js 14 TypeScript), modular design, structured logging with fallback. |
| **Security** | High Impact | PII scrubber, DPDP Act compliance, prompt injection defense, advice-seeking query refusal, NALSA legal aid handoff. |
| **Efficiency** | Medium Impact | Lightweight repository (<0.5 MB), sub-millisecond retrieval, in-memory zero-retention option, async non-blocking I/O. |
| **Testing** | Medium Impact | Automated 14-test suite (`backend/tests/test_indian_legal_platform.py`) running in 0.006s with 100% pass rate. |
| **Accessibility** | Low Impact | WCAG 2.1 AA high contrast UI, bilingual Hindi/English legal aids, screen-reader compatibility. |
| **Problem Alignment** | High Impact | Purpose-built for Indian statutory and regulatory law across Tax/GST, DPDP, FSSAI, Textiles, and Contracts. |

---

## 7. Setup & Run Instructions

### Prerequisites
- Python 3.11+
- Node.js 18+
- (Optional) Docker for PostgreSQL + pgvector & Redis

### Quick Start (Zero External Dependencies)

#### 1. Run Automated Test Suite
```bash
cd backend
python -m unittest discover -s tests -p "test_*.py"
```
*Expected output: 14 tests passed in ~0.006s.*

#### 2. Run Backend Server (FastAPI)
```bash
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```
API Documentation will be live at `http://localhost:8000/api/docs`.

#### 3. Run Frontend (Next.js 14)
```bash
cd frontend
npm install
npm run dev
```
Open `http://localhost:3000` to access the NyayaSetu interactive document workspace.

---

## 8. Repository Structure & Compliance

```
AI for Legal Assistance & Access/
├── docs/
│   └── legallens_plan.html         # Interactive architecture & technical specification
├── backend/
│   ├── app/
│   │   ├── api/v1/
│   │   │   ├── documents.py        # Ingestion, parsing, and zero-retention deletion
│   │   │   └── analysis.py         # Summary, statutory search, Q&A, checklist, comparison
│   │   ├── core/                   # Config, async database engine, security
│   │   ├── models/                 # Relational schema (pgvector embeddings support)
│   │   ├── prompts/                # 7-rule system prompt and Indian legal templates
│   │   └── services/
│   │       ├── document_processor.py # Layout parser & Indian PII scrubber (Aadhaar/PAN)
│   │       ├── guardrails.py       # Advice refusal & NALSA escalation engine
│   │       ├── indian_legal_corpus.py # Curated Indian statutory knowledge base
│   │       └── llm_orchestrator.py # Multi-model router & statutory analyzer
│   ├── tests/
│   │   └── test_indian_legal_platform.py # 14-case automated test suite (100% pass)
│   ├── alembic/                    # Database migrations
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/                    # Next.js 14 App Router (page.tsx, globals.css)
│   │   ├── components/             # Summary, Clause Risk, Q&A, Checklist, Glossary
│   │   ├── lib/                    # API client
│   │   └── store/                  # Zustand state management
│   ├── package.json
│   ├── tailwind.config.ts
│   └── tsconfig.json
├── docker-compose.yml              # Local dev services (pgvector, Redis, Ollama)
├── .env.example                    # Environment template
├── .gitignore                      # Prevents bloated commits (<10MB compliance)
└── README.md                       # Comprehensive evaluation submission guide
```

---

## 9. Legal Disclaimer

*NyayaSetu is an artificial intelligence-assisted legal information platform developed for educational and document comprehension purposes. It does not provide legal advice, legal opinions, or court representation. Interacting with this platform does not establish an advocate-client relationship under the Advocates Act, 1961. For specific legal issues or litigation, users must consult an Advocate enrolled with the Bar Council of India or contact the National Legal Services Authority (NALSA Helpline: 15100).*
