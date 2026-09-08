"""Cross-domain contract test: verifies the streaming domain's event
construction conforms to the shared event contract, built from a real
signal produced by the actual ingestion->transform->signal pipeline.
"""

from pathlib import Path

import pytest
from aggregation.candles import aggregate_to_5min_candles
from aggregation.reader import read_raw_zone_bars
from contracts.event.models import SignalCreatedEvent
from strategy.sma20 import compute_sma20_signal
from streaming.events import build_signal_created_event

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"
SMA20_SAMPLE_JSONL = FIXTURE_ROOT / "market_data" / "nq1_1min_sma20_sample.jsonl"


@pytest.mark.contract
def test_signal_created_event_conforms_to_contract():
    bars = read_raw_zone_bars(SMA20_SAMPLE_JSONL)
    candles = aggregate_to_5min_candles(bars, source_batch_id="NQ1!_20260904_test0001")
    signal = compute_sma20_signal(candles)
    assert signal is not None

    event = build_signal_created_event(signal, correlation_id="NQ1!_20260904_test0001")

    assert isinstance(event, SignalCreatedEvent)
    SignalCreatedEvent.model_validate(event.model_dump())
    assert event.event_type == "signal.created"
    assert event.correlation_id == "NQ1!_20260904_test0001"
    assert event.payload["symbol"] == "NQ1!"
