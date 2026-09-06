"""Wires reader -> aggregator -> signal computation -> persistence.

Decoupled from ingestion: consumes RawMarketBar/TransformedCandle values via
transforms' existing reader/aggregator rather than depending on ingestion's
raw-zone directory conventions directly. The caller (a future scheduler/CLI)
resolves the raw-zone file path and passes it in.
"""

from pathlib import Path
from typing import Optional

from aggregation.candles import aggregate_to_5min_candles
from aggregation.reader import read_raw_zone_bars
from contracts.signal.models import LatestSignal
from sqlalchemy.engine import Engine

from config import SignalEngineSettings
from persistence.signals import insert_signal
from strategy.sma20 import compute_sma20_signal


def run_from_raw_zone_file(
    raw_zone_path: Path,
    source_batch_id: str,
    engine: Engine,
    settings: Optional[SignalEngineSettings] = None,
) -> Optional[LatestSignal]:
    settings = settings or SignalEngineSettings()
    bars = read_raw_zone_bars(raw_zone_path)
    candles = aggregate_to_5min_candles(bars, source_batch_id=source_batch_id)
    signal = compute_sma20_signal(candles, sma_period=settings.sma_period)
    if signal is not None:
        insert_signal(engine, signal)
    return signal
