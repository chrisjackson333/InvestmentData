from datetime import datetime, timezone
from decimal import Decimal

import pytest
from contracts.market_tick.models import RawMarketBar

from aggregation.candles import aggregate_to_5min_candles


def _bar(minute: int, open_: str, high: str, low: str, close: str, volume: int) -> RawMarketBar:
    return RawMarketBar(
        symbol="NQ1!",
        timestamp=datetime(2026, 9, 4, 13, minute, tzinfo=timezone.utc),
        open=Decimal(open_),
        high=Decimal(high),
        low=Decimal(low),
        close=Decimal(close),
        volume=volume,
    )


@pytest.mark.unit
def test_full_window_has_no_gap_flag():
    bars = [_bar(m, "100", "101", "99", "100.5", 10) for m in range(30, 35)]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    assert len(candles) == 1
    assert candles[0].quality_flags == []


@pytest.mark.unit
def test_incomplete_window_flag_format():
    bars = [_bar(m, "100", "101", "99", "100.5", 10) for m in (30, 31, 32)]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    assert candles[0].quality_flags == ["incomplete_window:3/5"]


@pytest.mark.unit
@pytest.mark.parametrize("present", [1, 2, 3, 4])
def test_incomplete_window_various_counts(present):
    bars = [_bar(30 + i, "100", "101", "99", "100.5", 10) for i in range(present)]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    assert candles[0].quality_flags == [f"incomplete_window:{present}/5"]


@pytest.mark.unit
def test_open_high_low_close_math():
    bars = [
        _bar(30, "100", "105", "95", "101", 10),
        _bar(31, "101", "110", "90", "102", 10),
        _bar(32, "102", "103", "101", "103", 10),
    ]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    candle = candles[0]
    assert candle.open == Decimal("100")
    assert candle.close == Decimal("103")
    assert candle.high == Decimal("110")
    assert candle.low == Decimal("90")


@pytest.mark.unit
def test_volume_is_sum_of_window():
    bars = [_bar(m, "100", "101", "99", "100.5", 10) for m in (30, 31, 32)]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    assert candles[0].volume == Decimal(30)
    assert isinstance(candles[0].volume, Decimal)


@pytest.mark.unit
def test_clock_alignment_boundaries():
    bars = [
        _bar(34, "100", "101", "99", "100.5", 10),
        _bar(35, "101", "102", "100", "101.5", 10),
        _bar(39, "102", "103", "101", "102.5", 10),
    ]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    assert len(candles) == 2
    assert candles[0].candle_ts_utc == datetime(2026, 9, 4, 13, 30, tzinfo=timezone.utc)
    assert candles[1].candle_ts_utc == datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc)


@pytest.mark.unit
def test_multiple_windows_produce_multiple_candles_in_order():
    bars = [_bar(m, "100", "101", "99", "100.5", 10) for m in (30, 35, 40)]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    assert len(candles) == 3
    timestamps = [c.candle_ts_utc for c in candles]
    assert timestamps == sorted(timestamps)


@pytest.mark.unit
def test_unsorted_input_raises():
    bars = [
        _bar(31, "100", "101", "99", "100.5", 10),
        _bar(30, "100", "101", "99", "100.5", 10),
    ]
    with pytest.raises(ValueError):
        aggregate_to_5min_candles(bars, source_batch_id="batch-1")


@pytest.mark.unit
def test_empty_input_returns_empty_list():
    assert aggregate_to_5min_candles([], source_batch_id="batch-1") == []


@pytest.mark.unit
def test_source_batch_id_is_inherited():
    bars = [_bar(30, "100", "101", "99", "100.5", 10)]
    candles = aggregate_to_5min_candles(bars, source_batch_id="NQ1!_20260904_abcd1234")
    assert candles[0].source_batch_id == "NQ1!_20260904_abcd1234"


@pytest.mark.unit
def test_window_with_single_bar():
    bars = [_bar(30, "100", "101", "99", "100.5", 10)]
    candles = aggregate_to_5min_candles(bars, source_batch_id="batch-1")
    candle = candles[0]
    assert candle.open == Decimal("100")
    assert candle.close == Decimal("100.5")
    assert candle.high == Decimal("101")
    assert candle.low == Decimal("99")
    assert candle.quality_flags == ["incomplete_window:1/5"]
