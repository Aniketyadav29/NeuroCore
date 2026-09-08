"""
NeuroCore AI — FastAPI Application Entry Point
Phase 1: Base app with CORS, health check, and route stubs.
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
    description="AI Autonomous Company Intelligence Platform — cross-departmental RAG + automation engine",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# ── CORS Middleware ─────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.frontend_url, "http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Health Check ────────────────────────────────────────────
@app.get("/", tags=["Health"])
def root():
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": "1.0.0",
        "env": settings.app_env,
    }

@app.get("/health", tags=["Health"])
def health():
    return {"status": "healthy", "database": "sqlite", "vector_store": "chromadb"}

# ── Route Stubs (will be filled in subsequent phases) ───────
# Phase 2: /api/chat  and  /api/reindex
# Phase 3: /api/automation/*  and  /api/dashboard/stats
