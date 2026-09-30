# ResumeVerify AI 🛡️
### Public Evidence Verification Engine for Candidate Resumes

**ResumeVerify AI** is an evidence-corroboration web application that verifies whether statements, skills, projects, and technologies in candidate resumes are backed by publicly accessible evidence across **GitHub repositories, LinkedIn, Portfolios, and Developer Platforms**.

---

## 🚀 Key Features

1. **📄 PyMuPDF PDF Parsing & Extraction**
   - High-fidelity extraction of resume text, contact metadata, and sections (*Projects*, *Skills*, *Experience*, *Certifications*).
   - Extracts embedded PDF hyperlink annotations (clickable URLs behind text) and inline text URLs.

2. **🐙 Deep GitHub Verification (Official REST API)**
   - Resolves repository existence, owner, and active status.
   - Inspects language distribution with byte/percentage breakdown.
   - Decodes `README.md` content and searches for claimed features and architecture.
   - Analyzes package manifests (`requirements.txt`, `pyproject.toml`, `package.json`, `go.mod`, `Cargo.toml`, `Dockerfile`) to verify claimed frameworks and libraries.
   - Reviews commit activity, dates, file tree summaries, and contributor records.
   - Rate limit aware with `GITHUB_TOKEN` support from `.env`.

3. **🔒 SSRF Protection & Safe Web Scraper**
   - Built-in SSRF Shield (`ssrf_validator.py`) blocking private IP ranges (`10.0.0.0/8`, `172.16.0.0/12`, `192.168.0.0/16`), loopback (`127.0.0.1`), link-local metadata endpoints (`169.254.169.254`), and non-HTTP protocols.
   - Scrapes public portfolio websites to extract tech stacks, project cards, and outbound links.
   - Strictly respects authentication walls (e.g. LinkedIn login gates) without bypassing anti-bot systems.

4. **⚖️ Objective Claim-Evidence Matching**
   - Extracts atomic claims and breaks them down into individual verifiable entities.
   - Uses strict, non-judgmental status classifications:
     - ✅ **Supported**: Corroborated with direct evidence in repository code, manifests, or public pages.
     - 🟡 **Partially Supported**: Partial evidence found (e.g., Python and FastAPI verified, but secondary library unverified).
     - ⚪ **Unverified**: No public evidence found (neutral; candidates frequently work on proprietary/internal systems).
     - 🔴 **Broken Link**: Associated URL returned 404 or connection failure.
     - 🔒 **Restricted**: Resource is private or sign-in gated.
   - *Never marks unverified claims as "fake" or "fraudulent".*

5. **📊 Interactive HR Dashboard**
   - **Evidence Coverage Gauge** (% of claims supported by public evidence).
   - **Interactive Claims Explorer**: Filter by status, section, or search keyword; expand claim cards to view exact code/manifest quotes, line numbers, confidence scores, and source URLs.
   - **Discovered URLs & Repository Matrix**: Language breakdown bars, dependency badges, recent commits, and contributor lists.
   - **Export Capabilities**: Download complete JSON report, copy formatted Markdown summary, or print styled summary.

---

## 🏗️ Architecture

```text
Uploaded PDF
     ↓
PyMuPDF Parser (Text + Annotations + URLs)
     ↓
Claim & Entity Extractor (Projects, Skills, Roles)
     ↓
URL Classifier & SSRF Shield
     ↓
Evidence Providers
 ├── GitHub REST API (Manifests, READMEs, Langs, Commits, Trees)
 ├── LinkedIn Public Checker (Respects auth walls)
 ├── Portfolio & Web Scraper (BeautifulSoup4)
 └── Developer Platforms (LeetCode, Kaggle, HuggingFace)
     ↓
Claim-Evidence Matcher (Corroboration Engine)
     ↓
Report Compiler (Coverage %, Risk & Strengths Radar)
     ↓
Interactive React + Tailwind Dashboard
```

---

## 🛠️ Tech Stack

- **Backend**: Python 3.12, FastAPI, SQLAlchemy (Async), aiosqlite / PostgreSQL, PyMuPDF, HTTPX, BeautifulSoup4, Pydantic v2
- **Frontend**: React 19, TypeScript, Vite, Tailwind CSS, Lucide Icons, Canvas Confetti
- **Security**: SSRF Validation Shield, Rate-limit handling, Zero code execution

---

## ⚡ Quick Start

### 1. Backend Setup

```bash
# Navigate to backend and create virtual environment
python -m venv .venv
.\.venv\Scripts\activate

# Install dependencies
pip install -r backend/requirements.txt

# Run FastAPI server
python backend/run.py
```
Backend will start on `http://127.0.0.1:8000`. Swagger API docs available at `http://127.0.0.1:8000/docs`.

### 2. Frontend Setup

```bash
# Navigate to frontend
cd frontend

# Install dependencies
npm install

# Start Vite dev server
npm run dev
```
Frontend will be accessible at `http://127.0.0.1:5173`.

---

## ⚙️ Configuration (`.env`)

Create a `.env` file in the root directory:

```env
APP_NAME=ResumeVerify AI
DEBUG=True

# SQLite (Default) or PostgreSQL
DATABASE_URL=sqlite+aiosqlite:///./resume_verify.db

# GitHub REST API Token (Optional, boosts rate limit from 60 to 5,000 req/hr)
GITHUB_TOKEN=

# AI Provider ("rule_based", "openai", "gemini", "groq", "ollama")
LLM_PROVIDER=rule_based
```
