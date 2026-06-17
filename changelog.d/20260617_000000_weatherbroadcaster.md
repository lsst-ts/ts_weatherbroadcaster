### Backwards-incompatible changes

- Renamed the project, Python package, default URL prefix, Docker entry point, and Kubernetes resources from `ts_weatherbroadcaster` to `weatherbroadcaster`.
- Changed the settings environment variable prefix from `TS_WEATHERBROADCASTER_` to `WEATHERBROADCASTER_`.

### New features

- Added weather cache generation from EFD data, including atomic JSON cache replacement and local-development Kubernetes manifests for running the API and updater.
- Added Documenteer-based documentation and generated OpenAPI documentation support.

### Bug fixes

- Improved weather aggregation by handling missing/null EFD values, using the latest available data, and computing wind direction as a speed-weighted circular mean.
