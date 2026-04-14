"""Parse the SMN semicolon-separated CSV output published by MeteoSwiss.

The live files are encoded in Latin-1; callers are expected to decode
before passing text in here.
"""

from __future__ import annotations

import csv
from datetime import UTC, datetime
from io import StringIO

from .models import Observation

# Map of MeteoSwiss column codes to Observation field names.
_COLUMN_MAP: dict[str, str] = {
    "tre200s0": "temperature",
    "ure200s0": "humidity",
    "tde200s0": "dew_point",
    "prestas0": "pressure_qfe",
    "pp0qffs0": "pressure_qff",
    "rre150z0": "precipitation_10min",
    "dkl010z0": "wind_direction",
    "fkl010z0": "wind_speed",
    "fkl010z1": "wind_gust",
    "gre000z0": "global_radiation",
    "sre000z0": "sunshine_duration_10min",
}


def parse_timestamp_utc(raw: str) -> datetime:
    """Parse 'dd.mm.yyyy HH:MM' as UTC."""
    return datetime.strptime(raw.strip(), "%d.%m.%Y %H:%M").replace(tzinfo=UTC)


def parse_float(raw: str) -> float | None:
    """Parse a float; return None for empty strings and '-' placeholders."""
    stripped = raw.strip()
    if not stripped or stripped == "-":
        return None
    return float(stripped)


def parse_smn_observations(csv_text: str) -> list[Observation]:
    """Parse the full CSV text into a list of Observations, oldest-first."""
    reader = csv.DictReader(StringIO(csv_text), delimiter=";")
    observations: list[Observation] = []
    for row in reader:
        kwargs: dict[str, float | None] = {
            field: parse_float(row.get(column, "")) for column, field in _COLUMN_MAP.items()
        }
        observations.append(
            Observation(
                station=row["stn"].strip(),
                timestamp=parse_timestamp_utc(row["time"]),
                **kwargs,
            )
        )
    return observations
