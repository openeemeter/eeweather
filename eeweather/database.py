from collections import defaultdict
from datetime import datetime, timedelta
import json
import logging
import os
import shutil
import subprocess
import tempfile

import pandas as pd
import numpy as np

from .connections import (
    noaa_ftp_connection_proxy,
    metadata_db_connection_proxy
)


logger = logging.getLogger(__name__)

__all__ = (
    'build_metadata_db',
    'inspect_metadata_db',
)


class PrettyFloat(float):
    def __repr__(self):
        return '%.7g' % self


def pretty_floats(obj):
    if isinstance(obj, float):
        return PrettyFloat(round(obj, 4))
    elif isinstance(obj, dict):
        return dict((k, pretty_floats(v)) for k, v in obj.items())
    elif isinstance(obj, (list, tuple)):
        return list(map(pretty_floats, obj))
    return obj


def to_geojson(polygon):
    import simplejson
    from shapely.geometry import mapping
    return simplejson.dumps(pretty_floats(mapping(polygon)), separators=(',', ':'))


def _download_primary_sources():
    root_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    scripts_path = os.path.join(root_dir, 'scripts', 'download_primary_sources.sh')

    download_path = tempfile.mkdtemp()
    subprocess.call([scripts_path, download_path])
    return download_path


def _load_isd_station_metadata(download_path):
    ''' Collect metadata for US isd stations.
    '''
    from shapely.geometry import Point

    # load ISD history which contains metadata
    isd_history = pd.read_csv(
        os.path.join(download_path, 'isd-history.csv'),
        dtype=str,
        parse_dates=['BEGIN', 'END']
    )

    hasGEO = (
        isd_history.LAT.notnull() &
        isd_history.LON.notnull() &
        (isd_history.LAT != 0)
    )
    isUS = (
        ((isd_history.CTRY == 'US') & (isd_history.STATE.notnull()))
        # AQ = American Samoa, GQ = Guam, RQ = Peurto Rico, VQ = Virgin Islands
        | (isd_history.CTRY[1] == 'Q')
    )
    hasUSAF = isd_history.USAF != '999999'

    metadata = {}
    for usaf_station, group in isd_history[hasGEO & isUS & hasUSAF].groupby('USAF'):
        # find most recent
        recent = group.loc[group.END.idxmax()]
        wban_stations = list(group.WBAN)
        metadata[usaf_station] = {
            'usaf_id': usaf_station,
            'wban_ids': wban_stations,
            'recent_wban_id': recent.WBAN,
            'name': recent['STATION NAME'],
            'latitude': recent.LAT,
            'longitude': recent.LON,
            'point': Point(float(recent.LON), float(recent.LAT)),
            'elevation': recent['ELEV(M)'],
        }

    return metadata


def _load_isd_file_metadata(download_path, isd_station_metadata):
    ''' Collect data counts for isd files.
    '''

    isd_inventory = pd.read_csv(
        os.path.join(download_path, 'isd-inventory.csv'),
        dtype=str
    )

    # filter to stations with metadata
    station_keep = [usaf in isd_station_metadata for usaf in isd_inventory.USAF]
    isd_inventory = isd_inventory[station_keep]
    # filter by year
    year_keep = isd_inventory.YEAR > '2005'
    isd_inventory = isd_inventory[year_keep]

    metadata = {}
    for (usaf_station, year), group in isd_inventory.groupby(['USAF', 'YEAR']):
        if usaf_station not in metadata:
            metadata[usaf_station] = {
                'usaf_id': usaf_station,
                'years': {}
            }
        metadata[usaf_station]['years'][year] = [
            {
                'wban_id': row.WBAN,
                'counts': [
                    row.JAN, row.FEB, row.MAR, row.APR, row.MAY, row.JUN,
                    row.JUL, row.AUG, row.SEP, row.OCT, row.NOV, row.DEC,
                ]
            }
            for i, row in group.iterrows()
        ]
    return metadata


