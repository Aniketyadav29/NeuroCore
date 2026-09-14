"""
routers/chat.py
FastAPI routes for the RAG Intelligence Engine:
  POST /api/chat      — Ask a cross-department AI question
  POST /api/reindex   — Re-sync SQLite records into ChromaDB
  GET  /api/index/status — Check ChromaDB index status
"""

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from typing import List, Optional

from app.database import get_db
from app.rag.rag_engine import run_rag_query, reindex_all, get_index_status

router = APIRouter(prefix="/api", tags=["AI Chat"])


# ─────────────────────────────────────────────────────────────
#  Request / Response Schemas
# ─────────────────────────────────────────────────────────────

class ChatRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=1000, description="The user's natural language question")
    n_results: int = Field(default=10, ge=3, le=20, description="Number of context records to retrieve")


class RetrievedRecord(BaseModel):
    id:       str
    text:     str
    metadata: dict
    distance: float


class ChatResponse(BaseModel):
    query:            str
    answer:           str
    citations:        List[str]
    retrieved_records: List[RetrievedRecord]
    provider:         str
    context_used:     int


class ReindexResponse(BaseModel):
    status:        str
    total_indexed: int
    by_department: dict
    message:       str


# ─────────────────────────────────────────────────────────────
#  ENDPOINTS
# ─────────────────────────────────────────────────────────────

@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest, db: Session = Depends(get_db)):
    """
    Ask a cross-departmental AI question.
    
    The RAG engine retrieves semantically relevant records from HR, Sales,
    Finance, and Customer Support — then generates an answer with inline citations.
    
    Example queries:
    - "Why did support tickets spike this week?"
    - "Which clients have overdue invoices?"
    - "Is the support team understaffed?"
    - "What happened with ProPay Suite after the Q1 launch?"
    """
    try:
        result = run_rag_query(query=request.query, n_results=request.n_results)
        return ChatResponse(
            query=result["query"],
            answer=result["answer"],
            citations=result["citations"],
            retrieved_records=[
                RetrievedRecord(**r) for r in result["retrieved_records"]
            ],
            provider=result["provider"],
            context_used=result["context_used"],
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG engine error: {str(e)}")


@router.post("/reindex", response_model=ReindexResponse)
def reindex(db: Session = Depends(get_db)):
    """
    Re-synchronizes all SQLite department records into the ChromaDB vector store.
    
    Run this:
    - On first startup (after seeding the database)
    - Whenever new records are added to any department
    
    This operation resets the existing index and rebuilds from scratch.
    """
    try:
        result = reindex_all(db)
        return ReindexResponse(
            status=result["status"],
            total_indexed=result["total_indexed"],
            by_department=result["by_department"],
            message=(
                f"Successfully indexed {result['total_indexed']} records across "
                f"{len(result['by_department'])} departments into ChromaDB."
            )
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reindex error: {str(e)}")


@router.get("/index/status")
def index_status():
    """Returns the current ChromaDB index status and document count."""
    return get_index_status()
