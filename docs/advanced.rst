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

Charting Station mappings
-------------------------

.. note:: Requires `matplotlib` to be installed.

Within (for example) a jupyter notebook you can create plots like this::

    >>> station = eeweather.ISDStation('722990')
    >>> eeweather.plot_station_mapping(
    ...     lat, lng, station, distance_meters=21900, target='91104')

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