def _compute_isd_station_quality(
        isd_station_metadata, isd_file_metadata,
        end_year=None, years_back=None, quality_func=None):

    if end_year is None:
        end_year = datetime.now().year - 1  # last full year

    if years_back is None:
        years_back = 5

    if quality_func is None:
        def quality_func(values):
            minimum = values.min()
            if minimum > 24*25:
                return 'high'
            elif minimum > 24*15:
                return 'medium'
            else:
                return 'low'

    # e.g., if end_year == 2017, year_range = ["2013", "2014", ..., "2017"]
    year_range = set([
        str(y) for y in range(end_year - (years_back - 1), end_year + 1)
    ])

    def _compute_station_quality(usaf_id):
        years_data = isd_file_metadata.get(usaf_id, {}).get('years', {})
        if not all([year in years_data for year in year_range]):
            return quality_func(np.repeat(0, 60))
        counts = defaultdict(lambda: 0)
        for y, year in enumerate(year_range):
            for station in years_data[year]:
                for m, month_counts in enumerate(station['counts']):
                    counts[y*12 + m] += int(month_counts)
        return quality_func(np.array(list(counts.values())))

    # figure out counts for years of interest
    for usaf_id, metadata in isd_station_metadata.items():
        metadata['quality'] = _compute_station_quality(usaf_id)


def _load_zcta_metadata(download_path):
    from shapely.geometry import shape

    # load zcta geojson
    geojson_path = os.path.join(download_path, 'cb_2016_us_zcta510_500k.json')
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)

    metadata = {}
    for feature in geojson['features']:
        zcta = feature['properties']['GEOID10']
        geometry = feature['geometry']
        polygon = shape(geometry)
        centroid = polygon.centroid
        metadata[zcta] = {
            'zcta': zcta,
            'polygon': polygon,
            'geometry': to_geojson(polygon),
            'centroid': centroid,
            'latitude': centroid.coords[0][1],
            'longitude': centroid.coords[0][0],
        }
    return metadata


def _load_county_metadata(download_path):
    from shapely.geometry import shape

    # load county geojson
    geojson_path = os.path.join(download_path, 'cb_2016_us_county_500k.json')
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)

    metadata = {}
    for feature in geojson['features']:
        county = feature['properties']['GEOID']
        geometry = feature['geometry']
        polygon = shape(geometry)
        centroid = polygon.centroid
        metadata[county] = {
            'county': county,
            'polygon': polygon,
            'geometry': to_geojson(polygon),
            'centroid': centroid,
            'latitude': centroid.coords[0][1],
            'longitude': centroid.coords[0][0],
        }

    # load county climate zones
    county_climate_zones = pd.read_csv(os.path.join(download_path, 'climate_zones.csv'),
        dtype=str,
        usecols=[
            'State FIPS',
            'County FIPS',
            'IECC Climate Zone',
            'IECC Moisture Regime',
            'BA Climate Zone',
            'County Name'
        ]
    )

    for i, row in county_climate_zones.iterrows():

        county = row['State FIPS'] + row['County FIPS']
        if county not in metadata:
            logger.warn(
                'Could not find geometry for county {}, skipping.'
                .format(county)
            )
            continue

        metadata[county].update({
            'name': row['County Name'],
            'iecc_climate_zone': row['IECC Climate Zone'],
            'iecc_moisture_regime': (
                row['IECC Moisture Regime']
                if not pd.isnull(row['IECC Moisture Regime'])
                else None
            ),
            'ba_climate_zone': row['BA Climate Zone'],
        })

    return metadata


def _load_CA_climate_zone_metadata(download_path):
    from shapely.geometry import shape, mapping
    ca_climate_zone_names = {
        '01': 'Arcata',
        '02': 'Santa Rosa',
        '03': 'Oakland',
        '04': 'San Jose-Reid',
        '05': 'Santa Maria',
        '06': 'Torrance',
        '07': 'San Diego-Lindbergh',
        '08': 'Fullerton',
        '09': 'Burbank-Glendale',
        '10': 'Riverside',
        '11': 'Red Bluff',
        '12': 'Sacramento',
        '13': 'Fresno',
        '14': 'Palmdale',
        '15': 'Palm Spring-Intl',
        '16': 'Blue Canyon',
    }
    geojson_path = os.path.join(download_path, 'CA_Building_Standards_Climate_Zones.json')
    with open(geojson_path, 'r') as f:
        geojson = json.load(f)

    metadata = {}
    for feature in geojson['features']:
        zone = '{:02d}'.format(int(feature['properties']['Zone']))
        geometry = feature['geometry']
        polygon = shape(geometry)
        metadata[zone] = {
            'ca_climate_zone': 'CA_{}'.format(zone),
            'name': ca_climate_zone_names[zone],
            'polygon': polygon,
            'geometry': to_geojson(polygon),
        }
    return metadata


