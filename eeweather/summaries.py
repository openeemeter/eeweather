from .connections import metadata_db_connection_proxy

__all__ = (
    'get_zcta_ids',
)


def get_zcta_ids():
    ''' Get ids of all supported ZCTAs.

    Returns
    -------
    results : list of str
        List of all supported ZCTA IDs
    '''
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()
    cur.execute('select zcta_id from zcta_metadata')
    return [row[0] for row in cur.fetchall()]
