"""Tests for api.client — top-level facade."""

from __future__ import annotations

from datetime import UTC, datetime

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.meteoswiss.api import const
from custom_components.meteoswiss.api.client import MeteoSwissClient


@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as s:
        yield s


async def test_facade_exposes_both_subclients(session):
    client = MeteoSwissClient(session)
    assert client.stac is not None
    assert client.plz is not None


async def test_get_latest_observation_uses_stac(session, fixture_text):
    items_url = f"{const.STAC_BASE_URL}/collections/{const.COLLECTION_SMN}/items?station=BER"
    asset_url = "https://data.geo.admin.ch/ch.meteoschweiz.ogd-smn/ber/ogd-smn-ber-now.csv"
    items_body = fixture_text("stac_item_smn.json")
    with aioresponses() as m:
        m.get(items_url, body=items_body, status=200)
        m.get(asset_url, body=fixture_text("smn_vqha80_ber.csv").encode("latin-1"), status=200)
        client = MeteoSwissClient(session)
        obs = await client.get_latest_observation("BER")
    assert obs.station == "BER"
    assert obs.timestamp == datetime(2026, 4, 14, 7, 10, tzinfo=UTC)
    assert obs.temperature == 13.1


async def test_get_plz_detail_returns_detail(session, fixture_text):
    with aioresponses() as m:
        m.get(
            f"{const.PLZ_DETAIL_URL}?plz=690000",
            body=fixture_text("plz_detail_6900.json"),
            status=200,
        )
        client = MeteoSwissClient(session)
        detail = await client.get_plz_detail(6900)
    assert detail.city == "Lugano"
