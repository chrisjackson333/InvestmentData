from datetime import datetime, timezone

import pytest
from contracts.signal.models import LatestSignal
from fastapi.testclient import TestClient

from app.main import app
from app.routes import signals as signals_route


@pytest.fixture
def client():
    return TestClient(app)


def _signal(minute: int) -> LatestSignal:
    return LatestSignal(
        symbol="NQ1!",
        timeframe="5m",
        signal="LONG",
        strategy="sma20_long_only",
        signal_ts_utc=datetime(2026, 9, 4, 13, minute, tzinfo=timezone.utc),
        reason_code="close_above_sma20",
        input_ref="NQ1!_20260904_test0001",
    )


@pytest.mark.unit
def test_all_signals_default_limit_returns_list(client, monkeypatch):
    captured = {}

    def _fake_list_signals(engine, symbol, timeframe, limit):
        captured["limit"] = limit
        return [_signal(30), _signal(35), _signal(40)]

    monkeypatch.setattr(signals_route, "list_signals", _fake_list_signals)
    response = client.get("/allSignals")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 3
    assert len(body["signals"]) == 3
    assert captured["limit"] == 50


@pytest.mark.unit
def test_all_signals_respects_custom_limit(client, monkeypatch):
    captured = {}

    def _fake_list_signals(engine, symbol, timeframe, limit):
        captured["limit"] = limit
        return []

    monkeypatch.setattr(signals_route, "list_signals", _fake_list_signals)
    response = client.get("/allSignals", params={"limit": 5})
    assert response.status_code == 200
    assert captured["limit"] == 5


@pytest.mark.unit
def test_all_signals_rejects_limit_below_one(client):
    response = client.get("/allSignals", params={"limit": 0})
    assert response.status_code == 422


@pytest.mark.unit
def test_all_signals_rejects_limit_above_max(client):
    response = client.get("/allSignals", params={"limit": 501})
    assert response.status_code == 422


@pytest.mark.unit
def test_all_signals_returns_empty_list_when_no_signals(client, monkeypatch):
    monkeypatch.setattr(signals_route, "list_signals", lambda engine, s, t, limit: [])
    response = client.get("/allSignals")
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 0
    assert body["signals"] == []
