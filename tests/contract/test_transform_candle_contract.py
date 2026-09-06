"""Cross-domain contract test: verifies transforms' actual candle output
conforms to the shared transformed_candle contract.
"""

from pathlib import Path

import pytest

from aggregation.candles import aggregate_to_5min_candles
from aggregation.reader import read_raw_zone_bars
from contracts.transformed_candle.models import TransformedCandle

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"
GAP_SAMPLE_JSONL = FIXTURE_ROOT / "market_data" / "nq1_1min_gap_sample.jsonl"


@pytest.mark.contract
def test_transform_output_conforms_to_transformed_candle_contract():
    bars = read_raw_zone_bars(GAP_SAMPLE_JSONL)
    candles = aggregate_to_5min_candles(bars, source_batch_id="NQ1!_20260904_test0001")

    assert len(candles) == 4
    for candle in candles:
        assert isinstance(candle, TransformedCandle)
        TransformedCandle.model_validate(candle.model_dump())

    flagged = [c for c in candles if c.quality_flags]
    assert len(flagged) == 2
    all_flags = [f for c in flagged for f in c.quality_flags]
    assert "incomplete_window:4/5" in all_flags
    assert "incomplete_window:1/5" in all_flags
