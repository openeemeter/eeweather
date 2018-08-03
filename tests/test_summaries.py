from eeweather import get_zcta_ids, get_isd_station_usaf_ids


def test_get_zcta_ids():
    zcta_ids = get_zcta_ids()
    assert len(zcta_ids) == 33144
    assert zcta_ids[0] == '00601'


def test_get_zcta_ids_by_state():
    zcta_ids = get_zcta_ids(state='CA')
    assert len(zcta_ids) == 1763
    assert zcta_ids[0] == '90001'


def test_get_isd_station_usaf_ids():
    usaf_ids = get_isd_station_usaf_ids()
    assert len(usaf_ids) == 3864
    assert usaf_ids[0] == '102540'


def test_get_isd_station_usaf_ids_by_state():
    usaf_ids = get_isd_station_usaf_ids(state='IL')
    assert len(usaf_ids) == 76
    assert usaf_ids[0] == '720137'
