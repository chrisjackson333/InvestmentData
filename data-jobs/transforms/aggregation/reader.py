"""Reads RawMarketBar records landed by ingestion's raw-zone writer."""

from pathlib import Path
from typing import Iterator, List

from contracts.market_tick.models import RawMarketBar
from utils.datetime.timezones import to_utc


def read_raw_zone_bars(path: Path) -> List[RawMarketBar]:
    """Read one source_batch_id's .jsonl file of RawMarketBar records.

    Re-normalizes each bar's timestamp via to_utc() as a defensive
    domain-boundary check — RawMarketBar's own validator already guarantees
    UTC, this does not re-run OHLC/business validation.
    """
    bars: List[RawMarketBar] = []
    for line in _read_lines(path):
        bar = RawMarketBar.model_validate_json(line)
        bar = bar.model_copy(update={"timestamp": to_utc(bar.timestamp)})
        bars.append(bar)
    return bars


def _read_lines(path: Path) -> Iterator[str]:
    with path.open(encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                yield line
