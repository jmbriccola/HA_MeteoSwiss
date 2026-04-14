"""Tests for api.stac — STAC client against data.geo.admin.ch."""

from __future__ import annotations

import aiohttp
import pytest
from aioresponses import CallbackResult, aioresponses

from custom_components.meteoswiss.api import const
from custom_components.meteoswiss.api.stac import StacClient, StacError


@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as s:
        yield s


async def test_get_collection_items_returns_features(session, fixture_text):
    url = f"{const.STAC_BASE_URL}/collections/{const.COLLECTION_SMN}/items"
    with aioresponses() as m:
        m.get(url, body=fixture_text("stac_item_smn.json"), status=200)
        client = StacClient(session)
        features = await client.get_collection_items(const.COLLECTION_SMN)
    assert len(features) == 1
    assert features[0]["id"] == "ogd-smn-ber"


async def test_get_asset_text_returns_body(session, fixture_text):
    asset_url = "https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/ber/ogd-smn-ber-now.csv"
    body = fixture_text("smn_vqha80_ber.csv")
    with aioresponses() as m:
        m.get(asset_url, body=body.encode("latin-1"), status=200)
        client = StacClient(session)
        text = await client.get_asset_text(asset_url, encoding="latin-1")
    assert "BER" in text


async def test_get_collection_items_raises_stac_error_on_500(session):
    url = f"{const.STAC_BASE_URL}/collections/{const.COLLECTION_SMN}/items"
    with aioresponses() as m:
        m.get(url, status=500)
        client = StacClient(session)
        with pytest.raises(StacError):
            await client.get_collection_items(const.COLLECTION_SMN)


async def test_get_asset_bytes_returns_body(session):
    url = "https://data.geo.admin.ch/ch.meteoschweiz.ogd-radar/latest.png"
    with aioresponses() as m:
        m.get(url, body=b"\x89PNG\r\n\x1a\n...", status=200)
        client = StacClient(session)
        data = await client.get_asset_bytes(url)
    assert data.startswith(b"\x89PNG")


async def test_client_sets_user_agent(session):
    url = f"{const.STAC_BASE_URL}/collections/{const.COLLECTION_SMN}/items"
    captured: dict[str, str] = {}

    def handler(_url, **kwargs):
        captured.update(kwargs.get("headers", {}))
        return CallbackResult(
            status=200, body='{"type":"FeatureCollection","features":[]}'
        )

    with aioresponses() as m:
        m.get(url, callback=handler)
        client = StacClient(session)
        await client.get_collection_items(const.COLLECTION_SMN)

    assert captured.get("User-Agent") == const.USER_AGENT
