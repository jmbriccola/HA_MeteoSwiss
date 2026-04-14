"""Tests for api.models."""

from __future__ import annotations

from datetime import UTC, datetime

from custom_components.meteoswiss.api.models import (
    ForecastDay,
    ForecastHour,
    LightningStrike,
    Observation,
    PollenReading,
    Warning,
)


def test_observation_exposes_all_smn_fields():
    obs = Observation(
        station="BER",
        timestamp=datetime(2026, 4, 14, 7, 10, tzinfo=UTC),
        temperature=13.1,
        humidity=74.0,
        dew_point=8.3,
        pressure_qfe=946.4,
        pressure_qff=1014.3,
        precipitation_10min=0.0,
        wind_direction=225.0,
        wind_speed=3.0,
        wind_gust=4.5,
        global_radiation=262.0,
        sunshine_duration_10min=1.0,
    )
    assert obs.station == "BER"
    assert obs.temperature == 13.1


def test_observation_allows_missing_fields_as_none():
    obs = Observation(
        station="BER",
        timestamp=datetime(2026, 4, 14, 7, 10, tzinfo=UTC),
        temperature=None,
        humidity=None,
        dew_point=None,
        pressure_qfe=None,
        pressure_qff=None,
        precipitation_10min=None,
        wind_direction=None,
        wind_speed=None,
        wind_gust=None,
        global_radiation=None,
        sunshine_duration_10min=None,
    )
    assert obs.temperature is None


def test_forecast_day_has_min_max_and_icon():
    day = ForecastDay(
        date=datetime(2026, 4, 15, tzinfo=UTC).date(),
        icon=22,
        temperature_min=11.0,
        temperature_max=17.0,
        precipitation_mm=3.5,
        precipitation_min_mm=1.0,
        precipitation_max_mm=8.0,
    )
    assert day.icon == 22
    assert day.temperature_max == 17.0


def test_forecast_hour_is_time_indexed():
    hour = ForecastHour(
        time=datetime(2026, 4, 14, 10, 0, tzinfo=UTC),
        temperature=17.0,
        temperature_min=16.0,
        temperature_max=18.0,
        precipitation_mm=0.3,
        wind_speed=15.0,
        wind_gust=25.0,
        wind_direction=210.0,
    )
    assert hour.time.hour == 10


def test_warning_encodes_severity_and_validity():
    w = Warning(
        warn_type=2,
        severity=3,
        text="Starker Regen",
        valid_from=datetime(2026, 4, 14, 10, 0, tzinfo=UTC),
        valid_to=datetime(2026, 4, 14, 22, 0, tzinfo=UTC),
    )
    assert w.severity == 3
    assert 1 <= w.severity <= 5


def test_pollen_reading_levels_are_bounded():
    p = PollenReading(betula=2, poaceae=1, ambrosia=0, alnus=0, corylus=0)
    for value in (p.betula, p.poaceae, p.ambrosia, p.alnus, p.corylus):
        assert 0 <= value <= 4


def test_lightning_strike_has_geometry_and_time():
    strike = LightningStrike(
        time=datetime(2026, 4, 14, 6, 5, tzinfo=UTC),
        latitude=46.01,
        longitude=8.96,
        peak_current_ka=12.3,
    )
    assert strike.peak_current_ka == 12.3
