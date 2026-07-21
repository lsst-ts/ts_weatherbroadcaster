# Change log

weatherbroadcaster is versioned with [semver](https://semver.org/).
Dependencies are updated to the latest available version during each release, and aren't noted here.

Find changes for the upcoming release in the project's [changelog.d directory](https://github.com/lsst-sqre/weatherbroadcaster/tree/main/changelog.d/).

<!-- scriv-insert-here -->

<a id='changelog-v0.3.0'></a>
## v0.3.0 (2026-07-17)

### New features

- Add a weather-update CLI with bounded retries, configurable request timeout
  and update interval, and a local Kubernetes updater sidecar.

<a id='changelog-v0.2.0'></a>
## v0.2.0 (2026-06-17)

### Backwards-incompatible changes

- Renamed the project, Python package, default URL prefix, Docker entry point, and Kubernetes resources from `ts_weatherbroadcaster` to `weatherbroadcaster`.
- Changed the settings environment variable prefix from `TS_WEATHERBROADCASTER_` to `WEATHERBROADCASTER_`.

### New features

- Added weather cache generation from EFD data, including atomic JSON cache replacement and local-development Kubernetes manifests for running the API and updater.
- Added Documenteer-based documentation and generated OpenAPI documentation support.

### Bug fixes

- Improved weather aggregation by handling missing/null EFD values, using the latest available data, and computing wind direction as a speed-weighted circular mean.

<a id='changelog-v0.1.0'></a>
## v0.1.0 (2026-06-17)

### New features

- Added a weather update command that fetches EFD weather data and writes a cached MeteoBlue-compatible JSON payload.
- Added configurable weather data file path support via `WEATHERBROADCASTER_WEATHER_DATA_FILE_PATH`.

### Other changes

- Added Kubernetes manifests for the weather update CronJob and shared weather data persistent volume claim.
- Added tests for cached weather data reads, weather update cache writes, EFD query result parsing, and missing-data handling.
