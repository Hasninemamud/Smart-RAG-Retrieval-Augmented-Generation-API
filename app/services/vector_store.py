# backend/app/services/vector_store.py
import os
import json
from pathlib import Path
from typing import List, Dict, Any

import faiss
import numpy as np

from app import settings
from app.services.embedding import embed_texts

INDEX_DIR = Path(settings.INDEX_DIR)
FAISS_INDEX_PATH = INDEX_DIR / "faiss.index"
METADATA_PATH = INDEX_DIR / "metadata.json"

_index = None
_metadata: Dict[str, Dict[str, Any]] = {}


def ensure_index():
    global _index, _metadata
    INDEX_DIR.mkdir(parents=True, exist_ok=True)
    if _index is not None:
        return
    if FAISS_INDEX_PATH.exists() and METADATA_PATH.exists():
        try:
            print("Loading FAISS index and metadata...")
            _index = faiss.read_index(str(FAISS_INDEX_PATH))
            with open(METADATA_PATH, "r", encoding="utf-8") as f:
                _metadata = json.load(f)
            print("Loaded index with", int(_index.ntotal), "vectors")
            return
        except Exception as e:
            print("Failed to load index:", e)
    # create new index using dimension from embedder
    # Note: we get embedding dim by embedding a dummy vector
    dummy = embed_texts(["hello"])
    dim = dummy.shape[1]
    _index = faiss.IndexFlatIP(dim)
    _metadata = {}
    persist_index()


def persist_index():
    global _index, _metadata
    faiss.write_index(_index, str(FAISS_INDEX_PATH))
    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(_metadata, f, ensure_ascii=False, indent=2)
    print("Persisted index and metadata.")


def add_documents_to_index(source_name: str, chunks: List[str]) -> int:
    """
    Add list of chunk texts to FAISS and update metadata.
    Returns number of vectors added.
    """
    global _index, _metadata
    if not chunks:
        return 0
    embeddings = embed_texts(chunks)
    n = embeddings.shape[0]
    start_id = int(_index.ntotal)
    _index.add(embeddings)
    for i, txt in enumerate(chunks):
        doc_id = str(start_id + i)
        _metadata[doc_id] = {"source": source_name, "text": txt, "chunk": i}
    persist_index()
    return n


def search_index(query: str, top_k: int = 5) -> List[Dict[str, Any]]:
    """
    Return list of dicts {id, score, source, text}
    """
    global _index, _metadata
    if _index is None or int(_index.ntotal) == 0:
        return []
    q_emb = embed_texts([query])
    D, I = _index.search(q_emb, top_k)
    results = []
    for score, idx in zip(D[0], I[0]):
        if idx < 0:
            continue
        meta = _metadata.get(str(idx), {})
        results.append({"id": str(idx), "score": float(score), "source": meta.get("source"), "text": meta.get("text")})
    return results


def get_index_size() -> int:
    global _index
    if _index is None:
        return 0
    return int(_index.ntotal)
