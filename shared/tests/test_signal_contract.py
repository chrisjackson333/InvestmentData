from datetime import datetime, timezone

import pytest

from contracts.signal.models import LatestSignal


@pytest.mark.contract
def test_latest_signal_parses():
    signal = LatestSignal(
        symbol="NQ1!",
        timeframe="5m",
        signal="LONG",
        strategy="sma20_long_only",
        signal_ts_utc=datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc),
        reason_code="close_above_sma20",
        input_ref="NQ1!_20260904_abcd1234",
    )
    assert signal.signal == "LONG"
