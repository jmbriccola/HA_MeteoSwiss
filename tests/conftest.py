"""Shared test fixtures for the MeteoSwiss client tests."""

from __future__ import annotations

from pathlib import Path

import pytest

FIXTURES_DIR = Path(__file__).parent / "fixtures"


@pytest.fixture
def fixture_text() -> callable:
    """Return a loader that reads a fixture file as text."""

    def _load(name: str, encoding: str = "utf-8") -> str:
        return (FIXTURES_DIR / name).read_text(encoding=encoding)

    return _load


@pytest.fixture
def fixture_bytes() -> callable:
    """Return a loader that reads a fixture file as bytes."""

    def _load(name: str) -> bytes:
        return (FIXTURES_DIR / name).read_bytes()

    return _load
