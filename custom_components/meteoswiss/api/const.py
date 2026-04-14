"""Constants for the MeteoSwiss API client."""

from __future__ import annotations

from typing import Final

STAC_BASE_URL: Final[str] = "https://data.geo.admin.ch/api/stac/v1"
PLZ_DETAIL_URL: Final[str] = "https://app-prod-ws.meteoswiss-app.ch/v1/plzDetail"

COLLECTION_SMN: Final[str] = "ch.meteoschweiz.ogd-smn"
COLLECTION_SMN_PRECIP: Final[str] = "ch.meteoschweiz.ogd-smn-precip"
COLLECTION_RADAR: Final[str] = "ch.meteoschweiz.ogd-radar"
COLLECTION_LIGHTNING: Final[str] = "ch.meteoschweiz.ogd-lightning"

STATIONS_META_URL: Final[str] = (
    # placeholder — real URL for metadata asset resolved at runtime in Plan 2
    f"{STAC_BASE_URL}/collections/{COLLECTION_SMN}/items?forecast=no&meta=yes"
)

DEFAULT_TIMEOUT_SECONDS: Final[int] = 30

# Switzerland bounding box — used to validate user input.
SWISS_LAT_MIN: Final[float] = 45.8
SWISS_LAT_MAX: Final[float] = 47.9
SWISS_LON_MIN: Final[float] = 5.9
SWISS_LON_MAX: Final[float] = 10.5

USER_AGENT: Final[str] = "ha-meteoswiss/0.0.1 (+https://github.com/jmbriccola/HA_MeteoSwiss)"

ATTRIBUTION: Final[str] = "Source: MeteoSwiss"
