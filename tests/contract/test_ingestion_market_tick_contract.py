"""Cross-domain contract test: verifies ingestion's actual CSV output conforms
to the shared market_tick contract, tying the ingestion domain to the contract
defined in shared/contracts/market_tick/models.py.
"""

from pathlib import Path

import pytest

from adapters.csv import parse_and_validate, read_csv_rows
from contracts.market_tick.models import RawMarketBar

FIXTURE_ROOT = Path(__file__).resolve().parents[1] / "fixtures"
SAMPLE_CSV = FIXTURE_ROOT / "market_data" / "nq1_1min_sample.csv"


@pytest.mark.contract
def test_ingestion_output_conforms_to_market_tick_contract():
    rows = list(read_csv_rows(SAMPLE_CSV))
    bars, report, _flags = parse_and_validate(rows, source_batch_id="NQ1!_20260904_test0001")

    assert len(bars) == report.valid_count
    for bar in bars:
        assert isinstance(bar, RawMarketBar)
        RawMarketBar.model_validate(bar.model_dump())
