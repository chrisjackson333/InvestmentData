"""Contract for the raw NQ1! 1-minute OHLCV bar produced by CSV ingestion.

See docs/architecture/DomainContract.txt and
data-jobs/ingestion/schemas/raw_market_data.md for the raw CSV schema this validates.
"""

from datetime import datetime, timezone
from decimal import Decimal

from pydantic import BaseModel, field_validator, model_validator

from contracts.common import Symbol


class RawMarketBar(BaseModel):
    symbol: Symbol
    timestamp: datetime
    open: Decimal
    high: Decimal
    low: Decimal
    close: Decimal
    volume: int

    @field_validator("timestamp")
    @classmethod
    def timestamp_must_be_utc(cls, value: datetime) -> datetime:
        if value.tzinfo is None:
            raise ValueError("timestamp must be timezone-aware")
        return value.astimezone(timezone.utc)

    @field_validator("open", "high", "low", "close")
    @classmethod
    def price_must_be_positive(cls, value: Decimal) -> Decimal:
        if value <= 0:
            raise ValueError("price fields must be positive")
        return value

    @field_validator("volume")
    @classmethod
    def volume_must_be_non_negative(cls, value: int) -> int:
        if value < 0:
            raise ValueError("volume must be non-negative")
        return value

    @model_validator(mode="after")
    def ohlc_must_be_internally_consistent(self) -> "RawMarketBar":
        highest = max(self.open, self.close, self.low)
        lowest = min(self.open, self.close, self.high)
        if self.high < highest:
            raise ValueError("high must be >= max(open, close, low)")
        if self.low > lowest:
            raise ValueError("low must be <= min(open, close, high)")
        return self


class RawIngestionQualityReport(BaseModel):
    source_batch_id: str
    row_count: int
    valid_count: int
    invalid_count: int
    duplicate_count: int
