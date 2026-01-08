from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    # - In docker-compose, DATABASE_URL is provided for Postgres.
    # - For local dev (no env var), fall back to SQLite.
    DATABASE_URL: str = "sqlite:///./recruitment.db"

    # JWT
    # SECRET_KEY kept for backwards compatibility; JWT_SECRET is what the app uses.
    SECRET_KEY: str = "CHANGE_ME_SUPER_SECRET"
    JWT_SECRET: str = "CHANGE_ME_SUPER_SECRET"
    JWT_ALG: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    SMTP_HOST: str = ""
    SMTP_PORT: int = 587
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = ""

    # LM Studio's OpenAI-compatible server typically exposes endpoints under /v1
    # (e.g., http://localhost:1234/v1/chat/completions).
    LLM_BASE_URL: str = "http://host.docker.internal:1234/v1"
    # Leave empty to run the app without an LLM.
    LLM_API_KEY: str = "lm-studio"
    LLM_MODEL: str = "openai/gpt-oss-20b"

settings = Settings()
