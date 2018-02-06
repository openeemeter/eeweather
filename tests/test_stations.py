from datetime import datetime
import pandas as pd
import pytest
import pytz

from eeweather import (
    ISDStation,
    get_isd_station_metadata,
    get_isd_filenames,
    get_gsod_filenames,
    get_isd_file_metadata,
    fetch_isd_raw_temp_data,
    fetch_isd_hourly_temp_data,
    fetch_isd_daily_temp_data,
    fetch_gsod_raw_temp_data,
    fetch_gsod_daily_temp_data,
    get_isd_hourly_temp_data_cache_key,
    get_isd_daily_temp_data_cache_key,
    get_gsod_daily_temp_data_cache_key,
    cached_isd_hourly_temp_data_is_expired,
    cached_isd_daily_temp_data_is_expired,
    cached_gsod_daily_temp_data_is_expired,
    validate_isd_hourly_temp_data_cache,
    validate_isd_daily_temp_data_cache,
    validate_gsod_daily_temp_data_cache,
    serialize_isd_hourly_temp_data,
    serialize_isd_daily_temp_data,
    serialize_gsod_daily_temp_data,
    deserialize_isd_hourly_temp_data,
    deserialize_isd_daily_temp_data,
    deserialize_gsod_daily_temp_data,
    read_isd_hourly_temp_data_from_cache,
    read_isd_daily_temp_data_from_cache,
    read_gsod_daily_temp_data_from_cache,
    write_isd_hourly_temp_data_to_cache,
    write_isd_daily_temp_data_to_cache,
    write_gsod_daily_temp_data_to_cache,
    destroy_cached_isd_hourly_temp_data,
    destroy_cached_isd_daily_temp_data,
    destroy_cached_gsod_daily_temp_data,
    load_isd_hourly_temp_data_cached_proxy,
    load_isd_daily_temp_data_cached_proxy,
    load_gsod_daily_temp_data_cached_proxy,
    load_isd_hourly_temp_data,
    load_isd_daily_temp_data,
    load_gsod_daily_temp_data,
    load_cached_isd_hourly_temp_data,
    load_cached_isd_daily_temp_data,
    load_cached_gsod_daily_temp_data,
)
from eeweather.exceptions import (
    UnrecognizedUSAFIDError,
    ISDDataNotAvailableError,
    GSODDataNotAvailableError,
)
from mocks import MockNOAAFTPConnectionProxy, MockKeyValueStoreProxy


@pytest.fixture
def monkeypatch_noaa_ftp(monkeypatch):
    monkeypatch.setattr(
        'eeweather.connections.noaa_ftp_connection_proxy',
        MockNOAAFTPConnectionProxy()
    )


@pytest.fixture
def monkeypatch_key_value_store(monkeypatch):
    key_value_store_proxy = MockKeyValueStoreProxy()
    monkeypatch.setattr(
        'eeweather.connections.key_value_store_proxy',
        key_value_store_proxy
    )

    return key_value_store_proxy.get_store()

def test_get_isd_station_metadata():
    assert get_isd_station_metadata('722874') == {
        'ba_climate_zone': 'Hot-Dry',
        'ca_climate_zone': 'CA_08',
        'elevation': '+0054.6',
        'iecc_climate_zone': '3',
        'iecc_moisture_regime': 'B',
        'latitude': '+34.024',
        'longitude': '-118.291',
        'name': 'DOWNTOWN L.A./USC CAMPUS',
        'quality': 'high',
        'recent_wban_id': '93134',
        'usaf_id': '722874',
        'wban_ids': '93134',
    }


def test_isd_station_no_load_metadata():
    station = ISDStation('722880', load_metadata=False)
    assert station.usaf_id == '722880'
    assert station.iecc_climate_zone is None
    assert station.iecc_moisture_regime is None
    assert station.ba_climate_zone is None
    assert station.ca_climate_zone is None
    assert station.elevation is None
    assert station.latitude is None
    assert station.longitude is None
    assert station.coords is None
    assert station.name is None
    assert station.quality is None
    assert station.wban_ids is None
    assert station.recent_wban_id is None
    assert station.climate_zones == {}

    assert str(station) == '722880'
    assert repr(station) == "ISDStation('722880')"


def test_isd_station_no_load_metadata_invalid():
    with pytest.raises(UnrecognizedUSAFIDError):
        station = ISDStation('FAKE', load_metadata=False)


def test_isd_station_with_load_metadata():
    station = ISDStation('722880', load_metadata=True)
    assert station.usaf_id == '722880'
    assert station.iecc_climate_zone == '3'
    assert station.iecc_moisture_regime == 'B'
    assert station.ba_climate_zone == 'Hot-Dry'
    assert station.ca_climate_zone == 'CA_09'
    assert station.elevation == 236.2
    assert station.latitude == 34.201
    assert station.longitude == -118.358
    assert station.coords == (34.201, -118.358)
    assert station.name == 'BURBANK-GLENDALE-PASA ARPT'
    assert station.quality == 'high'
    assert station.wban_ids == ['23152', '99999']
    assert station.recent_wban_id == '23152'
    assert station.climate_zones == {
        'ba_climate_zone': 'Hot-Dry',
        'ca_climate_zone': 'CA_09',
        'iecc_climate_zone': '3',
        'iecc_moisture_regime': 'B',
    }


