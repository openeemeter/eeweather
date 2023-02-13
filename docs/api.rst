API Docs
========

International
-------

.. autofunction:: eeweather.get_weather_intl

.. autofunction:: eeweather.get_lat_long

.. autofunction:: eeweather.get_weather_intervals_for_similar_sites

Ranking
-------

.. autofunction:: eeweather.rank_stations

.. autofunction:: eeweather.combine_ranked_stations

.. autofunction:: eeweather.select_station

``ISDStation`` objects
----------------------

.. autoclass:: eeweather.ISDStation
   :members:

Summaries
---------

.. autofunction:: eeweather.summaries.get_zcta_ids

.. autofunction:: eeweather.summaries.get_isd_station_usaf_ids

Geography
---------

.. autofunction:: eeweather.geo.get_lat_long_climate_zones

.. autofunction:: eeweather.geo.get_zcta_metadata

.. autofunction:: eeweather.geo.zcta_to_lat_long

Database
--------

.. autofunction:: eeweather.database.build_metadata_db

Exceptions
----------

.. autoexception:: eeweather.EEWeatherError

.. autoexception:: eeweather.ISDDataNotAvailableError

.. autoexception:: eeweather.UnrecognizedZCTAError

.. autoexception:: eeweather.UnrecognizedUSAFIDError

Validators
----------

.. autofunction:: eeweather.validation.valid_zcta_or_raise

.. autofunction:: eeweather.validation.valid_usaf_id_or_raise

Visualization
-------------

.. autofunction:: eeweather.plot_station_mapping

.. autofunction:: eeweather.plot_station_mappings
