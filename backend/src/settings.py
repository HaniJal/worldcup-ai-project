from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{BASE_DIR}/.env", extra="ignore"
    )
    DATABASE_URL: str
    POSTGRES_USER: str =""
    POSTGRES_PASSWORD: str = ""
    POSTGRES_DB: str = ""

    QDRANT_URL: str = "http://qdrant:6333"
    QDRANT_COLLECTION: str = "worldcup_knowledge"
    EMBEDDING_MODEL_NAME: str = "all-MiniLM-L6-v2"

    ANTHROPIC_API_KEY: str = ""
    ANTHROPIC_MODEL: str = "claude-haiku-4-5-20251001"

    
settings = Settings()
