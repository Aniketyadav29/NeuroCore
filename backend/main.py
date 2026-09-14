"""
NeuroCore AI — FastAPI Application Entry Point
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import get_settings
from app.database import engine
from app import models

# Create all database tables on startup
models.Base.metadata.create_all(bind=engine)

settings = get_settings()

app = FastAPI(
    title="NeuroCore AI",
    description=(
        "AI Autonomous Company Intelligence Platform — "
        "Cross-departmental RAG engine + Rule-based automation with human-in-the-loop approvals."
    ),
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.frontend_url,
        "http://localhost:5173",
        "http://localhost:3000",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Register Routers ────────────────────────────────────────
from app.routers import chat, dashboard, automation

app.include_router(chat.router)
app.include_router(dashboard.router)
app.include_router(automation.router)

# ── Health Check ────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "app":     settings.app_name,
        "version": "2.0.0",
        "env":     settings.app_env,
        "docs":    "/docs",
    }

@app.get("/health", tags=["Health"])
def health():
    return {
        "status":        "healthy",
        "database":      "sqlite",
        "vector_store":  "chromadb",
        "llm_provider":  settings.llm_provider,
    }
