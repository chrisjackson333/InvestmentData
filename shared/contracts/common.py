"""Shared literal types reused across contract models to avoid drift between domains."""

from typing import Literal

Symbol = Literal["NQ1!"]
Timeframe = Literal["1m", "5m"]
SignalType = Literal["LONG", "HOLD"]
StrategyName = Literal["sma20_long_only"]
