# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict
from pathlib import Path

class Settings(BaseSettings):
    WREN_AI_BASE_URL: str
    BACKEND_URL: str
    SPEECHMATICS_API_KEY: str

    model_config = SettingsConfigDict(
        env_file=str(Path(__file__).parent / ".env"),
        env_file_encoding="utf-8"
    )

settings = Settings()