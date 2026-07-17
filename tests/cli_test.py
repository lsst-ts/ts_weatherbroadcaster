"""Tests for the command-line interface."""

import asyncio

import pytest

from weatherbroadcaster import cli
from weatherbroadcaster.config import config


@pytest.mark.asyncio
@pytest.mark.parametrize(
    "error", [RuntimeError("EFD unavailable"), TimeoutError()]
)
async def test_update_retries_are_bounded(
    monkeypatch: pytest.MonkeyPatch,
    error: Exception,
) -> None:
    """Stop retrying after the configured number of attempts."""
    calls = 0
    delays: list[int] = []

    async def fail_update() -> None:
        nonlocal calls
        calls += 1
        raise error

    async def record_sleep(delay: float) -> None:
        delays.append(int(delay))

    monkeypatch.setattr(
        "weatherbroadcaster.cli.update_weather.main", fail_update
    )
    monkeypatch.setattr("weatherbroadcaster.cli.asyncio.sleep", record_sleep)

    with pytest.raises(type(error)):
        await cli._update_with_retries()

    assert calls == 3
    assert delays == [5, 30]


@pytest.mark.asyncio
async def test_loop_uses_configured_update_interval(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """Sleep for the configured interval between loop iterations."""
    calls = 0

    async def update_once() -> None:
        nonlocal calls
        calls += 1

    async def stop_loop(delay: float) -> None:
        assert delay == 42
        raise asyncio.CancelledError

    monkeypatch.setattr(cli, "_update_with_retries", update_once)
    monkeypatch.setattr("weatherbroadcaster.cli.asyncio.sleep", stop_loop)
    monkeypatch.setattr(config, "weather_update_interval", 42)

    with pytest.raises(asyncio.CancelledError):
        await cli._run_updates(loop_=True)

    assert calls == 1
