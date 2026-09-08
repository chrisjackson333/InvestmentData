"""Pure event construction — no Kafka I/O.

Mirrors signal-engine's split of pure strategy logic (strategy/sma20.py)
from I/O (persistence/signals.py): this module builds the SignalCreatedEvent,
producer.py is the only place that touches Kafka.
"""

import uuid
from datetime import datetime, timezone

from contracts.event.models import SignalCreatedEvent
from contracts.signal.models import LatestSignal

EVENT_VERSION = "1.0"


def build_signal_created_event(signal: LatestSignal, correlation_id: str) -> SignalCreatedEvent:
    return SignalCreatedEvent(
        event_id=str(uuid.uuid4()),
        event_version=EVENT_VERSION,
        produced_ts_utc=datetime.now(timezone.utc),
        correlation_id=correlation_id,
        payload=signal.model_dump(mode="json"),
    )
