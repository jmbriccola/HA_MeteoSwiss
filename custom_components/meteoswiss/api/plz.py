"""Async client for the undocumented MeteoSwiss plzDetail endpoint."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import UTC, datetime

import aiohttp

from .const import DEFAULT_TIMEOUT_SECONDS, PLZ_DETAIL_URL, USER_AGENT
from .models import ForecastDay, ForecastHour, PollenReading, Warning


class PlzError(RuntimeError):
    """Raised for HTTP or parse failures against plzDetail."""


@dataclass(frozen=True, slots=True)
class CurrentWeather:
    time: datetime
    icon: int
    temperature: float


@dataclass(frozen=True, slots=True)
class PlzDetail:
    plz: int
    city: str
    latitude: float
    longitude: float
    current: CurrentWeather
    forecast_days: list[ForecastDay]
    forecast_hours: list[ForecastHour]
    warnings: list[Warning]
    pollen: PollenReading
    uv_index_today: int
    uv_index_tomorrow: int


class PlzDetailClient:
    """Fetch and parse the plzDetail JSON payload."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT_SECONDS)
        self._headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    async def fetch(self, postal_code: int) -> PlzDetail:
        if not 1000 <= postal_code <= 9999:
            raise ValueError(f"postal code must be 4 digits, got {postal_code}")
        # The endpoint expects the PLZ suffixed with 00 (historical PLZ6 format).
        url = f"{PLZ_DETAIL_URL}?plz={postal_code * 100}"
        try:
            async with self._session.get(
                url, headers=self._headers, timeout=self._timeout
            ) as resp:
                if resp.status >= 400:
                    raise PlzError(f"GET {url} -> {resp.status}")
                payload = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise PlzError(f"GET {url} failed: {err}") from err
        return _parse_plz_detail(payload)


def _parse_plz_detail(payload: dict) -> PlzDetail:
    try:
        current_raw = payload["currentWeather"]
        current = CurrentWeather(
            time=_ms_to_datetime(current_raw["time"]),
            icon=int(current_raw["iconV2"]),
            temperature=float(current_raw["temperature"]),
        )
        forecast_days = [
            ForecastDay(
                date=datetime.fromisoformat(day["dayDate"]).date(),
                icon=int(day["iconDayV2"]),
                temperature_min=float(day["temperatureMin"]),
                temperature_max=float(day["temperatureMax"]),
                precipitation_mm=float(day["precipitation"]),
                precipitation_min_mm=float(day["precipitationMin"]),
                precipitation_max_mm=float(day["precipitationMax"]),
            )
            for day in payload.get("forecast", [])
        ]
        graph = payload.get("graph", {})
        forecast_hours = _hourly_from_graph(graph)
        warnings = [
            Warning(
                warn_type=int(w["warnType"]),
                severity=int(w["warnLevel"]),
                text=str(w.get("text", "")),
                valid_from=_ms_to_datetime(w["validFrom"]),
                valid_to=_ms_to_datetime(w["validTo"]),
            )
            for w in payload.get("warnings", [])
        ]
        pollen_raw = payload.get("pollen", {})
        pollen = PollenReading(
            betula=int(pollen_raw.get("betula", 0)),
            poaceae=int(pollen_raw.get("poaceae", 0)),
            ambrosia=int(pollen_raw.get("ambrosia", 0)),
            alnus=int(pollen_raw.get("alnus", 0)),
            corylus=int(pollen_raw.get("corylus", 0)),
        )
        uv_raw = payload.get("uvIndex", {})
        return PlzDetail(
            plz=int(payload["plz"]) // 100,
            city=str(payload["city"]),
            latitude=float(payload["latitude"]),
            longitude=float(payload["longitude"]),
            current=current,
            forecast_days=forecast_days,
            forecast_hours=forecast_hours,
            warnings=warnings,
            pollen=pollen,
            uv_index_today=int(uv_raw.get("today", 0)),
            uv_index_tomorrow=int(uv_raw.get("tomorrow", 0)),
        )
    except (KeyError, TypeError, ValueError) as err:
        raise PlzError(f"malformed plzDetail payload: {err}") from err


def _hourly_from_graph(graph: dict) -> list[ForecastHour]:
    start_ms = graph.get("start")
    temps = graph.get("temperatureMean1h", [])
    temps_min = graph.get("temperatureMin1h", [])
    temps_max = graph.get("temperatureMax1h", [])
    precip = graph.get("precipitationMean1h", [])
    wind = graph.get("windSpeed1h", [])
    gust = graph.get("gustPeak1h", [])
    wdir = graph.get("windDirection1h", [])
    if start_ms is None:
        return []
    start = _ms_to_datetime(int(start_ms))
    result: list[ForecastHour] = []
    for i, t in enumerate(temps):
        result.append(
            ForecastHour(
                time=start.replace(minute=0, second=0, microsecond=0).replace(
                    hour=(start.hour + i) % 24
                ),
                temperature=float(t),
                temperature_min=float(temps_min[i]) if i < len(temps_min) else float(t),
                temperature_max=float(temps_max[i]) if i < len(temps_max) else float(t),
                precipitation_mm=float(precip[i]) if i < len(precip) else 0.0,
                wind_speed=float(wind[i]) if i < len(wind) else 0.0,
                wind_gust=float(gust[i]) if i < len(gust) else 0.0,
                wind_direction=float(wdir[i]) if i < len(wdir) else 0.0,
            )
        )
    return result


def _ms_to_datetime(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000, tz=UTC)
