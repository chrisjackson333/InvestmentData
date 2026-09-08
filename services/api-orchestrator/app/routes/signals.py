"""Signal read endpoints: getLatestSignal and allSignals.

Hardcoded to symbol="NQ1!", timeframe="5m" per the current MVP lock — no
query params for symbol/timeframe until multi-instrument/multi-timeframe
support is a real, separate increment.
"""

from typing import List

from contracts.signal.models import LatestSignal
from fastapi import APIRouter, Depends, HTTPException, Query
from persistence.signals import get_latest_signal, list_signals
from pydantic import BaseModel
from sqlalchemy.engine import Engine

from app.config import ApiSettings
from app.dependencies import get_engine

router = APIRouter()
_settings = ApiSettings()

SYMBOL = "NQ1!"
TIMEFRAME = "5m"


@router.get("/getLatestSignal", response_model=LatestSignal)
def get_latest_signal_endpoint(engine: Engine = Depends(get_engine)) -> LatestSignal:
    signal = get_latest_signal(engine, SYMBOL, TIMEFRAME)
    if signal is None:
        raise HTTPException(status_code=404, detail="no signal computed yet")
    return signal


class AllSignalsResponse(BaseModel):
    count: int
    signals: List[LatestSignal]


@router.get("/allSignals", response_model=AllSignalsResponse)
def all_signals_endpoint(
    limit: int = Query(
        default=_settings.default_signals_limit, ge=1, le=_settings.max_signals_limit
    ),
    engine: Engine = Depends(get_engine),
) -> AllSignalsResponse:
    signals = list_signals(engine, SYMBOL, TIMEFRAME, limit=limit)
    return AllSignalsResponse(count=len(signals), signals=signals)
