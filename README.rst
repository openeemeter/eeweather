EEweather: Weather station wrangling for EEmeter
================================================

.. image:: https://travis-ci.org/openeemeter/eeweather.svg?branch=master
    :target: https://travis-ci.org/openeemeter/eeweather

.. image:: https://img.shields.io/github/license/openeemeter/eeweather.svg
    :target: https://github.com/openeemeter/eeweather

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

Contributing
------------

Dev installation::

    $ pipenv --python 3.6.4  # create virtualenv with python 3.6.4
    $ pipenv install --dev   # install dev requirements with pipenv
    $ pipenv shell           # activate pipenv virtual environment

Build docs::

    make -C docs html

Autobuild docs::

    make -C docs livehtml

Run tests::

    pytest

Run tests on multiple python versions::

    tox
