# NeuroCore AI 🧠

> **AI-Powered Autonomous Company Intelligence Web Application**

NeuroCore AI is a unified corporate intelligence platform that integrates **HR, Sales, Finance, and Customer Support** data through a cross-departmental RAG (Retrieval-Augmented Generation) engine and a safe, rule-based automation system with human-in-the-loop approvals.

---

## Features

- **AI Intelligence Chat** — Ask natural-language questions across all departments. Get source-cited, verifiable answers (e.g. *"Why did support tickets spike this week?"*)
- **Cross-Department RAG Engine** — ChromaDB semantic search + LLM synthesis with inline citations (`[TCK-502]`, `[INV-2026-001]`, `[EMP-012]`)
- **Rule-Based Automation** — Deterministic trigger-condition-action rules (overdue invoices, support spikes, HR understaffing)
- **Human-in-the-Loop Approvals** — High-impact actions require manager sign-off before execution
- **Audit Trail** — Complete immutable history of all automated and human-reviewed actions
- **Executive Dashboard** — KPI tiles, department health, pending actions at a glance

---

## Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.10 + FastAPI + Uvicorn |
| Database | SQLite + SQLAlchemy ORM |
| Vector Store | ChromaDB |
| LLM | Google Gemini / OpenAI / Groq / Offline fallback |
| Frontend | React + Vite |

---

## Project Structure

```
NeuroCore/
├── backend/
│   ├── app/
│   │   ├── config.py        # Pydantic settings
│   │   ├── database.py      # SQLAlchemy engine & session
│   │   └── models.py        # ORM models (HR, Sales, Finance, Support, Automation, Audit)
│   ├── main.py              # FastAPI entry point
│   ├── seed_data.py         # Mock data generator (98 correlated records)
│   ├── requirements.txt     # Python dependencies
│   └── .env.example         # Environment variable template
└── frontend/                # React + Vite (Phase 4)
```

---

## Quick Start

### Backend

```bash
cd backend

# 1. Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Mac/Linux

# 2. Install dependencies
pip install -r requirements.txt

# 3. Configure environment
cp .env.example .env
# Edit .env — set LLM_PROVIDER=offline to run without API keys

# 4. Seed the database
python seed_data.py

# 5. Start the server
uvicorn main:app --reload --port 8000
```

Visit: http://localhost:8000/docs for the interactive API explorer.

---

## Demo Scenario

All mock data is cross-correlated around a realistic enterprise scenario:

> **ProPay Suite** was launched in Q1 2026 and closed with 5 enterprise clients → those same clients now have **5 overdue invoices** in Finance → generated **4 critical billing error tickets** in Customer Support → while **3 of 8 Support team members are on leave** → causing a growing unresolved ticket backlog.

Ask the AI: *"Why did customer complaints increase after the Q1 product launch?"* and watch it connect the dots across all 4 departments with citations.

---

## Environment Variables

| Variable | Description | Default |
|---|---|---|
| `LLM_PROVIDER` | LLM backend: `gemini`, `openai`, `groq`, `offline` | `offline` |
| `GEMINI_API_KEY` | Google Gemini API key | — |
| `OPENAI_API_KEY` | OpenAI API key | — |
| `GROQ_API_KEY` | Groq API key | — |
| `DATABASE_URL` | SQLite connection string | `sqlite:///./neurocore.db` |
| `CHROMA_PERSIST_DIR` | ChromaDB storage path | `./chroma_store` |

---

## Build Phases

- [x] **Phase 1** — Foundation: Project structure, DB models, mock data seed
- [ ] **Phase 2** — RAG Engine: ChromaDB indexing, cross-department semantic search, LLM citations
- [ ] **Phase 3** — Automation Engine: Rule evaluator, approval workflows, audit logging
- [ ] **Phase 4** — Frontend: React dashboard, chat UI, approval center, audit timeline
- [ ] **Phase 5** — Integration & Documentation

---

## License

MIT License — Built for academic and demonstration purposes.
