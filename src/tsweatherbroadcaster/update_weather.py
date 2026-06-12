"""Update the cached weather data."""

import asyncio
import json
from contextlib import suppress
from pathlib import Path

import aiofiles
import aiofiles.os

from tsweatherbroadcaster.config import config

from .weather import fetch_weather_data


async def main() -> None:
    """Fetch weather data and write it to the cache."""
    data = await fetch_weather_data()
    contents = json.dumps(data.model_dump(mode="json"))

    path = config.weather_data_file_path
    path.parent.mkdir(parents=True, exist_ok=True)
    # Consider replacing this with Redis/Postgres/S3/GCS/etc.
    tmp_path: Path | None = None
    try:
        async with aiofiles.tempfile.NamedTemporaryFile(
            mode="w",
            dir=path.parent,
            prefix=f".{path.name}.",
            suffix=".tmp",
            delete=False,
        ) as tmp:
            tmp_path = tmp.name
            await tmp.write(contents)
        await aiofiles.os.replace(tmp_path, path)
    except Exception:
        if tmp_path is not None:
            with suppress(FileNotFoundError):
                await aiofiles.os.remove(tmp_path)
        raise


if __name__ == "__main__":
    asyncio.run(main())