def _load_tmy3_station_metadata(download_path):
    from bs4 import BeautifulSoup
    path = os.path.join(download_path, 'tmy3-stations.html')
    with open(path, 'r') as f:
        soup = BeautifulSoup(f.read(), 'html.parser')
    tmy3_station_elements = soup.select('td .hide')

    metadata = {}
    for station_el in tmy3_station_elements:
        station_name_el = station_el.findNext('td').findNext('td')
        station_class_el = station_name_el.findNext('td')
        usaf_id = station_el.text.strip()
        name = (
            ''.join(station_name_el.text.split(',')[:-1])
            .replace('\n', '').replace('\t', '').strip()
        )
        metadata[usaf_id] = {
            'usaf_id': usaf_id,
            'name': name,
            'state': station_name_el.text.split(',')[-1].strip(),
            'class': station_class_el.text.split()[1].strip(),
        }
    return metadata


def _load_zipcode_to_cz2010_station(download_path):
    '''These are actual zipcodes, not ZCTAs afaik (philngo)'''
    zipcode_to_cz2010_station = pd.read_csv(
        os.path.join(download_path, 'zipcode_to_cz2010.csv'),
        dtype=str
    )
    return zipcode_to_cz2010_station


def _create_merged_climate_zones_metadata(county_metadata):
    from shapely.ops import cascaded_union

    iecc_climate_zone_polygons = defaultdict(list)
    iecc_moisture_regime_polygons = defaultdict(list)
    ba_climate_zone_polygons = defaultdict(list)

    for county in county_metadata.values():
        polygon = county['polygon']
        iecc_climate_zone = county.get('iecc_climate_zone')
        iecc_moisture_regime = county.get('iecc_moisture_regime')
        ba_climate_zone = county.get('ba_climate_zone')
        if iecc_climate_zone is not None:
            iecc_climate_zone_polygons[iecc_climate_zone].append(polygon)
        if iecc_moisture_regime is not None:
            iecc_moisture_regime_polygons[iecc_moisture_regime].append(polygon)
        if ba_climate_zone is not None:
            ba_climate_zone_polygons[ba_climate_zone].append(polygon)

    iecc_climate_zone_metadata = {}
    for iecc_climate_zone, polygons in iecc_climate_zone_polygons.items():
        polygon = cascaded_union(polygons)
        polygon = polygon.simplify(0.01)
        iecc_climate_zone_metadata[iecc_climate_zone] = {
            'iecc_climate_zone': iecc_climate_zone,
            'polygon': polygon,
            'geometry': to_geojson(polygon),
        }

    iecc_moisture_regime_metadata = {}
    for iecc_moisture_regime, polygons in iecc_moisture_regime_polygons.items():
        polygon = cascaded_union(polygons)
        polygon = polygon.simplify(0.01)
        iecc_moisture_regime_metadata[iecc_moisture_regime] = {
            'iecc_moisture_regime': iecc_moisture_regime,
            'polygon': polygon,
            'geometry': to_geojson(polygon),
        }

    ba_climate_zone_metadata = {}
    for ba_climate_zone, polygons in ba_climate_zone_polygons.items():
        polygon = cascaded_union(polygons)
        polygon = polygon.simplify(0.01)
        ba_climate_zone_metadata[ba_climate_zone] = {
            'ba_climate_zone': ba_climate_zone,
            'polygon': polygon,
            'geometry': to_geojson(polygon),
        }

    return (
        iecc_climate_zone_metadata,
        iecc_moisture_regime_metadata,
        ba_climate_zone_metadata,
    )


def _compute_containment(
        point_metadata, point_id_field,
        polygon_metadata, polygon_metadata_field):
    from shapely.vectorized import contains

    points, lats, lons = zip(*[
        (point, point['latitude'], point['longitude'])
        for point in point_metadata.values()
    ])

    for i, polygon in enumerate(polygon_metadata.values()):
        containment = contains(polygon['polygon'], lons, lats)
        for point, c in zip(points, containment):
            if c:
                point[polygon_metadata_field] = polygon[polygon_metadata_field]
    # fill in with None
    for point in point_metadata.values():
        point[polygon_metadata_field] = point.get(polygon_metadata_field, None)


