"""SMA20 long-only signal decisioning (Domain 2: Signal Engine).

Pure function: no I/O, no DB. Trusts that `candles` arrives sorted ascending
by candle_ts_utc (transforms' aggregate_to_5min_candles guarantees this) and
does not re-sort.
"""

from typing import List, Optional

from contracts.signal.models import LatestSignal
from contracts.transformed_candle.models import TransformedCandle

SMA_PERIOD = 20

REASON_CLOSE_ABOVE_SMA20 = "close_above_sma20"
REASON_CLOSE_AT_OR_BELOW_SMA20 = "close_at_or_below_sma20"
REASON_INSUFFICIENT_HISTORY = "insufficient_history"


def compute_sma20_signal(
    candles: List[TransformedCandle], sma_period: int = SMA_PERIOD
) -> Optional[LatestSignal]:
    """Compute the latest SMA20 long-only signal from a candle series.

    Rule: if the latest candle's close is strictly greater than the trailing
    `sma_period`-period SMA of closes, signal = LONG; else HOLD. No
    crossover/state tracking — purely a function of the latest window.

    Returns None if fewer than `sma_period` candles are available. The
    caller (orchestration) treats None as "skip persistence this run"
    rather than an error; REASON_INSUFFICIENT_HISTORY documents that case
    for callers/logs but is never attached to a persisted LatestSignal,
    since a LatestSignal cannot be constructed without a real signal.
    """
    if len(candles) < sma_period:
        return None

    window = candles[-sma_period:]
    latest = window[-1]
    sma = sum(c.close for c in window) / sma_period

    if latest.close > sma:
        signal, reason_code = "LONG", REASON_CLOSE_ABOVE_SMA20
    else:
        signal, reason_code = "HOLD", REASON_CLOSE_AT_OR_BELOW_SMA20

    return LatestSignal(
        symbol=latest.symbol,
        timeframe="5m",
        signal=signal,
        strategy="sma20_long_only",
        signal_ts_utc=latest.candle_ts_utc,
        reason_code=reason_code,
        input_ref=latest.source_batch_id,
    )
