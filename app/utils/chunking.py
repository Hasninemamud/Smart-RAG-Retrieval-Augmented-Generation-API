# backend/app/utils/chunking.py
from typing import List
from app import settings


def clean_text(s: str) -> str:
    return " ".join(s.split())


def chunk_text(text: str, chunk_size: int = None, overlap: int = None) -> List[str]:
    """
    Simple whitespace tokenizer chunker.
    Splits text into chunks of ~chunk_size tokens with specified overlap.
    """
    chunk_size = chunk_size or settings.CHUNK_SIZE
    overlap = overlap or settings.CHUNK_OVERLAP
    text = text.strip()
    if not text:
        return []
    tokens = text.split()
    chunks = []
    i = 0
    n = len(tokens)
    while i < n:
        chunk_tokens = tokens[i : i + chunk_size]
        chunks.append(" ".join(chunk_tokens))
        i += chunk_size - overlap
    return chunks


def build_prompt(question: str, context_chunks):
    lines = [
        "You are a helpful assistant. Use the provided context to answer the question. "
        "If the answer is not contained in the context, say you don't know. Provide concise, factual answers and cite sources by filename and chunk index."
    ]
    lines.append("\nCONTEXT:\n")
    for c in context_chunks:
        header = f"Source: {c.get('source')} (score: {c.get('score'):.4f}, id: {c.get('id')})"
        lines.append(header)
        chunk_text = c.get("text") or ""
        if len(chunk_text) > 2000:
            chunk_text = chunk_text[:2000] + "..."
        lines.append(chunk_text)
        lines.append("\n")
    lines.append("\nQUESTION:\n" + question)
    lines.append("\nAnswer with source citations like [source:filename chunk:idx].")
    return "\n".join(lines)
