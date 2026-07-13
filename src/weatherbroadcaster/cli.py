"""Command-line interface for weatherbroadcaster."""

import asyncio

import click
import structlog
from safir.asyncio import run_with_asyncio
from safir.logging import configure_logging

from . import update_weather
from .config import config

RETRY_DELAYS = (5, 30)

configure_logging(
    profile=config.log_profile,
    log_level=config.log_level,
    name="weatherbroadcaster",
)
logger = structlog.get_logger("weatherbroadcaster")


async def _update_with_retries() -> None:
    """Update weather data, retrying temporary failures twice."""
    for attempt in range(len(RETRY_DELAYS) + 1):
        try:
            await update_weather.main()
        except Exception:
            if attempt == len(RETRY_DELAYS):
                raise
            delay = RETRY_DELAYS[attempt]
            logger.exception(
                "Weather update failed; retrying.", retry_delay=delay
            )
            await asyncio.sleep(delay)
        else:
            return


async def _run_updates(*, loop_: bool) -> None:
    """Run one update or continue updating at the configured interval."""
    while True:
        try:
            await _update_with_retries()
        except Exception:
            if not loop_:
                raise
            logger.exception("Weather update failed.")
        if not loop_:
            return
        await asyncio.sleep(config.weather_update_interval)


@click.group(context_settings={"help_option_names": ["-h", "--help"]})
@click.version_option(message="%(version)s")
@run_with_asyncio
async def main() -> None:
    """Weatherbroadcaster command-line interface."""


@main.command()
@click.option(
    "--loop",
    "loop_",
    is_flag=True,
    help="Continue updating at the configured interval.",
)
@run_with_asyncio
async def update(*, loop_: bool) -> None:
    """Fetch weather data and update the cache."""
    await _run_updates(loop_=loop_)
