.. spelling::

   EmptyMapping
   ISDStationMapping
   eeweather
   resampled
   oee
   zcta
   metadata
   resample
   matplotlib
   cartopy
   Deserialize
   UnrecognizedZCTAError
   UnrecognizedUSAFIDError
   Validators
   isd

API Docs
========

Matching
--------

.. autofunction:: eeweather.match_zcta

Mappings for use with ``eeweather.match_zcta``
//////////////////////////////////////////////

.. autofunction:: eeweather.mappings.zcta_closest_within_climate_zone

.. autofunction:: eeweather.mappings.zcta_naive_closest_high_quality

.. autofunction:: eeweather.mappings.zcta_naive_closest_medium_quality

.. autofunction:: eeweather.mappings.oee_zcta

------------

.. autofunction:: eeweather.match_lat_long

Mappings for use with ``eeweather.match_lat_long``
//////////////////////////////////////////////////

.. autofunction:: eeweather.mappings.lat_long_closest_within_climate_zone

.. autofunction:: eeweather.mappings.lat_long_naive_closest

.. autofunction:: eeweather.mappings.oee_lat_long

``MappingResult`` objects
-------------------------

.. autoclass:: eeweather.MappingResult
   :members: is_empty

.. autoclass:: eeweather.EmptyMapping
   :members: is_empty

.. autoclass:: eeweather.ISDStationMapping
   :members: is_empty, plot

.. autofunction:: eeweather.plot_mapping_results

``ISDStation`` objects
----------------------

.. autoclass:: eeweather.ISDStation
   :members:

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
