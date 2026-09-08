from datetime import datetime, timezone

import pytest
from contracts.signal.models import LatestSignal
from fastapi.testclient import TestClient

from app.main import app
from app.routes import signals as signals_route


@pytest.fixture
def client():
    return TestClient(app)


def _signal() -> LatestSignal:
    return LatestSignal(
        symbol="NQ1!",
        timeframe="5m",
        signal="LONG",
        strategy="sma20_long_only",
        signal_ts_utc=datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc),
        reason_code="close_above_sma20",
        input_ref="NQ1!_20260904_test0001",
    )


@pytest.mark.unit
def test_get_latest_signal_returns_200_with_signal_payload(client, monkeypatch):
    monkeypatch.setattr(signals_route, "get_latest_signal", lambda engine, s, t: _signal())
    response = client.get("/getLatestSignal")
    assert response.status_code == 200
    assert response.json()["signal"] == "LONG"
    assert response.json()["symbol"] == "NQ1!"


@pytest.mark.unit
def test_get_latest_signal_returns_404_when_none(client, monkeypatch):
    monkeypatch.setattr(signals_route, "get_latest_signal", lambda engine, s, t: None)
    response = client.get("/getLatestSignal")
    assert response.status_code == 404
