"""Contract for the 5-minute candle handed from Ingestion/Transforms to the Signal Engine.

Locked field-level contract — see docs/architecture/DomainContract.txt, section
"Ingestion -> Signal Engine". Not yet consumed; the transforms job populates this
in a later increment.
"""

from datetime import datetime
from decimal import Decimal
from typing import List

from pydantic import BaseModel

from contracts.common import Symbol


class TransformedCandle(BaseModel):
    symbol: Symbol
    candle_ts_utc: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: Decimal
    source_batch_id: str
    quality_flags: List[str] = []
