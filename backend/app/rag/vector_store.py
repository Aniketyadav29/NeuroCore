"""
vector_store.py
ChromaDB vector store manager for NeuroCore AI.

Manages a single persistent ChromaDB collection named 'neurocore_company'
that stores all department documents with metadata for filtering.

Uses ChromaDB's built-in default embedding function (no external API needed).
"""

import chromadb
import hashlib
import math
import re
from typing import List, Dict, Any, Optional
from app.config import get_settings
import logging

logger = logging.getLogger(__name__)

settings = get_settings()

# Singleton client and collection
_client: Optional[chromadb.PersistentClient] = None
_collection = None

COLLECTION_NAME = "neurocore_company"

# ── Pure-Python embedding function (no DLL / onnxruntime needed) ──────────────

class _HashEmbeddingFunction:
    """
    Lightweight TF-IDF-inspired embedding using character n-gram hashing.
    Produces a 256-dimensional float vector from any text string.
    No native libraries required — runs on pure Python + stdlib.
    """
    DIM = 256

    def _embed_one(self, text: str) -> List[float]:
        tokens = re.findall(r'\b\w+\b', text.lower())
        vec = [0.0] * self.DIM
        for token in tokens:
            # Each token casts a vote into two bucket positions
            h1 = int(hashlib.md5(token.encode()).hexdigest(), 16) % self.DIM
            h2 = int(hashlib.sha1(token.encode()).hexdigest(), 16) % self.DIM
            vec[h1] += 1.0
            vec[h2] += 0.5
            # Character bigrams for richer signal
            for i in range(len(token) - 1):
                bigram = token[i:i+2]
                hb = int(hashlib.md5(bigram.encode()).hexdigest(), 16) % self.DIM
                vec[hb] += 0.25
        # L2-normalize
        norm = math.sqrt(sum(x * x for x in vec)) or 1.0
        return [x / norm for x in vec]

    def __call__(self, input: List[str]) -> List[List[float]]:  # noqa: A002
        return [self._embed_one(t) for t in input]


def _get_embedding_function():
    """Pure-Python hash embedding — no onnxruntime / DLL dependency."""
    return _HashEmbeddingFunction()


def get_chroma_client() -> chromadb.PersistentClient:
    """Returns a singleton ChromaDB persistent client."""
    global _client
    if _client is None:
        _client = chromadb.PersistentClient(path=settings.chroma_persist_dir)
        logger.info(f"ChromaDB client initialized at: {settings.chroma_persist_dir}")
    return _client


def get_collection():
    """Returns (or creates) the main company-wide ChromaDB collection."""
    global _collection
    if _collection is None:
        client = get_chroma_client()
        # ChromaDB 1.x: embedding_function is passed directly (still supported)
        _collection = client.get_or_create_collection(
            name=COLLECTION_NAME,
            embedding_function=_get_embedding_function(),
            metadata={"hnsw:space": "cosine"},
        )
        logger.info(f"ChromaDB collection '{COLLECTION_NAME}' ready. Count: {_collection.count()}")
    return _collection


def upsert_documents(documents: List[Dict[str, Any]]) -> int:
    """
    Upsert a list of semantic documents into ChromaDB.

    Each document must have:
      - 'id':       unique string ID  (e.g. 'HR-001', 'TCK-501')
      - 'text':     the full semantic text to embed
      - 'metadata': dict of filterable metadata fields
    
    Returns the number of documents upserted.
    """
    if not documents:
        return 0

    collection = get_collection()

    ids       = [d["id"] for d in documents]
    texts     = [d["text"] for d in documents]
    metadatas = [d["metadata"] for d in documents]

    collection.upsert(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
    )
    logger.info(f"Upserted {len(documents)} documents into ChromaDB.")
    return len(documents)


def query_documents(
    query_text: str,
    n_results: int = 8,
    source_filter: Optional[str] = None
) -> List[Dict[str, Any]]:
    """
    Perform a semantic similarity search against ChromaDB.

    Args:
        query_text:    The user's natural language query.
        n_results:     Number of top results to return.
        source_filter: Optional — filter by department source ('hr', 'sales', 'finance', 'support').

    Returns:
        List of result dicts with 'id', 'text', 'metadata', 'distance'.
    """
    collection = get_collection()

    if collection.count() == 0:
        logger.warning("ChromaDB collection is empty. Please run /api/reindex first.")
        return []

    where_clause = {"source": source_filter} if source_filter else None

    try:
        results = collection.query(
            query_texts=[query_text],
            n_results=min(n_results, collection.count()),
            where=where_clause,
            include=["documents", "metadatas", "distances"],
        )

        output = []
        if results and results["ids"] and results["ids"][0]:
            for i, doc_id in enumerate(results["ids"][0]):
                output.append({
                    "id":       doc_id,
                    "text":     results["documents"][0][i],
                    "metadata": results["metadatas"][0][i],
                    "distance": round(results["distances"][0][i], 4),
                })
        return output

    except Exception as e:
        logger.error(f"ChromaDB query error: {e}")
        return []


def get_collection_stats() -> Dict[str, Any]:
    """Returns count of documents in ChromaDB collection."""
    try:
        collection = get_collection()
        count = collection.count()
        return {
            "total_documents": count,
            "collection_name": COLLECTION_NAME,
            "status": "ready" if count > 0 else "empty",
        }
    except Exception as e:
        return {"total_documents": 0, "status": "error", "error": str(e)}


def reset_collection() -> bool:
    """Deletes and recreates the ChromaDB collection (used by /api/reindex)."""
    global _collection
    try:
        client = get_chroma_client()
        client.delete_collection(COLLECTION_NAME)
        _collection = None
        get_collection()  # recreate
        logger.info("ChromaDB collection reset successfully.")
        return True
    except Exception as e:
        logger.error(f"Error resetting ChromaDB collection: {e}")
        return False
