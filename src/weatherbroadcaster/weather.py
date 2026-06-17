"""Fetch weather data from the EFD."""

import asyncio
import inspect
import math
from datetime import UTC, datetime
from typing import Any

import pandas as pd
import structlog
from lsst_efd_client import EfdClient

from .models import Data


def _missing_value(field: str) -> float:
    if field == "mean_rain_rate":
        return 0
    return -999


def _read_mean(result: Any, field: str, topic: str) -> float:
    columns = list(getattr(result, "columns", ()))
    index = getattr(result, "index", ())
    log: structlog.stdlib.BoundLogger = structlog.getLogger(
        "weatherbroadcaster"
    )

    if len(index) == 0:
        log.warning(f"No results found for {field}.")
        return _missing_value(field)
    if field not in columns:
        raise RuntimeError(
            f"EFD query for {topic} did not return {field}; "
            f"columns were {columns}"
        )

    value = result[field].iloc[-1]
    if value == "null" or pd.isna(value):
        log.warning(f"{field} is null, setting {topic} to missing value.")
        return _missing_value(field)

    return value


def _read_numeric_series(result: Any, field: str, topic: str) -> pd.Series:
    columns = list(getattr(result, "columns", ()))
    index = getattr(result, "index", ())
    if len(index) == 0:
        return pd.Series(dtype="float64")
    if field not in columns:
        raise RuntimeError(
            f"EFD query for {topic} did not return {field}; "
            f"columns were {columns}"
        )
    return pd.to_numeric(result[field], errors="coerce").dropna()


def _calculate_wind_direction(result: Any) -> float:
    directions = _read_numeric_series(result, "direction", "airFlow")
    speeds = _read_numeric_series(result, "speed", "airFlow")
    wind = pd.DataFrame({"direction": directions, "speed": speeds}).dropna()
    if len(wind) == 0 or wind["speed"].sum() == 0:
        return -999

    radians = wind["direction"].map(math.radians)
    weights = wind["speed"]
    mean_sin = (weights * radians.map(math.sin)).sum() / weights.sum()
    mean_cos = (weights * radians.map(math.cos)).sum() / weights.sum()

    direction = math.degrees(math.atan2(mean_sin, mean_cos))
    if direction < 0:
        direction += 360
    return direction


def _calculate_wind_speed(result: Any) -> float:
    speeds = _read_numeric_series(result, "speed", "airFlow")
    if len(speeds) == 0:
        return -999
    return speeds.mean()


def _latest_timestamp(*results: Any) -> datetime:
    timestamps = [
        result.index[-1]
        for result in results
        if len(getattr(result, "index", ())) > 0
    ]
    if timestamps:
        return max(timestamps)
    return datetime.now(tz=UTC)


async def _close_client(client: EfdClient) -> None:
    influx_client = getattr(client, "_influx_client", None)
    close = getattr(influx_client, "close", None)
    if close is None:
        return

    result = close()
    if inspect.isawaitable(result):
        await result


async def fetch_weather_data() -> Data:
    """Fetch recent weather data from the EFD."""
    client = EfdClient(efd_name="usdf_efd")
    temp_query = (
        "SELECT mean(temperatureItem0) AS mean_temperature FROM "
        '"efd"."autogen"."lsst.sal.ESS.temperature" '
        "WHERE salIndex=301 AND time > now() - 1h "
    )
    humidity_query = (
        "SELECT mean(relativeHumidityItem) "
        "AS mean_relative_humidity FROM "
        '"efd"."autogen"."lsst.sal.ESS.relativeHumidity" '
        "WHERE salIndex=301 AND time > now() - 1h "
    )
    wind_query = (
        "SELECT direction, speed FROM "
        '"efd"."autogen"."lsst.sal.ESS.airFlow" '
        "WHERE salIndex=301 AND time > now() - 1h "
    )
    dew_point_query = (
        "SELECT mean(dewPointItem) AS mean_dew_point FROM "
        '"efd"."autogen"."lsst.sal.ESS.dewPoint" '
        "WHERE salIndex=301 AND time > now() - 1h "
    )
    rain_rate_query = (
        "SELECT mean(rainRateItem) AS mean_rain_rate FROM "
        '"efd"."autogen"."lsst.sal.ESS.rainRate" '
        "WHERE salIndex=301 AND time > now() - 1h "
    )

    try:
        (
            temperature_result,
            wind_result,
            humidity_result,
            dew_point_result,
            rain_rate_result,
        ) = await asyncio.gather(
            client.influxql_query(temp_query),
            client.influxql_query(wind_query),
            client.influxql_query(humidity_query),
            client.influxql_query(dew_point_query),
            client.influxql_query(rain_rate_query),
        )
    finally:
        await _close_client(client)

    return Data(
        TIME=_latest_timestamp(
            temperature_result,
            humidity_result,
            wind_result,
            dew_point_result,
            rain_rate_result,
        ),
        TEMPERATURE=_read_mean(
            temperature_result, "mean_temperature", "temperature"
        ),
        RELATIVEHUMIDITY=_read_mean(
            humidity_result, "mean_relative_humidity", "relativeHumidity"
        ),
        WINDDIRECTION=_calculate_wind_direction(wind_result),
        WINDSPEED=_calculate_wind_speed(wind_result),
        DEWPOINT=_read_mean(dew_point_result, "mean_dew_point", "dewPoint"),
        PRECIPITATION=_read_mean(
            rain_rate_result, "mean_rain_rate", "rainRate"
        ),
    )
