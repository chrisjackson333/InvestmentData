from datetime import datetime, timezone
from decimal import Decimal

import pytest
from pydantic import ValidationError

from contracts.market_tick.models import RawIngestionQualityReport, RawMarketBar


def _bar(**overrides) -> dict:
    base = dict(
        symbol="NQ1!",
        timestamp=datetime(2026, 9, 4, 13, 31, tzinfo=timezone.utc),
        open=Decimal("100.0"),
        high=Decimal("101.0"),
        low=Decimal("99.5"),
        close=Decimal("100.5"),
        volume=1000,
    )
    base.update(overrides)
    return base


@pytest.mark.contract
def test_valid_bar_parses():
    bar = RawMarketBar.model_validate(_bar())
    assert bar.symbol == "NQ1!"
    assert bar.timestamp.tzinfo is not None


@pytest.mark.contract
def test_naive_timestamp_rejected():
    with pytest.raises(ValidationError):
        RawMarketBar.model_validate(_bar(timestamp=datetime(2026, 9, 4, 13, 31)))


@pytest.mark.contract
def test_negative_volume_rejected():
    with pytest.raises(ValidationError):
        RawMarketBar.model_validate(_bar(volume=-1))


@pytest.mark.contract
def test_ohlc_inconsistency_rejected():
    with pytest.raises(ValidationError):
        RawMarketBar.model_validate(_bar(low=Decimal("200.0")))


@pytest.mark.contract
def test_quality_report_shape():
    report = RawIngestionQualityReport(
        source_batch_id="NQ1!_20260904_abcd1234",
        row_count=10,
        valid_count=8,
        invalid_count=1,
        duplicate_count=1,
    )
    assert report.valid_count + report.invalid_count + report.duplicate_count == report.row_count
