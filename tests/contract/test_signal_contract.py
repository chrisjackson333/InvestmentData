"""Cross-domain contract test: verifies signal-engine's actual output
conforms to the shared signal contract.
"""

from pathlib import Path

import pytest

from aggregation.candles import aggregate_to_5min_candles
from aggregation.reader import read_raw_zone_bars
from contracts.signal.models import LatestSignal
from strategy.sma20 import compute_sma20_signal

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"
SMA20_SAMPLE_JSONL = FIXTURE_ROOT / "market_data" / "nq1_1min_sma20_sample.jsonl"


@pytest.mark.contract
def test_signal_output_conforms_to_latest_signal_contract():
    bars = read_raw_zone_bars(SMA20_SAMPLE_JSONL)
    candles = aggregate_to_5min_candles(bars, source_batch_id="NQ1!_20260904_test0001")
    signal = compute_sma20_signal(candles)

    assert signal is not None
    assert isinstance(signal, LatestSignal)
    LatestSignal.model_validate(signal.model_dump())
    assert signal.symbol == "NQ1!"
    assert signal.timeframe == "5m"
