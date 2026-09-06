from datetime import datetime, timezone

import pytest

from contracts.event.models import SignalCreatedEvent


@pytest.mark.contract
def test_signal_created_event_parses():
    event = SignalCreatedEvent(
        event_id="evt-1",
        event_version="1.0",
        produced_ts_utc=datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc),
        correlation_id="corr-1",
        payload={"symbol": "NQ1!", "signal": "LONG"},
    )
    assert event.event_type == "signal.created"
