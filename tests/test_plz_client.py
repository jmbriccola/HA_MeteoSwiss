"""Tests for api.plz — plzDetail endpoint client."""

from __future__ import annotations

from datetime import UTC, datetime

import aiohttp
import pytest
from aioresponses import aioresponses

from custom_components.meteoswiss.api import const
from custom_components.meteoswiss.api.plz import PlzDetailClient, PlzError


@pytest.fixture
async def session():
    async with aiohttp.ClientSession() as s:
        yield s


def _plz_url(plz: int) -> str:
    return f"{const.PLZ_DETAIL_URL}?plz={plz * 100}"


async def test_fetch_returns_current_weather(session, fixture_text):
    with aioresponses() as m:
        m.get(_plz_url(6900), body=fixture_text("plz_detail_6900.json"), status=200)
        client = PlzDetailClient(session)
        detail = await client.fetch(6900)
    assert detail.current.temperature == 16.5
    assert detail.current.icon == 2


async def test_fetch_returns_forecast_days(session, fixture_text):
    with aioresponses() as m:
        m.get(_plz_url(6900), body=fixture_text("plz_detail_6900.json"), status=200)
        client = PlzDetailClient(session)
        detail = await client.fetch(6900)
    assert len(detail.forecast_days) == 2
    day2 = detail.forecast_days[1]
    assert day2.temperature_max == 17.0
    assert day2.precipitation_mm == 3.5
    assert day2.icon == 22


async def test_fetch_returns_hourly_graph(session, fixture_text):
    with aioresponses() as m:
        m.get(_plz_url(6900), body=fixture_text("plz_detail_6900.json"), status=200)
        client = PlzDetailClient(session)
        detail = await client.fetch(6900)
    assert len(detail.forecast_hours) == 4
    first = detail.forecast_hours[0]
    assert first.temperature == 15.0
    assert first.wind_speed == 10.0


async def test_fetch_returns_warnings(session, fixture_text):
    with aioresponses() as m:
        m.get(_plz_url(6900), body=fixture_text("plz_detail_6900.json"), status=200)
        client = PlzDetailClient(session)
        detail = await client.fetch(6900)
    assert len(detail.warnings) == 1
    w = detail.warnings[0]
    assert w.warn_type == 2
    assert w.severity == 3
    assert w.valid_from == datetime(2026, 4, 14, 10, 0, tzinfo=UTC)


async def test_fetch_returns_pollen(session, fixture_text):
    with aioresponses() as m:
        m.get(_plz_url(6900), body=fixture_text("plz_detail_6900.json"), status=200)
        client = PlzDetailClient(session)
        detail = await client.fetch(6900)
    assert detail.pollen.betula == 2
    assert detail.pollen.ambrosia == 0


async def test_fetch_returns_uv_index(session, fixture_text):
    with aioresponses() as m:
        m.get(_plz_url(6900), body=fixture_text("plz_detail_6900.json"), status=200)
        client = PlzDetailClient(session)
        detail = await client.fetch(6900)
    assert detail.uv_index_today == 5


async def test_fetch_returns_location(session, fixture_text):
    with aioresponses() as m:
        m.get(_plz_url(6900), body=fixture_text("plz_detail_6900.json"), status=200)
        client = PlzDetailClient(session)
        detail = await client.fetch(6900)
    assert detail.city == "Lugano"
    assert detail.latitude == pytest.approx(46.00412)
    assert detail.longitude == pytest.approx(8.96024)


async def test_fetch_raises_on_404(session):
    with aioresponses() as m:
        m.get(_plz_url(9999), status=404)
        client = PlzDetailClient(session)
        with pytest.raises(PlzError):
            await client.fetch(9999)


async def test_fetch_validates_plz_length(session):
    client = PlzDetailClient(session)
    with pytest.raises(ValueError):
        await client.fetch(123)
    with pytest.raises(ValueError):
        await client.fetch(12345)
