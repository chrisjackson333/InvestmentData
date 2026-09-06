"""Ingestion domain configuration, loaded from env vars prefixed INGESTION_."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class IngestionSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="INGESTION_")

    raw_zone_root: Path = Path("./.localstack_raw")
    source: str = "csv"
    strict_validation: bool = False
