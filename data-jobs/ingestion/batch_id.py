"""Helper for generating source_batch_id values that flow through the ingestion contract."""

from datetime import date
from uuid import uuid4


def generate_batch_id(symbol: str, as_of: date) -> str:
    return f"{symbol}_{as_of:%Y%m%d}_{uuid4().hex[:8]}"
