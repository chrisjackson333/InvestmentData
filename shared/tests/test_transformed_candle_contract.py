from datetime import datetime, timezone
from decimal import Decimal

import pytest

from contracts.transformed_candle.models import TransformedCandle


@pytest.mark.contract
def test_transformed_candle_round_trip():
    candle = TransformedCandle(
        symbol="NQ1!",
        candle_ts_utc=datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc),
        open=Decimal("100.0"),
        high=Decimal("101.0"),
        low=Decimal("99.5"),
        close=Decimal("100.5"),
        volume=Decimal("5000"),
        source_batch_id="NQ1!_20260904_abcd1234",
        quality_flags=["gap_filled"],
    )
    assert candle.quality_flags == ["gap_filled"]


@pytest.mark.contract
def test_quality_flags_defaults_empty():
    candle = TransformedCandle(
        symbol="NQ1!",
        candle_ts_utc=datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc),
        open=Decimal("100.0"),
        high=Decimal("101.0"),
        low=Decimal("99.5"),
        close=Decimal("100.5"),
        volume=Decimal("5000"),
        source_batch_id="NQ1!_20260904_abcd1234",
    )
    assert candle.quality_flags == []
