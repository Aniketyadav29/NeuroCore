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
| Frontend | React 19 + Vite 8 |

---

## Project Structure

```
NeuroCore/
├── backend/
│   ├── app/
│   │   ├── automation/       # Rule engine + audit log creation
│   │   ├── rag/              # ChromaDB indexing, LLM service, vector store
│   │   ├── routers/          # FastAPI routes (chat, dashboard, automation)
│   │   ├── config.py         # Pydantic settings
│   │   ├── database.py       # SQLAlchemy engine & session
│   │   └── models.py         # ORM models (HR, Sales, Finance, Support, Automation, Audit)
│   ├── main.py               # FastAPI entry point
│   ├── seed_data.py          # Mock data generator (98 correlated records)
│   ├── requirements.txt      # Python dependencies
│   └── .env.example          # Environment variable template
└── frontend/
    ├── src/
    │   ├── components/       # Sidebar, KpiCard
    │   ├── pages/            # Dashboard, Chat, Automation, Audit
    │   ├── api.js            # Centralized API client
    │   └── index.css         # Design system (dark glassmorphism)
    └── vite.config.js        # Vite + dev proxy config
```

---

## Quick Start

### 1. Backend

```bash
cd backend

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate     # Mac/Linux

# Install dependencies
pip install -r requirements.txt

# Configure environment
copy .env.example .env
# Edit .env — set LLM_PROVIDER=offline to run without API keys

# Seed the database with 98 cross-correlated mock records
python seed_data.py

# Start the FastAPI server
uvicorn main:app --reload --port 8000
```

Visit **http://localhost:8000/docs** for the interactive API explorer.

### 2. Frontend

```bash
cd frontend

# Install dependencies
npm install

# Start the dev server (Vite proxy forwards /api/* to :8000)
npm run dev
```

Visit **http://localhost:5173** to open the app.

---

## First Run (after seeding)

1. Navigate to **AI Intelligence Chat** → click **🔄 Reindex Database**
2. Ask a cross-department question (e.g. *"Why did support tickets spike after the Q1 launch?"*)
3. Navigate to **Automation Center** → click **▶ Run Rule Evaluation**
4. Approve or reject the pending actions that appear
5. Check the **Audit Trail** for the full history

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

The offline LLM provider works **without any API keys** using a built-in keyword-based synthesizer over retrieved context.

---

## Build Phases

- [x] **Phase 1** — Foundation: Project structure, DB models, mock data seed (98 records)
- [x] **Phase 2** — RAG Engine: ChromaDB indexing, cross-department semantic search, LLM citations
- [x] **Phase 3** — Automation Engine: Rule evaluator, approval workflows, audit logging
- [x] **Phase 4** — Frontend: React dashboard, chat UI, approval center, audit timeline
- [x] **Phase 5** — Integration & Polish: Vite proxy, live backend status, responsive design, documentation

---

## License

MIT License — Built for academic and demonstration purposes.