def _map_zcta_to_climate_zones(
        zcta_metadata, iecc_climate_zone_metadata, iecc_moisture_regime_metadata,
        ba_climate_zone_metadata, ca_climate_zone_metadata):

    _compute_containment(
        zcta_metadata, 'zcta',
        iecc_climate_zone_metadata, 'iecc_climate_zone')

    _compute_containment(
        zcta_metadata, 'zcta',
        iecc_moisture_regime_metadata, 'iecc_moisture_regime')

    _compute_containment(
        zcta_metadata, 'zcta',
        ba_climate_zone_metadata, 'ba_climate_zone')

    _compute_containment(
        zcta_metadata, 'zcta',
        ca_climate_zone_metadata, 'ca_climate_zone')


def _map_isd_station_to_climate_zones(
        isd_station_metadata, iecc_climate_zone_metadata, iecc_moisture_regime_metadata,
        ba_climate_zone_metadata, ca_climate_zone_metadata):

    _compute_containment(
        isd_station_metadata, 'usaf_id',
        iecc_climate_zone_metadata, 'iecc_climate_zone')

    _compute_containment(
        isd_station_metadata, 'usaf_id',
        iecc_moisture_regime_metadata, 'iecc_moisture_regime')

    _compute_containment(
        isd_station_metadata, 'usaf_id',
        ba_climate_zone_metadata, 'ba_climate_zone')

    _compute_containment(
        isd_station_metadata, 'usaf_id',
        ca_climate_zone_metadata, 'ca_climate_zone')


def _find_zcta_closest_isd_stations(
        zcta_metadata, isd_station_metadata, limit=None):
    if limit is None:
        limit = 10
    import pyproj
    geod = pyproj.Geod(ellps='WGS84')

    isd_usaf_ids, isd_lats, isd_lngs = zip(*[
        (
            isd_station['usaf_id'],
            float(isd_station['latitude']),
            float(isd_station['longitude'])
        )
        for isd_station in isd_station_metadata.values()
    ])

    isd_lats = np.array(isd_lats)
    isd_lngs = np.array(isd_lngs)

    for zcta in zcta_metadata.values():
        zcta_lats = np.tile(zcta['latitude'], isd_lats.shape)
        zcta_lngs = np.tile(zcta['longitude'], isd_lngs.shape)

        dists = geod.inv(zcta_lngs, zcta_lats, isd_lngs, isd_lats)[2]
        sorted_dists = np.argsort(dists)[:limit]

        closest_isd_stations = []
        for i, idx in enumerate(sorted_dists):
            usaf_id = isd_usaf_ids[idx]
            isd_station = isd_station_metadata[usaf_id]
            closest_isd_stations.append({
                'usaf_id': usaf_id,
                'distance_meters': int(round(dists[idx])),
                'rank': i + 1,
                'iecc_climate_zone_match': (
                    zcta.get('iecc_climate_zone') ==
                    isd_station.get('iecc_climate_zone')
                ),
                'iecc_moisture_regime_match': (
                    zcta.get('iecc_moisture_regime') ==
                    isd_station.get('iecc_moisture_regime')
                ),
                'ba_climate_zone_match': (
                    zcta.get('ba_climate_zone') ==
                    isd_station.get('ba_climate_zone')
                ),
                'ca_climate_zone_match': (
                    zcta.get('ca_climate_zone') ==
                    isd_station.get('ca_climate_zone')
                )
            })
        zcta['closest_isd_stations'] = closest_isd_stations


