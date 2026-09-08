"""CSV adapter: reads raw NQ1! 1-minute OHLCV files, validates rows against the
shared market_tick contract, and lands validated bars into the raw zone.

Does NOT perform candle aggregation, signal calculation, or Kafka publishing —
those belong to other domains (see docs/architecture/DomainContract.txt).
"""

import csv
import json
from pathlib import Path
from typing import Iterable, Iterator, List, Set, Tuple

from contracts.market_tick.models import RawIngestionQualityReport, RawMarketBar
from pydantic import ValidationError

from ingestion_config import IngestionSettings


def read_csv_rows(path: Path) -> Iterator[dict]:
    with path.open(newline="", encoding="utf-8") as f:
        yield from csv.DictReader(f)


def parse_and_validate(
    rows: Iterable[dict], source_batch_id: str, strict: bool = False
) -> Tuple[List[RawMarketBar], RawIngestionQualityReport, List[str]]:
    """Validate raw CSV rows against RawMarketBar, flag quality issues, drop
    invalid/duplicate rows (unless strict=True, in which case invalid rows raise),
    and return bars sorted by timestamp ascending.
    """
    valid_bars: List[RawMarketBar] = []
    seen_keys: Set[Tuple[str, object]] = set()
    quality_flags: List[str] = []
    row_count = 0
    invalid_count = 0
    duplicate_count = 0

    for row in rows:
        row_count += 1
        try:
            bar = RawMarketBar.model_validate(row)
        except ValidationError as exc:
            if strict:
                raise
            invalid_count += 1
            quality_flags.append(_classify_validation_error(exc))
            continue

        key = (bar.symbol, bar.timestamp)
        if key in seen_keys:
            duplicate_count += 1
            quality_flags.append("duplicate_bar")
            continue
        seen_keys.add(key)
        valid_bars.append(bar)

    valid_bars.sort(key=lambda b: b.timestamp)

    report = RawIngestionQualityReport(
        source_batch_id=source_batch_id,
        row_count=row_count,
        valid_count=len(valid_bars),
        invalid_count=invalid_count,
        duplicate_count=duplicate_count,
    )
    return valid_bars, report, quality_flags


def _classify_validation_error(exc: ValidationError) -> str:
    errors = exc.errors()
    if not errors:
        return "invalid_row"
    error_type = errors[0]["type"]
    field_name = errors[0]["loc"][0] if errors[0]["loc"] else ""
    if error_type == "missing":
        return "missing_column"
    if not errors[0]["loc"]:
        # model-level validator (e.g. OHLC internal consistency) reports no field loc
        return "ohlc_out_of_range"
    if field_name == "timestamp":
        return "bad_timestamp"
    if field_name == "volume":
        return "negative_volume" if error_type == "value_error" else "missing_column"
    if field_name in ("open", "high", "low", "close"):
        return "ohlc_out_of_range"
    return "invalid_row"


class RawZoneWriter:
    """Writes validated bars + quality report to a local filesystem path,
    standing in for an S3 raw-zone landing convention. Swap this class out
    for an S3-backed implementation later without changing adapter logic.
    """

    def __init__(self, raw_zone_root: Path):
        self.raw_zone_root = raw_zone_root

    def write(
        self, bars: List[RawMarketBar], report: RawIngestionQualityReport, symbol: str
    ) -> Path:
        if not bars:
            raise ValueError("cannot land an empty batch of bars")

        first_ts = bars[0].timestamp
        target_dir = (
            self.raw_zone_root / symbol / f"{first_ts:%Y}" / f"{first_ts:%m}" / f"{first_ts:%d}"
        )
        target_dir.mkdir(parents=True, exist_ok=True)

        data_path = target_dir / f"{report.source_batch_id}.jsonl"
        with data_path.open("w", encoding="utf-8") as f:
            for bar in bars:
                f.write(bar.model_dump_json() + "\n")

        quality_path = target_dir / f"{report.source_batch_id}.quality.json"
        quality_path.write_text(json.dumps(json.loads(report.model_dump_json()), indent=2))

        return data_path


def land_to_raw_zone(
    bars: List[RawMarketBar],
    report: RawIngestionQualityReport,
    settings: IngestionSettings,
    symbol: str = "NQ1!",
) -> Path:
    writer = RawZoneWriter(settings.raw_zone_root)
    return writer.write(bars, report, symbol)
