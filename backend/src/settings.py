from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

Base_DIR = Path(__file__).resolve.parent.parent.parent

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=f"{Base_DIR}/.env", extra="ignore"
    )
    DATABASE_URL: str
    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str

    
settings = Settings()
