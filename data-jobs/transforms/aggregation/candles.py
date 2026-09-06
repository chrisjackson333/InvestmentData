"""Aggregates 1-minute RawMarketBar records into 5-minute TransformedCandle
records with clock-aligned windows and gap-tolerant quality flagging.

Domain boundary: trusts that `bars` arrives sorted ascending and deduplicated
by (symbol, timestamp) per the Ingestion -> Signal Engine contract. Does not
re-sort or re-dedup; raises if that trust is violated (see _assert_sorted).
"""

from collections import defaultdict
from datetime import datetime
from decimal import Decimal
from typing import Dict, List

from contracts.market_tick.models import RawMarketBar
from contracts.transformed_candle.models import TransformedCandle

WINDOW_MINUTES = 5
EXPECTED_BARS_PER_WINDOW = 5


def _assert_sorted(bars: List[RawMarketBar]) -> None:
    for prev, curr in zip(bars, bars[1:]):
        if curr.timestamp < prev.timestamp:
            raise ValueError(
                "transforms requires bars pre-sorted by ingestion; "
                f"found {curr.timestamp} after {prev.timestamp}"
            )


def _floor_to_window(ts: datetime) -> datetime:
    minute_bucket = (ts.minute // WINDOW_MINUTES) * WINDOW_MINUTES
    return ts.replace(minute=minute_bucket, second=0, microsecond=0)


def group_bars_by_window(bars: List[RawMarketBar]) -> Dict[datetime, List[RawMarketBar]]:
    windows: Dict[datetime, List[RawMarketBar]] = defaultdict(list)
    for bar in bars:
        windows[_floor_to_window(bar.timestamp)].append(bar)
    return windows


def build_candle(
    window_start: datetime, bars_in_window: List[RawMarketBar], source_batch_id: str
) -> TransformedCandle:
    ordered = sorted(bars_in_window, key=lambda b: b.timestamp)
    present = len(ordered)
    quality_flags: List[str] = []
    if present < EXPECTED_BARS_PER_WINDOW:
        quality_flags.append(f"incomplete_window:{present}/{EXPECTED_BARS_PER_WINDOW}")

    return TransformedCandle(
        symbol=ordered[0].symbol,
        candle_ts_utc=window_start,
        open=ordered[0].open,
        high=max(b.high for b in ordered),
        low=min(b.low for b in ordered),
        close=ordered[-1].close,
        volume=Decimal(sum(b.volume for b in ordered)),
        source_batch_id=source_batch_id,
        quality_flags=quality_flags,
    )


def aggregate_to_5min_candles(
    bars: List[RawMarketBar], source_batch_id: str
) -> List[TransformedCandle]:
    """Main entry point: 1-min RawMarketBar list -> 5-min TransformedCandle list.

    Assumes `bars` is already sorted/deduped by ingestion (raises if violated).
    Windows are never dropped, including windows with fewer than 5 bars — see
    build_candle for the incomplete_window flag format. A window with zero
    bars simply has nothing to aggregate and does not appear in the output.
    """
    if not bars:
        return []
    _assert_sorted(bars)
    windows = group_bars_by_window(bars)
    return [
        build_candle(window_start, windows[window_start], source_batch_id)
        for window_start in sorted(windows)
    ]
