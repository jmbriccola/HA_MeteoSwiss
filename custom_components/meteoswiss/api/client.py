"""Top-level facade for the MeteoSwiss API."""

from __future__ import annotations

import aiohttp

from .const import COLLECTION_SMN, DEFAULT_TIMEOUT_SECONDS, STAC_BASE_URL, USER_AGENT
from .csv_parser import parse_smn_observations
from .models import Observation
from .plz import PlzDetail, PlzDetailClient
from .stac import StacClient, StacError


class MeteoSwissClient:
    """High-level async client combining the STAC and plzDetail subclients."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self.stac = StacClient(session)
        self.plz = PlzDetailClient(session)

    async def get_latest_observation(self, station_code: str) -> Observation:
        """Return the newest SMN observation for a station code (e.g. 'BER')."""
        url = f"{STAC_BASE_URL}/collections/{COLLECTION_SMN}/items?station={station_code}"
        timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT_SECONDS)
        headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}
        try:
            async with self._session.get(url, headers=headers, timeout=timeout) as resp:
                if resp.status >= 400:
                    raise StacError(f"GET {url} -> {resp.status}")
                payload = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise StacError(f"GET {url} failed: {err}") from err
        features = payload.get("features", [])
        if not features:
            raise StacError(f"no items for station {station_code}")
        assets = features[0].get("assets", {})
        csv_asset = next(
            (asset for asset in assets.values() if asset.get("type") == "text/csv"),
            None,
        )
        if csv_asset is None:
            raise StacError(f"no CSV asset for station {station_code}")
        csv_text = await self.stac.get_asset_text(csv_asset["href"], encoding="latin-1")
        observations = parse_smn_observations(csv_text)
        if not observations:
            raise StacError(f"empty CSV for station {station_code}")
        return observations[-1]

    async def get_plz_detail(self, postal_code: int) -> PlzDetail:
        return await self.plz.fetch(postal_code)
