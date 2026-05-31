import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    PROJECT_NAME: str = "FaithGuide AI Backend"
    DATABASE_PATH: str = os.getenv("DATABASE_PATH", "data/faithguide.db")
    CHROMA_PATH: str = os.getenv("CHROMA_PATH", "data/chromadb")
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    HUGGINGFACE_API_KEY: Optional[str] = os.getenv("HUGGINGFACE_API_KEY", None)
    PORT: int = int(os.getenv("PORT", "8000"))

    class Config:
        env_file = ".env"

settings = Settings()
# Ensure data directory exists
os.makedirs(os.path.dirname(settings.DATABASE_PATH), exist_ok=True)
