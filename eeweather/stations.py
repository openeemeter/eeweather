from datetime import datetime, timedelta
import gzip
import json

import pandas as pd
import pytz

# this import allows monkeypatching noaa_ftp_connection_proxy in tests because
# the fully qualified package path name is preserved
import eeweather.connections

from eeweather.connections import (
    metadata_db_connection_proxy,
)

from .exceptions import (
    UnrecognizedUSAFIDError,
    ISDDataNotAvailableError,
    GSODDataNotAvailableError,
)
from .validation import valid_usaf_id_or_raise

DATA_EXPIRATION_DAYS = 1

__all__ = (
    'ISDStation',
    'get_isd_filenames',
    'get_gsod_filenames',
    'get_isd_station_metadata',
    'get_isd_file_metadata',

    'get_isd_raw_temp_data',
    'get_isd_hourly_temp_data',
    'get_isd_daily_temp_data',

    'get_gsod_raw_temp_data',
    'get_gsod_daily_temp_data',

    'get_isd_hourly_temp_data_cache_key',
    'get_isd_daily_temp_data_cache_key',
    'get_gsod_daily_temp_data_cache_key',

    'cached_isd_hourly_temp_data_is_expired',
    'cached_isd_daily_temp_data_is_expired',
    'cached_gsod_daily_temp_data_is_expired',

    'validate_isd_hourly_temp_data_cache',
    'validate_isd_daily_temp_data_cache',
    'validate_gsod_daily_temp_data_cache',

    'serialize_isd_hourly_temp_data',
    'serialize_isd_daily_temp_data',
    'serialize_gsod_daily_temp_data',

    'deserialize_isd_hourly_temp_data',
    'deserialize_isd_daily_temp_data',
    'deserialize_gsod_daily_temp_data',

    'read_isd_hourly_temp_data_from_cache',
    'read_isd_daily_temp_data_from_cache',
    'read_gsod_daily_temp_data_from_cache',

    'write_isd_hourly_temp_data_to_cache',
    'write_isd_daily_temp_data_to_cache',
    'write_gsod_daily_temp_data_to_cache',

    'destroy_cached_isd_hourly_temp_data',
    'destroy_cached_isd_daily_temp_data',
    'destroy_cached_gsod_daily_temp_data',

    'load_isd_hourly_temp_data_cached_proxy',
    'load_isd_daily_temp_data_cached_proxy',
    'load_gsod_daily_temp_data_cached_proxy',

    'load_isd_hourly_temp_data',
    'load_isd_daily_temp_data',
    'load_gsod_daily_temp_data',

    'load_cached_isd_hourly_temp_data',
    'load_cached_isd_daily_temp_data',
    'load_cached_gsod_daily_temp_data',
)


def get_isd_filenames(usaf_id, target_year=None, filename_format=None, with_host=False):
    valid_usaf_id_or_raise(usaf_id)
    if filename_format is None:
        filename_format = '/pub/data/noaa/{year}/{usaf_id}-{wban_id}-{year}.gz'
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()

    if target_year is None:
        # all years
        cur.execute('''
          select
            wban_id
            , year
          from
            isd_file_metadata
          where
            usaf_id = ?
          order by
            year
        ''', (usaf_id,))
    else:
        # single year
        cur.execute('''
          select
            wban_id
            , year
          from
            isd_file_metadata
          where
            usaf_id = ? and year = ?
        ''', (usaf_id, target_year))

    filenames = []
    for (wban_id, year) in cur.fetchall():
        filenames.append(filename_format.format(
            usaf_id=usaf_id,
            wban_id=wban_id,
            year=year,
        ))

    if len(filenames) == 0 and target_year is not None:
        # fallback - use most recent wban id
        cur.execute('''
          select
            recent_wban_id
          from
            isd_station_metadata
          where
            usaf_id = ?
        ''', (usaf_id,))
        row = cur.fetchone()
        if row is not None:
            filenames.append(filename_format.format(
                usaf_id=usaf_id,
                wban_id=row[0],
                year=target_year,
            ))

    if with_host:
        filenames = ['ftp://ftp.ncdc.noaa.gov{}'.format(f) for f in filenames]

    return filenames


