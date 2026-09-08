"""Shared FastAPI dependencies: a process-wide SQLAlchemy engine, sourced
from signal-engine's DatabaseSettings rather than duplicating DB config.
"""

from functools import lru_cache

from signal_engine_config import DatabaseSettings
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine


@lru_cache
def _engine() -> Engine:
    return create_engine(DatabaseSettings().sqlalchemy_url())


def get_engine() -> Engine:
    return _engine()
