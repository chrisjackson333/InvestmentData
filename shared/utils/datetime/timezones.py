"""Timezone normalization helpers shared by ingestion and transforms."""

from datetime import datetime, timezone


def to_utc(ts: datetime) -> datetime:
    """Normalize a timezone-aware datetime to UTC.

    Raises ValueError if `ts` is naive — every timestamp crossing a domain
    boundary in this platform must be explicit about its timezone.
    """
    if ts.tzinfo is None:
        raise ValueError("timestamp must be timezone-aware")
    return ts.astimezone(timezone.utc)