def test_isd_station_json():
    station = ISDStation('722880', load_metadata=True)
    assert station.json() == {
        'elevation': 236.2,
        'latitude': 34.201,
        'longitude': -118.358,
        'name': 'BURBANK-GLENDALE-PASA ARPT',
        'quality': 'high',
        'recent_wban_id': '23152',
        'wban_ids': ['23152', '99999'],
        'climate_zones': {
            'ba_climate_zone': 'Hot-Dry',
            'ca_climate_zone': 'CA_09',
            'iecc_climate_zone': '3',
            'iecc_moisture_regime': 'B',
        }
    }


def test_isd_station_unrecognized_usaf_id():
    with pytest.raises(UnrecognizedUSAFIDError):
        station = ISDStation('FAKE', load_metadata=True)


def test_get_isd_filenames_bad_usaf_id():
    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        get_isd_filenames('000000', 2007)
    assert excinfo.value.value == '000000'


def test_get_isd_filenames_single_year():
    filenames = get_isd_filenames('722860', 2007)
    assert filenames == [
        '/pub/data/noaa/2007/722860-23119-2007.gz',
        '/pub/data/noaa/2007/722860-99999-2007.gz'
    ]


def test_get_isd_filenames_multiple_year():
    filenames = get_isd_filenames('722860')
    assert filenames == [
        '/pub/data/noaa/2006/722860-23119-2006.gz',
        '/pub/data/noaa/2007/722860-23119-2007.gz',
        '/pub/data/noaa/2007/722860-99999-2007.gz',
        '/pub/data/noaa/2008/722860-23119-2008.gz',
        '/pub/data/noaa/2009/722860-23119-2009.gz',
        '/pub/data/noaa/2010/722860-23119-2010.gz',
        '/pub/data/noaa/2011/722860-23119-2011.gz',
        '/pub/data/noaa/2012/722860-23119-2012.gz',
        '/pub/data/noaa/2013/722860-23119-2013.gz',
        '/pub/data/noaa/2014/722860-23119-2014.gz',
        '/pub/data/noaa/2015/722860-23119-2015.gz',
        '/pub/data/noaa/2016/722860-23119-2016.gz',
        '/pub/data/noaa/2017/722860-23119-2017.gz',
        '/pub/data/noaa/2018/722860-23119-2018.gz'
    ]


def test_get_isd_filenames_future_year():
    filenames = get_isd_filenames('722860', 2050)
    assert filenames == ['/pub/data/noaa/2050/722860-23119-2050.gz']


def test_get_isd_filenames_with_host():
    filenames = get_isd_filenames('722860', 2017, with_host=True)
    assert filenames == ['ftp://ftp.ncdc.noaa.gov/pub/data/noaa/2017/722860-23119-2017.gz']


def test_isd_station_get_isd_filenames():
    station = ISDStation('722860')
    filenames = station.get_isd_filenames()
    assert filenames == [
        '/pub/data/noaa/2006/722860-23119-2006.gz',
        '/pub/data/noaa/2007/722860-23119-2007.gz',
        '/pub/data/noaa/2007/722860-99999-2007.gz',
        '/pub/data/noaa/2008/722860-23119-2008.gz',
        '/pub/data/noaa/2009/722860-23119-2009.gz',
        '/pub/data/noaa/2010/722860-23119-2010.gz',
        '/pub/data/noaa/2011/722860-23119-2011.gz',
        '/pub/data/noaa/2012/722860-23119-2012.gz',
        '/pub/data/noaa/2013/722860-23119-2013.gz',
        '/pub/data/noaa/2014/722860-23119-2014.gz',
        '/pub/data/noaa/2015/722860-23119-2015.gz',
        '/pub/data/noaa/2016/722860-23119-2016.gz',
        '/pub/data/noaa/2017/722860-23119-2017.gz',
        '/pub/data/noaa/2018/722860-23119-2018.gz'
]


def test_isd_station_get_isd_filenames_with_year():
    station = ISDStation('722860')
    filenames = station.get_isd_filenames(2007)
    assert filenames == [
        '/pub/data/noaa/2007/722860-23119-2007.gz',
        '/pub/data/noaa/2007/722860-99999-2007.gz'
    ]

def test_isd_station_get_isd_filenames_with_host():
    station = ISDStation('722860')
    filenames = station.get_isd_filenames(2017, with_host=True)
    assert filenames == ['ftp://ftp.ncdc.noaa.gov/pub/data/noaa/2017/722860-23119-2017.gz']


def test_get_gsod_filenames_bad_usaf_id():
    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        get_gsod_filenames('000000', 2007)
    assert excinfo.value.value == '000000'


def test_get_gsod_filenames_single_year():
    filenames = get_gsod_filenames('722860', 2007)
    assert filenames == [
        '/pub/data/gsod/2007/722860-23119-2007.op.gz',
        '/pub/data/gsod/2007/722860-99999-2007.op.gz'
    ]


