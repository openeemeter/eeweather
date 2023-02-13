#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""

   Copyright 2023 The Society for the Reduction of Carbon, Ltd (T/A Carbon Co-op).

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.

"""

import warnings

import numpy as np
import pandas as pd
from dateutil.relativedelta import relativedelta
import xarray as xr
import cdsapi
from datetime import datetime
from geopy.geocoders import Nominatim
import tempfile
import logging
import time

__all__ = (
    "get_weather_intl",
    "get_lat_long",
    "get_weather_intervals_for_similar_sites",
)


# function for api request
def call_ecmwf_api(year, months, days, filename, area):
    times = ["{:02d}:00".format(hour) for hour in range(24)]

    c = cdsapi.Client()
    c.retrieve(
        "reanalysis-era5-single-levels",
        {
            "product_type": "reanalysis",
            "format": "grib",
            "variable": "2m_temperature",
            "year": year,
            "month": months,
            "day": days,
            "time": times,
            "area": area,
        },
        filename,
    )


def _get_weather_xr(ds, latitude, longitude):
    temp = xr.DataArray.to_numpy(
        ds.sel(latitude=latitude, method="nearest")
        .sel(longitude=longitude, method="nearest")
        .t2m
    )

    temp = np.subtract(temp, 273.15)
    temp_df = pd.DataFrame(
        temp,
        columns=["temp"],
        index=list(xr.DataArray.to_numpy(ds.time)),
    )
    temp_df.index.name = "Datetime"
    return temp_df


def get_ecmwf_df(year, months, days, filename, area, latitude, longitude):
    # Disable logging
    logging.disable(logging.INFO)
    logging.disable(logging.WARNING)
    call_ecmwf_api(
        year,
        months,
        days,
        filename,
        area,
    )
    ds = xr.open_dataset(filename, engine="cfgrib")
    df = _get_weather_xr(ds, latitude, longitude)
    # Enable logging
    logging.disable(logging.NOTSET)
    return df


def get_lat_long(areacode):
    """Derive the latitude/longitude co-ordinates of a given areacode (postcode/zipcode).

    This function makes use of the Nominatim package, available at: https://nominatim.org/. Nominatim converts any
    postcode/zipcode to global latitude/longitude co-ordinates to facilitate weather calls via the CDS API. Nominatim
    best practice requires that API calls do not exceed an absolute maximum of 1 per second.

    Use of Nominatim is governed by the OSMF Terms of Use, available at:
    https://wiki.osmfoundation.org/wiki/Terms_of_Use.


    Parameters
    ----------
    areacode : :any:`str`
        The postcode/zipcode relevant to a given site. For example:
            'SW1A 2DX' for Trafalgar Square, London, UK;
            '10117 Berlin' for Brandenburger Tor, Berlin, Germany;
            'NY 10036' for Times Square, New York, USA.

    Returns
    -------
    latitude : :any: 'float' between -180 and 180
        The actual latitude of the site concerned.
    longitude : :any: 'float' between -90 and 90
        The actual longitude of the site concerned.
    """

    # get bounding box for location
    locator = Nominatim(user_agent="untitled")
    location = locator.geocode(areacode)
    time.sleep(1)
    location = location.raw
    latitude = float(location["lat"])
    longitude = float(location["lon"])

    return latitude, longitude


def round_quarter(x: float):
    quarter = round(x * 4) / 4
    return quarter


def get_weather_intervals_for_similar_sites(df):
    """A function to identify unique co-ordinates across a DataFrame of sites
    and weather requirements, and to return a DataFrame with the maximum
    intervals required for each site. This function primarily exists to
    improve performance of the CDS API, used in EEWeather international.
    Instead of duplicating time-consuming weather calls for similar sites,
    this function instead identifies similar sites so that fewer calls can be
    made to the CDS API to return the same results.

    Parameters
    ----------
    df : : pandas 'DataFrame'
        Any pandas.DataFrame comprising energy consumption metadata arranged
        according to the following categories:
        - start_date: any 'datetime' corresponding to the beginning of each
        site's weather call interval. For CalTRACK, this is likely to
        correspond to the first meter recording.
        - end_date: any 'datetime' corresponding to the end of each
        site's weather call interval. For CalTRACK, this is likely to
        correspond to the last meter recording.
        - latitude: any 'float' corresponding to the latitude of the relevant
         site.
        - longitude: any 'float' corresponding to the latitude of the relevant
         site.
        Index can be any format, such as unique household identifiers if
        desired.

    Returns
    -------
    df_collated : : any: 'pandas.DataFrame'.
        A maximum-interval dataframe with start_date, end_date, latitude and
        longitude for each unique site across a geographically distributed
        portfolio of sites.
    """

    df["latitude"] = round_quarter(df["latitude"])
    df["longitude"] = round_quarter(df["longitude"])

    df_start_sort = (
        df.sort_values(by="start_date")
        .drop_duplicates(["latitude", "longitude"], keep="first")
        .sort_values(by=["latitude", "longitude"])
    )
    df_end_sort = (
        df.sort_values(by="end_date")
        .drop_duplicates(["latitude", "longitude"], keep="last")
        .sort_values(by=["latitude", "longitude"])
    )
    df_collated = pd.DataFrame(
        {
            "start_date": list(df_start_sort["start_date"]),
            "end_date": list(df_end_sort["end_date"]),
            "latitude": df_start_sort["latitude"],
            "longitude": df_start_sort["longitude"],
        }
    )

    # Merge the two dataframes on the index column
    merged_df = pd.merge(
        df, df_collated, left_index=True, right_index=True, how="outer", indicator=True
    )
    # Identify the rows that are only in df
    dropped_sites = list(merged_df[merged_df["_merge"] == "left_only"].index)

    df_shorter_intervals = df.loc[dropped_sites, :]

    def match_index(row):
        match = df_collated[
            (df_collated["latitude"] == row["latitude"])
            & (df_collated["longitude"] == row["longitude"])
        ]
        if match.empty:
            return None
        else:
            return match.index[0]

    df_shorter_intervals["matching_index"] = df_shorter_intervals.apply(
        match_index, axis=1
    )

    return df_collated, df_shorter_intervals


def get_weather_intl(
    start_date,
    end_date,
    latitude=None,
    longitude=None,
    areacode: str = None,
):
    """Download hourly 2m temperature data from the European Centre for Medium-range Weather Forecasts (ECMWF)'s via
    its Climate Data Store (CDS) API for anywhere in the world. CDS provides temperature data from 1959 to five days
    prior to any given request.

    This API call provides access to a broader range of temperature data than USAF/IECC/ISD data as provided elsewhere
    in EEWeather but performs more slowly. USAF/IECC/ISD weather calls should be utilised where possible, principally in
    the United States where relevant weather stations can be found. If the distance between the relevant site(s) and a
    United States weather station is excessively large to undertake meaningful analysis, the CDS API should be used.

    Note that get_weather_intl can call temperature data to a minimum interval of 1 day. This means that every call will
    return hourly temperature data for at least 24h for day(s) concerned, i.e. from 00:00:00 to 23:00:00. If the user
    requires temperature data only for a sub-section of a given day, df.loc[] should be used to sub-select temperature
    dataframes.

    The CDS API is subject to API rate limits, available at: https://cds.climate.copernicus.eu/live/limits. The relevant
    call is the 'online CDS data' as phrased.

    All data generated using Copernicus Climate Change Service information 2022 (or current year) as applicable in the
    CDS licence: https://cds.climate.copernicus.eu/cdsapp/#!/terms/licence-to-use-copernicus-products. While this data
    is free to use, distribute and adapt, the data is and will remain the property of the European Union. All
    reproductions/adaptations of this data should comply with the Copernicus terms of use, including attributing the
    Copernicus programme and the European Union as required.

    TECHNICAL NOTES

    1. Use of the CDS API requires all users to set up a CDS account and agree to the terms of the CDS licence,
    linked above.
    2. Users may also be required to set up the CDS API key and install a .cdsapirc file, in their home
    directory, guidance on which is available at: https://cds.climate.copernicus.eu/api-how-to.
    3. Users may be required to install the eccodes library, used for the interpretation of GRIB weather files.
        3a. This package has been designed for Linux systems, on which it can be installed using the following link:
        https://confluence.ecmwf.int/display/ECC/Releases; alternatively eccodes can be installed on Python 3 using
        pip3 install eccodes.
        3b. For Windows users, eccodes and the related Magics package can be installed with conda using
        conda install -c conda-forge eccodes Magics. Further details available at:
        https://www.ecmwf.int/en/newsletter/159/news/eccodes-and-magics-available-under-windows
    4. The cfgrib package is also required for the functioning of this package. If not already installed, users should
    install cfgrib via pip install cfgrib==0.8.4.5. Details available at: https://pypi.org/project/cfgrib/0.8.4.5/

    To check the progress of your download, visit: https://cds.climate.copernicus.eu/cdsapp#!/yourrequests

    Parameters
    ----------
    start_date : :any: 'datetime.datetime'
        The start date and time for the requested temperature series. Must be timezone-naive.
    end_date : :any: 'datetime.datetime'
        The end date and time for the requested temperature series. Must be timezone-naive.
    latitude : :any: 'float' between -90 and 90, optional
        The actual latitude of the site concerned.
    longitude : :any: 'float' between -180 and 180, optional
        The actual longitude of the site concerned.
    areacode : :any:`str`, optional
        The postcode/zipcode relevant to a given site. For example:
        'SW1A 2DX' for Trafalgar Square, London, UK;
        '10117 Berlin' for Brandenburger Tor, Berlin, Germany;
        'NY 10036' for Times Square, New York, USA.

    Returns
    -------
    weather : :any: 'pandas.DataFrame'
        Hourly deg C temperature data for the specified location in ascending order.

    """
    start_date = start_date.replace(tzinfo=None)
    end_date = end_date.replace(tzinfo=None)

    if end_date > (datetime.now() - relativedelta(days=5)):
        warnings.warn("Data not available for most recent 5 days.")

    if areacode is not None:
        latitude, longitude = get_lat_long(areacode)

    elif areacode is None and latitude is None and longitude is None:
        raise ValueError(
            "areacode cannot be None while latitude and longitude are also None. Enter either areacode or latitude and longitude values."
        )

    latitude = round_quarter(latitude)
    longitude = round_quarter(longitude)

    bounding_box = [
        latitude + 0.001,
        longitude - 0.001,
        latitude - 0.001,
        longitude + 0.001,
    ]

    end_date = min(
        end_date.replace(tzinfo=None), datetime.now() - relativedelta(days=6)
    )

    weather_list = []

    with tempfile.TemporaryDirectory() as td:
        filename = f"{td}/temp.grib"
        all_days = [str(n).rjust(2, "0") for n in range(1, 32)]

        for year in range(start_date.year, end_date.year + 1):
            if year == start_date.year:
                start_month = start_date.month
            else:
                start_month = 1

            if year == end_date.year:
                end_month = end_date.month
            else:
                end_month = 12

            months = [str(n).rjust(2, "0") for n in range(start_month, end_month + 1)]

            for month in months:
                weather_list.append(
                    get_ecmwf_df(
                        year,
                        month,
                        all_days,
                        filename,
                        bounding_box,
                        latitude,
                        longitude,
                    )
                )

    weather = pd.concat(weather_list)
    weather.sort_index(inplace=True)
    # Trim the dataframe to the correct start and end dates
    weather = weather[start_date:end_date]

    return weather
