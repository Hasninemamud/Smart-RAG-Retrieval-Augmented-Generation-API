# backend/app/services/llm_client.py
import requests
from fastapi import HTTPException

from app import settings


def call_llm_with_prompt(prompt: str, max_tokens: int = 512) -> str:
    kind = settings.RAG_LLM_KIND.lower()
    headers = {}
    if settings.RAG_LLM_API_KEY:
        headers["Authorization"] = f"Bearer {settings.RAG_LLM_API_KEY}"

    if kind == "ollama":
        payload = {"model": settings.RAG_LLM_URL or "meta-llama/llama-3.3-70b-instruct:free", "prompt": prompt, "max_tokens": max_tokens}
        resp = requests.post("http://localhost:11434/api/generate", json=payload, headers=headers, timeout=settings.LLM_TIMEOUT)
        if resp.status_code != 200:
            raise HTTPException(status_code=502, detail="LLM (Ollama) error: " + resp.text)
        data = resp.json()
        if "text" in data:
            return data["text"]
        if "choices" in data and data["choices"]:
            return data["choices"][0].get("message", {}).get("content", "") or data["choices"][0].get("text", "")
        return str(data)

    if kind == "hf":
        if not settings.RAG_LLM_URL:
            raise HTTPException(status_code=500, detail="Missing RAG_LLM_URL for HuggingFace")
        resp = requests.post(settings.RAG_LLM_URL, headers=headers, json={"inputs": prompt, "parameters": {"max_new_tokens": max_tokens}}, timeout=settings.LLM_TIMEOUT)
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail="LLM (HF) error: " + resp.text)
        out = resp.json()
        if isinstance(out, dict) and "generated_text" in out:
            return out["generated_text"]
        if isinstance(out, list) and out and "generated_text" in out[0]:
            return out[0]["generated_text"]
        return str(out)

    # custom: call configured URL expecting JSON response with 'answer' or 'text'
    if kind == "custom":
        if not settings.RAG_LLM_URL:
            raise HTTPException(status_code=500, detail="Missing RAG_LLM_URL for custom LLM")
        resp = requests.post(settings.RAG_LLM_URL, headers=headers, json={"prompt": prompt, "max_tokens": max_tokens}, timeout=settings.LLM_TIMEOUT)
        if resp.status_code not in (200, 201):
            raise HTTPException(status_code=502, detail="LLM (custom) error: " + resp.text)
        out = resp.json()
        if isinstance(out, dict):
            return out.get("answer") or out.get("text") or str(out)
        return str(out)

    raise HTTPException(status_code=500, detail=f"Unsupported RAG_LLM_KIND: {settings.RAG_LLM_KIND}")
