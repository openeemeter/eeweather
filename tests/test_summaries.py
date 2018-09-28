from eeweather import get_zcta_ids, get_isd_station_usaf_ids


def test_get_zcta_ids(snapshot):
    zcta_ids = get_zcta_ids()
    snapshot.assert_match(len(zcta_ids), "n_zcta_ids")
    assert zcta_ids[0] == "00601"


def test_get_zcta_ids_by_state(snapshot):
    zcta_ids = get_zcta_ids(state="CA")
    snapshot.assert_match(len(zcta_ids), "n_zcta_ids")
    assert zcta_ids[0] == "90001"


def test_get_isd_station_usaf_ids(snapshot):
    usaf_ids = get_isd_station_usaf_ids()
    snapshot.assert_match(len(usaf_ids), "n_usaf_ids")
    assert usaf_ids[0] == "102540"


def test_get_isd_station_usaf_ids_by_state(snapshot):
    usaf_ids = get_isd_station_usaf_ids(state="IL")
    snapshot.assert_match(len(usaf_ids), "n_usaf_ids")
    assert usaf_ids[0] == "720137"