def get_gsod_filenames(usaf_id, year=None, with_host=False):
    filename_format = '/pub/data/gsod/{year}/{usaf_id}-{wban_id}-{year}.op.gz'
    return get_isd_filenames(
        usaf_id, year, filename_format=filename_format, with_host=with_host)


def get_isd_station_metadata(usaf_id):
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()
    cur.execute('''
      select
        *
      from
        isd_station_metadata
      where
        usaf_id = ?
    ''', (usaf_id,))
    row = cur.fetchone()
    if row is None:
        raise UnrecognizedUSAFIDError(usaf_id)
    return {
        col[0]: row[i]
        for i, col in enumerate(cur.description)
    }


def get_isd_file_metadata(usaf_id):
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()
    cur.execute('''
      select
        *
      from
        isd_file_metadata
      where
        usaf_id = ?
    ''', (usaf_id,))
    rows = cur.fetchall()
    if rows == []:
        raise UnrecognizedUSAFIDError(usaf_id)
    return [
        {
            col[0]: row[i]
            for i, col in enumerate(cur.description)
        }
        for row in rows
    ]


def fetch_isd_raw_temp_data(usaf_id, year):
    # possible locations of this data, errors if station is not recognized
    filenames = get_isd_filenames(usaf_id, year)

    data = []
    for filename in filenames:

        # using fully-qualified name facilitates monkeypatching
        gzipped = eeweather.connections.noaa_ftp_connection_proxy \
                .read_file_as_bytes(filename)

        if gzipped is not None:
            f = gzip.GzipFile(fileobj=gzipped)
            for line in f.readlines():
                if line[87:92].decode('utf-8') == '+9999':
                    tempC = float('nan')
                else:
                    tempC = float(line[87:92]) / 10.
                if pd.isnull(tempC):
                    continue
                date_str = line[15:27].decode('utf-8')
                dt = pytz.UTC.localize(datetime.strptime(date_str, '%Y%m%d%H%M'))
                data.append([dt, tempC])
            gzipped.close()

    if data == []:
        raise ISDDataNotAvailableError(usaf_id, year)

    dates, temps = zip(*sorted(data))
    ts = pd.Series(temps, index=dates)
    ts = ts.groupby(ts.index).mean()
    return ts


def fetch_isd_hourly_temp_data(usaf_id, year):
    # TODO(philngo): allow swappable resample method
    # TODO(philngo): record data sufficiency warnings
    ts = fetch_isd_raw_temp_data(usaf_id, year)
    return ts.resample('Min').mean() \
           .interpolate(method='linear', limit=60, limit_direction='both') \
           .resample('H').mean()


def fetch_isd_daily_temp_data(usaf_id, year):
    # TODO(philngo): allow swappable resample method
    # TODO(philngo): record data sufficiency warnings
    ts = fetch_isd_raw_temp_data(usaf_id, year)
    return ts.resample('Min').mean() \
           .interpolate(method='linear', limit=60, limit_direction='both') \
           .resample('D').mean()


def fetch_gsod_raw_temp_data(usaf_id, year):

    filenames = get_gsod_filenames(usaf_id, year)

    data = []
    for filename in filenames:

        # using fully-qualified name facilitates monkeypatching
        gzipped = eeweather.connections.noaa_ftp_connection_proxy \
                .read_file_as_bytes(filename)

        if gzipped is not None:
            f = gzip.GzipFile(fileobj=gzipped)
            lines = f.readlines()
            for line in lines[1:]:
                columns = line.split()
                date_str = columns[2].decode('utf-8')
                tempF = float(columns[3])
                tempC = (5. / 9.) * (tempF - 32.)
                dt = pytz.UTC.localize(datetime.strptime(date_str, "%Y%m%d"))
                data.append([dt, tempC])
            gzipped.close()

    if data == []:
        raise GSODDataNotAvailableError(usaf_id, year)

    dates, temps = zip(*sorted(data))
    ts = pd.Series(temps, index=dates)
    ts = ts.groupby(ts.index).mean()
    return ts


