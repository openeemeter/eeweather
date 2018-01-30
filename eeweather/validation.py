from .connections import metadata_db_connection_proxy
from .exceptions import (
    UnrecognizedZCTAError,
    UnrecognizedUSAFIDError,
)


__all__ = (
    'valid_zcta_or_raise',
    'valid_usaf_id_or_raise',
)


def valid_zcta_or_raise(zcta):
    ''' Check if ZCTA is valid and raise eeweather.UnrecognizedZCTAError if not. '''
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()

    cur.execute('''
      select exists (
        select
          zcta_id
        from
          zcta_metadata
        where
          zcta_id = ?
      )
    ''', (zcta, ))
    (exists,) = cur.fetchone()
    if exists:
        return True
    else:
        raise UnrecognizedZCTAError(zcta)


def valid_usaf_id_or_raise(usaf_id):
    ''' Check if USAF ID is valid and raise eeweather.UnrecognizedUSAFIDError if not. '''
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()

    cur.execute('''
      select exists (
        select
          usaf_id
        from
          isd_station_metadata
        where
          usaf_id = ?
      )
    ''', (usaf_id, ))
    (exists,) = cur.fetchone()
    if exists:
        return True
    else:
        raise UnrecognizedUSAFIDError(usaf_id)
