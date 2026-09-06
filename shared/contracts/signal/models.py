"""Contract for the latest-signal record handed from the Signal Engine to the API Layer.

Locked field-level contract — see docs/architecture/DomainContract.txt, section
"Signal Engine -> API Layer". Not yet consumed; the signal-engine service populates
this in a later increment.
"""

from datetime import datetime

from pydantic import BaseModel

from contracts.common import SignalType, StrategyName, Symbol, Timeframe


class LatestSignal(BaseModel):
    symbol: Symbol
    timeframe: Timeframe
    signal: SignalType
    strategy: StrategyName
    signal_ts_utc: datetime
    reason_code: str
    input_ref: str
