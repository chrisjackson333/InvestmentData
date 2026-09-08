"""Producer/consumer round-trip against a real Kafka broker.

Requires `docker compose up -d kafka` (see repo-root docker-compose.yml)
before running. Deferred from the base quality gate per Standards.txt's
allowance for integration tests to be reserved for the merge/main pipeline.
"""

from datetime import datetime, timezone

import pytest
from contracts.signal.models import LatestSignal

from streaming.consumer import run_consumer
from streaming.producer import publish_signal_created


def _signal() -> LatestSignal:
    return LatestSignal(
        symbol="NQ1!",
        timeframe="5m",
        signal="LONG",
        strategy="sma20_long_only",
        signal_ts_utc=datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc),
        reason_code="close_above_sma20",
        input_ref="NQ1!_20260904_test0001",
    )


@pytest.mark.integration
def test_publish_and_consume_round_trip():
    publish_signal_created(_signal(), correlation_id="corr-it-1")
    events = run_consumer(max_messages=1, timeout_s=15)
    assert len(events) == 1
    assert events[0].correlation_id == "corr-it-1"
    assert events[0].payload["symbol"] == "NQ1!"
