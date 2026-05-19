# app/config.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    DB_USER: str
    DB_PASSWORD: str
    DB_HOST: str
    DB_PORT: int
    DB_NAME: str

    WREN_AI_BASE_URL: str
    BACKEND_URL: str
    SPEECHMATICS_API_KEY: str

    model_config = SettingsConfigDict(
        env_file="./modules/.env",
        env_file_encoding="utf-8"
    )

settings = Settings()