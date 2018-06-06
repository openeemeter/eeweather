import pandas as pd
import pytest

from eeweather import get_candidate_stations


@pytest.fixture
def lat_long_fresno():
    return 36.7378, -119.7871

@pytest.fixture
def lat_long_africa():
    return 0, 0


def test_get_candidate_stations_no_filter(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = get_candidate_stations(lat, lng)
    assert df.shape == (3895, 14)
    assert round(df.distance_meters.iloc[0]) == 3008.0
    assert round(df.distance_meters.iloc[-10]) == 9614514.0
    assert pd.isnull(df.distance_meters.iloc[-1]) is True


def test_get_candidate_stations_match_climate_zones_not_null(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = get_candidate_stations(lat, lng, match_iecc_climate_zone=True)
    assert df.shape == (747, 14)

    df = get_candidate_stations(lat, lng, match_iecc_moisture_regime=True)
    assert df.shape == (711, 14)

    df = get_candidate_stations(lat, lng, match_ba_climate_zone=True)
    assert df.shape == (281, 14)

    df = get_candidate_stations(lat, lng, match_ca_climate_zone=True)
    assert df.shape == (10, 14)


def test_get_candidate_stations_match_climate_zones_null(lat_long_africa):
    lat, lng = lat_long_africa
    df = get_candidate_stations(lat, lng, match_iecc_climate_zone=True)
    assert df.shape == (506, 14)

    df = get_candidate_stations(lat, lng, match_iecc_moisture_regime=True)
    assert df.shape == (947, 14)

    df = get_candidate_stations(lat, lng, match_ba_climate_zone=True)
    assert df.shape == (511, 14)

    df = get_candidate_stations(lat, lng, match_ca_climate_zone=True)
    assert df.shape == (3658, 14)


def test_get_candidate_stations_match_state(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = get_candidate_stations(lat, lng, site_state='CA')
    assert df.shape == (3895, 14)

    df = get_candidate_stations(lat, lng, site_state='CA', match_state=True)
    assert df.shape == (312, 14)

    df = get_candidate_stations(lat, lng, site_state=None, match_state=True)
    assert df.shape == (75, 14)


def test_get_candidate_stations_is_tmy3(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = get_candidate_stations(lat, lng, is_tmy3=True)
    assert df.shape == (1019, 14)

    df = get_candidate_stations(lat, lng, is_tmy3=False)
    assert df.shape == (2876, 14)


def test_get_candidate_stations_is_cz2010(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = get_candidate_stations(lat, lng, is_cz2010=True)
    assert df.shape == (86, 14)

    df = get_candidate_stations(lat, lng, is_cz2010=False)
    assert df.shape == (3809, 14)


def test_get_candidate_stations_minimum_quality(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = get_candidate_stations(lat, lng, minimum_quality='low')
    assert df.shape == (3895, 14)

    df = get_candidate_stations(lat, lng, minimum_quality='medium')
    assert df.shape == (1972, 14)

    df = get_candidate_stations(lat, lng, minimum_quality='high')
    assert df.shape == (1778, 14)


def test_get_candidate_stations_minimum_tmy3_class(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = get_candidate_stations(lat, lng, minimum_tmy3_class='III')
    assert df.shape == (1019, 14)

    df = get_candidate_stations(lat, lng, minimum_tmy3_class='II')
    assert df.shape == (857, 14)

    df = get_candidate_stations(lat, lng, minimum_tmy3_class='I')
    assert df.shape == (222, 14)


def test_get_candidate_stations_max_distance_meters(lat_long_fresno):
    lat, lng = lat_long_fresno

    df = get_candidate_stations(lat, lng, max_distance_meters=200000)
    assert df.shape == (54, 14)

    df = get_candidate_stations(lat, lng, max_distance_meters=50000)
    assert df.shape == (5, 14)


def test_get_candidate_stations_max_difference_elevation_meters(lat_long_fresno):
    lat, lng = lat_long_fresno

    # no site_elevation
    df = get_candidate_stations(
        lat, lng, max_difference_elevation_meters=200)
    assert df.shape == (3895, 14)

    df = get_candidate_stations(
        lat, lng, site_elevation=0,
        max_difference_elevation_meters=200)
    assert df.shape == (2208, 14)

    df = get_candidate_stations(
        lat, lng, site_elevation=0,
        max_difference_elevation_meters=50)
    assert df.shape == (1385, 14)

    df = get_candidate_stations(
        lat, lng, site_elevation=1000,
        max_difference_elevation_meters=50)
    assert df.shape == (47, 14)
