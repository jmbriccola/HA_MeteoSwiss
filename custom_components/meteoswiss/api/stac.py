"""Async STAC client for data.geo.admin.ch."""

from __future__ import annotations

import aiohttp

from .const import DEFAULT_TIMEOUT_SECONDS, STAC_BASE_URL, USER_AGENT


class StacError(RuntimeError):
    """Raised for HTTP errors or malformed STAC payloads."""


class StacClient:
    """Thin async wrapper around the data.geo.admin.ch STAC API."""

    def __init__(self, session: aiohttp.ClientSession) -> None:
        self._session = session
        self._timeout = aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT_SECONDS)
        self._headers = {"User-Agent": USER_AGENT, "Accept": "application/json"}

    async def get_collection_items(self, collection_id: str) -> list[dict]:
        url = f"{STAC_BASE_URL}/collections/{collection_id}/items"
        try:
            async with self._session.get(
                url, headers=self._headers, timeout=self._timeout
            ) as resp:
                if resp.status >= 400:
                    raise StacError(f"GET {url} -> {resp.status}")
                payload = await resp.json(content_type=None)
        except aiohttp.ClientError as err:
            raise StacError(f"GET {url} failed: {err}") from err
        features = payload.get("features")
        if not isinstance(features, list):
            raise StacError(f"GET {url}: missing 'features' array")
        return features

    async def get_asset_text(self, url: str, *, encoding: str = "utf-8") -> str:
        raw = await self.get_asset_bytes(url)
        return raw.decode(encoding)

    async def get_asset_bytes(self, url: str) -> bytes:
        try:
            async with self._session.get(
                url, headers={"User-Agent": USER_AGENT}, timeout=self._timeout
            ) as resp:
                if resp.status >= 400:
                    raise StacError(f"GET {url} -> {resp.status}")
                return await resp.read()
        except aiohttp.ClientError as err:
            raise StacError(f"GET {url} failed: {err}") from err