def fetch_gsod_daily_temp_data(usaf_id, year):
    ts = fetch_gsod_raw_temp_data(usaf_id, year)
    return ts.resample('D').mean()


def get_isd_hourly_temp_data_cache_key(usaf_id, year):
    return 'isd-hourly-{}-{}'.format(usaf_id, year)


def get_isd_daily_temp_data_cache_key(usaf_id, year):
    return 'isd-daily-{}-{}'.format(usaf_id, year)


def get_gsod_daily_temp_data_cache_key(usaf_id, year):
    return 'gsod-daily-{}-{}'.format(usaf_id, year)


def _expired(last_updated, year):
    if last_updated is None:
        return True
    expiration_limit = pytz.UTC.localize(
        datetime.now() - timedelta(days=DATA_EXPIRATION_DAYS))
    updated_during_data_year = (year == last_updated.year)
    return expiration_limit > last_updated and updated_during_data_year


def cached_isd_hourly_temp_data_is_expired(usaf_id, year):
    key = get_isd_hourly_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    last_updated = store.key_updated(key)
    return _expired(last_updated, year)


def cached_isd_daily_temp_data_is_expired(usaf_id, year):
    key = get_isd_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    last_updated = store.key_updated(key)
    return _expired(last_updated, year)


def cached_gsod_daily_temp_data_is_expired(usaf_id, year):
    key = get_gsod_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    last_updated = store.key_updated(key)
    return _expired(last_updated, year)


def validate_isd_hourly_temp_data_cache(usaf_id, year):
    key = get_isd_hourly_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()

    # fail if no key
    if not store.key_exists(key):
        return False

    # check for expired data, fail if so
    if cached_isd_hourly_temp_data_is_expired(usaf_id, year):
        store.clear(key)
        return False

    return True


def validate_isd_daily_temp_data_cache(usaf_id, year):
    key = get_isd_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()

    # fail if no key
    if not store.key_exists(key):
        return False

    # check for expired data, fail if so
    if cached_isd_daily_temp_data_is_expired(usaf_id, year):
        store.clear(key)
        return False

    return True


def validate_gsod_daily_temp_data_cache(usaf_id, year):
    key = get_gsod_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()

    # fail if no key
    if not store.key_exists(key):
        return False

    # check for expired data, fail if so
    if cached_gsod_daily_temp_data_is_expired(usaf_id, year):
        store.clear(key)
        return False

    return True


def _serialize(ts, freq):
    if freq == 'H':
        dt_format = '%Y%m%d%H'
    elif freq == 'D':
        dt_format = '%Y%m%d'
    else:  # pragma: no cover
        raise ValueError('Unrecognized frequency "{}"'.format(freq))

    return [
        [d.strftime(dt_format), round(temp, 4) if pd.notnull(temp) else None]
        for d, temp in ts.iteritems()
    ]


def serialize_isd_hourly_temp_data(ts):
    return _serialize(ts, 'H')


def serialize_isd_daily_temp_data(ts):
    return _serialize(ts, 'D')


def serialize_gsod_daily_temp_data(ts):
    return _serialize(ts, 'D')


def _deserialize(data, freq):
    if freq == 'H':
        dt_format = '%Y%m%d%H'
    elif freq == 'D':
        dt_format = '%Y%m%d'
    else:  # pragma: no cover
        raise ValueError('Unrecognized frequency "{}"'.format(freq))

    dates, values = zip(*data)
    index = pd.to_datetime(dates, format=dt_format, utc=True)
    return pd.Series(values, index=index, dtype=float) \
        .sort_index().resample(freq).mean()


def deserialize_isd_hourly_temp_data(data):
    return _deserialize(data, 'H')


def deserialize_isd_daily_temp_data(data):
    return _deserialize(data, 'D')


def deserialize_gsod_daily_temp_data(data):
    return _deserialize(data, 'D')


def read_isd_hourly_temp_data_from_cache(usaf_id, year):
    key = get_isd_hourly_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return deserialize_isd_hourly_temp_data(store.retrieve_json(key))


def read_isd_daily_temp_data_from_cache(usaf_id, year):
    key = get_isd_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return deserialize_isd_daily_temp_data(store.retrieve_json(key))


