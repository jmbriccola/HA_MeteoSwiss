"""SwissMetNet station metadata and nearest-station lookup."""

from __future__ import annotations

import csv
import math
from dataclasses import dataclass
from io import StringIO

_EARTH_RADIUS_KM = 6371.0088


@dataclass(frozen=True, slots=True)
class Station:
    """A SwissMetNet station."""

    code: str
    name: str
    latitude: float
    longitude: float
    altitude: int


def haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in kilometers between two points."""
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp = math.radians(lat2 - lat1)
    dl = math.radians(lon2 - lon1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * _EARTH_RADIUS_KM * math.asin(math.sqrt(a))


def parse_stations_csv(raw: str) -> list[Station]:
    """Parse the stations metadata CSV published by MeteoSwiss."""
    reader = csv.DictReader(StringIO(raw), delimiter=";")
    seen: dict[str, Station] = {}
    for row in reader:
        code = row["Abbr."].strip()
        if code in seen:
            continue
        seen[code] = Station(
            code=code,
            name=row["Station"].strip(),
            latitude=float(row["Latitude"]),
            longitude=float(row["Longitude"]),
            altitude=int(float(row["Height m. a. sea level"])),
        )
    return list(seen.values())


def nearest_station(
    stations: list[Station], *, latitude: float, longitude: float
) -> Station:
    """Return the station closest to the given coordinates."""
    if not stations:
        raise ValueError("station list is empty")
    return min(
        stations,
        key=lambda s: haversine_km(latitude, longitude, s.latitude, s.longitude),
    )
