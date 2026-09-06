import json
from pathlib import Path

import pytest

from adapters.csv import parse_and_validate, read_csv_rows

FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
SAMPLE_CSV = FIXTURE_ROOT / "market_data" / "nq1_1min_sample.csv"
EXPECTED_REPORT = FIXTURE_ROOT / "expected_outputs" / "nq1_1min_sample_quality_report.json"


@pytest.mark.unit
def test_parse_and_validate_matches_expected_quality_report():
    rows = list(read_csv_rows(SAMPLE_CSV))
    bars, report, _flags = parse_and_validate(rows, source_batch_id="NQ1!_20260904_test0001")

    expected = json.loads(EXPECTED_REPORT.read_text())
    assert report.row_count == expected["row_count"]
    assert report.valid_count == expected["valid_count"]
    assert report.invalid_count == expected["invalid_count"]
    assert report.duplicate_count == expected["duplicate_count"]
    assert len(bars) == expected["valid_count"]


@pytest.mark.unit
def test_valid_bars_are_sorted_by_timestamp():
    rows = list(read_csv_rows(SAMPLE_CSV))
    bars, _report, _flags = parse_and_validate(rows, source_batch_id="NQ1!_20260904_test0001")
    timestamps = [b.timestamp for b in bars]
    assert timestamps == sorted(timestamps)


@pytest.mark.unit
def test_duplicate_bar_is_flagged():
    rows = list(read_csv_rows(SAMPLE_CSV))
    _bars, _report, flags = parse_and_validate(rows, source_batch_id="NQ1!_20260904_test0001")
    assert "duplicate_bar" in flags


@pytest.mark.unit
def test_ohlc_out_of_range_is_flagged():
    rows = list(read_csv_rows(SAMPLE_CSV))
    _bars, _report, flags = parse_and_validate(rows, source_batch_id="NQ1!_20260904_test0001")
    assert "ohlc_out_of_range" in flags


@pytest.mark.unit
def test_strict_mode_raises_on_invalid_row():
    rows = list(read_csv_rows(SAMPLE_CSV))
    with pytest.raises(Exception):
        parse_and_validate(rows, source_batch_id="NQ1!_20260904_test0001", strict=True)
