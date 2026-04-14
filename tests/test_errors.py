"""Tests for the MeteoSwiss error hierarchy."""

from __future__ import annotations

from custom_components.meteoswiss.api import MeteoSwissError, PlzError, StacError


def test_stac_error_is_meteoswiss_error():
    err = StacError("boom")
    assert isinstance(err, MeteoSwissError)


def test_plz_error_is_meteoswiss_error():
    err = PlzError("boom")
    assert isinstance(err, MeteoSwissError)


def test_meteoswiss_error_is_runtime_error():
    err = MeteoSwissError("boom")
    assert isinstance(err, RuntimeError)
