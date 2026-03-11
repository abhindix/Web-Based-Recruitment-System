from typing import List
from pydantic import field_validator
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    # - In docker-compose, DATABASE_URL is provided for Postgres.
    # - For local dev (no env var), fall back to SQLite.
    DATABASE_URL: str = "sqlite:///./recruitment.db"

    # JWT
    SECRET_KEY: str = "CHANGE_ME_SUPER_SECRET"
    JWT_SECRET: str = "CHANGE_ME_SUPER_SECRET"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # CORS — comma-separated list of allowed origins.
    # Example: "http://localhost:5173,https://yourapp.example.com"
    CORS_ORIGINS: List[str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    @field_validator("CORS_ORIGINS", mode="before")
    @classmethod
    def parse_cors_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(",") if origin.strip()]
        return v

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # LM Studio's OpenAI-compatible server typically exposes endpoints under /v1
    # (e.g., http://localhost:1234/v1/chat/completions).
    LLM_BASE_URL: str = "http://host.docker.internal:1234/v1"
    # Leave empty to run the app without an LLM.
    LLM_API_KEY: str = ""
    LLM_MODEL: str = "openai/gpt-oss-20b"

    # Seed admin user — leave both empty to skip seeding.
    SEED_ADMIN_EMAIL: str = ""
    SEED_ADMIN_PASSWORD: str = ""

settings = Settings()
