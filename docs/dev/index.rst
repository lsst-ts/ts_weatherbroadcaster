###########
Development
###########

Run the test suite with:

.. code-block:: bash

   uv run pytest

Run static typing checks with:

.. code-block:: bash

   uv run tox run -e typing

Run the development server with:

.. code-block:: bash

   make run

For local development, set the weather data file path to a writable local path
before running the API and updater:

.. code-block:: bash

   WEATHERBROADCASTER_WEATHER_DATA_FILE_PATH=/tmp/weatherbroadcaster/weather.json make run