def _create_table_structures(conn):
    cur = conn.cursor()
    cur.execute('''
      create table isd_station_metadata (
        usaf_id text not null
        , wban_ids text not null
        , recent_wban_id text not null
        , name text not null
        , latitude text not null
        , longitude text not null
        , elevation text
        , quality text default 'low'
        , iecc_climate_zone text
        , iecc_moisture_regime text
        , ba_climate_zone text
        , ca_climate_zone text
      )
    ''')

    cur.execute('''
      create table isd_file_metadata (
        usaf_id text not null
        , year text not null
        , wban_id text not null
      )
    ''')

    cur.execute('''
      create table zcta_metadata (
        zcta_id text not null
        , geometry text
        , latitude text not null
        , longitude text not null
        , iecc_climate_zone text
        , iecc_moisture_regime text
        , ba_climate_zone text
        , ca_climate_zone text
      )
    ''')

    cur.execute('''
      create table zcta_to_isd_station (
        zcta_id text not null
        , usaf_id text not null
        , rank integer not null
        , distance_meters text not null
        , iecc_climate_zone_match boolean not null
        , iecc_moisture_regime_match boolean not null
        , ba_climate_zone_match boolean not null
        , ca_climate_zone_match boolean not null
      )
    ''')

    cur.execute('''
      create table iecc_climate_zone_metadata (
        iecc_climate_zone text not null
        , geometry text
      )
    ''')

    cur.execute('''
      create table iecc_moisture_regime_metadata (
        iecc_moisture_regime text not null
        , geometry text
      )
    ''')

    cur.execute('''
      create table ba_climate_zone_metadata (
        ba_climate_zone text not null
        , geometry text
      )
    ''')

    cur.execute('''
      create table ca_climate_zone_metadata (
        ca_climate_zone text not null
        , name text not null
        , geometry text
      )
    ''')

    cur.execute('''
      create table tmy3_station_metadata (
        usaf_id text not null
        , name text not null
        , state text not null
        , class text not null
      )
    ''')

    cur.execute('''
      create table zipcode_to_cz2010_station (
        zipcode text not null
        , usaf_id text not null
      )
    ''')


def _write_isd_station_metadata_table(conn, isd_station_metadata):
    cur = conn.cursor()

    rows = [
        (
            metadata['usaf_id'],
            ','.join(metadata['wban_ids']),
            metadata['recent_wban_id'],
            metadata['name'],
            metadata['latitude'],
            metadata['longitude'],
            metadata['elevation'],
            metadata['quality'],
            metadata['iecc_climate_zone'],
            metadata['iecc_moisture_regime'],
            metadata['ba_climate_zone'],
            metadata['ca_climate_zone'],
        )
        for station, metadata in sorted(isd_station_metadata.items())
    ]
    cur.executemany('''
      insert into isd_station_metadata(
        usaf_id
        , wban_ids
        , recent_wban_id
        , name
        , latitude
        , longitude
        , elevation
        , quality
        , iecc_climate_zone
        , iecc_moisture_regime
        , ba_climate_zone
        , ca_climate_zone
      ) values (?,?,?,?,?,?,?,?,?,?,?,?)
    ''', rows)
    cur.execute('''
      create index isd_station_metadata_usaf_id on isd_station_metadata(usaf_id)
    ''')
    cur.execute('''
      create index isd_station_metadata_iecc_climate_zone on
        isd_station_metadata(iecc_climate_zone)
    ''')
    cur.execute('''
      create index isd_station_metadata_iecc_moisture_regime on
        isd_station_metadata(iecc_moisture_regime)
    ''')
    cur.execute('''
      create index isd_station_metadata_ba_climate_zone on
        isd_station_metadata(ba_climate_zone)
    ''')
    cur.execute('''
      create index isd_station_metadata_ca_climate_zone on
        isd_station_metadata(ca_climate_zone)
    ''')
    cur.close()
    conn.commit()


def _write_isd_file_metadata_table(conn, isd_file_metadata):
    cur = conn.cursor()

    rows = [
        (
            metadata['usaf_id'],
            year,
            station_data['wban_id']
        )
        for isd_station, metadata in sorted(isd_file_metadata.items())
        for year, year_data in sorted(metadata['years'].items())
        for station_data in year_data
    ]

    cur.executemany('''
      insert into isd_file_metadata(
        usaf_id
        , year
        , wban_id
      ) values (?,?,?)
    ''', rows)

    cur.execute('''
      create index isd_file_metadata_usaf_id on
        isd_file_metadata(usaf_id)
    ''')
    cur.execute('''
      create index isd_file_metadata_year on
        isd_file_metadata(year)
    ''')
    cur.execute('''
      create index isd_file_metadata_usaf_id_year on
        isd_file_metadata(usaf_id, year)
    ''')
    cur.execute('''
      create index isd_file_metadata_wban_id on
        isd_file_metadata(wban_id)
    ''')

    cur.close()
    conn.commit()


