"""Tests for application configuration."""

import pytest
from pydantic import ValidationError

from weatherbroadcaster.config import Config


@pytest.mark.parametrize(
    "setting", ["weather_fetch_timeout", "weather_update_interval"]
)
def test_weather_timing_settings_must_be_positive(setting: str) -> None:
    """Reject non-positive weather timing settings."""
    with pytest.raises(ValidationError):
        Config(**{setting: 0})
