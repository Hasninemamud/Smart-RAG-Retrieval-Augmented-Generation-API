# backend/app/main.py
import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routes import upload, query
from app import settings
from app.services.vector_store import ensure_index

app = FastAPI(title="Smart RAG API")

# CORS (for the lightweight UI)
origins = [o.strip() for o in settings.CORS_ORIGINS.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins or ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# include routers
app.include_router(upload.router, prefix="", tags=["upload"])
app.include_router(query.router, prefix="", tags=["query"])


@app.on_event("startup")
def startup():
    # ensure index directory exists and load or create index
    os.makedirs(settings.INDEX_DIR, exist_ok=True)
    ensure_index()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