def read_gsod_daily_temp_data_from_cache(usaf_id, year):
    key = get_gsod_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return deserialize_gsod_daily_temp_data(store.retrieve_json(key))


def write_isd_hourly_temp_data_to_cache(usaf_id, year, ts):
    key = get_isd_hourly_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return store.save_json(key, serialize_isd_hourly_temp_data(ts))


def write_isd_daily_temp_data_to_cache(usaf_id, year, ts):
    key = get_isd_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return store.save_json(key, serialize_isd_daily_temp_data(ts))


def write_gsod_daily_temp_data_to_cache(usaf_id, year, ts):
    key = get_gsod_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return store.save_json(key, serialize_gsod_daily_temp_data(ts))


def destroy_cached_isd_hourly_temp_data(usaf_id, year):
    key = get_isd_hourly_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return store.clear(key)


def destroy_cached_isd_daily_temp_data(usaf_id, year):
    key = get_isd_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return store.clear(key)


def destroy_cached_gsod_daily_temp_data(usaf_id, year):
    key = get_gsod_daily_temp_data_cache_key(usaf_id, year)
    store = eeweather.connections.key_value_store_proxy.get_store()
    return store.clear(key)


def load_isd_hourly_temp_data_cached_proxy(
        usaf_id, year, read_from_cache=True, write_to_cache=True):
    # take from cache?
    data_ok = validate_isd_hourly_temp_data_cache(usaf_id, year)

    if not read_from_cache or not data_ok:
        # need to actually fetch the data
        ts = fetch_isd_hourly_temp_data(usaf_id, year)
        if write_to_cache:
            write_isd_hourly_temp_data_to_cache(usaf_id, year, ts)
    else:
        # read_from_cache=True and data_ok=True
        ts = read_isd_hourly_temp_data_from_cache(usaf_id, year)
    return ts


def load_isd_daily_temp_data_cached_proxy(
        usaf_id, year, read_from_cache=True, write_to_cache=True):
    # take from cache?
    data_ok = validate_isd_daily_temp_data_cache(usaf_id, year)

    if not read_from_cache or not data_ok:
        # need to actually fetch the data
        ts = fetch_isd_daily_temp_data(usaf_id, year)
        if write_to_cache:
            write_isd_daily_temp_data_to_cache(usaf_id, year, ts)
    else:
        # read_from_cache=True and data_ok=True
        ts = read_isd_daily_temp_data_from_cache(usaf_id, year)
    return ts


def load_gsod_daily_temp_data_cached_proxy(
        usaf_id, year, read_from_cache=True, write_to_cache=True):
    # take from cache?
    data_ok = validate_gsod_daily_temp_data_cache(usaf_id, year)

    if not read_from_cache or not data_ok:
        # need to actually fetch the data
        ts = fetch_gsod_daily_temp_data(usaf_id, year)
        if write_to_cache:
            write_gsod_daily_temp_data_to_cache(usaf_id, year, ts)
    else:
        # read_from_cache=True and data_ok=True
        ts = read_gsod_daily_temp_data_from_cache(usaf_id, year)
    return ts


def load_isd_hourly_temp_data(usaf_id, start, end, read_from_cache=True, write_to_cache=True):
    data = [
        load_isd_hourly_temp_data_cached_proxy(
            usaf_id, year, read_from_cache=read_from_cache,
            write_to_cache=write_to_cache
        )
        for year in range(start.year, end.year + 1)
    ]

    # get raw data
    ts = pd.concat(data).resample('H').mean()

    # whittle down
    ts = ts[start:end]

    # fill in gaps
    ts = ts.reindex(pd.date_range(start, end, freq='H'))
    return ts


def load_isd_daily_temp_data(usaf_id, start, end, read_from_cache=True, write_to_cache=True):
    data = [
        load_isd_daily_temp_data_cached_proxy(
            usaf_id, year, read_from_cache=read_from_cache,
            write_to_cache=write_to_cache
        )
        for year in range(start.year, end.year + 1)
    ]

    # get raw data
    ts = pd.concat(data).resample('D').mean()

    # whittle down
    ts = ts[start:end]

    # fill in gaps
    ts = ts.reindex(pd.date_range(start, end, freq='D'))
    return ts


