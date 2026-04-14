"""MeteoSwiss API client — public surface."""

from __future__ import annotations

from .client import MeteoSwissClient
from .errors import MeteoSwissError
from .models import (
    ForecastDay,
    ForecastHour,
    LightningStrike,
    Observation,
    PollenReading,
    Warning,
)
from .plz import PlzDetail, PlzError
from .stac import StacError
from .stations import Station, haversine_km, nearest_station, parse_stations_csv

__all__ = [
    "ForecastDay",
    "ForecastHour",
    "LightningStrike",
    "MeteoSwissClient",
    "MeteoSwissError",
    "Observation",
    "PlzDetail",
    "PlzError",
    "PollenReading",
    "StacError",
    "Station",
    "Warning",
    "haversine_km",
    "nearest_station",
    "parse_stations_csv",
]
