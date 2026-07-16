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

    # AWS Authentication
    AWS_REGION: str = "eu-central-1"
    AWS_ACCESS_KEY: str | None = None
    AWS_SECRET_KEY: str | None = None
    AWS_ARN_ROLE: str | None = None

    # UV
    UV_LINK_MODE: str = "copy"

    @classmethod
    def load_settings(cls) -> "Settings":
        settings = cls()
        logger.info("Loaded settings from the environment")
        return settings


settings = Settings.load_settings()
