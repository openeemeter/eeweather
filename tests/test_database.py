''' Note about database tests.

    The database can be rebuilt from scratch using the command:

        $ eeweather rebuild_db

    The database can be inspected using the command (opens sqlite3 CLI):

        $ eeweather inspect_db

    These tests do not cover these main functions - instead, they test the
    content of the database. They can be thought of as integration tests.
'''
from eeweather.connections import metadata_db_connection_proxy


def test_database_tables():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select name from sqlite_master where type='table' ''')
    tables = [name for (name,) in cur.fetchall()]
    assert tables == [
        'isd_station_metadata',
        'isd_file_metadata',
        'zcta_metadata',
        'zcta_to_isd_station',
        'iecc_climate_zone_metadata',
        'iecc_moisture_regime_metadata',
        'ba_climate_zone_metadata',
        'ca_climate_zone_metadata',
        'tmy3_station_metadata',
        'zipcode_to_cz2010_station',
    ]


def test_isd_station_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from isd_station_metadata ''')
    (count,) = cur.fetchone()
    assert count == 3774


def test_isd_station_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select * from isd_station_metadata where quality='high' limit 1 ''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {
        'ba_climate_zone': 'Hot-Dry',
        'ca_climate_zone': 'CA_14',
        'elevation': '+0625.1',
        'iecc_climate_zone': '3',
        'iecc_moisture_regime': 'B',
        'latitude': '+34.300',
        'longitude': '-116.167',
        'name': 'TWENTY NINE PALMS',
        'quality': 'high',
        'recent_wban_id': '93121',
        'usaf_id': '690150',
        'wban_ids': '93121,99999'
    }

def test_isd_file_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from isd_file_metadata ''')
    (count,) = cur.fetchone()
    assert count == 34651  # this count is brittle b/c of frequent updates


def test_isd_file_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select * from isd_file_metadata limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {'usaf_id': '423630', 'wban_id': '99999', 'year': '2013'}


def test_zcta_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from zcta_metadata ''')
    (count,) = cur.fetchone()
    assert count == 33144


def test_zcta_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select * from zcta_metadata limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {
        'ba_climate_zone': 'Hot-Humid',
        'ca_climate_zone': None,
        'geometry': None,
        'iecc_climate_zone': '1',
        'iecc_moisture_regime': 'A',
        'latitude': '18.1800455429617',
        'longitude': '-66.752178136408',
        'zcta_id': '00601'
    }


def test_zcta_to_isd_station_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from zcta_to_isd_station ''')
    (count,) = cur.fetchone()
    assert count == 331440


def test_zcta_to_isd_station_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select * from zcta_to_isd_station limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {
        'ba_climate_zone_match': 1,
        'ca_climate_zone_match': 1,
        'distance_meters': '42764',
        'iecc_climate_zone_match': 1,
        'iecc_moisture_regime_match': 1,
        'rank': 1,
        'usaf_id': '785145',
        'zcta_id': '00601'
    }


def test_iecc_climate_zone_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from iecc_climate_zone_metadata ''')
    (count,) = cur.fetchone()
    assert count == 8


def test_iecc_climate_zone_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select iecc_climate_zone from iecc_climate_zone_metadata limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {'iecc_climate_zone': '1'}


def test_iecc_moisture_regime_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from iecc_moisture_regime_metadata ''')
    (count,) = cur.fetchone()
    assert count == 3


def test_iecc_moisture_regime_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select iecc_moisture_regime from iecc_moisture_regime_metadata limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {'iecc_moisture_regime': 'A'}


def test_ba_climate_zone_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from ba_climate_zone_metadata ''')
    (count,) = cur.fetchone()
    assert count == 8


def test_ba_climate_zone_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select ba_climate_zone from ba_climate_zone_metadata limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {'ba_climate_zone': 'Cold'}


def test_ca_climate_zone_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from ca_climate_zone_metadata ''')
    (count,) = cur.fetchone()
    assert count == 16


def test_ca_climate_zone_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select ca_climate_zone, name from ca_climate_zone_metadata limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {
        'ca_climate_zone': 'CA_01',
        'name': 'Arcata',
    }


def test_tmy3_station_metadata_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from tmy3_station_metadata ''')
    (count,) = cur.fetchone()
    assert count == 1020


def test_tmy3_station_metadata_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select * from tmy3_station_metadata limit 1''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {
        'class': 'I',
        'name': 'Twentynine Palms',
        'state': 'CA',
        'usaf_id': '690150',
    }


def test_zipcode_to_cz2010_station_table_count():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select count(*) from zipcode_to_cz2010_station ''')
    (count,) = cur.fetchone()
    assert count == 1664


def test_zipcode_to_cz2010_station_table_content():
    conn = metadata_db_connection_proxy.get_connection()

    cur = conn.cursor()
    cur.execute(''' select * from zipcode_to_cz2010_station limit 1 ''')
    row = cur.fetchone()
    data = {desc[0]: value for value, desc in zip(row, cur.description)}
    assert data == {'usaf_id': '722956', 'zipcode': '90001'}