def load_gsod_daily_temp_data(usaf_id, start, end, read_from_cache=True, write_to_cache=True):
    data = [
        load_gsod_daily_temp_data_cached_proxy(
            usaf_id, year, read_from_cache=read_from_cache,
            write_to_cache=write_to_cache
        )
        for year in range(start.year, end.year + 1)
    ]
    # get raw data
    ts = pd.concat(data).resample('D').mean()

    # whittle down
    ts = ts[start:end]

    # fill in gaps
    ts = ts.reindex(pd.date_range(start, end, freq='D'))
    return ts


def load_cached_isd_hourly_temp_data(usaf_id):
    store = eeweather.connections.key_value_store_proxy.get_store()

    data = [
        read_isd_hourly_temp_data_from_cache(usaf_id, year)
        for year in range(2000, datetime.now().year + 1)
        if store.key_exists(get_isd_hourly_temp_data_cache_key(usaf_id, year))
    ]
    if data == []:
        return None
    return pd.concat(data).resample('H').mean()


def load_cached_isd_daily_temp_data(usaf_id):
    store = eeweather.connections.key_value_store_proxy.get_store()

    data = [
        read_isd_daily_temp_data_from_cache(usaf_id, year)
        for year in range(2000, datetime.now().year + 1)
        if store.key_exists(get_isd_daily_temp_data_cache_key(usaf_id, year))
    ]
    if data == []:
        return None
    return pd.concat(data).resample('D').mean()


def load_cached_gsod_daily_temp_data(usaf_id):
    store = eeweather.connections.key_value_store_proxy.get_store()

    data = [
        read_gsod_daily_temp_data_from_cache(usaf_id, year)
        for year in range(2000, datetime.now().year + 1)
        if store.key_exists(get_gsod_daily_temp_data_cache_key(usaf_id, year))
    ]
    if data == []:
        return None
    return pd.concat(data).resample('D').mean()