def test_get_gsod_filenames_multiple_year():
    filenames = get_gsod_filenames('722860')
    assert filenames == [
        '/pub/data/gsod/2006/722860-23119-2006.op.gz',
        '/pub/data/gsod/2007/722860-23119-2007.op.gz',
        '/pub/data/gsod/2007/722860-99999-2007.op.gz',
        '/pub/data/gsod/2008/722860-23119-2008.op.gz',
        '/pub/data/gsod/2009/722860-23119-2009.op.gz',
        '/pub/data/gsod/2010/722860-23119-2010.op.gz',
        '/pub/data/gsod/2011/722860-23119-2011.op.gz',
        '/pub/data/gsod/2012/722860-23119-2012.op.gz',
        '/pub/data/gsod/2013/722860-23119-2013.op.gz',
        '/pub/data/gsod/2014/722860-23119-2014.op.gz',
        '/pub/data/gsod/2015/722860-23119-2015.op.gz',
        '/pub/data/gsod/2016/722860-23119-2016.op.gz',
        '/pub/data/gsod/2017/722860-23119-2017.op.gz',
        '/pub/data/gsod/2018/722860-23119-2018.op.gz'
    ]


def test_get_gsod_filenames_future_year():
    filenames = get_gsod_filenames('722860', 2050)
    assert filenames == ['/pub/data/gsod/2050/722860-23119-2050.op.gz']


def test_get_gsod_filenames_with_host():
    filenames = get_gsod_filenames('722860', 2017, with_host=True)
    assert filenames == ['ftp://ftp.ncdc.noaa.gov/pub/data/gsod/2017/722860-23119-2017.op.gz']


def test_isd_station_get_gsod_filenames():
    station = ISDStation('722860')
    filenames = station.get_gsod_filenames()
    assert filenames == [
        '/pub/data/gsod/2006/722860-23119-2006.op.gz',
        '/pub/data/gsod/2007/722860-23119-2007.op.gz',
        '/pub/data/gsod/2007/722860-99999-2007.op.gz',
        '/pub/data/gsod/2008/722860-23119-2008.op.gz',
        '/pub/data/gsod/2009/722860-23119-2009.op.gz',
        '/pub/data/gsod/2010/722860-23119-2010.op.gz',
        '/pub/data/gsod/2011/722860-23119-2011.op.gz',
        '/pub/data/gsod/2012/722860-23119-2012.op.gz',
        '/pub/data/gsod/2013/722860-23119-2013.op.gz',
        '/pub/data/gsod/2014/722860-23119-2014.op.gz',
        '/pub/data/gsod/2015/722860-23119-2015.op.gz',
        '/pub/data/gsod/2016/722860-23119-2016.op.gz',
        '/pub/data/gsod/2017/722860-23119-2017.op.gz',
        '/pub/data/gsod/2018/722860-23119-2018.op.gz'
    ]


def test_isd_station_get_gsod_filenames_with_year():
    station = ISDStation('722860')
    filenames = station.get_gsod_filenames(2007)
    assert filenames == [
        '/pub/data/gsod/2007/722860-23119-2007.op.gz',
        '/pub/data/gsod/2007/722860-99999-2007.op.gz',
    ]


def test_isd_station_get_gsod_filenames_with_host():
    station = ISDStation('722860')
    filenames = station.get_gsod_filenames(2017, with_host=True)
    assert filenames == ['ftp://ftp.ncdc.noaa.gov/pub/data/gsod/2017/722860-23119-2017.op.gz']


def test_get_isd_file_metadata():
    assert get_isd_file_metadata('722874') == [
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2006'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2007'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2008'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2009'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2010'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2011'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2012'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2013'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2014'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2015'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2016'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2017'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2018'},
    ]

    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        get_isd_file_metadata('000000')
    assert excinfo.value.value == '000000'


def test_isd_station_get_isd_file_metadata():
    station = ISDStation('722874')
    assert station.get_isd_file_metadata() == [
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2006'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2007'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2008'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2009'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2010'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2011'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2012'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2013'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2014'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2015'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2016'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2017'},
        {'usaf_id': '722874', 'wban_id': '93134', 'year': '2018'},
    ]


# fetch raw
def test_fetch_isd_raw_temp_data(monkeypatch_noaa_ftp):
    data = fetch_isd_raw_temp_data('722874', 2007)
    assert data.sum() == 185945.40000000002
    assert data.shape == (10719,)


def test_fetch_gsod_raw_temp_data(monkeypatch_noaa_ftp):
    data = fetch_gsod_raw_temp_data('722874', 2007)
    assert data.sum() == 6509.5
    assert data.shape == (365,)


# station fetch raw
def test_isd_station_fetch_isd_raw_temp_data(monkeypatch_noaa_ftp):
    station = ISDStation('722874')
    data = station.fetch_isd_raw_temp_data(2007)
    assert data.sum() == 185945.40000000002
    assert data.shape == (10719,)


def test_isd_station_fetch_gsod_raw_temp_data(monkeypatch_noaa_ftp):
    station = ISDStation('722874')
    data = station.fetch_gsod_raw_temp_data(2007)
    assert data.sum() == 6509.5
    assert data.shape == (365,)


# fetch raw invalid station
def test_fetch_isd_raw_temp_data_invalid_station():
    with pytest.raises(UnrecognizedUSAFIDError):
        fetch_isd_raw_temp_data('INVALID', 2007)


