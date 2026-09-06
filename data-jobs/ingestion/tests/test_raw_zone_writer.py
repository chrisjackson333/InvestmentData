import json
from pathlib import Path

import pytest

from adapters.csv import RawZoneWriter, parse_and_validate, read_csv_rows

FIXTURE_ROOT = Path(__file__).resolve().parents[3] / "tests" / "fixtures"
SAMPLE_CSV = FIXTURE_ROOT / "market_data" / "nq1_1min_sample.csv"


@pytest.mark.unit
def test_writer_lands_bars_and_quality_report(tmp_path):
    rows = list(read_csv_rows(SAMPLE_CSV))
    bars, report, _flags = parse_and_validate(rows, source_batch_id="NQ1!_20260904_test0001")

    writer = RawZoneWriter(tmp_path)
    data_path = writer.write(bars, report, symbol="NQ1!")

    assert data_path.exists()
    expected_dir = tmp_path / "NQ1!" / "2026" / "09" / "04"
    assert data_path.parent == expected_dir

    lines = data_path.read_text().strip().splitlines()
    assert len(lines) == len(bars)

    quality_path = expected_dir / "NQ1!_20260904_test0001.quality.json"
    assert quality_path.exists()
    quality_data = json.loads(quality_path.read_text())
    assert quality_data["valid_count"] == len(bars)


@pytest.mark.unit
def test_writer_rejects_empty_batch(tmp_path):
    writer = RawZoneWriter(tmp_path)
    with pytest.raises(ValueError):
        writer.write([], report=None, symbol="NQ1!")
