# backend/app/routes/query.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Optional

from app.services.vector_store import search_index, get_index_size
from app.services.llm_client import call_llm_with_prompt
from app.utils.chunking import build_prompt

router = APIRouter()


class QueryRequest(BaseModel):
    question: str
    top_k: Optional[int] = 5


@router.post("/query")
async def query(req: QueryRequest):
    if get_index_size() == 0:
        raise HTTPException(status_code=404, detail="Index is empty. Upload documents first.")
    q = req.question
    top_k = req.top_k or 5
    results = search_index(q, top_k=top_k)
    prompt = build_prompt(q, results)
    answer = call_llm_with_prompt(prompt)
    return {"answer": answer, "sources": results}


@router.get("/info")
def info():
    return {"vectors": get_index_size()}
