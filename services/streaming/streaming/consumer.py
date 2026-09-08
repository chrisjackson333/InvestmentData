"""Minimal Kafka consumer: logs each signal.created event received.

Not a full read-model/audit-table service — proves the event flows
end-to-end. max_messages=None runs long (real use via
`python -m streaming.consumer`); max_messages=N bounds the loop for
tests/demos and returns the collected events.
"""

import json
import logging
from typing import List, Optional

from confluent_kafka import Consumer
from contracts.event.models import SignalCreatedEvent

from .streaming_config import KafkaSettings
from .topics import SIGNAL_CREATED_TOPIC

logger = logging.getLogger(__name__)


def run_consumer(
    settings: Optional[KafkaSettings] = None,
    max_messages: Optional[int] = None,
    timeout_s: float = 1.0,
) -> List[SignalCreatedEvent]:
    settings = settings or KafkaSettings()
    consumer = Consumer(
        {
            "bootstrap.servers": settings.bootstrap_servers,
            "group.id": settings.consumer_group_id,
            "auto.offset.reset": "earliest",
        }
    )
    consumer.subscribe([SIGNAL_CREATED_TOPIC])
    events: List[SignalCreatedEvent] = []
    try:
        while max_messages is None or len(events) < max_messages:
            msg = consumer.poll(timeout=timeout_s)
            if msg is None:
                continue
            if msg.error():
                logger.error("Kafka consume error: %s", msg.error())
                continue
            event = SignalCreatedEvent.model_validate(json.loads(msg.value()))
            logger.info("Received signal.created event: %s", event.model_dump())
            events.append(event)
    finally:
        consumer.close()
    return events


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    run_consumer(max_messages=None)
