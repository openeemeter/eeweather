from .connections import metadata_db_connection_proxy

__all__ = (
    'get_zcta_ids',
    'get_isd_station_usaf_ids',
)


def get_zcta_ids(state=None):
    ''' Get ids of all supported ZCTAs, optionally by state.

    Parameters
    ----------
    state : str, optional
        Select zipcodes only from this state or territory, given as 2-letter
        abbreviation (e.g., ``'CA'``, ``'PR'``).

    Returns
    -------
    results : list of str
        List of all supported selected ZCTA IDs.
    '''
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()

    if state is None:
        cur.execute('''
          select zcta_id from zcta_metadata
        ''')
    else:
        cur.execute('''
          select zcta_id from zcta_metadata where state = ?
        ''', (state,))
    return [row[0] for row in cur.fetchall()]


def get_isd_station_usaf_ids(state=None):
    ''' Get USAF IDs of all supported ISD stations, optionally by state.

    Parameters
    ----------
    state : str, optional
        Select ISD station USAF IDs only from this state or territory, given
        as 2-letter abbreviation (e.g., ``'CA'``, ``'PR'``).

    Returns
    -------
    results : list of str
        List of all supported selected ISD station USAF IDs.
    '''
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()

    if state is None:
        cur.execute('''
          select usaf_id from isd_station_metadata
        ''')
    else:
        cur.execute('''
          select usaf_id from isd_station_metadata where state = ?
        ''', (state,))
    return [row[0] for row in cur.fetchall()]
