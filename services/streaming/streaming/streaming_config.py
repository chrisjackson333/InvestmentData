"""Streaming domain configuration: Kafka connection settings (KAFKA_)."""

from pydantic_settings import BaseSettings, SettingsConfigDict


class KafkaSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="KAFKA_")

    bootstrap_servers: str = "localhost:9092"
    consumer_group_id: str = "investment-platform-streaming-consumer"
