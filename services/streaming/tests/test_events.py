from datetime import datetime, timezone
from decimal import Decimal

import pytest
from contracts.signal.models import LatestSignal

from streaming.events import build_signal_created_event


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


@pytest.mark.unit
def test_event_type_defaults_to_signal_created():
    event = build_signal_created_event(_signal(), correlation_id="corr-1")
    assert event.event_type == "signal.created"


@pytest.mark.unit
def test_event_ids_are_unique_across_calls():
    e1 = build_signal_created_event(_signal(), correlation_id="corr-1")
    e2 = build_signal_created_event(_signal(), correlation_id="corr-1")
    assert e1.event_id != e2.event_id


@pytest.mark.unit
def test_correlation_id_passed_through():
    event = build_signal_created_event(_signal(), correlation_id="NQ1!_20260904_abcd1234")
    assert event.correlation_id == "NQ1!_20260904_abcd1234"


@pytest.mark.unit
def test_payload_matches_signal_dump():
    signal = _signal()
    event = build_signal_created_event(signal, correlation_id="corr-1")
    assert event.payload == signal.model_dump(mode="json")


@pytest.mark.unit
def test_produced_ts_is_utc_aware():
    event = build_signal_created_event(_signal(), correlation_id="corr-1")
    assert event.produced_ts_utc.tzinfo is not None
    assert event.produced_ts_utc.utcoffset() == timezone.utc.utcoffset(None)


@pytest.mark.unit
def test_decimal_fields_serialize_as_json_compatible():
    signal = _signal()
    event = build_signal_created_event(signal, correlation_id="corr-1")
    # payload must be JSON-round-trippable (no raw Decimal objects)
    assert not any(isinstance(v, Decimal) for v in event.payload.values())