def _write_zcta_metadata_table(conn, zcta_metadata, geometry=False):
    cur = conn.cursor()

    rows = [
        (
            metadata['zcta'],
            metadata['geometry'] if geometry else None,
            metadata['latitude'],
            metadata['longitude'],
            metadata['iecc_climate_zone'],
            metadata['iecc_moisture_regime'],
            metadata['ba_climate_zone'],
            metadata['ca_climate_zone'],
        )
        for zcta, metadata in sorted(zcta_metadata.items())
    ]
    cur.executemany('''
      insert into zcta_metadata(
        zcta_id
        , geometry
        , latitude
        , longitude
        , iecc_climate_zone
        , iecc_moisture_regime
        , ba_climate_zone
        , ca_climate_zone
      ) values (?,?,?,?,?,?,?,?)
    ''', rows)
    cur.execute('''
      create index zcta_metadata_zcta_id on zcta_metadata(zcta_id)
    ''')
    cur.execute('''
      create index zcta_metadata_iecc_climate_zone on zcta_metadata(iecc_climate_zone)
    ''')
    cur.execute('''
      create index zcta_metadata_iecc_moisture_regime on zcta_metadata(iecc_moisture_regime)
    ''')
    cur.execute('''
      create index zcta_metadata_ba_climate_zone on zcta_metadata(ba_climate_zone)
    ''')
    cur.execute('''
      create index zcta_metadata_ca_climate_zone on zcta_metadata(ca_climate_zone)
    ''')
    cur.close()
    conn.commit()


def _write_iecc_climate_zone_metadata_table(
        conn, iecc_climate_zone_metadata, geometry=True):
    cur = conn.cursor()

    rows = [
        (
            metadata['iecc_climate_zone'],
            metadata['geometry'] if geometry else None,
        )
        for iecc_climate_zone, metadata in sorted(iecc_climate_zone_metadata.items())
    ]
    cur.executemany('''
      insert into iecc_climate_zone_metadata(
        iecc_climate_zone
        , geometry
      ) values (?,?)
    ''', rows)
    cur.execute('''
      create index iecc_climate_zone_metadata_iecc_climate_zone on
      iecc_climate_zone_metadata(iecc_climate_zone)
    ''')
    cur.close()
    conn.commit()


def _write_iecc_moisture_regime_metadata_table(
        conn, iecc_moisture_regime_metadata, geometry=True):
    cur = conn.cursor()

    rows = [
        (
            metadata['iecc_moisture_regime'],
            metadata['geometry'] if geometry else None,
        )
        for iecc_moisture_regime, metadata in sorted(iecc_moisture_regime_metadata.items())
    ]
    cur.executemany('''
      insert into iecc_moisture_regime_metadata(
        iecc_moisture_regime
        , geometry
      ) values (?,?)
    ''', rows)
    cur.execute('''
      create index iecc_moisture_regime_metadata_iecc_moisture_regime on
      iecc_moisture_regime_metadata(iecc_moisture_regime)
    ''')
    cur.close()
    conn.commit()


def _write_ba_climate_zone_metadata_table(
        conn, ba_climate_zone_metadata, geometry=True):
    cur = conn.cursor()

    rows = [
        (
            metadata['ba_climate_zone'],
            metadata['geometry'] if geometry else None,
        )
        for ba_climate_zone, metadata in sorted(ba_climate_zone_metadata.items())
    ]
    cur.executemany('''
      insert into ba_climate_zone_metadata(
        ba_climate_zone
        , geometry
      ) values (?,?)
    ''', rows)
    cur.execute('''
      create index ba_climate_zone_metadata_ba_climate_zone on
      ba_climate_zone_metadata(ba_climate_zone)
    ''')
    cur.close()
    conn.commit()


def _write_ca_climate_zone_metadata_table(
        conn, ca_climate_zone_metadata, geometry=True):
    cur = conn.cursor()

    rows = [
        (
            metadata['ca_climate_zone'],
            metadata['name'],
            metadata['geometry'] if geometry else None,
        )
        for ca_climate_zone, metadata in sorted(ca_climate_zone_metadata.items())
    ]
    cur.executemany('''
      insert into ca_climate_zone_metadata(
        ca_climate_zone
        , name
        , geometry
      ) values (?,?,?)
    ''', rows)
    cur.execute('''
      create index ca_climate_zone_metadata_ca_climate_zone on
      ca_climate_zone_metadata(ca_climate_zone)
    ''')
    cur.close()
    conn.commit()


