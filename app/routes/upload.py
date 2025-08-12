# backend/app/routes/upload.py
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from typing import List

from app.services.text_extraction import extract_text_from_file
from app.utils.chunking import clean_text, chunk_text
from app.services.vector_store import add_documents_to_index, get_index_size

router = APIRouter()


@router.post("/upload")
async def upload(files: List[UploadFile] = File(...)):
    """
    Upload and index documents. Accepts multiple files.
    Returns per-file result: chunks_added or error.
    """
    results = {}
    for f in files:
        name = f.filename
        try:
            body = await f.read()
            text = extract_text_from_file(name, body)
            text = clean_text(text)
            chunks = chunk_text(text)
            n = add_documents_to_index(name, chunks)
            results[name] = {"chunks_added": n}
        except Exception as e:
            # do not crash entire upload on one file
            results[name] = {"error": str(e)}
    return JSONResponse(results)
