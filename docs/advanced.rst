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

ZCTA to latitude/longitude conversion
-------------------------------------

Convert ZCTA targets into latitude/longitudes based on their centroid::

    >>> eeweather.zcta_to_lat_long(90210)
    (34.1010279124639, -118.414760978568)

If the ZCTA or station is not recognized, an error will be thrown::

    >>> eeweather.zcta_to_lat_long('BAD_ZCTA')
    ...
    UnrecognizedZCTAError: BAD_STATION

Custom weather mappings
-----------------------

To use a custom weather mapping, a dictionary or function can be passed to one of the matching functions.

Example with function returning ISDStationMapping::

    >>> lat, long = 34.0522, -118.2437
    >>> mapping = lambda lat, long: '722880'
    >>> eeweather.match_lat_long(lat,long, mapping = mapping)
    ISDStationMapping('722880', distance_meters=19585)

Example with library function returning mappings based only on distance::

    >>> from eeweather.mappings import lat_long_naive_closest
    >>> lat, long = 34.0522, -118.2437
    >>> eeweather.match_lat_long(lat, long, mapping=lat_long_naive_closest)
    ISDStationMapping('722874', distance_meters=5372)

Example with library function returning mappings for stations based only on distance that contain TMY3 data::

    >>> from eeweather.mappings import lat_long_naive_closest_tmy3
    >>> lat, long = 34.0522, -118.2437
    >>> eeweather.match_lat_long(lat, long, mapping=lat_long_naive_closest)
    ISDStationMapping('722956', distance_meters=16583)

Example with library function returning mappings for stations based only on distance that contain CZ2010 data::

    >>> from eeweather.mappings import lat_long_naive_closest_cz2010
    >>> lat, long = 34.0522, -118.2437
    >>> eeweather.match_lat_long(lat, long, mapping=lat_long_naive_closest_cz2010)
    ISDStationMapping('722956', distance_meters=16583)

Example with library function returning mappings based on distance within the same climate_zone::

    >>> from eeweather.mappings import lat_long_closest_within_climate_zone
    >>> lat, long = 34.0522, -118.2437
    >>> eeweather.match_lat_long(lat, long, mapping=lat_long_closest_within_climate_zone)
    ISDStationMapping('722880', distance_meters=19585)

Example with library function returning mappings based on distance within the same climate_zone that contain TMY3 data::

    >>> from eeweather.mappings import lat_long_closest_within_climate_zone_tmy3
    >>> lat, long = 34.0522, -118.2437
    >>> eeweather.match_lat_long(lat, long, mapping=lat_long_closest_within_climate_zone_tmy3)
    IISDStationMapping('722880', distance_meters=19585)

Example with library function returning mappings based on distance within the same climate_zone that contain CZ2010 data::

    >>> from eeweather.mappings import lat_long_closest_within_climate_zone_cz2010
    >>> lat, long = 34.0522, -118.2437
    >>> eeweather.match_lat_long(lat, long, mapping=lat_long_closest_within_climate_zone_cz2010)
    ISDStationMapping('722880', distance_meters=19585)

Example with library function returning mappings for stations based only on distance that contain CZ2010 data::

    >>> from eeweather.mappings import lat_long_naive_closest_cz2010
    >>> lat, long = 34.0522, -118.2437
    >>> eeweather.match_lat_long(lat, long, mapping=lat_long_naive_closest_cz2010)
    ISDStationMapping('722956', distance_meters=16583)


If the station is not recognized, an error will be thrown::
    >>> lat, long = 34.0522, -1108.2437
    >>> mapping = lambda lat, long: 'BAD_STATION'
    >>> eeweather.match_lat_long(lat, long, mapping=mapping)
    ...
    eeweather.exceptions.UnrecognizedUSAFIDError: BAD_STATION

Charting ISDStationMapping objects
----------------------------------

.. note:: Requires `matplotlib` to be installed.

Within (for example) a jupyter notebook you can create plots like this::

    lat, long = 34.0522, -1108.2437
    result = eeweather.match_lat_long(lat, long)
    result.plot()

This will create a plot like the following:

.. image:: _static/plot-91104-to-722880.png
   :target: _static/plot-91104-to-722880.png

Advanced database inspection
----------------------------

Using the CLI
/////////////

If you prefer a GUI: `SQLite Browser <http://sqlitebrowser.org/>`_

The default database location is ``~/.eeweather/cache.db``.

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