def _write_tmy3_station_metadata_table(conn, tmy3_station_metadata):
    cur = conn.cursor()
    rows = [
        (
            metadata['usaf_id'],
            metadata['name'],
            metadata['state'],
            metadata['class'],
        )
        for tmy3_station, metadata in sorted(tmy3_station_metadata.items())
    ]
    cur.executemany('''
      insert into tmy3_station_metadata(
        usaf_id
        , name
        , state
        , class
      ) values (?,?,?,?)
    ''', rows)
    cur.execute('''
      create index tmy3_station_metadata_usaf_id on
        tmy3_station_metadata(usaf_id)
    ''')
    cur.close()
    conn.commit()


def _write_zcta_to_isd_station_table(conn, zcta_metadata):
    cur = conn.cursor()
    rows = [
        (
            metadata['zcta'],
            match['usaf_id'],
            match['rank'],
            match['distance_meters'],
            match['iecc_climate_zone_match'],
            match['iecc_moisture_regime_match'],
            match['ba_climate_zone_match'],
            match['ca_climate_zone_match'],
        )
        for zcta, metadata in sorted(zcta_metadata.items())
        for match in metadata['closest_isd_stations']
    ]
    cur.executemany('''
      insert into zcta_to_isd_station(
        zcta_id
        , usaf_id
        , rank
        , distance_meters
        , iecc_climate_zone_match
        , iecc_moisture_regime_match
        , ba_climate_zone_match
        , ca_climate_zone_match
      ) values (?,?,?,?,?,?,?,?)
    ''', rows)

    cur.execute('''
      create index zcta_to_isd_station_zcta_id on
        zcta_to_isd_station(zcta_id)
    ''')
    cur.execute('''
      create index zcta_to_isd_station_zcta_id_rank on
        zcta_to_isd_station(zcta_id, rank)
    ''')
    cur.execute('''
      create index zcta_to_isd_station_rank on
        zcta_to_isd_station(rank)
    ''')
    cur.close()
    conn.commit()


def _write_zipcode_to_cz2010_station_table(conn, zipcode_to_cz2010_station):
    cur = conn.cursor()
    rows = [
        (row.zipcode, row.cz2010_usaf_id)
        for i, row in zipcode_to_cz2010_station.iterrows()
    ]

    cur.executemany('''
      insert into zipcode_to_cz2010_station(
        zipcode
        , usaf_id
      ) values (?,?)
    ''', rows)

    cur.execute('''
      create index zipcode_to_cz2010_station_zipcode on
        zipcode_to_cz2010_station(zipcode)
    ''')
    cur.execute('''
      create index zipcode_to_cz2010_station_usaf_id on
        zipcode_to_cz2010_station(usaf_id)
    ''')
    cur.close()
    conn.commit()


