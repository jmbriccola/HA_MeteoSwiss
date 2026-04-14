"""Base exception hierarchy for the MeteoSwiss API client."""

from __future__ import annotations


class MeteoSwissError(RuntimeError):
    """Base class for all MeteoSwiss API client errors."""
