# NyayaSetu — GenAI-Powered Legal Assistance Platform

> Helping non-lawyers understand, compare, and navigate legal documents using generative AI — without replacing professional advice.

## 🚀 Live Demo
* **Frontend:** [Insert your Vercel URL here]
* **Backend API:** [Insert your Render URL here]/api/docs

## 📖 Overview
NyayaSetu is an AI-powered legal tech platform built for our hackathon submission. It breaks down complex legal jargon into plain language, helping users understand contracts before they sign them. 

**Core Capabilities:**
- **Smart PDF Parsing:** Extracts and chunks text from legal PDFs.
- **Plain-Language Summaries:** Translates dense legalese into understandable summaries.
- **Clause Highlighting:** Identifies risk levels, obligations, and critical clauses automatically.
- **Secure Cloud Architecture:** Fully serverless, cloud-hosted pipeline.

⚠️ **Disclaimer: This tool provides informational analysis only and does not constitute legal advice.** Always consult a licensed attorney for binding legal guidance.

## 💻 Tech Stack
| Layer | Technology | Hosting |
|---|---|---|
| **Frontend** | Next.js 14, TypeScript, Tailwind CSS | Vercel |
| **Backend** | FastAPI (Python 3.12+), PyMuPDF | Render |
| **Database** | PostgreSQL + `pgvector` | Neon (Serverless) |
| **AI / LLM** | Google Gemini 1.5 Pro (REST API) | Google Cloud |

## ⚙️ Architecture & Data Flow
1. User uploads a PDF contract via the **Next.js** frontend.
2. The file is sent to the **FastAPI** backend where `PyMuPDF` parses and chunks the text.
3. The chunks are saved securely in a **Neon PostgreSQL** database.
4. The backend orchestrates a call to the **Gemini API** with strict safety guardrails.
5. The AI extracts clauses, assigns risk scores, and streams the structured JSON back to the UI.

## 🛠️ Local Development Setup

### Prerequisites
- Node.js 20+
- Python 3.12+
- A free Neon PostgreSQL Database URL
- A Gemini API Key

### 1. Clone and Install
```bash
git clone https://github.com/amritsingh047/NyayaSetu.git
cd NyayaSetu

# Install Frontend
cd frontend
npm install

# Install Backend
cd ../backend
pip install -r requirements.txt
