Advanced Usage
==============

Digging deeper into eeweather features.

Caching Weather Data
--------------------

By default, a small SQLite database is setup at ``~/.eeweather/cache.db`` that
is used to save weather data that is pulled from primary sources, such as the
NOAA FTP site. This is done partially out of courtesy to the service, but also
because it vastly speeds up the process of obtaining weather data. This local
cache can be pointed to a different database by setting the environment
variable `EEWEATHER_CACHE_URL` to any URL supported by SQLalchemy.

For example::

    export EEWEATHER_CACHE_URL=postgres://user:password@host:port/dbname

Custom Weather Mappings
-----------------------

To use a custom weather mapping, a dictionary or function can be passed to one of the matching functions.

Example with dict::

    >>> mapping = {'93505': '723171'}
    >>> eeweather.match_zcta('93505', mapping=mapping)
    ISDStationMapping('723171')

Example with function returning usaf_id::

    >>> mapping = lambda zcta: '722860'
    >>> eeweather.match_zcta('93505', mapping=mapping)
    ISDStationMapping('723171')

Example with library function returning mappings::

    >>> from eeweather.mappings import zcta_naive_closest_high_quality
    >>> eeweather.match_zcta('93505', mapping=zcta_naive_closest_high_quality)
    ISDStationMapping('723171')

If the supplied mapping does not contain the ZCTA target, an empty mapping result will be returned::

    >>> eeweather.match_zcta('93501', mapping=mapping)
    EmptyMapping(warnings=['ZCTA ID "93501" was not found in mapping dictionary.'])

If the ZCTA or station is not recognized, an error will be thrown::

    >>> mapping = {'93505': 'BAD_STATION'}
    >>> eeweather.match_zcta('BAD_ZCTA', mapping=mapping)
    ...
    eeweather.exceptions.UnrecognizedZCTAError: BAD_ZCTA
    >>> eeweather.match_zcta('93505', mapping=mapping)
    ...
    eeweather.exceptions.UnrecognizedUSAFIDError: BAD_STATION

Charting ISDStationMapping objects
----------------------------------

.. note:: Requires `matplotlib` to be installed.

Within (for example) a jupyter notebook you can create plots like this::

    result = eeweather.match_zcta('91104')
    result.plot()

This will create a plot like the following:

.. image:: _static/plot-91104-to-722880.png
   :target: _static/plot-91104-to-722880.png

Advanced database inspection
----------------------------

Using the CLI
/////////////

If you prefer a GUI: `SQLite Browser <http://sqlitebrowser.org/>`_

The default database location is at ``~/.eeweather/cache.db``.

How to log into the database::

    $ eeweather inspect_db
    SQLite version 3.19.3 2017-06-27 16:48:08
    Enter ".help" for usage hints.
    sqlite>

List all tables::

    sqlite> .tables

Turn on headers for results::

    sqlite> .headers on

Example queries
///////////////

Get more information about a specific ISD station.

.. code-block:: sql

    select
      *
    from
      isd_station_metadata
    where
      usaf_id = '722860'

List top ten closest ISD stations for a particular ZCTA:

.. code-block:: sql

    select
      *
    from
      zcta_to_isd_station
    where
      zcta_id = '90001'
    order by
      rank

Find closest high quality USAF_ID station in the same climate zones with high quality data, reporting distance to that station, and the lat/long coordinates of the target ZCTA:

.. code-block:: sql

    select
      z2i.usaf_id
      , z2i.distance_meters
      , zcta.latitude
      , zcta.longitude
    from
      zcta_to_isd_station z2i
      join isd_station_metadata isd on
        z2i.usaf_id = isd.usaf_id
      join zcta_metadata zcta on
        z2i.zcta_id = zcta.zcta_id
    where
      z2i.zcta_id = '90001'
      and isd.quality = 'high'
      and z2i.iecc_climate_zone_match
      and z2i.iecc_moisture_regime_match
      and z2i.ba_climate_zone_match
      and z2i.ca_climate_zone_match
    order by
      rank
    limit 1

Rebuilding the Database
-----------------------

The metadata database can be rebuilt from primary sources using the CLI.

Exercise some caution when running this command, as it will overwrite the existing db::

    $ eeweather rebuild_db

To see all options, run::

    $ eeweather rebuild_db --help
    Usage: eeweather rebuild_db [OPTIONS]

    Options:
      --zcta-geometry / --no-zcta-geometry
      --iecc-climate-zone-geometry / --no-iecc-climate-zone-geometry
      --iecc-moisture-regime-geometry / --no-iecc-moisture-regime-geometry
      --ba-climate-zone-geometry / --no-ba-climate-zone-geometry
      --ca-climate-zone-geometry / --no-ca-climate-zone-geometry
      --n-closest-stations INTEGER
      --help                          Show this message and exit.
