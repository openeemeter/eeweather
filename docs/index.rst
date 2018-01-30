.. spelling::

   EEmeter
   shapefiles
   metadata

EEweather: Weather station wrangling for EEmeter
================================================

.. image:: https://travis-ci.org/openeemeter/eeweather.svg?branch=master
    :target: https://travis-ci.org/openeemeter/eeweather

.. image:: https://img.shields.io/github/license/openeemeter/eeweather.svg
    :target: https://github.com/openeemeter/eeweather

.. image:: https://readthedocs.org/projects/eeweather/badge/?version=latest
    :target: http://eeweather.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/pypi/v/eeweather.svg
    :target: https://img.shields.io/pypi/v/eeweather.svg

---------------

**EEweather** — tools for matching to and fetching data from NCDC ISD, TMY3, or CZ2010 weather stations.

EEweather comes with a database of weather station metadata, ZCTA metadata, and GIS data that makes it easier to find the right weather station to use for a particular ZIP code or lat/long coordinate.

Installation
------------

EEweather is a python package and can be installed with pip.

::

    $ pip install eeweather

Supported Sources of Weather Data
---------------------------------

- NCDC Integrated Surface Database (ISD)
- Global Summary of the Day (GSOD)
- NREL Typical Meteorological Year 3 (TMY3)
- California Energy Commission 1998-2009 Weather Normals (CZ2010)

Features
--------

- Match by ZIP code (ZCTA) or by lat/long coordinates
- Use user-supplied weather station mappings
- Match within climate zones

  - IECC Climate Zones
  - IECC Moisture Regimes
  - Building America Climate Zones
  - California Building Climate Zone Areas

- User-friendly SQLite database of metadata compiled from primary sources

  - US Census Bureau (ZCTAs, county shapefiles)
  - Building America climate zone county lists
  - NOAA NCDC Integrated Surface Database Station History
  - NREL TMY3 site

- Plot maps of outputs

Command-line Usage
------------------

Once installed, ``eeweather`` can be run from the command-line. To see all available commands, run ``eeweather --help``.

Find a weather station near the ZIP code 90001::

    $ eeweather match_zcta 90001
    722874

Find a weather station near the lat-long coordinate (38.561, -121.487)::

    $ eeweather match_lat_long -- 38.561 -121.487
    724830

View ISD station metadata::

    $ eeweather inspect_isd_station 722874
    {
      "usaf_id": "722874",
      "wban_ids": "93134",
      "recent_wban_id": "93134",
      "name": "DOWNTOWN L.A./USC CAMPUS",
      "latitude": "+34.024",
      "longitude": "-118.291",
      "elevation": "+0054.6",
      "quality": "high",
      "iecc_climate_zone": "3",
      "iecc_moisture_regime": "B",
      "ba_climate_zone": "Hot-Dry",
      "ca_climate_zone": "CA_08"
    }

Download raw ISD files::

    $ wget `eeweather inspect_isd_filenames 722874 2017`

Download raw GSOD files::

    $ wget `eeweather inspect_gsod_filenames 722874 2017`

Enter the SQLite command line for the metadata database::

    $ eeweather inspect_db
    SQLite version 3.19.3 2017-06-27 16:48:08
    Enter ".help" for usage hints.
    sqlite> .tables
    ba_climate_zone_metadata       isd_station_metadata
    ca_climate_zone_metadata       tmy3_station_metadata
    iecc_climate_zone_metadata     zcta_metadata
    iecc_moisture_regime_metadata  zcta_to_isd_station
    isd_file_metadata              zipcode_to_cz2010_station
    sqlite> .headers on
    sqlite> select * from isd_station_metadata where ca_climate_zone = 'CA_06' limit 10;
    usaf_id|wban_ids|recent_wban_id|name|latitude|longitude|elevation|quality|iecc_climate_zone|iecc_moisture_regime|ba_climate_zone|ca_climate_zone
    722883|99999|99999|HERMOSA BEACH PIER|+33.870|-118.400|+0008.0|low|3|B|Hot-Dry|CA_06
    722885|93197,99999|93197|SANTA MONICA MUNI AIRPORT|+34.016|-118.451|+0053.0|high|3|B|Hot-Dry|CA_06
    722913|99999|99999|MARINA DEL REY|+33.970|-118.430|+0008.0|low|3|B|Hot-Dry|CA_06
    722917|99999|99999|LONG BEACH|+33.770|-118.170|+0003.0|low|3|B|Hot-Dry|CA_06
    722933|99999|99999|SAN CLEMENTE|+33.420|-117.620|+0003.0|low|3|B|Hot-Dry|CA_06
    722935|99999|99999|EL CAPITAN BEACH|+34.467|-120.033|+0027.0|low|3|C|Marine|CA_06
    722950|23174|23174|LOS ANGELES INTERNATIONAL AIRPORT|+33.938|-118.389|+0029.6|high|3|B|Hot-Dry|CA_06
    722954|99999|99999|ZUMA BEACH|+34.020|-118.820|+0006.0|low|3|B|Hot-Dry|CA_06
    722955|03122,03174,99999|03174|ZAMPERINI FIELD AIRPORT|+33.803|-118.340|+0029.6|low|3|B|Hot-Dry|CA_06
    722974|99999|99999|LONG BEACH|+33.767|-118.167|+0003.0|low|3|B|Hot-Dry|CA_06
    sqlite> .quit

Usage Guides
------------

.. toctree::
   :maxdepth: 2

   basics
   advanced
   api
