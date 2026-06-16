"""The main application factory for the ts_weatherbroadcaster service.

Notes
-----
Be aware that, following the normal pattern for FastAPI services, the app is
constructed when this module is loaded and is not deferred until a function is
called.
"""

import json
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from importlib.metadata import metadata, version

import structlog
from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi
from rubin.repertoire import discovery_dependency
from safir.dependencies.http_client import http_client_dependency
from safir.logging import configure_logging, configure_uvicorn_logging
from safir.middleware.x_forwarded import XForwardedMiddleware
from safir.slack.webhook import SlackRouteErrorHandler

from .config import config
from .handlers.external import external_router
from .handlers.internal import internal_router

__all__ = ["app", "create_openapi"]


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None]:
    """Set up and tear down the application."""
    # Any code here will be run when the application starts up.
    yield

    # Any code here will be run when the application shuts down.
    await http_client_dependency.aclose()


configure_logging(
    profile=config.log_profile,
    log_level=config.log_level,
    name="tsweatherbroadcaster",
)
configure_uvicorn_logging(config.log_level)

app = FastAPI(
    title="ts_weatherbroadcaster",
    description=metadata("ts_weatherbroadcaster")["Summary"],
    version=version("ts_weatherbroadcaster"),
    openapi_url=f"{config.path_prefix}/openapi.json",
    docs_url=f"{config.path_prefix}/docs",
    redoc_url=f"{config.path_prefix}/redoc",
    lifespan=lifespan,
)
"""The main FastAPI application for ts_weatherbroadcaster."""

# Attach the routers.
app.include_router(internal_router)
app.include_router(external_router, prefix=f"{config.path_prefix}")

# Add middleware.
app.add_middleware(XForwardedMiddleware)

# Configure Slack alerts.
if config.slack_webhook:
    logger = structlog.get_logger("tsweatherbroadcaster")
    SlackRouteErrorHandler.initialize(
        config.slack_webhook, "ts_weatherbroadcaster", logger
    )
    logger.debug("Initialized Slack webhook")

logger = structlog.getLogger("tsweatherbroadcaster")
discovery_dependency.initialize(logger)


def create_openapi() -> str:
    """Create the OpenAPI specification for static documentation."""
    spec = get_openapi(
        title=app.title,
        version=app.version,
        description=app.description,
        routes=app.routes,
    )
    return json.dumps(spec)
