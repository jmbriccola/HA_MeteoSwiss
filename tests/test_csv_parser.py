"""Tests for api.csv_parser."""

from __future__ import annotations

from datetime import UTC, datetime

import pytest

from custom_components.meteoswiss.api.csv_parser import (
    parse_float,
    parse_smn_observations,
    parse_timestamp_utc,
)


def test_parse_timestamp_utc_parses_meteoswiss_format():
    ts = parse_timestamp_utc("14.04.2026 07:10")
    assert ts == datetime(2026, 4, 14, 7, 10, tzinfo=UTC)


def test_parse_timestamp_utc_raises_on_garbage():
    with pytest.raises(ValueError):
        parse_timestamp_utc("not a timestamp")


def test_parse_float_handles_empty_string_as_none():
    assert parse_float("") is None


def test_parse_float_handles_dash_as_none():
    assert parse_float("-") is None


def test_parse_float_handles_minus_only_as_none():
    # MeteoSwiss sometimes emits '-' for missing values.
    assert parse_float("  -  ") is None


def test_parse_float_converts_dot_decimal():
    assert parse_float("12.3") == 12.3


def test_parse_smn_observations_returns_all_rows(fixture_text):
    csv_text = fixture_text("smn_vqha80_ber.csv")
    rows = parse_smn_observations(csv_text)
    assert len(rows) == 3


def test_parse_smn_observations_returns_latest(fixture_text):
    csv_text = fixture_text("smn_vqha80_ber.csv")
    rows = parse_smn_observations(csv_text)
    latest = rows[-1]
    assert latest.station == "BER"
    assert latest.timestamp == datetime(2026, 4, 14, 7, 10, tzinfo=UTC)
    assert latest.temperature == 13.1
    assert latest.humidity == 74.0
    assert latest.pressure_qfe == 946.4
    assert latest.pressure_qff == 1014.3
    assert latest.precipitation_10min == 0.0
    assert latest.wind_direction == 225.0
    assert latest.wind_speed == 3.0
    assert latest.wind_gust == 4.5
    assert latest.global_radiation == 262.0
    assert latest.sunshine_duration_10min == 1.0
    assert latest.dew_point == 8.3


def test_parse_smn_observations_handles_missing_values():
    csv_text = (
        "stn;time;tre200s0;ure200s0;prestas0;pp0qffs0;"
        "rre150z0;dkl010z0;fkl010z0;fkl010z1;gre000z0;sre000z0;tde200s0\n"
        "BER;14.04.2026 07:20;-;-;-;-;-;-;-;-;-;-;-\n"
    )
    rows = parse_smn_observations(csv_text)
    assert len(rows) == 1
    assert rows[0].temperature is None
    assert rows[0].pressure_qfe is None
