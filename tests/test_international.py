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

import datetime
from dateutil.relativedelta import relativedelta
import eeweather
import numpy as np
import pandas as pd
from pathlib import Path


def test_get_lat_long():
    p = Path().resolve().parents[0]
    df = pd.read_csv(str(p) + "/samples/test_locations.csv", index_col=0)
    postcodes = df["postal_code"].to_list()
    latitude_ref = df["latitude"].to_list()
    longitude_ref = df["longitude"].to_list()
    for postcode, latitude, longitude in zip(postcodes, latitude_ref, longitude_ref):
        latitude_test, longitude_test = eeweather.get_lat_long(postcode)
        assert isinstance(latitude_test, float)
        assert isinstance(longitude_test, float)
        assert latitude_test - 1 < latitude < latitude_test + 1
        assert longitude_test - 1 < longitude < longitude_test + 1


def test_get_weather_intervals_for_similar_sites():
    p = Path().resolve().parents[0]
    df = pd.read_csv(str(p) + "/samples/sample_sites.csv", index_col=0)
    df["end_date"] = pd.to_datetime(df["end_date"])
    df["start_date"] = pd.to_datetime(df["start_date"])
    (
        df_collated,
        df_shorter_intervals,
    ) = eeweather.get_weather_intervals_for_similar_sites(df)
    for i in df_shorter_intervals.iterrows():
        shorter_interval = i[-1]["end_date"] - i[-1]["start_date"]
        larger_interval = (
            df_collated[df_collated.index == i[-1]["matching_index"]]["end_date"]
            - df_collated[df_collated.index == i[-1]["matching_index"]]["start_date"]
        )
        larger_interval = larger_interval.iloc[0]
        assert larger_interval > shorter_interval


def test_get_weather_intl():
    p = Path().resolve().parents[0]
    df = pd.read_csv(str(p) + "/samples/test_locations.csv", index_col=0)
    for lat, long in zip(df["latitude"], df["longitude"]):
        weather = eeweather.get_weather_intl(
            start_date=datetime.datetime.now() - relativedelta(years=1),
            end_date=datetime.datetime.now(),
            latitude=lat,
            longitude=long,
        )
        assert isinstance(weather["temp"].iloc[0], np.float32)
        assert isinstance(weather.index, pd.DatetimeIndex)
