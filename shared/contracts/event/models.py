"""Contract for the `signal.created` event published by the Signal Engine to Streaming.

Locked field-level contract — see docs/architecture/DomainContract.txt, section
"Signal Engine -> Streaming". Not yet consumed; the signal-engine service publishes
this in a later increment.
"""

from datetime import datetime
from typing import Any, Dict

from pydantic import BaseModel


class SignalCreatedEvent(BaseModel):
    event_id: str
    event_type: str = "signal.created"
    event_version: str
    produced_ts_utc: datetime
    correlation_id: str
    payload: Dict[str, Any]
