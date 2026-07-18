import os

from pydantic_settings import BaseSettings, SettingsConfigDict
from loguru import logger


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )

    # --- Settings even when working locally. ---

    # Claude API
    CLAUDE_API_KEY_ANTI: str | None = None
    CLAUDE_BASE_URL: str
    CLAUDE_MODEL_ID: str
    SUMMARIZE_MODEL: str

    # Serper API
    SERPER_API_KEY: str | None = None

    # LangSmith
    LANGSMITH_TRACING: bool = False
    LANGSMITH_ENDPOINT: str | None = None
    LANGSMITH_API_KEY: str | None = None
    LANGSMITH_PROJECT: str | None = None

    # AWS Authentication
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None

    # Workflow Settings
    CONFIDENCE_THRESHOLD: float
    MAX_RETRIES: int
    ADD_MAX_RESULTS: int

    # UV
    UV_LINK_MODE: str = "copy"

    @classmethod
    def load_settings(cls) -> "Settings":
        settings = cls()
        if settings.LANGSMITH_TRACING:
            os.environ["LANGSMITH_TRACING"] = "true"
        if settings.LANGSMITH_ENDPOINT:
            os.environ["LANGSMITH_ENDPOINT"] = settings.LANGSMITH_ENDPOINT
        if settings.LANGSMITH_API_KEY:
            os.environ["LANGSMITH_API_KEY"] = settings.LANGSMITH_API_KEY
        if settings.LANGSMITH_PROJECT:
            os.environ["LANGSMITH_PROJECT"] = settings.LANGSMITH_PROJECT
        logger.info("Loaded settings from the environment")
        return settings


settings = Settings.load_settings()
