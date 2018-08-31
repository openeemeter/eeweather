from datetime import datetime
import pandas as pd
import pytest
import pytz

from eeweather import (
    rank_stations,
    combine_ranked_stations,
    select_station,
)
from eeweather.exceptions import ISDDataNotAvailableError


@pytest.fixture
def lat_long_fresno():
    return 36.7378, -119.7871

@pytest.fixture
def lat_long_africa():
    return 0, 0


def test_rank_stations_no_filter(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = rank_stations(lat, lng)
    assert df.shape == (3864, 15)
    assert list(df.columns) == [
        'rank',
        'distance_meters',
        'latitude',
        'longitude',
        'iecc_climate_zone',
        'iecc_moisture_regime',
        'ba_climate_zone',
        'ca_climate_zone',
        'rough_quality',
        'elevation',
        'state',
        'tmy3_class',
        'is_tmy3',
        'is_cz2010',
        'difference_elevation_meters',
    ]
    assert round(df.distance_meters.iloc[0]) == 3008.0
    assert round(df.distance_meters.iloc[-10]) == 9614514.0
    assert pd.isnull(df.distance_meters.iloc[-1]) is True


def test_rank_stations_match_climate_zones_not_null(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = rank_stations(lat, lng, match_iecc_climate_zone=True)
    assert df.shape == (737, 15)

    df = rank_stations(lat, lng, match_iecc_moisture_regime=True)
    assert df.shape == (708, 15)

    df = rank_stations(lat, lng, match_ba_climate_zone=True)
    assert df.shape == (277, 15)

    df = rank_stations(lat, lng, match_ca_climate_zone=True)
    assert df.shape == (9, 15)


def test_rank_stations_match_climate_zones_null(lat_long_africa):
    lat, lng = lat_long_africa
    df = rank_stations(lat, lng, match_iecc_climate_zone=True)
    assert df.shape == (501, 15)

    df = rank_stations(lat, lng, match_iecc_moisture_regime=True)
    assert df.shape == (942, 15)

    df = rank_stations(lat, lng, match_ba_climate_zone=True)
    assert df.shape == (506, 15)

    df = rank_stations(lat, lng, match_ca_climate_zone=True)
    assert df.shape == (3630, 15)


def test_rank_stations_match_state(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = rank_stations(lat, lng, site_state='CA')
    assert df.shape == (3864, 15)

    df = rank_stations(lat, lng, site_state='CA', match_state=True)
    assert df.shape == (309, 15)

    df = rank_stations(lat, lng, site_state=None, match_state=True)
    assert df.shape == (73, 15)


def test_rank_stations_is_tmy3(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = rank_stations(lat, lng, is_tmy3=True)
    assert df.shape == (1019, 15)

    df = rank_stations(lat, lng, is_tmy3=False)
    assert df.shape == (2845, 15)


def test_rank_stations_is_cz2010(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = rank_stations(lat, lng, is_cz2010=True)
    assert df.shape == (86, 15)

    df = rank_stations(lat, lng, is_cz2010=False)
    assert df.shape == (3778, 15)


def test_rank_stations_minimum_quality(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = rank_stations(lat, lng, minimum_quality='low')
    assert df.shape == (3864, 15)

    df = rank_stations(lat, lng, minimum_quality='medium')
    assert df.shape == (1724, 15)

    df = rank_stations(lat, lng, minimum_quality='high')
    assert df.shape == (1619, 15)


def test_rank_stations_minimum_tmy3_class(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = rank_stations(lat, lng, minimum_tmy3_class='III')
    assert df.shape == (1019, 15)

    df = rank_stations(lat, lng, minimum_tmy3_class='II')
    assert df.shape == (857, 15)

    df = rank_stations(lat, lng, minimum_tmy3_class='I')
    assert df.shape == (222, 15)


def test_rank_stations_max_distance_meters(lat_long_fresno):
    lat, lng = lat_long_fresno

    df = rank_stations(lat, lng, max_distance_meters=200000)
    assert df.shape == (51, 15)

    df = rank_stations(lat, lng, max_distance_meters=50000)
    assert df.shape == (5, 15)


def test_rank_stations_max_difference_elevation_meters(lat_long_fresno):
    lat, lng = lat_long_fresno

    # no site_elevation
    df = rank_stations(
        lat, lng, max_difference_elevation_meters=200)
    assert df.shape == (3864, 15)

    df = rank_stations(
        lat, lng, site_elevation=0,
        max_difference_elevation_meters=200)
    assert df.shape == (2184, 15)

    df = rank_stations(
        lat, lng, site_elevation=0,
        max_difference_elevation_meters=50)
    assert df.shape == (1371, 15)

    df = rank_stations(
        lat, lng, site_elevation=1000,
        max_difference_elevation_meters=50)
    assert df.shape == (47, 15)


@pytest.fixture
def cz_candidates(lat_long_fresno):
    lat, lng = lat_long_fresno
    return rank_stations(
        lat, lng,
        match_iecc_climate_zone=True,
        match_iecc_moisture_regime=True,
        match_ba_climate_zone=True,
        match_ca_climate_zone=True,
        minimum_quality='high',
        is_tmy3=True,
        is_cz2010=True,
    )


@pytest.fixture
def naive_candidates(lat_long_fresno):
    lat, lng = lat_long_fresno
    return rank_stations(
        lat, lng,
        minimum_quality='high',
        is_tmy3=True,
        is_cz2010=True,
    ).head()


def test_combine_ranked_stations_empty():
    with pytest.raises(ValueError):
        combine_ranked_stations([])


def test_combine_ranked_stations(cz_candidates, naive_candidates):
    assert list(cz_candidates.index) == [
        '723890', '747020', '723896', '723895', '723840'
    ]
    assert list(naive_candidates.index) == [
        '723890', '747020', '723896', '724815', '723895'
    ]

    combined_candidates = combine_ranked_stations(
        [cz_candidates, naive_candidates])

    assert combined_candidates.shape == (6, 15)
    assert combined_candidates['rank'].iloc[0] == 1
    assert combined_candidates['rank'].iloc[-1] == 6
    assert list(combined_candidates.index) == [
        '723890', '747020', '723896', '723895', '723840', '724815'
    ]


def test_select_station_no_coverage_check(cz_candidates):
    station, warnings = select_station(cz_candidates)
    assert station.usaf_id == '723890'


@pytest.fixture
def monkeypatch_load_isd_hourly_temp_data(monkeypatch):
    def load_isd_hourly_temp_data(station, start, end):
        # because result datetimes should fall exactly on hours
        normalized_start = datetime(
            start.year, start.month, start.day, start.hour, tzinfo=pytz.UTC)
        normalized_end = datetime(
            end.year, end.month, end.day, end.hour, tzinfo=pytz.UTC)
        index = pd.date_range(
            normalized_start, normalized_end, freq='H', tz='UTC')

        # simulate missing data
        if station.usaf_id == '723890':
            return pd.Series(1, index=index)[:-24*50].reindex(index)
        elif station.usaf_id == '747020':
            return pd.Series(1, index=index)[:-24*30].reindex(index)
        return pd.Series(1, index=index)[:-24*10].reindex(index)

    monkeypatch.setattr(
        'eeweather.mockable.load_isd_hourly_temp_data',
        load_isd_hourly_temp_data
    )


def test_select_station_full_data(
    cz_candidates, monkeypatch_load_isd_hourly_temp_data
):
    start = datetime(2017, 1, 1, tzinfo=pytz.UTC)
    end = datetime(2018, 1, 1, tzinfo=pytz.UTC)

    # 1st misses qualification
    station, warnings = select_station(
        cz_candidates, coverage_range=(start, end),
    )
    assert station.usaf_id == '747020'

    # 1st meets qualification
    station, warnings = select_station(
        cz_candidates, coverage_range=(start, end),
        min_fraction_coverage=0.8
    )
    assert station.usaf_id == '723890'

    # none meet qualification
    station, warnings = select_station(
        cz_candidates, coverage_range=(start, end),
        min_fraction_coverage=0.99
    )
    assert station is None


@pytest.fixture
def monkeypatch_load_isd_hourly_temp_data_with_error(monkeypatch):

    def load_isd_hourly_temp_data(station, start, end):
        index = pd.date_range(start, end, freq='H', tz='UTC')
        if station.usaf_id == '723890':
            raise ISDDataNotAvailableError('723890', start.year)  # first choice not available
        elif station.usaf_id == '747020':
            return pd.Series(1, index=index)[:-24*10].reindex(index)
    monkeypatch.setattr(
        'eeweather.mockable.load_isd_hourly_temp_data',
        load_isd_hourly_temp_data
    )


def test_select_station_with_isd_data_not_available_error(
    cz_candidates, monkeypatch_load_isd_hourly_temp_data_with_error
):
    start = datetime(2017, 1, 1, tzinfo=pytz.UTC)
    end = datetime(2018, 1, 1, tzinfo=pytz.UTC)

    # 1st misses qualification because data not available
    station, warnings = select_station(
        cz_candidates, coverage_range=(start, end),
        min_fraction_coverage=0.8
    )
    assert station.usaf_id == '747020'


@pytest.fixture
def monkeypatch_load_isd_hourly_temp_data_with_empty(monkeypatch):

    def load_isd_hourly_temp_data(station, start, end):
        index = pd.date_range(start, end, freq='H', tz='UTC')
        if station.usaf_id == '723890':
            return pd.Series(1, index=index)[:0]
        elif station.usaf_id == '747020':
            return pd.Series(1, index=index)[:-24*10].reindex(index)
    monkeypatch.setattr(
        'eeweather.mockable.load_isd_hourly_temp_data',
        load_isd_hourly_temp_data
    )


def test_select_station_with_empty_tempC(
    cz_candidates, monkeypatch_load_isd_hourly_temp_data_with_empty
):
    start = datetime(2017, 1, 1, tzinfo=pytz.UTC)
    end = datetime(2018, 1, 1, tzinfo=pytz.UTC)

    # 1st misses qualification because data not available
    station, warnings = select_station(
        cz_candidates, coverage_range=(start, end),
        min_fraction_coverage=0.8
    )
    assert station.usaf_id == '747020'


def test_select_station_distance_warnings_check(lat_long_africa):
    lat, lng = lat_long_africa
    df = rank_stations(lat, lng)
    station, warnings = select_station(df)
    assert len(warnings) == 2
    assert warnings[0].qualified_name == 'eeweather.exceeds_maximum_distance'
    assert warnings[1].qualified_name == 'eeweather.exceeds_maximum_distance'
    assert warnings[0].data['max_distance_meters'] == 50000
    assert warnings[1].data['max_distance_meters'] == 200000


def test_select_station_no_station_warnings_check():
    df = pd.DataFrame()
    station, warnings = select_station(df)
    assert warnings[0].qualified_name == 'eeweather.no_weather_station_selected'
    assert warnings[0].data == {
        'rank': 1,
        'min_fraction_coverage': 0.9
    }


def test_select_station_with_second_level_dates(
    cz_candidates, monkeypatch_load_isd_hourly_temp_data
):
    # dates don't fall exactly on the hour
    start = datetime(2017, 1, 1, 2, 3, 4, tzinfo=pytz.UTC)
    end = datetime(2018, 1, 1, 12, 13, 14, tzinfo=pytz.UTC)

    station, warnings = select_station(
        cz_candidates, coverage_range=(start, end),
    )
    assert station.usaf_id == '747020'
