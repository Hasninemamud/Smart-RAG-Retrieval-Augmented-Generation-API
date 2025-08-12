# backend/app/config.py
from pydantic import BaseSettings, Field


class Settings(BaseSettings):
    EMBEDDING_MODEL: str = Field("all-MiniLM-L6-v2", env="EMBEDDING_MODEL")
    INDEX_DIR: str = Field("./indexes", env="INDEX_DIR")
    RAG_LLM_KIND: str = Field("custom", env="RAG_LLM_KIND")  # 'ollama'|'hf'|'custom'
    RAG_LLM_URL: str = Field("", env="RAG_LLM_URL")
    RAG_LLM_API_KEY: str = Field("", env="RAG_LLM_API_KEY")
    CHUNK_SIZE: int = Field(800, env="CHUNK_SIZE")
    CHUNK_OVERLAP: int = Field(200, env="CHUNK_OVERLAP")
    EMBEDDING_BATCH: int = Field(64, env="EMBEDDING_BATCH")
    CORS_ORIGINS: str = Field("*", env="CORS_ORIGINS")  # comma separated
    # LLM call timeout seconds
    LLM_TIMEOUT: int = Field(120, env="LLM_TIMEOUT")

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
