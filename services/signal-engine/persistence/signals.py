"""Signal history persistence: insert + latest-read for Postgres."""

from typing import Optional

from contracts.common import Symbol, Timeframe
from contracts.signal.models import LatestSignal
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.engine import Engine

from .schema import signal_history


def insert_signal(engine: Engine, signal: LatestSignal) -> None:
    """Insert one signal into history.

    Idempotent: ON CONFLICT DO NOTHING on the (symbol, timeframe,
    signal_ts_utc) unique constraint, so re-running orchestration against
    the same candle is a safe no-op rather than an error.
    """
    stmt = (
        pg_insert(signal_history)
        .values(
            symbol=signal.symbol,
            timeframe=signal.timeframe,
            signal=signal.signal,
            strategy=signal.strategy,
            signal_ts_utc=signal.signal_ts_utc,
            reason_code=signal.reason_code,
            input_ref=signal.input_ref,
        )
        .on_conflict_do_nothing(constraint="uq_signal_history_symbol_tf_ts")
    )
    with engine.begin() as conn:
        conn.execute(stmt)


def get_latest_signal(
    engine: Engine, symbol: Symbol, timeframe: Timeframe
) -> Optional[LatestSignal]:
    """Latest signal computation for API read use (DomainContract.txt)."""
    stmt = (
        select(signal_history)
        .where(signal_history.c.symbol == symbol, signal_history.c.timeframe == timeframe)
        .order_by(signal_history.c.signal_ts_utc.desc())
        .limit(1)
    )
    with engine.connect() as conn:
        row = conn.execute(stmt).mappings().first()
    if row is None:
        return None
    return LatestSignal(
        symbol=row["symbol"],
        timeframe=row["timeframe"],
        signal=row["signal"],
        strategy=row["strategy"],
        signal_ts_utc=row["signal_ts_utc"],
        reason_code=row["reason_code"],
        input_ref=row["input_ref"],
    )
