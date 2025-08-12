# Smart RAG — Retrieval-Augmented Generation API

## Overview

Smart RAG is a powerful API service built with **FastAPI** that enables question answering over uploaded documents of various formats — PDFs, Word files, images (via OCR), text files, CSVs, and even small SQLite databases. The system extracts text, embeds content into a FAISS vector store, and uses a Large Language Model (LLM) to generate answers based on relevant context retrieved from the documents.

A lightweight **Streamlit** frontend allows users to upload documents and ask questions interactively.

---

## Features

* Accepts multiple document formats:

  * PDF, DOCX, TXT, CSV
  * Images: JPG, PNG, TIFF (OCR text extraction)
  * SQLite database files
* Extracts and preprocesses text, chunks it intelligently
* Creates vector embeddings using SentenceTransformers
* Stores embeddings and metadata in a FAISS index for similarity search
* Supports configurable LLM backends (Ollama, HuggingFace, or custom)
* Provides REST API endpoints for uploading documents and querying
* Minimal Streamlit web UI for document upload and interactive Q\&A

---

## Architecture

```
User --> Frontend (Streamlit)
              |
              v
       FastAPI Backend
     /                \
Document Processing    LLM Adapter
     |                      |
Text Extraction --> Embedding --> FAISS Vector Store --> Similarity Search
                                                 |
                                                 v
                                       Context + Question --> LLM --> Answer
```

---

## Getting Started

### Prerequisites

* Python 3.8+
* System dependencies for OCR (Tesseract)
* FAISS (CPU) installed
* Optional: Ollama or HuggingFace LLM service or custom LLM API

---

### Installation

```bash
# Clone repository
git clone https://github.com/yourusername/smart-rag.git
cd smart-rag

# Create virtual environment and activate
python -m venv venv
source venv/bin/activate  # Linux/macOS
# .\venv\Scripts\activate  # Windows

# Install dependencies
pip install -r requirements.txt

# Install system packages (Ubuntu example)
sudo apt-get install -y tesseract-ocr libtesseract-dev
```

---

### Configuration

Create a `.env` file in the project root:

```env
EMBEDDING_MODEL=all-MiniLM-L6-v2
INDEX_DIR=./indexes

RAG_LLM_KIND=custom
RAG_LLM_URL=http://localhost:5000/llm
RAG_LLM_API_KEY=your_api_key_here
```

Modify values to your environment.

---

### Running the API Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

API will be accessible at `http://localhost:8000`

---

### Running the Streamlit Frontend

```bash
cd frontend
pip install streamlit requests
streamlit run app.py
```

Open browser at `http://localhost:8501` by default.

---

## API Reference

### POST `/upload`

Upload one or more documents for indexing.

* Request: Multipart form-data with files field
* Response: JSON mapping filenames to number of chunks indexed or errors

Example:

```bash
curl -F "files=@doc1.pdf" -F "files=@image.png" http://localhost:8000/upload
```

---

### POST `/query`

Ask a question based on indexed documents.

* Request body (JSON):

```json
{
  "question": "What is the refund policy?",
  "top_k": 5  # Optional, default=5
}
```

* Response:

```json
{
  "answer": "... generated answer ...",
  "sources": [
    {
      "id": "123",
      "score": 0.987,
      "source": "doc1.pdf",
      "text": "..."
    }
  ]
}
```

---

### GET `/info`

Get info about index size.

* Response:

```json
{
  "vectors": 1000,
  "metadata_entries": 1000
}
```

---

## Folder Structure

```
smart-rag/
├── app/
│   ├── main.py          # FastAPI app and routes
│   ├── embedding.py     # Embedding and FAISS index logic
│   ├── extractor.py     # Document text extraction utilities
│   ├── llm.py           # LLM adapter and prompt builder
│   ├── config.py        # Env and config loader
│   └── utils.py         # Helper functions (chunking, cleaning)
├── frontend/
│   └── app.py           # Streamlit frontend app
├── requirements.txt
├── .env
└── README.md
```

---






