"""Typed dataclasses exposed by the MeteoSwiss API client."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime


@dataclass(frozen=True, slots=True)
class Observation:
    """A single 10-minute observation from an SMN station."""

    station: str
    timestamp: datetime
    temperature: float | None
    humidity: float | None
    dew_point: float | None
    pressure_qfe: float | None
    pressure_qff: float | None
    precipitation_10min: float | None
    wind_direction: float | None
    wind_speed: float | None
    wind_gust: float | None
    global_radiation: float | None
    sunshine_duration_10min: float | None


@dataclass(frozen=True, slots=True)
class ForecastDay:
    """A daily forecast entry."""

    date: date
    icon: int
    temperature_min: float
    temperature_max: float
    precipitation_mm: float
    precipitation_min_mm: float
    precipitation_max_mm: float


@dataclass(frozen=True, slots=True)
class ForecastHour:
    """An hourly forecast entry."""

    time: datetime
    temperature: float
    temperature_min: float
    temperature_max: float
    precipitation_mm: float
    wind_speed: float
    wind_gust: float
    wind_direction: float


@dataclass(frozen=True, slots=True)
class Warning:
    """A MeteoSwiss weather warning (severity 1 = info to 5 = extreme)."""

    warn_type: int
    severity: int
    text: str
    valid_from: datetime
    valid_to: datetime


@dataclass(frozen=True, slots=True)
class PollenReading:
    """Current pollen levels 0-4 for the five tracked species."""

    betula: int
    poaceae: int
    ambrosia: int
    alnus: int
    corylus: int


@dataclass(frozen=True, slots=True)
class LightningStrike:
    """A single detected lightning strike."""

    time: datetime
    latitude: float
    longitude: float
    peak_current_ka: float