class ISDStation(object):
    ''' A representation of an Integrated Surface Database weather station.

    Contains data about a particular ISD station, as well as methods to pull data for this station.

    Parameters
    ----------
    usaf_id : str
        ISD station USAF ID
    load_metatdata : bool, optional
        Whether or not to auto-load metadata for this station

    Attributes
    ----------
    usaf_id : str
        ISD station USAF ID
    iecc_climate_zone : str
        IECC Climate Zone
    iecc_moisture_regime : str
        IECC Moisture Regime
    ba_climate_zone : str
        Building America Climate Zone
    ca_climate_zone : str
        California Building Climate Zone
    elevation : float
        elevation of station
    latitude : float
        latitude of station
    longitude : float
        longitude of station
    coords : tuple of (float, float)
        lat/long coordinates of station
    name : str
        name of the station
    quality : str
        "high", "medium", "low"
    wban_ids : list of str
        list of WBAN IDs, or "99999" which have been used to identify the station.
    recent_wban_id = None
        WBAN ID most recently used to identify the station.
    climate_zones = {}
        dict of all climate zones.
    '''

    def __init__(self, usaf_id, load_metadata=True):
        self.usaf_id = usaf_id

        if load_metadata:
            self._load_metadata()
        else:
            valid_usaf_id_or_raise(usaf_id)
            self.iecc_climate_zone = None
            self.iecc_moisture_regime = None
            self.ba_climate_zone = None
            self.ca_climate_zone = None
            self.elevation = None
            self.latitude = None
            self.longitude = None
            self.coords = None
            self.name = None
            self.quality = None
            self.wban_ids = None
            self.recent_wban_id = None
            self.climate_zones = {}

    def __str__(self):
        return self.usaf_id

    def __repr__(self):
        return "ISDStation('{}')".format(self.usaf_id)

    def _load_metadata(self):
        metadata = get_isd_station_metadata(self.usaf_id)

        self.iecc_climate_zone = metadata['iecc_climate_zone']
        self.iecc_moisture_regime = metadata['iecc_moisture_regime']
        self.ba_climate_zone = metadata['ba_climate_zone']
        self.ca_climate_zone = metadata['ca_climate_zone']
        self.elevation = float(metadata['elevation'])  # meters
        self.latitude = float(metadata['latitude'])
        self.longitude = float(metadata['longitude'])
        self.coords = (self.latitude, self.longitude)
        self.name = metadata['name']
        self.quality = metadata['quality']
        self.wban_ids = metadata['wban_ids'].split(',')
        self.recent_wban_id = metadata['recent_wban_id']
        self.climate_zones = {
            'iecc_climate_zone': metadata['iecc_climate_zone'],
            'iecc_moisture_regime': metadata['iecc_moisture_regime'],
            'ba_climate_zone': metadata['ba_climate_zone'],
            'ca_climate_zone': metadata['ca_climate_zone'],
        }

    def json(self):
        ''' Return a JSON-serializeable object containing station metadata.'''
        return {
            'elevation': self.elevation,
            'latitude': self.latitude,
            'longitude': self.longitude,
            'name': self.name,
            'quality': self.quality,
            'wban_ids': self.wban_ids,
            'recent_wban_id': self.recent_wban_id,
            'climate_zones': {
                'iecc_climate_zone': self.iecc_climate_zone,
                'iecc_moisture_regime': self.iecc_moisture_regime,
                'ba_climate_zone': self.ba_climate_zone,
                'ca_climate_zone': self.ca_climate_zone,
            }
        }

    def get_isd_filenames(self, year=None, with_host=False):
        ''' Get filenames of raw ISD station data. '''
        return get_isd_filenames(self.usaf_id, year, with_host=with_host)

    def get_gsod_filenames(self, year=None, with_host=False):
        ''' Get filenames of raw GSOD station data. '''
        return get_gsod_filenames(self.usaf_id, year, with_host=with_host)

    def get_isd_file_metadata(self):
        ''' Get raw file metadata for the station. '''
        return get_isd_file_metadata(self.usaf_id)

    # fetch raw data
    def fetch_isd_raw_temp_data(self, year):
        ''' Pull raw ISD data for the given year directly from FTP. '''
        return fetch_isd_raw_temp_data(self.usaf_id, year)

    def fetch_gsod_raw_temp_data(self, year):
        ''' Pull raw GSOD data for the given year directly from FTP. '''
        return fetch_gsod_raw_temp_data(self.usaf_id, year)

    # fetch raw data then frequency-normalize
    def fetch_isd_hourly_temp_data(self, year):
        ''' Pull raw ISD temperature data for the given year directly from FTP and resample to hourly time series. '''
        return fetch_isd_hourly_temp_data(self.usaf_id, year)

    def fetch_isd_daily_temp_data(self, year):
        ''' Pull raw ISD temperature data for the given year directly from FTP and resample to daily time series. '''
        return fetch_isd_daily_temp_data(self.usaf_id, year)

    def fetch_gsod_daily_temp_data(self, year):
        ''' Pull raw GSOD temperature data for the given year directly from FTP and resample to daily time series. '''
        return fetch_gsod_daily_temp_data(self.usaf_id, year)

    # get key-value store key
    def get_isd_hourly_temp_data_cache_key(self, year):
        ''' Get key used to cache resampled hourly ISD temperature data for the given year. '''
        return get_isd_hourly_temp_data_cache_key(self.usaf_id, year)

    def get_isd_daily_temp_data_cache_key(self, year):
        ''' Get key used to cache resampled daily ISD temperature data for the given year. '''
        return get_isd_daily_temp_data_cache_key(self.usaf_id, year)

    def get_gsod_daily_temp_data_cache_key(self, year):
        ''' Get key used to cache resampled daily GSOD temperature data for the given year. '''
        return get_gsod_daily_temp_data_cache_key(self.usaf_id, year)

    # is cached data expired? boolean. true if expired or not in cache
    def cached_isd_hourly_temp_data_is_expired(self, year):
        ''' Return True if cache of resampled hourly ISD temperature data has expired or does not exist for the given year. '''
        return cached_isd_hourly_temp_data_is_expired(self.usaf_id, year)

    def cached_isd_daily_temp_data_is_expired(self, year):
        ''' Return True if cache of resampled daily ISD temperature data has expired or does not exist for the given year. '''
        return cached_isd_daily_temp_data_is_expired(self.usaf_id, year)

    def cached_gsod_daily_temp_data_is_expired(self, year):
        ''' Return True if cache of resampled daily GSOD temperature data has expired or does not exist for the given year. '''
        return cached_gsod_daily_temp_data_is_expired(self.usaf_id, year)

    # delete data in the cache if it's expired
    def validate_isd_hourly_temp_data_cache(self, year):
        ''' Delete cached resampled hourly ISD temperature data if it has expired for the given year. '''
        return validate_isd_hourly_temp_data_cache(self.usaf_id, year)

    def validate_isd_daily_temp_data_cache(self, year):
        ''' Delete cached resampled daily ISD temperature data if it has expired for the given year. '''
        return validate_isd_daily_temp_data_cache(self.usaf_id, year)

    def validate_gsod_daily_temp_data_cache(self, year):
        ''' Delete cached resampled daily GSOD temperature data if it has expired for the given year. '''
        return validate_gsod_daily_temp_data_cache(self.usaf_id, year)

    # pandas time series to json
    def serialize_isd_hourly_temp_data(self, ts):
        ''' Serialize resampled hourly ISD pandas time series as JSON for caching. '''
        return serialize_isd_hourly_temp_data(ts)

    def serialize_isd_daily_temp_data(self, ts):
        ''' Serialize resampled daily ISD pandas time series as JSON for caching. '''
        return serialize_isd_daily_temp_data(ts)

    def serialize_gsod_daily_temp_data(self, ts):
        ''' Serialize resampled daily GSOD pandas time series as JSON for caching. '''
        return serialize_gsod_daily_temp_data(ts)

    # json to pandas time series
    def deserialize_isd_hourly_temp_data(self, data):
        ''' Deserialize JSON representation of resampled hourly ISD into pandas time series. '''
        return deserialize_isd_hourly_temp_data(data)

    def deserialize_isd_daily_temp_data(self, data):
        ''' Deserialize JSON representation of resampled daily ISD into pandas time series. '''
        return deserialize_isd_daily_temp_data(data)

    def deserialize_gsod_daily_temp_data(self, data):
        ''' Deserialize JSON representation of resampled daily GSOD into pandas time series. '''
        return deserialize_gsod_daily_temp_data(data)

    # return pandas time series of data from cache
    def read_isd_hourly_temp_data_from_cache(self, year):
        ''' Get cached version of resampled hourly ISD temperature data for given year. '''
        return read_isd_hourly_temp_data_from_cache(self.usaf_id, year)

    def read_isd_daily_temp_data_from_cache(self, year):
        ''' Get cached version of resampled daily ISD temperature data for given year. '''
        return read_isd_daily_temp_data_from_cache(self.usaf_id, year)

    def read_gsod_daily_temp_data_from_cache(self, year):
        ''' Get cached version of resampled daily GSOD temperature data for given year. '''
        return read_gsod_daily_temp_data_from_cache(self.usaf_id, year)

    # write pandas time series of data to cache for a particular year
    def write_isd_hourly_temp_data_to_cache(self, year, ts):
        ''' Write resampled hourly ISD temperature data to cache for given year. '''
        return write_isd_hourly_temp_data_to_cache(self.usaf_id, year, ts)

    def write_isd_daily_temp_data_to_cache(self, year, ts):
        ''' Write resampled daily ISD temperature data to cache for given year. '''
        return write_isd_daily_temp_data_to_cache(self.usaf_id, year, ts)

    def write_gsod_daily_temp_data_to_cache(self, year, ts):
        ''' Write resampled daily GSOD temperature data to cache for given year. '''
        return write_gsod_daily_temp_data_to_cache(self.usaf_id, year, ts)

    # delete cached data for a particular year
    def destroy_cached_isd_hourly_temp_data(self, year):
        ''' Remove cached resampled hourly ISD temperature data to cache for given year. '''
        return destroy_cached_isd_hourly_temp_data(self.usaf_id, year)

    def destroy_cached_isd_daily_temp_data(self, year):
        ''' Remove cached resampled daily ISD temperature data to cache for given year. '''
        return destroy_cached_isd_daily_temp_data(self.usaf_id, year)

    def destroy_cached_gsod_daily_temp_data(self, year):
        ''' Remove cached resampled daily GSOD temperature data to cache for given year. '''
        return destroy_cached_gsod_daily_temp_data(self.usaf_id, year)

    # load data either from cache if valid or directly from source
    def load_isd_hourly_temp_data_cached_proxy(self, year):
        ''' Load resampled hourly ISD temperature data from cache, or if it is expired or hadn't been cached, fetch from FTP for given year. '''
        return load_isd_hourly_temp_data_cached_proxy(self.usaf_id, year)

    def load_isd_daily_temp_data_cached_proxy(self, year):
        ''' Load resampled daily ISD temperature data from cache, or if it is expired or hadn't been cached, fetch from FTP for given year. '''
        return load_isd_daily_temp_data_cached_proxy(self.usaf_id, year)

    def load_gsod_daily_temp_data_cached_proxy(self, year):
        ''' Load resampled daily GSOD temperature data from cache, or if it is expired or hadn't been cached, fetch from FTP for given year. '''
        return load_gsod_daily_temp_data_cached_proxy(self.usaf_id, year)

    # main interface: load data from start date to end date
    def load_isd_hourly_temp_data(
            self, start, end, read_from_cache=True, write_to_cache=True):
        ''' Load resampled hourly ISD temperature data from start date to end date (inclusive).

        This is the primary convenience method for loading resampled hourly ISD temperature data.

        Parameters
        ----------
        start : datetime.datetime
            The earliest date from which to load data.
        end : datetime.datetime
            The latest date until which to load data.
        read_from_cache : bool
            Whether or not to load data from cache.
        write_to_cache : bool
            Whether or not to write newly loaded data to cache.
        '''
        return load_isd_hourly_temp_data(
            self.usaf_id, start, end, read_from_cache=read_from_cache,
            write_to_cache=write_to_cache)

    def load_isd_daily_temp_data(
            self, start, end, read_from_cache=True, write_to_cache=True):
        ''' Load resampled daily ISD temperature data from start date to end date (inclusive).

        This is the primary convenience method for loading resampled daily ISD temperature data.

        Parameters
        ----------
        start : datetime.datetime
            The earliest date from which to load data.
        end : datetime.datetime
            The latest date until which to load data.
        read_from_cache : bool
            Whether or not to load data from cache.
        write_to_cache : bool
            Whether or not to write newly loaded data to cache.
        '''
        return load_isd_daily_temp_data(
            self.usaf_id, start, end, read_from_cache=read_from_cache,
            write_to_cache=write_to_cache)

    def load_gsod_daily_temp_data(
            self, start, end, read_from_cache=True, write_to_cache=True):
        ''' Load resampled daily GSOD temperature data from start date to end date (inclusive).

        This is the primary convenience method for loading resampled daily GSOD temperature data.

        Parameters
        ----------
        start : datetime.datetime
            The earliest date from which to load data.
        end : datetime.datetime
            The latest date until which to load data.
        read_from_cache : bool
            Whether or not to load data from cache.
        write_to_cache : bool
            Whether or not to write newly loaded data to cache.
        '''
        return load_gsod_daily_temp_data(
            self.usaf_id, start, end, read_from_cache=read_from_cache,
            write_to_cache=write_to_cache)

    # load all cached data for this station
    def load_cached_isd_hourly_temp_data(self):
        ''' Load all cached resampled hourly ISD temperature data. '''
        return load_cached_isd_hourly_temp_data(self.usaf_id)

    def load_cached_isd_daily_temp_data(self):
        ''' Load all cached resampled daily ISD temperature data. '''
        return load_cached_isd_daily_temp_data(self.usaf_id)

    def load_cached_gsod_daily_temp_data(self):
        ''' Load all cached resampled daily GSOD temperature data. '''
        return load_cached_gsod_daily_temp_data(self.usaf_id)
