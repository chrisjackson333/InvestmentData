"""API layer configuration, loaded from env vars prefixed API_."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class ApiSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="API_")

    host: str = "0.0.0.0"
    port: int = 8000
    default_signals_limit: int = 50
    max_signals_limit: int = 500
