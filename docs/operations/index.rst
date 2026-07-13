##########
Operations
##########

The service is intended to run as a FastAPI web application with a Kubernetes
sidecar container that periodically refreshes the cached weather data file.

Weather cache
=============

Both containers in the API deployment must use the same
``WEATHERBROADCASTER_WEATHER_DATA_FILE_PATH`` value, or must mount the same
Kubernetes volume at the default path:

.. code-block:: text

   /data/weather.json

The API reads this file for ``GET /weatherbroadcaster/data``. The API
container mounts the volume read-only. Its ``update-weather`` sidecar mounts
the volume read-write and runs:

.. code-block:: bash

   weatherbroadcaster update --loop

The sidecar updates immediately when its pod starts, and then at the configured
interval. Kubernetes restarts it if the updater process exits.

EFD request timeout
===================

``WEATHERBROADCASTER_WEATHER_FETCH_TIMEOUT`` sets the maximum number of
seconds to wait for all EFD weather queries. It defaults to 30 seconds. A
timed-out update exits with an error, leaving the existing cache file intact.

When using ``weatherbroadcaster update --loop``, a timeout is retried twice,
after 5 and 30 seconds. The next update cycle begins after the final attempt.

Update interval
===============

``WEATHERBROADCASTER_WEATHER_UPDATE_INTERVAL`` sets the number of seconds
between sidecar update cycles. It defaults to 3600 seconds. The local
Deployment sets it explicitly to one hour.

Local Kubernetes resources
==========================

The repository includes manifests under ``k8s/`` for local development and
manual testing of the service deployment, service, persistent volume claim, and
weather update sidecar.

These manifests are not the production Kubernetes deployment configuration.
Production deployment is managed through a separate Kubernetes setup.
