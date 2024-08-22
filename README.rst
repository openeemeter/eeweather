EEweather: Weather station wrangling for EEmeter
================================================

.. image:: https://travis-ci.org/openeemeter/eeweather.svg?branch=master
    :target: https://travis-ci.org/openeemeter/eeweather

.. image:: https://img.shields.io/github/license/openeemeter/eeweather.svg
    :target: https://github.com/openeemeter/eeweather

.. image:: https://readthedocs.org/projects/eeweather/badge/?version=latest
    :target: http://eeweather.readthedocs.io/en/latest/?badge=latest

.. image:: https://img.shields.io/pypi/v/eeweather.svg
    :target: https://pypi.python.org/pypi/eeweather

.. image:: https://codecov.io/gh/openeemeter/eeweather/branch/master/graph/badge.svg
  :target: https://codecov.io/gh/openeemeter/eeweather

---------------

**EEweather** — tools for matching to and fetching data from NCDC ISD, TMY3, or CZ2010 weather stations.

EEweather comes with a database of weather station metadata, ZCTA metadata, and GIS data that makes it easier to find the right weather station to use for a particular ZIP code or lat/long coordinate.

`Read the docs. <https://eeweather.readthedocs.org/>`_

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
    $ pipenv install -e .    # install package in editable mode
    $ pipenv shell           # activate pipenv virtual environment

Build docs::

    $ make -C docs html

Autobuild docs::

    $ make -C docs livehtml

Check spelling in docs::

    $ make -C docs spelling

Run tests::

    $ pytest

Run tests on multiple python versions::

    $ tox

Upload to pypi (using twine)::

    $ python setup.py upload

Use with Docker
---------------

To use with docker-compose, use the following:

Run a tutorial notebook (copy link w/ token, open tutorial.ipynb)::

    $ docker-compose up jupyter

Live-edit docs::

    $ docker-compose up docs

Open a shell::

    $ docker-compose run --rm shell

Run tests::

    $ docker-compose run --rm test

Run the CLI::

    $ docker-compose run --rm eeweather --help


Notice Regarding CZ2010 Data
----------------------------

There may be conditions placed on their international commercial use.
They can be used within the U.S. or for non-commercial international activities without restriction.
The non-U.S. data cannot be redistributed for commercial purposes.
Re-distribution of these data by others must provide this same notification.

See `further explanation <http://weather.whiteboxtechnologies.com/faq#Q12/>`_ here. 

Metadata Yearly Updates
-----------------------
Every year, the metadata database needs to be updated. This can be done by running:

```
docker-compose run --rm eeweather rebuild-db
```
