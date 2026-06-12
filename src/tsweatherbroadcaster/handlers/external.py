"""Handlers for the app's external root, ``/ts_weatherbroadcaster/``."""

from typing import Annotated

import aiofiles
from fastapi import APIRouter, Depends, HTTPException, status
from safir.dependencies.logger import logger_dependency
from safir.metadata import get_metadata
from safir.slack.webhook import SlackRouteErrorHandler
from structlog.stdlib import BoundLogger

from ..config import config
from ..models import Data, Index

__all__ = ["external_router"]


external_router = APIRouter(route_class=SlackRouteErrorHandler)
"""FastAPI router for all external handlers."""


@external_router.get(
    "/",
    description=(
        "Provides basic application metadata such as version and name."
    ),
    response_model_exclude_none=True,
    summary="Application metadata",
)
async def get_index(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Index:
    # Customize this handler to return whatever the top-level resource of your
    # application should return. For example, consider listing key API URLs.
    # When doing so, also change or customize the response model in
    # tsweatherbroadcaster.models.Index.
    #
    # By convention, the root of the external API includes a field called
    # metadata that provides the same Safir-generated metadata as the internal
    # root endpoint.

    # There is no need to log simple requests since uvicorn will do this
    # automatically, but this is included as an example of how to use the
    # logger for more complex logging.
    logger.info("Request for application metadata")

    metadata = get_metadata(
        package_name="ts_weatherbroadcaster",
        application_name=config.name,
    )
    return Index(metadata=metadata)


@external_router.get(
    "/data",
    description="Returns the weather data in the expected MeteoBlue format.",
)
async def get_data(
    logger: Annotated[BoundLogger, Depends(logger_dependency)],
) -> Data:
    """Return weather data in expected MeteoBlue format."""
    try:
        async with aiofiles.open(config.weather_data_file_path) as f:
            logger.info("Reading and validating file.")
            return Data.model_validate_json(await f.read())
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Weather data has not been cached yet.",
        ) from e
