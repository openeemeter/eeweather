from .connections import metadata_db_connection_proxy

__all__ = (
    'get_zcta_ids',
)


def get_zcta_ids():
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()
    cur.execute('select zcta_id from zcta_metadata')
    return [row[0] for row in cur.fetchall()]
