import pytest

from streaming.streaming_config import KafkaSettings


@pytest.mark.unit
def test_kafka_settings_defaults(monkeypatch):
    monkeypatch.delenv("KAFKA_BOOTSTRAP_SERVERS", raising=False)
    monkeypatch.delenv("KAFKA_CONSUMER_GROUP_ID", raising=False)
    settings = KafkaSettings()
    assert settings.bootstrap_servers == "localhost:9092"
    assert settings.consumer_group_id == "investment-platform-streaming-consumer"


@pytest.mark.unit
def test_kafka_settings_reads_env_prefix(monkeypatch):
    monkeypatch.setenv("KAFKA_BOOTSTRAP_SERVERS", "broker1:9092,broker2:9092")
    settings = KafkaSettings()
    assert settings.bootstrap_servers == "broker1:9092,broker2:9092"
