from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest
from contracts.transformed_candle.models import TransformedCandle

from strategy.sma20 import compute_sma20_signal


def _candle(close: str, minute_offset: int, source_batch_id: str = "batch-1") -> TransformedCandle:
    ts = datetime(2026, 9, 4, 13, 0, tzinfo=timezone.utc) + timedelta(minutes=5 * minute_offset)
    close_dec = Decimal(close)
    return TransformedCandle(
        symbol="NQ1!",
        candle_ts_utc=ts,
        open=close_dec,
        high=close_dec + Decimal("1"),
        low=close_dec - Decimal("1"),
        close=close_dec,
        volume=Decimal("1000"),
        source_batch_id=source_batch_id,
    )


@pytest.mark.unit
def test_insufficient_history_returns_none():
    candles = [_candle("100", i) for i in range(19)]
    assert compute_sma20_signal(candles) is None


@pytest.mark.unit
def test_exactly_20_candles_computes_signal():
    candles = [_candle("100", i) for i in range(19)] + [_candle("105", 19)]
    signal = compute_sma20_signal(candles)
    assert signal is not None


@pytest.mark.unit
def test_close_above_sma_returns_long():
    candles = [_candle("100", i) for i in range(19)] + [_candle("110", 19)]
    signal = compute_sma20_signal(candles)
    assert signal.signal == "LONG"
    assert signal.reason_code == "close_above_sma20"


@pytest.mark.unit
def test_close_below_sma_returns_hold():
    candles = [_candle("100", i) for i in range(19)] + [_candle("90", 19)]
    signal = compute_sma20_signal(candles)
    assert signal.signal == "HOLD"
    assert signal.reason_code == "close_at_or_below_sma20"


@pytest.mark.unit
def test_close_equal_sma_returns_hold():
    candles = [_candle("100", i) for i in range(20)]
    signal = compute_sma20_signal(candles)
    assert signal.signal == "HOLD"
    assert signal.reason_code == "close_at_or_below_sma20"


@pytest.mark.unit
def test_signal_ts_uses_latest_candle_timestamp():
    candles = [_candle("100", i) for i in range(19)] + [_candle("110", 19)]
    signal = compute_sma20_signal(candles)
    assert signal.signal_ts_utc == candles[-1].candle_ts_utc


@pytest.mark.unit
def test_input_ref_uses_latest_candle_source_batch_id():
    candles = [_candle("100", i, source_batch_id="old-batch") for i in range(19)]
    candles.append(_candle("110", 19, source_batch_id="new-batch"))
    signal = compute_sma20_signal(candles)
    assert signal.input_ref == "new-batch"


@pytest.mark.unit
def test_only_trailing_window_considered():
    # Older candles prepended ahead of the trailing 20 must not affect the
    # computed SMA or the resulting signal at all.
    trailing = [_candle("100", i) for i in range(19)] + [_candle("100.5", 19)]
    signal_without_extra = compute_sma20_signal(trailing)

    older = [_candle("10", i) for i in range(5)]
    signal_with_extra = compute_sma20_signal(older + trailing)

    assert signal_with_extra.signal == signal_without_extra.signal
    assert signal_with_extra.signal_ts_utc == signal_without_extra.signal_ts_utc


@pytest.mark.unit
def test_strategy_and_timeframe_fields_fixed():
    candles = [_candle("100", i) for i in range(19)] + [_candle("110", 19)]
    signal = compute_sma20_signal(candles)
    assert signal.strategy == "sma20_long_only"
    assert signal.timeframe == "5m"


@pytest.mark.unit
def test_custom_sma_period_parameter():
    candles = [_candle("100", i) for i in range(4)] + [_candle("110", 4)]
    signal = compute_sma20_signal(candles, sma_period=5)
    assert signal is not None
    assert signal.signal == "LONG"