def test_fetch_gsod_raw_temp_data_invalid_station():
    with pytest.raises(UnrecognizedUSAFIDError):
        fetch_gsod_raw_temp_data('INVALID', 2007)


# fetch raw invalid year
def test_fetch_isd_raw_temp_data_invalid_year(monkeypatch_noaa_ftp):
    with pytest.raises(ISDDataNotAvailableError):
        fetch_isd_raw_temp_data('722874', 1800)


def test_fetch_gsod_raw_temp_data_invalid_year(monkeypatch_noaa_ftp):
    with pytest.raises(GSODDataNotAvailableError):
        fetch_gsod_raw_temp_data('722874', 1800)


# fetch
def test_fetch_isd_hourly_temp_data(monkeypatch_noaa_ftp):
    data = fetch_isd_hourly_temp_data('722874', 2007)
    assert data.sum() == 156160.0355
    assert data.shape == (8760,)


def test_fetch_isd_daily_temp_data(monkeypatch_noaa_ftp):
    data = fetch_isd_daily_temp_data('722874', 2007)
    assert data.sum() == 6510.002260821784
    assert data.shape == (365,)


def test_fetch_gsod_daily_temp_data(monkeypatch_noaa_ftp):
    data = fetch_gsod_daily_temp_data('722874', 2007)
    assert data.sum() == 6509.5
    assert data.shape == (365,)


# station fetch
def test_isd_station_fetch_isd_hourly_temp_data(monkeypatch_noaa_ftp):
    station = ISDStation('722874')
    data = station.fetch_isd_hourly_temp_data(2007)
    assert data.sum() == 156160.0355
    assert data.shape == (8760,)


def test_isd_station_fetch_isd_daily_temp_data(monkeypatch_noaa_ftp):
    station = ISDStation('722874')
    data = station.fetch_isd_daily_temp_data(2007)
    assert data.sum() == 6510.002260821784
    assert data.shape == (365,)


def test_isd_station_fetch_gsod_daily_temp_data(monkeypatch_noaa_ftp):
    station = ISDStation('722874')
    data = station.fetch_gsod_daily_temp_data(2007)
    assert data.sum() == 6509.5
    assert data.shape == (365,)


# fetch invalid station
def test_fetch_isd_hourly_temp_data_invalid():
    with pytest.raises(UnrecognizedUSAFIDError):
        fetch_isd_hourly_temp_data('INVALID', 2007)


def test_fetch_isd_daily_temp_data_invalid():
    with pytest.raises(UnrecognizedUSAFIDError):
        fetch_isd_daily_temp_data('INVALID', 2007)


def test_fetch_gsod_daily_temp_data_invalid():
    with pytest.raises(UnrecognizedUSAFIDError):
        fetch_gsod_daily_temp_data('INVALID', 2007)


# get cache key
def test_get_isd_hourly_temp_data_cache_key():
    assert get_isd_hourly_temp_data_cache_key('722874', 2007) == 'isd-hourly-722874-2007'


def test_get_isd_daily_temp_data_cache_key():
    assert get_isd_daily_temp_data_cache_key('722874', 2007) == 'isd-daily-722874-2007'


def test_get_gsod_daily_temp_data_cache_key():
    assert get_gsod_daily_temp_data_cache_key('722874', 2007) == 'gsod-daily-722874-2007'


# station get cache key
def test_isd_station_get_isd_hourly_temp_data_cache_key():
    station = ISDStation('722874')
    assert station.get_isd_hourly_temp_data_cache_key(2007) == 'isd-hourly-722874-2007'


def test_isd_station_get_isd_daily_temp_data_cache_key():
    station = ISDStation('722874')
    assert station.get_isd_daily_temp_data_cache_key(2007) == 'isd-daily-722874-2007'


def test_isd_station_get_gsod_daily_temp_data_cache_key():
    station = ISDStation('722874')
    assert station.get_gsod_daily_temp_data_cache_key(2007) == 'gsod-daily-722874-2007'


# cache expired empty
def test_cached_isd_hourly_temp_data_is_expired_empty(monkeypatch_key_value_store):
    assert cached_isd_hourly_temp_data_is_expired('722874', 2007) is True


def test_cached_isd_daily_temp_data_is_expired_empty(monkeypatch_key_value_store):
    assert cached_isd_daily_temp_data_is_expired('722874', 2007) is True


def test_cached_gsod_daily_temp_data_is_expired_empty(monkeypatch_key_value_store):
    assert cached_gsod_daily_temp_data_is_expired('722874', 2007) is True


# station cache expired empty
def test_isd_station_cached_isd_hourly_temp_data_is_expired_empty(monkeypatch_key_value_store):
    station = ISDStation('722874')
    assert station.cached_isd_hourly_temp_data_is_expired(2007) is True


def test_isd_station_cached_isd_daily_temp_data_is_expired_empty(monkeypatch_key_value_store):
    station = ISDStation('722874')
    assert station.cached_isd_daily_temp_data_is_expired(2007) is True


