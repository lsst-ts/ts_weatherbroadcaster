"""Tests for the tsweatherbroadcaster.handlers.external module and routes."""

from pathlib import Path
from typing import Self

import aiofiles
import pytest
from httpx import AsyncClient

from tsweatherbroadcaster.config import config


class _AsyncReadableFile:
    def __init__(self, contents: str) -> None:
        self._contents = contents

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self, exc_type: object, exc: object, traceback: object
    ) -> None:
        return None

    async def read(self) -> str:
        return self._contents


@pytest.mark.asyncio
async def test_get_index(client: AsyncClient) -> None:
    """Test ``GET /ts_weatherbroadcaster/``."""
    response = await client.get("/ts_weatherbroadcaster/")
    assert response.status_code == 200
    data = response.json()
    metadata = data["metadata"]
    assert metadata["name"] == config.name
    assert isinstance(metadata["version"], str)
    assert isinstance(metadata["description"], str)
    assert isinstance(metadata["repository_url"], str)
    assert isinstance(metadata["documentation_url"], str)


@pytest.mark.asyncio
async def test_get_data(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test ``GET /ts_weatherbroadcaster/data``."""

    def open_override(path: Path) -> _AsyncReadableFile:
        assert path == Path("/data/weather.json")
        return _AsyncReadableFile(
            """
            {
                "STATIONID": "RUBINOBS01",
                "TIME": "2026-05-22T12:00:00Z",
                "LAT": -30.244633333,
                "LON": -70.7494166667,
                "HEIGHT": 2647,
                "TEMPERATURE": 8.2,
                "WINDSPEED": 4.3,
                "WINDDIRECTION": 275.0,
                "RELATIVEHUMIDITY": 41.5,
                "DEWPOINT": 1.2,
                "PRECIPITATION": 0.1
            }
            """
        )

    monkeypatch.setattr(aiofiles, "open", open_override)

    response = await client.get("/ts_weatherbroadcaster/data")

    assert response.status_code == 200
    assert response.json() == {
        "STATIONID": "RUBINOBS01",
        "TIME": "2026-05-22T12:00:00Z",
        "LAT": -30.244633333,
        "LON": -70.7494166667,
        "HEIGHT": 2647.0,
        "TEMPERATURE": 8.2,
        "WINDSPEED": 4.3,
        "WINDDIRECTION": 275.0,
        "RELATIVEHUMIDITY": 41.5,
        "DEWPOINT": 1.2,
        "PRECIPITATION": 0.1,
    }


@pytest.mark.asyncio
async def test_get_data_not_cached(
    client: AsyncClient, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Test ``GET /ts_weatherbroadcaster/data`` when no cache exists."""

    def open_override(path: Path) -> _AsyncReadableFile:
        assert path == Path("/data/weather.json")
        raise FileNotFoundError

    monkeypatch.setattr(aiofiles, "open", open_override)

    response = await client.get("/ts_weatherbroadcaster/data")

    assert response.status_code == 503
    assert response.json() == {
        "detail": "Weather data has not been cached yet."
    }
