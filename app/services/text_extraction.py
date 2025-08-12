# backend/app/services/text_extraction.py
import io
import uuid
import sqlite3
from pathlib import Path
from typing import List

from PIL import Image
import pytesseract
from pypdf import PdfReader
import docx
import pandas as pd

from app.services.db_extraction import read_sqlite_db
from app.utils.file_utils import write_temp_file

# NOTE: If tesseract is missing on the system, pytesseract will raise an exception;
# instruct users to install system package (e.g. apt-get install -y tesseract-ocr)


def _read_pdf(file_bytes: bytes) -> str:
    reader = PdfReader(io.BytesIO(file_bytes))
    texts = []
    for p in reader.pages:
        texts.append(p.extract_text() or "")
    return "\n".join(texts)


def _read_docx(file_bytes: bytes) -> str:
    f = io.BytesIO(file_bytes)
    doc = docx.Document(f)
    paragraphs = [p.text for p in doc.paragraphs]
    return "\n".join(paragraphs)


def _read_txt(file_bytes: bytes) -> str:
    return file_bytes.decode(errors="ignore")


def _read_csv(file_bytes: bytes) -> str:
    df = pd.read_csv(io.BytesIO(file_bytes))
    return df.to_csv(index=False)


def _read_image(file_bytes: bytes) -> str:
    image = Image.open(io.BytesIO(file_bytes)).convert("RGB")
    return pytesseract.image_to_string(image)


def extract_text_from_file(filename: str, file_bytes: bytes) -> str:
    name = filename.lower()
    if name.endswith(".pdf"):
        return _read_pdf(file_bytes)
    if name.endswith(".docx") or name.endswith(".doc"):
        return _read_docx(file_bytes)
    if name.endswith(".txt"):
        return _read_txt(file_bytes)
    if name.endswith(".csv"):
        return _read_csv(file_bytes)
    if name.endswith(".db") or name.endswith(".sqlite"):
        # delegate to db_extraction
        return read_sqlite_db(file_bytes)
    if name.endswith(".png") or name.endswith(".jpg") or name.endswith(".jpeg") or name.endswith(".tiff"):
        return _read_image(file_bytes)
    # fallback: try reading as text
    try:
        return _read_txt(file_bytes)
    except Exception:
        return ""
