"""Configuration definition."""

from pathlib import Path

from pydantic import Field, SecretStr
from pydantic_settings import BaseSettings, SettingsConfigDict
from safir.logging import LogLevel, Profile

__all__ = ["Config", "config"]


class Config(BaseSettings):
    """Configuration for ts_weatherbroadcaster."""

    model_config = SettingsConfigDict(
        env_prefix="TS_WEATHERBROADCASTER_", case_sensitive=False
    )

    log_level: LogLevel = Field(
        LogLevel.INFO, title="Log level of the application's logger"
    )

    log_profile: Profile = Field(
        Profile.development, title="Application logging profile"
    )

    name: str = Field("ts_weatherbroadcaster", title="Name of application")

    path_prefix: str = Field(
        "/ts_weatherbroadcaster", title="URL prefix for application"
    )

    slack_webhook: SecretStr | None = Field(
        None,
        title="Slack webhook for alerts",
        description="If set, alerts will be posted to this Slack webhook",
    )
    weather_data_file_path: Path = Field(
        Path("/data/weather.json"),
        title="The path to write the weather.json file.",
    )


config = Config()
"""Configuration for ts_weatherbroadcaster."""
