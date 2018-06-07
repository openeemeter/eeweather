import pandas as pd
import pytest

from eeweather import (
    ranked_candidate_stations,
    combine_ranked_candidates,
    ranked_mappings,
)


@pytest.fixture
def lat_long_fresno():
    return 36.7378, -119.7871

@pytest.fixture
def lat_long_africa():
    return 0, 0


def test_ranked_candidate_stations_no_filter(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = ranked_candidate_stations(lat, lng)
    assert df.shape == (3895, 15)
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


def test_ranked_candidate_stations_match_climate_zones_not_null(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = ranked_candidate_stations(lat, lng, match_iecc_climate_zone=True)
    assert df.shape == (747, 15)

    df = ranked_candidate_stations(lat, lng, match_iecc_moisture_regime=True)
    assert df.shape == (711, 15)

    df = ranked_candidate_stations(lat, lng, match_ba_climate_zone=True)
    assert df.shape == (281, 15)

    df = ranked_candidate_stations(lat, lng, match_ca_climate_zone=True)
    assert df.shape == (10, 15)


def test_ranked_candidate_stations_match_climate_zones_null(lat_long_africa):
    lat, lng = lat_long_africa
    df = ranked_candidate_stations(lat, lng, match_iecc_climate_zone=True)
    assert df.shape == (506, 15)

    df = ranked_candidate_stations(lat, lng, match_iecc_moisture_regime=True)
    assert df.shape == (947, 15)

    df = ranked_candidate_stations(lat, lng, match_ba_climate_zone=True)
    assert df.shape == (511, 15)

    df = ranked_candidate_stations(lat, lng, match_ca_climate_zone=True)
    assert df.shape == (3658, 15)


def test_ranked_candidate_stations_match_state(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = ranked_candidate_stations(lat, lng, site_state='CA')
    assert df.shape == (3895, 15)

    df = ranked_candidate_stations(lat, lng, site_state='CA', match_state=True)
    assert df.shape == (312, 15)

    df = ranked_candidate_stations(lat, lng, site_state=None, match_state=True)
    assert df.shape == (75, 15)


def test_ranked_candidate_stations_is_tmy3(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = ranked_candidate_stations(lat, lng, is_tmy3=True)
    assert df.shape == (1019, 15)

    df = ranked_candidate_stations(lat, lng, is_tmy3=False)
    assert df.shape == (2876, 15)


def test_ranked_candidate_stations_is_cz2010(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = ranked_candidate_stations(lat, lng, is_cz2010=True)
    assert df.shape == (86, 15)

    df = ranked_candidate_stations(lat, lng, is_cz2010=False)
    assert df.shape == (3809, 15)


def test_ranked_candidate_stations_minimum_quality(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = ranked_candidate_stations(lat, lng, minimum_quality='low')
    assert df.shape == (3895, 15)

    df = ranked_candidate_stations(lat, lng, minimum_quality='medium')
    assert df.shape == (1972, 15)

    df = ranked_candidate_stations(lat, lng, minimum_quality='high')
    assert df.shape == (1778, 15)


def test_ranked_candidate_stations_minimum_tmy3_class(lat_long_fresno):
    lat, lng = lat_long_fresno
    df = ranked_candidate_stations(lat, lng, minimum_tmy3_class='III')
    assert df.shape == (1019, 15)

    df = ranked_candidate_stations(lat, lng, minimum_tmy3_class='II')
    assert df.shape == (857, 15)

    df = ranked_candidate_stations(lat, lng, minimum_tmy3_class='I')
    assert df.shape == (222, 15)


def test_ranked_candidate_stations_max_distance_meters(lat_long_fresno):
    lat, lng = lat_long_fresno

    df = ranked_candidate_stations(lat, lng, max_distance_meters=200000)
    assert df.shape == (54, 15)

    df = ranked_candidate_stations(lat, lng, max_distance_meters=50000)
    assert df.shape == (5, 15)


def test_ranked_candidate_stations_max_difference_elevation_meters(lat_long_fresno):
    lat, lng = lat_long_fresno

    # no site_elevation
    df = ranked_candidate_stations(
        lat, lng, max_difference_elevation_meters=200)
    assert df.shape == (3895, 15)

    df = ranked_candidate_stations(
        lat, lng, site_elevation=0,
        max_difference_elevation_meters=200)
    assert df.shape == (2208, 15)

    df = ranked_candidate_stations(
        lat, lng, site_elevation=0,
        max_difference_elevation_meters=50)
    assert df.shape == (1385, 15)

    df = ranked_candidate_stations(
        lat, lng, site_elevation=1000,
        max_difference_elevation_meters=50)
    assert df.shape == (47, 15)


@pytest.fixture
def cz_candidates(lat_long_fresno):
    lat, lng = lat_long_fresno
    return ranked_candidate_stations(
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
    return ranked_candidate_stations(
        lat, lng,
        minimum_quality='high',
        is_tmy3=True,
        is_cz2010=True,
    ).head()


def test_combined_ranked_candidates_empty():
    with pytest.raises(ValueError):
        combine_ranked_candidates([])


def test_combined_ranked_candidates(cz_candidates, naive_candidates):
    assert list(cz_candidates.index) == [
        '723890', '747020', '723896', '723895', '723840'
    ]
    assert list(naive_candidates.index) == [
        '723890', '747020', '723896', '724815', '723895'
    ]

    combined_candidates = combine_ranked_candidates(
        [cz_candidates, naive_candidates])

    assert combined_candidates.shape == (6, 15)
    assert combined_candidates['rank'].iloc[0] == 1
    assert combined_candidates['rank'].iloc[-1] == 6
    assert list(combined_candidates.index) == [
        '723890', '747020', '723896', '723895', '723840', '724815'
    ]


def test_ranked_mappings(lat_long_fresno, cz_candidates):
    lat, lng = lat_long_fresno
    mapping_results = ranked_mappings(lat, lng, cz_candidates)
    assert mapping_results[0].isd_station.usaf_id == '723890'