def build_metadata_db(
        zcta_geometry=False,
        iecc_climate_zone_geometry=True,
        iecc_moisture_regime_geometry=True,
        ba_climate_zone_geometry=True,
        ca_climate_zone_geometry=True,
        n_closest_stations=10):
    ''' Build database of metadata from primary sources.

    Downloads primary sources, clears existing DB, and rebuilds from scratch.

    Parameters
    ----------
    zcta_geometry : bool, optional
        Whether or not to include ZCTA geometry in database.
    iecc_climate_zone_geometry : bool, optional
        Whether or not to include IECC Climate Zone geometry in database.
    iecc_moisture_regime_geometry : bool, optional
        Whether or not to include IECC Moisture Regime geometry in database.
    ba_climate_zone_geometry : bool, optional
        Whether or not to include Building America Climate Zone geometry in database.
    ca_climate_zone_geometry : bool, optional
        Whether or not to include California Building Climate Zone Area geometry in database.
    n_closest_stations : int, optional
        The number of closest stations to include in zcta_to_isd_station table.
    '''

    try:
        import shapely
    except ImportError:
        raise ImportError('Loading polygons requires shapely.')

    try:
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError('Scraping TMY3 station data requires beautifulsoup4.')

    try:
        import pyproj
    except ImportError:
        raise ImportError('Computing distances requires pyproj.')

    try:
        import simplejson
    except ImportError:
        raise ImportError('Writing geojson requires simplejson.')

    download_path = _download_primary_sources()
    conn = metadata_db_connection_proxy.reset_database()

    # Load data into memory
    print('Loading ZCTAs')
    zcta_metadata = _load_zcta_metadata(download_path)

    print('Loading counties')
    county_metadata = _load_county_metadata(download_path)

    print('Merging county climate zones')
    (
        iecc_climate_zone_metadata,
        iecc_moisture_regime_metadata,
        ba_climate_zone_metadata,
    ) = _create_merged_climate_zones_metadata(county_metadata)

    print('Loading CA climate zones')
    ca_climate_zone_metadata = _load_CA_climate_zone_metadata(download_path)

    print('Loading ISD station metadata')
    isd_station_metadata = _load_isd_station_metadata(download_path)

    print('Loading ISD station file metadata')
    isd_file_metadata = _load_isd_file_metadata(
        download_path, isd_station_metadata)

    print('Loading TMY3 station metadata')
    tmy3_station_metadata = _load_tmy3_station_metadata(download_path)

    print('Loading ZIP code to CZ2010 station mapping')
    zipcode_to_cz2010_station = _load_zipcode_to_cz2010_station(download_path)

    # Augment data in memory
    print('Computing ISD station quality')
    # add rough station quality to station metadata
    # (all months in last 5 years have at least 600 points)
    _compute_isd_station_quality(isd_station_metadata, isd_file_metadata)

    print('Mapping ZCTAs to climate zones')
    # add county and ca climate zone mappings
    _map_zcta_to_climate_zones(
        zcta_metadata, iecc_climate_zone_metadata, iecc_moisture_regime_metadata,
        ba_climate_zone_metadata, ca_climate_zone_metadata)

    print('Mapping ISD stations to climate zones')
    # add county and ca climate zone mappings
    _map_isd_station_to_climate_zones(
        isd_station_metadata, iecc_climate_zone_metadata, iecc_moisture_regime_metadata,
        ba_climate_zone_metadata, ca_climate_zone_metadata)

    print('Finding closest ISD stations for each ZCTA')
    _find_zcta_closest_isd_stations(
        zcta_metadata, isd_station_metadata, n_closest_stations)

    # Write tables
    print('Creating table structures')
    _create_table_structures(conn)

    print('Writing ZCTA data')
    _write_zcta_metadata_table(conn, zcta_metadata, geometry=zcta_geometry)

    print('Writing IECC climate zone data')
    _write_iecc_climate_zone_metadata_table(
        conn, iecc_climate_zone_metadata,
        geometry=iecc_climate_zone_geometry)

    print('Writing IECC moisture regime data')
    _write_iecc_moisture_regime_metadata_table(
        conn, iecc_moisture_regime_metadata,
        geometry=iecc_moisture_regime_geometry)

    print('Writing BA climate zone data')
    _write_ba_climate_zone_metadata_table(
        conn, ba_climate_zone_metadata,
        geometry=ba_climate_zone_geometry)

    print('Writing CA climate zone data')
    _write_ca_climate_zone_metadata_table(
        conn, ca_climate_zone_metadata,
        geometry=ca_climate_zone_geometry)

    print('Writing ISD station metadata')
    _write_isd_station_metadata_table(conn, isd_station_metadata)

    print('Writing ISD file metadata')
    _write_isd_file_metadata_table(conn, isd_file_metadata)

    print('Writing TMY3 station metadata')
    _write_tmy3_station_metadata_table(conn, tmy3_station_metadata)

    print('Writing ZCTA to ISD station mapping')
    _write_zcta_to_isd_station_table(conn, zcta_metadata)

    print('Writing ZIP code to CZ2010 station mapping')
    _write_zipcode_to_cz2010_station_table(conn, zipcode_to_cz2010_station)

    print('Cleaning up...')
    shutil.rmtree(download_path)

    print('\u2728  Completed! \u2728')


def inspect_metadata_db():
    subprocess.call(['sqlite3', metadata_db_connection_proxy.db_path])
