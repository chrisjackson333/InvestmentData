"""Kafka producer: publishes signal.created events.

Reliability: synchronous produce() + flush() before returning — a real
delivery acknowledgment, but no custom retry/DLQ system (deferred, see
docs/backlog/TODO.txt item 15).
"""

import logging
from typing import Optional

from confluent_kafka import Producer
from contracts.signal.models import LatestSignal

from .events import build_signal_created_event
from .streaming_config import KafkaSettings
from .topics import SIGNAL_CREATED_TOPIC

logger = logging.getLogger(__name__)


def _delivery_callback(err, msg) -> None:
    if err is not None:
        logger.error("Kafka delivery failed for topic=%s: %s", msg.topic(), err)


def publish_signal_created(
    signal: LatestSignal,
    correlation_id: str,
    settings: Optional[KafkaSettings] = None,
) -> None:
    settings = settings or KafkaSettings()
    event = build_signal_created_event(signal, correlation_id)
    producer = Producer({"bootstrap.servers": settings.bootstrap_servers})
    producer.produce(
        SIGNAL_CREATED_TOPIC,
        value=event.model_dump_json().encode("utf-8"),
        callback=_delivery_callback,
    )
    producer.flush(timeout=10)
