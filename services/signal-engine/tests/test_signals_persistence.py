"""Persistence-layer tests against a real PostgreSQL instance.

Requires `docker compose up -d postgres` (see repo-root docker-compose.yml)
before running. Deferred from the base quality gate per Standards.txt's
allowance for integration tests to be reserved for the merge/main pipeline.
"""

from datetime import datetime, timezone

import pytest
from contracts.signal.models import LatestSignal
from sqlalchemy import create_engine, text

from config import DatabaseSettings
from persistence.schema import metadata
from persistence.signals import get_latest_signal, insert_signal


@pytest.fixture
def engine():
    settings = DatabaseSettings()
    eng = create_engine(settings.sqlalchemy_url())
    metadata.create_all(eng)
    yield eng
    with eng.begin() as conn:
        conn.execute(text("TRUNCATE TABLE signal_history"))
    eng.dispose()


def _signal(signal_ts_utc: datetime, signal: str = "LONG") -> LatestSignal:
    return LatestSignal(
        symbol="NQ1!",
        timeframe="5m",
        signal=signal,
        strategy="sma20_long_only",
        signal_ts_utc=signal_ts_utc,
        reason_code="close_above_sma20",
        input_ref="NQ1!_20260904_test0001",
    )


@pytest.mark.integration
def test_insert_and_get_latest_signal_roundtrip(engine):
    sig = _signal(datetime(2026, 9, 4, 13, 30, tzinfo=timezone.utc))
    insert_signal(engine, sig)
    result = get_latest_signal(engine, "NQ1!", "5m")
    assert result is not None
    assert result.signal_ts_utc == sig.signal_ts_utc
    assert result.signal == sig.signal


@pytest.mark.integration
def test_get_latest_signal_returns_none_when_no_rows(engine):
    assert get_latest_signal(engine, "NQ1!", "5m") is None


@pytest.mark.integration
def test_get_latest_signal_returns_most_recent_by_ts(engine):
    older = _signal(datetime(2026, 9, 4, 13, 30, tzinfo=timezone.utc), signal="HOLD")
    newer = _signal(datetime(2026, 9, 4, 13, 35, tzinfo=timezone.utc), signal="LONG")
    insert_signal(engine, older)
    insert_signal(engine, newer)
    result = get_latest_signal(engine, "NQ1!", "5m")
    assert result.signal_ts_utc == newer.signal_ts_utc
    assert result.signal == "LONG"


@pytest.mark.integration
def test_insert_signal_is_idempotent_on_conflict(engine):
    sig = _signal(datetime(2026, 9, 4, 13, 30, tzinfo=timezone.utc))
    insert_signal(engine, sig)
    insert_signal(engine, sig)
    with engine.connect() as conn:
        count = conn.execute(text("SELECT COUNT(*) FROM signal_history")).scalar()
    assert count == 1
