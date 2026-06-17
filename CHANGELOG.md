# Change log

ts_weatherbroadcaster is versioned with [semver](https://semver.org/).
Dependencies are updated to the latest available version during each release, and aren't noted here.

Find changes for the upcoming release in the project's [changelog.d directory](https://github.com/lsst-sqre/ts_weatherbroadcaster/tree/main/changelog.d/).

<!-- scriv-insert-here -->

<a id='changelog-v0.1.0'></a>
## v0.1.0 (2026-06-17)

### New features

- Added a weather update command that fetches EFD weather data and writes a cached MeteoBlue-compatible JSON payload.
- Added configurable weather data file path support via `TS_WEATHERBROADCASTER_WEATHER_DATA_FILE_PATH`.

### Other changes

- Added Kubernetes manifests for the weather update CronJob and shared weather data persistent volume claim.
- Added tests for cached weather data reads, weather update cache writes, EFD query result parsing, and missing-data handling.
