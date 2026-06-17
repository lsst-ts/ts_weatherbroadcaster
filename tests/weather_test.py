"""Tests for weather data retrieval."""

from datetime import UTC, datetime
from math import nan
from typing import ClassVar

import pandas as pd
import pytest

from weatherbroadcaster import weather


def _efd_result(
    fields: dict[str, float | str | None | list[float | str | None]],
    index: list[datetime] | None = None,
) -> pd.DataFrame:
    """Create a fake EFD query result."""
    values = {
        field: value if isinstance(value, list) else [value]
        for field, value in fields.items()
    }
    if index is None:
        index = [
            datetime(2026, 5, 22, 11, 0, tzinfo=UTC),
            datetime(2026, 5, 22, 12, 0, tzinfo=UTC),
        ]
    return pd.DataFrame(values, index=index)


class _InfluxClient:
    closed = False

    def close(self) -> None:
        self.closed = True


class _EfdClient:
    queries: ClassVar[list[str]] = []
    influx_client = _InfluxClient()

    def __init__(self, *, efd_name: str) -> None:
        assert efd_name == "usdf_efd"
        self._influx_client = self.influx_client

    async def influxql_query(self, query: str) -> pd.DataFrame:
        assert "salIndex=301" in query
        self.queries.append(query)

        if "lsst.sal.ESS.temperature" in query:
            return _efd_result({"mean_temperature": [7.1, 8.2]})
        if "lsst.sal.ESS.relativeHumidity" in query:
            return _efd_result({"mean_relative_humidity": [40.0, 41.5]})
        if "lsst.sal.ESS.airFlow" in query:
            return _efd_result(
                {
                    "direction": [270.0, 280.0],
                    "speed": [3.1, 4.3],
                }
            )
        if "lsst.sal.ESS.dewPoint" in query:
            return _efd_result({"mean_dew_point": [0.5, 1.2]})
        if "lsst.sal.ESS.rainRate" in query:
            return _efd_result({"mean_rain_rate": [0.0, 0.1]})

        raise AssertionError(f"Unexpected query: {query}")


@pytest.mark.asyncio
async def test_fetch_weather_data(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Test fetching weather data from the EFD."""
    _EfdClient.queries = []
    _EfdClient.influx_client = _InfluxClient()
    monkeypatch.setattr(weather, "EfdClient", _EfdClient)

    data = await weather.fetch_weather_data()

    assert len(_EfdClient.queries) == 5
    assert any("mean_temperature" in query for query in _EfdClient.queries)
    assert any(
        "mean_relative_humidity" in query for query in _EfdClient.queries
    )
    assert any("direction, speed" in query for query in _EfdClient.queries)
    assert any("mean_dew_point" in query for query in _EfdClient.queries)
    assert any("mean_rain_rate" in query for query in _EfdClient.queries)

    assert datetime(2026, 5, 22, 12, 0, tzinfo=UTC) == data.TIME
    assert data.TEMPERATURE == 8.2
    assert data.RELATIVEHUMIDITY == 41.5
    assert pytest.approx(275.813, abs=0.001) == data.WINDDIRECTION
    assert data.WINDSPEED == 3.7
    assert data.DEWPOINT == 1.2
    assert data.PRECIPITATION == 0.1
    assert data.LAT == -30.244633333
    assert data.LON == -70.7494166667
    assert data.HEIGHT == 2647
    assert _EfdClient.influx_client.closed


def test_read_mean_missing_column() -> None:
    """Test missing EFD result columns are reported clearly."""
    result = _efd_result({})
    result.index = [datetime(2026, 5, 22, 12, 0, tzinfo=UTC)]

    with pytest.raises(RuntimeError, match="mean_relative_humidity"):
        weather._read_mean(
            result, "mean_relative_humidity", "relativeHumidity"
        )


def test_read_mean_empty_result() -> None:
    """Test empty EFD query results return the missing-value marker."""
    result = pd.DataFrame({"mean_relative_humidity": []})

    assert (
        weather._read_mean(
            result, "mean_relative_humidity", "relativeHumidity"
        )
        == -999
    )


@pytest.mark.parametrize("value", [None, nan, "null"])
def test_read_mean_null_value(value: float | str | None) -> None:
    """Test null non-rain values return the missing-value marker."""
    result = _efd_result({"mean_temperature": value})

    assert (
        weather._read_mean(result, "mean_temperature", "temperature") == -999
    )


@pytest.mark.parametrize("value", [None, nan, "null"])
def test_read_mean_null_rain_rate(value: float | str | None) -> None:
    """Test null rain-rate values are returned as zero."""
    result = _efd_result({"mean_rain_rate": value})

    assert weather._read_mean(result, "mean_rain_rate", "rainRate") == 0


def test_read_mean_uses_latest_bucket() -> None:
    """Test grouped query results use the newest bucket."""
    result = _efd_result({"mean_temperature": [7.1, 8.2]})

    assert weather._read_mean(result, "mean_temperature", "temperature") == 8.2


def test_calculate_wind_direction_weights_by_speed() -> None:
    """Test stronger winds contribute more to average direction."""
    result = _efd_result(
        {
            "direction": [0.0, 90.0],
            "speed": [1.0, 3.0],
        }
    )

    assert pytest.approx(71.565, abs=0.001) == (
        weather._calculate_wind_direction(result)
    )


def test_calculate_wind_direction_zero_speed() -> None:
    """Test wind direction is missing when all speed weights are zero."""
    result = _efd_result(
        {
            "direction": [0.0, 90.0],
            "speed": [0.0, 0.0],
        }
    )

    assert weather._calculate_wind_direction(result) == -999


def test_latest_timestamp_uses_latest_non_empty_result() -> None:
    """Test timestamp selection uses the latest available query result."""
    older = _efd_result(
        {"mean_temperature": 8.2},
        index=[datetime(2026, 5, 22, 12, 0, tzinfo=UTC)],
    )
    newer = _efd_result(
        {"mean_relative_humidity": 41.5},
        index=[datetime(2026, 5, 22, 13, 0, tzinfo=UTC)],
    )
    empty = _efd_result({"mean_dew_point": 1.2}, index=[])

    assert datetime(2026, 5, 22, 13, 0, tzinfo=UTC) == (
        weather._latest_timestamp(older, newer, empty)
    )
