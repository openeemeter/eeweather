from eeweather import get_zcta_ids


def test_get_zcta_ids():
    assert len(get_zcta_ids()) == 33144
