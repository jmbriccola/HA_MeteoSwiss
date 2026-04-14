"""Tests for api.stations."""

from __future__ import annotations

import math

import pytest

from custom_components.meteoswiss.api.stations import (
    Station,
    haversine_km,
    nearest_station,
    parse_stations_csv,
)


def test_parse_stations_csv_returns_all_three(fixture_text):
    raw = fixture_text("stations_meta.csv")
    stations = parse_stations_csv(raw)
    ids = {s.code for s in stations}
    assert ids == {"BER", "LUG", "ZER"}


def test_parse_stations_csv_reads_coordinates(fixture_text):
    raw = fixture_text("stations_meta.csv")
    stations = parse_stations_csv(raw)
    lug = next(s for s in stations if s.code == "LUG")
    assert lug.name == "Lugano"
    assert lug.longitude == pytest.approx(8.96024)
    assert lug.latitude == pytest.approx(46.00412)
    assert lug.altitude == 273


def test_haversine_between_lugano_and_bern_is_around_170km():
    distance = haversine_km(46.00412, 8.96024, 46.99081, 7.46414)
    assert 150 < distance < 170


def test_haversine_zero_for_same_point():
    assert haversine_km(46.0, 8.0, 46.0, 8.0) == pytest.approx(0.0, abs=1e-6)


def test_nearest_station_picks_lugano_for_ticino_coords(fixture_text):
    raw = fixture_text("stations_meta.csv")
    stations = parse_stations_csv(raw)
    # Bellinzona-ish coordinates
    nearest = nearest_station(stations, latitude=46.195, longitude=9.024)
    assert nearest.code == "LUG"


def test_nearest_station_picks_zermatt_for_alpine_coords(fixture_text):
    raw = fixture_text("stations_meta.csv")
    stations = parse_stations_csv(raw)
    nearest = nearest_station(stations, latitude=46.020, longitude=7.75)
    assert nearest.code == "ZER"


def test_nearest_station_raises_on_empty_list():
    with pytest.raises(ValueError):
        nearest_station([], latitude=46.0, longitude=8.0)


def test_station_is_immutable():
    s = Station(code="BER", name="Bern", latitude=46.99, longitude=7.46, altitude=552)
    with pytest.raises(AttributeError):
        s.code = "LUG"  # type: ignore[misc]


def test_haversine_is_symmetric():
    d1 = haversine_km(46.0, 8.0, 47.0, 9.0)
    d2 = haversine_km(47.0, 9.0, 46.0, 8.0)
    assert math.isclose(d1, d2)
