"""
rag_engine.py
The main RAG pipeline for NeuroCore AI.

Orchestrates:
  1. Database sync -> ChromaDB vector indexing (reindex)
  2. Query -> semantic retrieval -> LLM generation -> citations (query)
"""

import logging
from typing import Dict, Any, List
from sqlalchemy.orm import Session

from app.models import HREmployee, SalesDeal, FinanceInvoice, SupportTicket
from app.rag.document_builder import (
    build_hr_documents,
    build_sales_documents,
    build_finance_documents,
    build_support_documents,
)
from app.rag.vector_store import (
    upsert_documents,
    query_documents,
    reset_collection,
    get_collection_stats,
)
from app.rag.llm_service import generate_response

logger = logging.getLogger(__name__)


# ─────────────────────────────────────────────────────────────
#  REINDEX — Sync SQLite -> ChromaDB
# ─────────────────────────────────────────────────────────────

def reindex_all(db: Session) -> Dict[str, Any]:
    """
    Reads all records from SQLite and upserts them into ChromaDB.
    Resets the existing collection first for a clean sync.
    
    Returns a summary of indexed records per department.
    """
    logger.info("Starting full reindex of all departments...")

    # Step 1: Reset existing collection
    reset_collection()

    # Step 2: Build documents per department
    employees = db.query(HREmployee).all()
    deals     = db.query(SalesDeal).all()
    invoices  = db.query(FinanceInvoice).all()
    tickets   = db.query(SupportTicket).all()

    hr_docs      = build_hr_documents(employees)
    sales_docs   = build_sales_documents(deals)
    finance_docs = build_finance_documents(invoices)
    support_docs = build_support_documents(tickets)

    all_docs = hr_docs + sales_docs + finance_docs + support_docs

    # Step 3: Upsert all into ChromaDB in one batch
    total = upsert_documents(all_docs)

    summary = {
        "status":         "success",
        "total_indexed":  total,
        "by_department": {
            "hr":      len(hr_docs),
            "sales":   len(sales_docs),
            "finance": len(finance_docs),
            "support": len(support_docs),
        }
    }
    logger.info(f"Reindex complete: {summary}")
    return summary


# ─────────────────────────────────────────────────────────────
#  QUERY — Cross-Department RAG Pipeline
# ─────────────────────────────────────────────────────────────

def run_rag_query(query: str, n_results: int = 10) -> Dict[str, Any]:
    """
    Executes the full RAG pipeline for a user query:
      1. Query ChromaDB for semantically similar records (cross-department)
      2. Send retrieved context + query to LLM
      3. Return structured response with answer, citations, and raw records

    Args:
        query:     Natural language question from the user.
        n_results: Number of top documents to retrieve.

    Returns:
        {
            "answer":            str   — Markdown-formatted AI response
            "citations":         list  — List of cited record IDs
            "retrieved_records": list  — Raw retrieved documents
            "provider":          str   — LLM provider used
            "context_used":      int   — Number of context records
            "query":             str   — The original query
        }
    """
    stats = get_collection_stats()
    if stats["status"] == "empty":
        return {
            "answer": (
                "**The vector store is empty.** Please run the **/api/reindex** endpoint first "
                "to index the company database into ChromaDB before querying."
            ),
            "citations":         [],
            "retrieved_records": [],
            "provider":          "none",
            "context_used":      0,
            "query":             query,
        }

    # Semantic retrieval — cross-department
    retrieved = query_documents(query, n_results=n_results)

    if not retrieved:
        return {
            "answer": (
                "I couldn't find any relevant records in the company database for your query. "
                "Please try rephrasing or asking about HR, Sales, Finance, or Support data."
            ),
            "citations":         [],
            "retrieved_records": [],
            "provider":          "none",
            "context_used":      0,
            "query":             query,
        }

    # LLM generation with citations
    result = generate_response(query, retrieved)
    result["query"] = query

    return result


# ─────────────────────────────────────────────────────────────
#  VECTOR STORE STATUS
# ─────────────────────────────────────────────────────────────

def get_index_status() -> Dict[str, Any]:
    """Returns the current state of the ChromaDB index."""
    return get_collection_stats()
