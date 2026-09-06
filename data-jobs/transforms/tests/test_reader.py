from datetime import datetime, timedelta, timezone
from decimal import Decimal
from pathlib import Path

import pytest
from contracts.market_tick.models import RawMarketBar

from aggregation.reader import read_raw_zone_bars

FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
GAP_SAMPLE_JSONL = FIXTURE_ROOT / "market_data" / "nq1_1min_gap_sample.jsonl"


@pytest.mark.unit
def test_read_raw_zone_bars_parses_all_lines(tmp_path):
    bar = RawMarketBar(
        symbol="NQ1!",
        timestamp=datetime(2026, 9, 4, 13, 30, tzinfo=timezone.utc),
        open=Decimal("100"),
        high=Decimal("101"),
        low=Decimal("99"),
        close=Decimal("100.5"),
        volume=10,
    )
    path = tmp_path / "sample.jsonl"
    path.write_text(bar.model_dump_json() + "\n")

    bars = read_raw_zone_bars(path)
    assert len(bars) == 1
    assert bars[0].symbol == "NQ1!"
    assert bars[0].open == Decimal("100")


@pytest.mark.unit
def test_read_raw_zone_bars_normalizes_timestamp_to_utc(tmp_path):
    non_utc_tz = timezone(timedelta(hours=-5))
    bar = RawMarketBar(
        symbol="NQ1!",
        timestamp=datetime(2026, 9, 4, 8, 30, tzinfo=non_utc_tz),
        open=Decimal("100"),
        high=Decimal("101"),
        low=Decimal("99"),
        close=Decimal("100.5"),
        volume=10,
    )
    path = tmp_path / "sample.jsonl"
    path.write_text(bar.model_dump_json() + "\n")

    bars = read_raw_zone_bars(path)
    assert bars[0].timestamp.tzinfo == timezone.utc
    assert bars[0].timestamp == datetime(2026, 9, 4, 13, 30, tzinfo=timezone.utc)


@pytest.mark.unit
def test_read_raw_zone_bars_uses_gap_fixture():
    bars = read_raw_zone_bars(GAP_SAMPLE_JSONL)
    assert len(bars) == 15
