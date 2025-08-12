# backend/app/services/embedding.py
from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer

from app import settings

# Singleton embedder
_embedder: SentenceTransformer = None


def get_embedder() -> SentenceTransformer:
    global _embedder
    if _embedder is None:
        print("Loading embedding model:", settings.EMBEDDING_MODEL)
        _embedder = SentenceTransformer(settings.EMBEDDING_MODEL)
    return _embedder


def embed_texts(texts: List[str], batch_size: int = None) -> np.ndarray:
    embedder = get_embedder()
    batch_size = batch_size or settings.EMBEDDING_BATCH
    embeddings = embedder.encode(texts, batch_size=batch_size, show_progress_bar=False)
    arr = np.array(embeddings, dtype="float32")
    # normalize
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1e-9
    arr = arr / norms
    return arr
