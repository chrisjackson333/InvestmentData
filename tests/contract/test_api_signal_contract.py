"""Cross-domain contract test: verifies the API layer's /getLatestSignal
response conforms to the shared signal contract.
"""

from datetime import datetime, timezone

import pytest
from app.main import app
from app.routes import signals as signals_route
from contracts.signal.models import LatestSignal
from fastapi.testclient import TestClient


@pytest.mark.contract
def test_get_latest_signal_response_conforms_to_contract(monkeypatch):
    fixed = LatestSignal(
        symbol="NQ1!",
        timeframe="5m",
        signal="LONG",
        strategy="sma20_long_only",
        signal_ts_utc=datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc),
        reason_code="close_above_sma20",
        input_ref="NQ1!_20260904_test0001",
    )
    monkeypatch.setattr(signals_route, "get_latest_signal", lambda engine, s, t: fixed)
    client = TestClient(app)
    response = client.get("/getLatestSignal")
    assert response.status_code == 200
    LatestSignal.model_validate(response.json())
