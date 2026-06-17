"""Models for weatherbroadcaster."""

from typing import Literal

from pydantic import BaseModel, Field
from safir.metadata import Metadata as SafirMetadata
from safir.pydantic import UtcDatetime

__all__ = ["Data", "Index"]


class Index(BaseModel):
    """Metadata returned by the external root URL of the application."""

    metadata: SafirMetadata = Field(..., title="Package metadata")


class Data(BaseModel):
    """Weather data returned by the public API."""

    STATIONID: Literal["RUBINOBS01"] = "RUBINOBS01"
    TIME: UtcDatetime
    LAT: float = -30.244633333
    LON: float = -70.7494166667
    HEIGHT: float = 2647
    TEMPERATURE: float = -999
    WINDSPEED: float = -999
    WINDDIRECTION: float = -999
    RELATIVEHUMIDITY: float = -999
    DEWPOINT: float = -999
    PRECIPITATION: float = -999
