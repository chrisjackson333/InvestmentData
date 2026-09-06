"""SQLAlchemy Core table definition for signal history (PostgreSQL)."""

from sqlalchemy import (
    BigInteger,
    Column,
    DateTime,
    MetaData,
    String,
    Table,
    UniqueConstraint,
    func,
)

metadata = MetaData()

signal_history = Table(
    "signal_history",
    metadata,
    Column("id", BigInteger, primary_key=True, autoincrement=True),
    Column("symbol", String(16), nullable=False),
    Column("timeframe", String(8), nullable=False),
    Column("signal", String(16), nullable=False),
    Column("strategy", String(64), nullable=False),
    Column("signal_ts_utc", DateTime(timezone=True), nullable=False),
    Column("reason_code", String(64), nullable=False),
    Column("input_ref", String(128), nullable=False),
    Column("inserted_at_utc", DateTime(timezone=True), nullable=False, server_default=func.now()),
    UniqueConstraint("symbol", "timeframe", "signal_ts_utc", name="uq_signal_history_symbol_tf_ts"),
)
