.. spelling::

    metadata

Basic Usage
===========

This document describes how to get started with eeweather.


Matching to weather stations
----------------------------

EEweather is designed to support the process of finding sources of data that correspond to particular sites. As there are many approaches to this process of matching, the EEweather package is designed to be flexible and to accommodate many different approaches.

EEweather provides sensible default mappings from geographical markers to weather stations so that it can be used out of the box.

EEweather can use either ZCTAs or lat/long coordinates as targets for weather matching. Both of these methods are described below.

Latitude/Longitude Coordinates
//////////////////////////////

The recommended way to find the weather station(s) that correspond to a particular site is to use the lat-long coordinates of that site. Lat/long data is not always available, so ZCTAs can also be used.

Example usage::

    >>> import eeweather
    >>> result = eeweather.match_lat_long(35, -95)
    >>> result
    ISDStationMapping('722178')

This ``ISDStationMapping`` object captures some information about the mapping::

    >>> result.distance_meters
    34672.136079403026
    >>> result.warnings
    []

That particular result has no associated warnings, but other mappings may have associated warnings, such as the mapping from this point which is in the middle of the Gulf of Mexico, 700km away from the nearest weather station and outside of the climate zone boundary::

    >>> result = eeweather.match_lat_long(20, -95)
    >>> result.distance_meters
    700435
    >>> result.warnings
    ['Distance from target to weather station is greater than 50km.', 'Mapped weather station is not in the same climate zone as the provided lat/long point.']

ZIP Code Tabulation Areas (ZCTAs)
/////////////////////////////////

ZIP codes are often abused as rough geographic markers. They are not particularly well set up be used as the basis of a GIS system - some ZIP codes correspond to single buildings or post-offices, some cover thousands of square miles of land. The US Census Bureau transforms census blocks into what they call ZIP Code Tabulation Areas, and use these instead. There are roughly 10k ZIP codes that are not used as ZCTAs, and ZCTAs do not correspond directly to ZIP codes, but for matching to weather stations, which are much sparser than ZIP codes, this rough mapping is usually sufficient. Often tens or hundreds of ZCTAs will be matched to the same weather station.

.. image:: _static/station-mapping.png
   :target: _static/station-mapping.png

*Our default mapping of ZCTA centroids (points at spokes) to high-quality ISD stations (points at centers).*

.. note:: The default mapping concentrates on weather stations in US states (including AK, HI) and territories, including PR, GU, VI etc).

Example usage::

    >>> result = eeweather.match_zcta('70001')
    >>> result
    ISDStationMapping('998194')

This ``ISDStationMapping`` object also captures some information about the mapping::

    >>> result.distance_meters
    6088
    >>> result.warnings
    []

Obtaining temperature data
--------------------------

These matching results carry a reference to a weather station object. The weather station object has some associated metadata and - most importantly - has methods for obtaining weather data.

Let's look at the mapping result object from the section above::

    >>> station = result.isd_station
    >>> station
    ISDStation('722500')

This ``ISDStation`` object carries information about that station and methods for fetching corresponding weather data.

The ``.json()`` method gives a quick summary of associated metadata in a format that can easily be serialized::

    >>> import json
    >>> print(json.dumps(station.json(), indent=2)
    {
      "elevation": 7.3,
      "latitude": 25.914,
      "longitude": -97.423,
      "name": "BROWNSVILLE/S PADRE  ISLAND INTL AP",
      "quality": "high",
      "wban_ids": [
        "12919"
      ],
      "recent_wban_id": "12919",
      "climate_zones": {
        "iecc_climate_zone": "2",
        "iecc_moisture_regime": "A",
        "ba_climate_zone": "Hot-Humid",
        "ca_climate_zone": null
      }
    }

Most of these are also stored as attributes on the object::

    >>> station.usaf_id
    '722500'
    >>> station.latitude, station.longitude
    (25.914, -97.423)
    >>> station.coords
    (25.914, -97.423)
    >>> station.name
    'BROWNSVILLE/S PADRE  ISLAND INTL AP'
    >>> station.iecc_climate_zone
    '2'
    >>> station.iecc_moisture_regime
    'A'

In addition to these simple attributes there are a host of methods that can be used to fetch temperature data. The simplest are these, which return `pandas.Series` objects.

Note that this temperature data is given in degrees *Celsius*, not Fahrenheit. (:math:`T_F = T_C \cdot 1.8 + 32`), and that the ``pd.Timestamp`` index is given in UTC.


ISD temperature data as an hourly time series::

    >>> import datetime
    >>> start_date = datetime.datetime(2016, 6, 1)
    >>> end_date = datetime.datetime(2017, 9, 15)
    >>> tempC = station.load_isd_hourly_temp_data(start_date, end_date)
    >>> tempC.head()
    2016-06-01 00:00:00+00:00    28.291500
    2016-06-01 01:00:00+00:00    27.438500
    2016-06-01 02:00:00+00:00    27.197083
    2016-06-01 03:00:00+00:00    26.898750
    2016-06-01 04:00:00+00:00    26.701810
    Freq: H, dtype: float64
    >>> tempF = tempC * 1.8 + 32
    >>> tempF.head()
    2016-06-01 00:00:00+00:00    82.924700
    2016-06-01 01:00:00+00:00    81.389300
    2016-06-01 02:00:00+00:00    80.954750
    2016-06-01 03:00:00+00:00    80.417750
    2016-06-01 04:00:00+00:00    80.063259

ISD temperature data as a daily time series::

    >>> tempC = station.load_isd_daily_temp_data(start_date, end_date)
    >>> tempC.head()
    2016-06-01 00:00:00+00:00    26.017917
    2016-06-02 00:00:00+00:00    26.256624
    2016-06-03 00:00:00+00:00    24.297847
    2016-06-04 00:00:00+00:00    23.836875
    2016-06-05 00:00:00+00:00    23.782465
    Freq: D, dtype: float64
    >>> tempF = tempC * 1.8 + 32
    >>> tempF.head()
    2016-06-01 00:00:00+00:00    78.83222
    2016-06-02 00:00:00+00:00    79.26188
    2016-06-03 00:00:00+00:00    75.73604
    2016-06-04 00:00:00+00:00    74.90642
    2016-06-05 00:00:00+00:00    74.80850
    Freq: D, dtype: float64

GSOD temperature data as a daily time series::

    >>> tempC = station.load_gsod_daily_temp_data(start_date, end_date)
    >>> tempC.head()
    2016-06-01 00:00:00+00:00    26.055556
    2016-06-02 00:00:00+00:00    26.388889
    2016-06-03 00:00:00+00:00    24.555556
    2016-06-04 00:00:00+00:00    23.888889
    2016-06-05 00:00:00+00:00    23.722222
    Freq: D, dtype: float64
    >>> tempF = temps * 1.8 + 32
    >>> tempF.head()
    2016-06-01 00:00:00+00:00    78.83222
    2016-06-02 00:00:00+00:00    79.26188
    2016-06-03 00:00:00+00:00    75.73604
    2016-06-04 00:00:00+00:00    74.90642
    2016-06-05 00:00:00+00:00    74.80850
    Freq: D, dtype: float64
