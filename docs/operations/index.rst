##########
Operations
##########

The service is intended to run as a FastAPI web application alongside a
Kubernetes CronJob that periodically refreshes the cached weather data file.

Weather cache
=============

Both the API deployment and the weather update CronJob must be configured with
the same ``WEATHERBROADCASTER_WEATHER_DATA_FILE_PATH`` value, or must mount
the same Kubernetes volume at the default path:

.. code-block:: text

   /data/weather.json

The API reads this file for ``GET /weatherbroadcaster/data``. The CronJob
writes it by running:

.. code-block:: bash

   python -m weatherbroadcaster.update_weather

Local Kubernetes resources
==========================

The repository includes manifests under ``k8s/`` for local development and
manual testing of the service deployment, service, persistent volume claim, and
weather update CronJob.

These manifests are not the production Kubernetes deployment configuration.
Production deployment is managed through a separate Kubernetes setup.
