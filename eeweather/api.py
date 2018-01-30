import json

from .connections import metadata_db_connection_proxy
from .exceptions import (
    UnrecognizedUSAFIDError,
    UnrecognizedZCTAError,
)

from .utils import lazy_property


__all__ = (
    'get_lat_long_climate_zones',
    'get_zcta_metadata',
)


class CachedData(object):

    @lazy_property
    def climate_zone_geometry(self):
        try:
            from shapely.geometry import shape
        except ImportError:  # pragma: no cover
            raise ImportError('Matching by lat/lng within climate zone requires shapely')

        conn = metadata_db_connection_proxy.get_connection()
        cur = conn.cursor()

        cur.execute('''
          select
            iecc_climate_zone, geometry
          from
            iecc_climate_zone_metadata
        ''')
        iecc_climate_zones = [
            (cz_id, shape(json.loads(geometry)))
            for (cz_id, geometry) in cur.fetchall()
        ]

        cur.execute('''
          select
            iecc_moisture_regime, geometry
          from
            iecc_moisture_regime_metadata
        ''')
        iecc_moisture_regimes = [
            (cz_id, shape(json.loads(geometry)))
            for (cz_id, geometry) in cur.fetchall()
        ]

        cur.execute('''
          select
            ba_climate_zone, geometry
          from
            ba_climate_zone_metadata
        ''')
        ba_climate_zones = [
            (cz_id, shape(json.loads(geometry)))
            for (cz_id, geometry) in cur.fetchall()
        ]

        cur.execute('''
          select
            ca_climate_zone, geometry
          from
            ca_climate_zone_metadata
        ''')
        ca_climate_zones = [
            (cz_id, shape(json.loads(geometry)))
            for (cz_id, geometry) in cur.fetchall()
        ]


        return (
            iecc_climate_zones,
            iecc_moisture_regimes,
            ba_climate_zones,
            ca_climate_zones,
        )


cached_data = CachedData()


def get_lat_long_climate_zones(latitude, longitude):
    try:
        from shapely.geometry import Point
    except ImportError:  # pragma: no cover
        raise ImportError('Finding climate zone of lat/long points requires shapely.')

    (
        iecc_climate_zones,
        iecc_moisture_regimes,
        ba_climate_zones,
        ca_climate_zones,
    ) = cached_data.climate_zone_geometry

    point = Point(longitude, latitude)  # x,y
    climate_zones = {}
    for iecc_climate_zone, shape in iecc_climate_zones:
        if shape.contains(point):
            climate_zones['iecc_climate_zone'] = iecc_climate_zone
            break
    else:
        climate_zones['iecc_climate_zone'] = None

    for iecc_moisture_regime, shape in iecc_moisture_regimes:
        if shape.contains(point):
            climate_zones['iecc_moisture_regime'] = iecc_moisture_regime
            break
    else:
        climate_zones['iecc_moisture_regime'] = None

    for ba_climate_zone, shape in ba_climate_zones:
        if shape.contains(point):
            climate_zones['ba_climate_zone'] = ba_climate_zone
            break
    else:
        climate_zones['ba_climate_zone'] = None

    for ca_climate_zone, shape in ca_climate_zones:
        if shape.contains(point):
            climate_zones['ca_climate_zone'] = ca_climate_zone
            break
    else:
        climate_zones['ca_climate_zone'] = None

    return climate_zones


def get_zcta_metadata(zcta):
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()
    cur.execute('''
      select
        *
      from
        zcta_metadata
      where
        zcta_id = ?
    ''', (zcta,))
    row = cur.fetchone()
    if row is None:
        raise UnrecognizedZCTAError(zcta)
    return {
        col[0]: row[i]
        for i, col in enumerate(cur.description)
    }
