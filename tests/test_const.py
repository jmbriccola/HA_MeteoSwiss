"""Tests for api.const."""

from __future__ import annotations

from custom_components.meteoswiss.api import const


def test_stac_base_url_is_public_https():
    assert const.STAC_BASE_URL.startswith("https://")
    assert "data.geo.admin.ch/api/stac/v1" in const.STAC_BASE_URL


def test_plz_detail_base_url_is_public_https():
    assert const.PLZ_DETAIL_URL.startswith("https://")
    assert "plzDetail" in const.PLZ_DETAIL_URL


def test_smn_collection_id():
    assert const.COLLECTION_SMN == "ch.meteoschweiz.ogd-smn"


def test_default_timeout_is_reasonable():
    assert 5 <= const.DEFAULT_TIMEOUT_SECONDS <= 60


def test_swiss_bbox_covers_major_cities():
    # Bern, Lugano, Zermatt should all fall inside.
    assert const.SWISS_LAT_MIN <= 46.99 <= const.SWISS_LAT_MAX
    assert const.SWISS_LAT_MIN <= 46.00 <= const.SWISS_LAT_MAX
    assert const.SWISS_LON_MIN <= 7.46 <= const.SWISS_LON_MAX
    assert const.SWISS_LON_MIN <= 8.96 <= const.SWISS_LON_MAX
