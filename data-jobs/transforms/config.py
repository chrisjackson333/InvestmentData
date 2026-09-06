"""Transforms domain configuration, loaded from env vars prefixed TRANSFORM_."""

from pathlib import Path

from pydantic_settings import BaseSettings, SettingsConfigDict


class TransformSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="TRANSFORM_")

    raw_zone_root: Path = Path("./.localstack_raw")
    transformed_zone_root: Path = Path("./.localstack_transformed")