def test_isd_station_cached_gsod_daily_temp_data_is_expired_empty(monkeypatch_key_value_store):
    station = ISDStation('722874')
    assert station.cached_gsod_daily_temp_data_is_expired(2007) is True


# cache expired false
def test_cached_isd_hourly_temp_data_is_expired_false(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_hourly_temp_data_cached_proxy('722874', 2007)
    assert cached_isd_hourly_temp_data_is_expired('722874', 2007) is False


def test_cached_isd_daily_temp_data_is_expired_false(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_daily_temp_data_cached_proxy('722874', 2007)
    assert cached_isd_daily_temp_data_is_expired('722874', 2007) is False


def test_cached_gsod_daily_temp_data_is_expired_false(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_gsod_daily_temp_data_cached_proxy('722874', 2007)
    assert cached_gsod_daily_temp_data_is_expired('722874', 2007) is False


# cache expired true
def test_cached_isd_hourly_temp_data_is_expired_true(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_hourly_temp_data_cached_proxy('722874', 2007)

    # manually expire key value item
    key = get_isd_hourly_temp_data_cache_key('722874', 2007)
    store = monkeypatch_key_value_store
    store.items.update() \
        .where(store.items.c.key == key) \
        .values(updated=pytz.UTC.localize(datetime(2007, 3, 3))) \
        .execute()

    assert cached_isd_hourly_temp_data_is_expired('722874', 2007) is True


def test_cached_isd_daily_temp_data_is_expired_true(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_daily_temp_data_cached_proxy('722874', 2007)

    # manually expire key value item
    key = get_isd_daily_temp_data_cache_key('722874', 2007)
    store = monkeypatch_key_value_store
    store.items.update() \
        .where(store.items.c.key == key) \
        .values(updated=pytz.UTC.localize(datetime(2007, 3, 3))) \
        .execute()

    assert cached_isd_daily_temp_data_is_expired('722874', 2007) is True


def test_cached_gsod_daily_temp_data_is_expired_true(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_gsod_daily_temp_data_cached_proxy('722874', 2007)

    # manually expire key value item
    key = get_gsod_daily_temp_data_cache_key('722874', 2007)
    store = monkeypatch_key_value_store
    store.items.update() \
        .where(store.items.c.key == key) \
        .values(updated=pytz.UTC.localize(datetime(2007, 3, 3))) \
        .execute()

    assert cached_gsod_daily_temp_data_is_expired('722874', 2007) is True


# validate cache empty
def test_validate_isd_hourly_temp_data_cache_empty(monkeypatch_key_value_store):
    assert validate_isd_hourly_temp_data_cache('722874', 2007) is False


def test_validate_isd_daily_temp_data_cache_empty(monkeypatch_key_value_store):
    assert validate_isd_daily_temp_data_cache('722874', 2007) is False


def test_validate_gsod_daily_temp_data_cache_empty(monkeypatch_key_value_store):
    assert validate_gsod_daily_temp_data_cache('722874', 2007) is False


# station validate cache empty
def test_isd_station_validate_isd_hourly_temp_data_cache_empty(monkeypatch_key_value_store):
    station = ISDStation('722874')
    assert station.validate_isd_hourly_temp_data_cache(2007) is False


def test_isd_station_validate_isd_daily_temp_data_cache_empty(monkeypatch_key_value_store):
    station = ISDStation('722874')
    assert station.validate_isd_daily_temp_data_cache(2007) is False


def test_isd_station_validate_gsod_daily_temp_data_cache_empty(monkeypatch_key_value_store):
    station = ISDStation('722874')
    assert station.validate_gsod_daily_temp_data_cache(2007) is False


# validate updated recently
def test_validate_isd_hourly_temp_data_cache_updated_recently(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_hourly_temp_data_cached_proxy('722874', 2007)
    assert validate_isd_hourly_temp_data_cache('722874', 2007) is True


def test_validate_isd_daily_temp_data_cache_updated_recently(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_daily_temp_data_cached_proxy('722874', 2007)
    assert validate_isd_daily_temp_data_cache('722874', 2007) is True


def test_validate_gsod_daily_temp_data_cache_updated_recently(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_gsod_daily_temp_data_cached_proxy('722874', 2007)
    assert validate_gsod_daily_temp_data_cache('722874', 2007) is True


# validate expired
def test_validate_isd_hourly_temp_data_cache_expired(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_hourly_temp_data_cached_proxy('722874', 2007)

    # manually expire key value item
    key = get_isd_hourly_temp_data_cache_key('722874', 2007)
    store = monkeypatch_key_value_store
    store.items.update() \
        .where(store.items.c.key == key) \
        .values(updated=pytz.UTC.localize(datetime(2007, 3, 3))) \
        .execute()

    assert validate_isd_hourly_temp_data_cache('722874', 2007) is False


def test_validate_isd_daily_temp_data_cache_expired(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_isd_daily_temp_data_cached_proxy('722874', 2007)

    # manually expire key value item
    key = get_isd_daily_temp_data_cache_key('722874', 2007)
    store = monkeypatch_key_value_store
    store.items.update() \
        .where(store.items.c.key == key) \
        .values(updated=pytz.UTC.localize(datetime(2007, 3, 3))) \
        .execute()

    assert validate_isd_daily_temp_data_cache('722874', 2007) is False


def test_validate_gsod_daily_temp_data_cache_expired(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    load_gsod_daily_temp_data_cached_proxy('722874', 2007)

    # manually expire key value item
    key = get_gsod_daily_temp_data_cache_key('722874', 2007)
    store = monkeypatch_key_value_store
    store.items.update() \
        .where(store.items.c.key == key) \
        .values(updated=pytz.UTC.localize(datetime(2007, 3, 3))) \
        .execute()

    assert validate_gsod_daily_temp_data_cache('722874', 2007) is False


# serialize
def test_serialize_isd_hourly_temp_data():
    ts = pd.Series([1], index=[pytz.UTC.localize(datetime(2017, 1, 1))])
    assert serialize_isd_hourly_temp_data(ts) == [['2017010100', 1]]


def test_serialize_isd_daily_temp_data():
    ts = pd.Series([1], index=[pytz.UTC.localize(datetime(2017, 1, 1))])
    assert serialize_isd_daily_temp_data(ts) == [['20170101', 1]]


def test_serialize_gsod_daily_temp_data():
    ts = pd.Series([1], index=[pytz.UTC.localize(datetime(2017, 1, 1))])
    assert serialize_gsod_daily_temp_data(ts) == [['20170101', 1]]


# station serialize
def test_isd_station_serialize_isd_hourly_temp_data():
    station = ISDStation('722874')
    ts = pd.Series([1], index=[pytz.UTC.localize(datetime(2017, 1, 1))])
    assert station.serialize_isd_hourly_temp_data(ts) == [['2017010100', 1]]


def test_isd_station_serialize_isd_daily_temp_data():
    station = ISDStation('722874')
    ts = pd.Series([1], index=[pytz.UTC.localize(datetime(2017, 1, 1))])
    assert station.serialize_isd_daily_temp_data(ts) == [['20170101', 1]]


def test_isd_station_serialize_gsod_daily_temp_data():
    station = ISDStation('722874')
    ts = pd.Series([1], index=[pytz.UTC.localize(datetime(2017, 1, 1))])
    assert station.serialize_gsod_daily_temp_data(ts) == [['20170101', 1]]


# deserialize
def test_deserialize_isd_hourly_temp_data():
    ts = deserialize_isd_hourly_temp_data([['2017010100', 1]])
    assert ts.sum() == 1
    assert ts.index.freq.name == 'H'


def test_deserialize_isd_daily_temp_data():
    ts = deserialize_isd_daily_temp_data([['20170101', 1]])
    assert ts.sum() == 1
    assert ts.index.freq.name == 'D'


def test_deserialize_gsod_daily_temp_data():
    ts = deserialize_gsod_daily_temp_data([['20170101', 1]])
    assert ts.sum() == 1
    assert ts.index.freq.name == 'D'


# station deserialize
def test_isd_station_deserialize_isd_hourly_temp_data():
    station = ISDStation('722874')
    ts = station.deserialize_isd_hourly_temp_data([['2017010100', 1]])
    assert ts.sum() == 1
    assert ts.index.freq.name == 'H'


def test_isd_station_deserialize_isd_daily_temp_data():
    station = ISDStation('722874')
    ts = station.deserialize_isd_daily_temp_data([['20170101', 1]])
    assert ts.sum() == 1
    assert ts.index.freq.name == 'D'


def test_isd_station_deserialize_gsod_daily_temp_data():
    station = ISDStation('722874')
    ts = station.deserialize_gsod_daily_temp_data([['20170101', 1]])
    assert ts.sum() == 1
    assert ts.index.freq.name == 'D'


# write read destroy
def test_write_read_destroy_isd_hourly_temp_data_to_from_cache(monkeypatch_key_value_store):
    store = monkeypatch_key_value_store
    key = get_isd_hourly_temp_data_cache_key('123456', 1990)
    assert store.key_exists(key) is False

    ts1 = pd.Series([1], index=[pytz.UTC.localize(datetime(1990, 1, 1))])
    write_isd_hourly_temp_data_to_cache('123456', 1990, ts1)
    assert store.key_exists(key) is True

    ts2 = read_isd_hourly_temp_data_from_cache('123456', 1990)
    assert store.key_exists(key) is True
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape

    destroy_cached_isd_hourly_temp_data('123456', 1990)
    assert store.key_exists(key) is False


def test_write_read_destroy_isd_daily_temp_data_to_from_cache(monkeypatch_key_value_store):
    store = monkeypatch_key_value_store
    key = get_isd_daily_temp_data_cache_key('123456', 1990)
    assert store.key_exists(key) is False

    ts1 = pd.Series([1], index=[pytz.UTC.localize(datetime(1990, 1, 1))])
    write_isd_daily_temp_data_to_cache('123456', 1990, ts1)
    assert store.key_exists(key) is True

    ts2 = read_isd_daily_temp_data_from_cache('123456', 1990)
    assert store.key_exists(key) is True
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape

    destroy_cached_isd_daily_temp_data('123456', 1990)
    assert store.key_exists(key) is False


def test_write_read_destroy_gsod_daily_temp_data_to_from_cache(monkeypatch_key_value_store):
    store = monkeypatch_key_value_store
    key = get_gsod_daily_temp_data_cache_key('123456', 1990)
    assert store.key_exists(key) is False

    ts1 = pd.Series([1], index=[pytz.UTC.localize(datetime(1990, 1, 1))])
    write_gsod_daily_temp_data_to_cache('123456', 1990, ts1)
    assert store.key_exists(key) is True

    ts2 = read_gsod_daily_temp_data_from_cache('123456', 1990)
    assert store.key_exists(key) is True
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape

    destroy_cached_gsod_daily_temp_data('123456', 1990)
    assert store.key_exists(key) is False


# station write read destroy
def test_isd_station_write_read_destroy_isd_hourly_temp_data_to_from_cache(
        monkeypatch_key_value_store):
    station = ISDStation('722874')
    store = monkeypatch_key_value_store
    key = station.get_isd_hourly_temp_data_cache_key(1990)
    assert store.key_exists(key) is False

    ts1 = pd.Series([1], index=[pytz.UTC.localize(datetime(1990, 1, 1))])
    station.write_isd_hourly_temp_data_to_cache(1990, ts1)
    assert store.key_exists(key) is True

    ts2 = station.read_isd_hourly_temp_data_from_cache(1990)
    assert store.key_exists(key) is True
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape

    station.destroy_cached_isd_hourly_temp_data(1990)
    assert store.key_exists(key) is False


def test_isd_station_write_read_destroy_isd_daily_temp_data_to_from_cache(
        monkeypatch_key_value_store):
    station = ISDStation('722874')
    store = monkeypatch_key_value_store
    key = station.get_isd_daily_temp_data_cache_key(1990)
    assert store.key_exists(key) is False

    ts1 = pd.Series([1], index=[pytz.UTC.localize(datetime(1990, 1, 1))])
    station.write_isd_daily_temp_data_to_cache(1990, ts1)
    assert store.key_exists(key) is True

    ts2 = station.read_isd_daily_temp_data_from_cache(1990)
    assert store.key_exists(key) is True
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape

    station.destroy_cached_isd_daily_temp_data(1990)
    assert store.key_exists(key) is False


def test_isd_station_write_read_destroy_gsod_daily_temp_data_to_from_cache(
        monkeypatch_key_value_store):
    station = ISDStation('722874')
    store = monkeypatch_key_value_store
    key = station.get_gsod_daily_temp_data_cache_key(1990)
    assert store.key_exists(key) is False

    ts1 = pd.Series([1], index=[pytz.UTC.localize(datetime(1990, 1, 1))])
    station.write_gsod_daily_temp_data_to_cache(1990, ts1)
    assert store.key_exists(key) is True

    ts2 = station.read_gsod_daily_temp_data_from_cache(1990)
    assert store.key_exists(key) is True
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape

    station.destroy_cached_gsod_daily_temp_data(1990)
    assert store.key_exists(key) is False


# load cached proxy
def test_load_isd_hourly_temp_data_cached_proxy(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    # doesn't yet guarantee that all code paths are taken,
    # except that coverage picks it up either here or elsewhere
    ts1 = load_isd_hourly_temp_data_cached_proxy('722874', 2007)
    ts2 = load_isd_hourly_temp_data_cached_proxy('722874', 2007)
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape


def test_load_isd_daily_temp_data_cached_proxy(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    # doesn't yet guarantee that all code paths are taken,
    # except that coverage picks it up either here or elsewhere
    ts1 = load_isd_daily_temp_data_cached_proxy('722874', 2007)
    ts2 = load_isd_daily_temp_data_cached_proxy('722874', 2007)
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape


def test_load_gsod_daily_temp_data_cached_proxy(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    # doesn't yet guarantee that all code paths are taken,
    # except that coverage picks it up either here or elsewhere
    ts1 = load_gsod_daily_temp_data_cached_proxy('722874', 2007)
    ts2 = load_gsod_daily_temp_data_cached_proxy('722874', 2007)
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape


# station load cached proxy
def test_isd_station_load_isd_hourly_temp_data_cached_proxy(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    station = ISDStation('722874')

    # doesn't yet guarantee that all code paths are taken,
    # except that coverage picks it up either here or elsewhere
    ts1 = station.load_isd_hourly_temp_data_cached_proxy(2007)
    ts2 = station.load_isd_hourly_temp_data_cached_proxy(2007)
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape


def test_isd_station_load_isd_daily_temp_data_cached_proxy(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    station = ISDStation('722874')

    # doesn't yet guarantee that all code paths are taken,
    # except that coverage picks it up either here or elsewhere
    ts1 = station.load_isd_daily_temp_data_cached_proxy(2007)
    ts2 = station.load_isd_daily_temp_data_cached_proxy(2007)
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape


def test_isd_station_load_gsod_daily_temp_data_cached_proxy(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    station = ISDStation('722874')

    # doesn't yet guarantee that all code paths are taken,
    # except that coverage picks it up either here or elsewhere
    ts1 = station.load_gsod_daily_temp_data_cached_proxy(2007)
    ts2 = station.load_gsod_daily_temp_data_cached_proxy(2007)
    assert int(ts1.sum()) == int(ts2.sum())
    assert ts1.shape == ts2.shape


# load data between dates
def test_load_isd_hourly_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    start = datetime(2006, 1, 3, tzinfo=pytz.UTC)
    end = datetime(2007, 4, 3, tzinfo=pytz.UTC)
    ts = load_isd_hourly_temp_data('722874', start, end)
    assert ts.index[0] == start
    assert pd.isnull(ts[0])
    assert ts.index[-1] == end
    assert pd.notnull(ts[-1])


def test_load_isd_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    start = datetime(2006, 1, 3, tzinfo=pytz.UTC)
    end = datetime(2007, 4, 3, tzinfo=pytz.UTC)
    ts = load_isd_daily_temp_data('722874', start, end)
    assert ts.index[0] == start
    assert pd.isnull(ts[0])
    assert ts.index[-1] == end
    assert pd.notnull(ts[-1])


def test_load_gsod_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    start = datetime(2006, 1, 3, tzinfo=pytz.UTC)
    end = datetime(2007, 4, 3, tzinfo=pytz.UTC)
    ts = load_gsod_daily_temp_data('722874', start, end)
    assert ts.index[0] == start
    assert pd.isnull(ts[0])
    assert ts.index[-1] == end
    assert pd.notnull(ts[-1])



# station load data between dates
def test_isd_station_load_isd_hourly_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    station = ISDStation('722874')
    start = datetime(2007, 3, 3, tzinfo=pytz.UTC)
    end = datetime(2007, 4, 3, tzinfo=pytz.UTC)
    ts = station.load_isd_hourly_temp_data(start, end)
    assert ts.index[0] == start
    assert ts.index[-1] == end


def test_isd_station_load_isd_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    station = ISDStation('722874')
    start = datetime(2007, 3, 3, tzinfo=pytz.UTC)
    end = datetime(2007, 4, 3, tzinfo=pytz.UTC)
    ts = station.load_isd_daily_temp_data(start, end)
    assert ts.index[0] == start
    assert ts.index[-1] == end


def test_isd_station_load_gsod_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    station = ISDStation('722874')
    start = datetime(2007, 3, 3, tzinfo=pytz.UTC)
    end = datetime(2007, 4, 3, tzinfo=pytz.UTC)
    ts = station.load_gsod_daily_temp_data(start, end)
    assert ts.index[0] == start
    assert ts.index[-1] == end


# load cached
def test_load_cached_isd_hourly_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    ts = load_cached_isd_hourly_temp_data('722874')
    assert ts is None

    # load data
    ts = load_isd_hourly_temp_data_cached_proxy('722874', 2007)
    assert int(ts.sum()) == 156160
    assert ts.shape == (8760,)

    ts = load_cached_isd_hourly_temp_data('722874')
    assert int(ts.sum()) == 156160
    assert ts.shape == (8760,)


def test_load_cached_isd_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    ts = load_cached_isd_daily_temp_data('722874')
    assert ts is None

    # load data
    ts = load_isd_daily_temp_data_cached_proxy('722874', 2007)
    assert int(ts.sum()) == 6510
    assert ts.shape == (365,)

    ts = load_cached_isd_daily_temp_data('722874')
    assert int(ts.sum()) == 6510
    assert ts.shape == (365,)


def test_load_cached_gsod_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):

    ts = load_cached_gsod_daily_temp_data('722874')
    assert ts is None

    # load data
    ts = load_gsod_daily_temp_data_cached_proxy('722874', 2007)
    assert int(ts.sum()) == 6509
    assert ts.shape == (365,)

    ts = load_cached_gsod_daily_temp_data('722874')
    assert int(ts.sum()) == 6509
    assert ts.shape == (365,)


# station load cached
def test_isd_station_load_cached_isd_hourly_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    station = ISDStation('722874')

    ts = station.load_cached_isd_hourly_temp_data()
    assert ts is None

    # load data
    ts = station.load_isd_hourly_temp_data_cached_proxy(2007)
    assert int(ts.sum()) == 156160
    assert ts.shape == (8760,)

    ts = station.load_cached_isd_hourly_temp_data()
    assert int(ts.sum()) == 156160
    assert ts.shape == (8760,)


def test_isd_station_load_cached_isd_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    station = ISDStation('722874')

    ts = station.load_cached_isd_daily_temp_data()
    assert ts is None

    # load data
    ts = station.load_isd_daily_temp_data_cached_proxy(2007)
    assert int(ts.sum()) == 6510
    assert ts.shape == (365,)

    ts = station.load_cached_isd_daily_temp_data()
    assert int(ts.sum()) == 6510
    assert ts.shape == (365,)


def test_isd_station_load_cached_gsod_daily_temp_data(
        monkeypatch_noaa_ftp, monkeypatch_key_value_store):
    station = ISDStation('722874')

    ts = station.load_cached_gsod_daily_temp_data()
    assert ts is None

    # load data
    ts = station.load_gsod_daily_temp_data_cached_proxy(2007)
    assert int(ts.sum()) == 6509
    assert ts.shape == (365,)

    ts = station.load_cached_gsod_daily_temp_data()
    assert int(ts.sum()) == 6509
    assert ts.shape == (365,)
