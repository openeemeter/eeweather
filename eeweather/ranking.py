import pandas as pd
import numpy as np
import pyproj

from .api import get_lat_long_climate_zones
from .connections import metadata_db_connection_proxy
from .utils import lazy_property

__all__ = (
    'get_candidate_stations',
)

class CachedData(object):

    @lazy_property
    def all_station_metadata(self):
        conn = metadata_db_connection_proxy.get_connection()
        cur = conn.cursor()
        cur.execute('''
          select
            isd.usaf_id
            , isd.latitude
            , isd.longitude
            , isd.iecc_climate_zone
            , isd.iecc_moisture_regime
            , isd.ba_climate_zone
            , isd.ca_climate_zone
            , isd.quality as rough_quality
            , isd.elevation
            , isd.state
            , tmy3.class as tmy3_class
            , tmy3.usaf_id is not null as is_tmy3
            , cz2010.usaf_id is not null as is_cz2010
          from
            isd_station_metadata as isd
            left join cz2010_station_metadata as cz2010 on
              isd.usaf_id = cz2010.usaf_id
            left join tmy3_station_metadata as tmy3 on
              isd.usaf_id = tmy3.usaf_id
          order by
            isd.usaf_id
        ''')

        df = pd.DataFrame([
            {
                col[0]: val
                for col, val in zip(cur.description, row)
            }
            for row in cur.fetchall()
        ], columns=[
            'usaf_id', 'latitude', 'longitude',
            'iecc_climate_zone', 'iecc_moisture_regime',
            'ba_climate_zone', 'ca_climate_zone',
            'rough_quality', 'elevation', 'state',
            'tmy3_class', 'is_tmy3', 'is_cz2010',
        ]).set_index('usaf_id')

        df['latitude'] = df.latitude.astype(float)
        df['longitude'] = df.longitude.astype(float)
        df['elevation'] = df.elevation.astype(float)
        df['is_tmy3'] = df.is_tmy3.astype(bool)
        df['is_cz2010'] = df.is_cz2010.astype(bool)
        return df

cached_data = CachedData()


def _combine_filters(filters, index):
    combined_filters = pd.Series(True, index=index)
    for f in filters:
        combined_filters &= f
    return combined_filters


def get_candidate_stations(
    site_latitude, site_longitude, site_state=None, site_elevation=None,
    match_iecc_climate_zone=False, match_iecc_moisture_regime=False,
    match_ba_climate_zone=False, match_ca_climate_zone=False,
    match_state=False, minimum_quality=None, minimum_tmy3_class=None,
    max_distance_meters=None, max_difference_elevation_meters=None,
    is_tmy3=None, is_cz2010=None,
):
    candidates = cached_data.all_station_metadata

    # compute distances
    candidates_defined_lat_long = candidates[
        candidates.latitude.notnull() & candidates.longitude.notnull()]
    candidates_latitude = candidates_defined_lat_long.latitude
    candidates_longitude = candidates_defined_lat_long.longitude
    tiled_site_latitude = np.tile(site_latitude, candidates_latitude.shape)
    tiled_site_longitude = np.tile(site_longitude, candidates_longitude.shape)
    geod = pyproj.Geod(ellps='WGS84')
    dists = geod.inv(
        tiled_site_longitude, tiled_site_latitude,
        candidates_longitude.values, candidates_latitude.values)[2]
    distance_meters = pd.Series(
        dists, index=candidates_defined_lat_long.index
    ).reindex(candidates.index)
    candidates['distance_meters'] = distance_meters

    if site_elevation is not None:
        difference_elevation_meters = (
            candidates.elevation - site_elevation).abs()
    else:
        difference_elevation_meters = None
    candidates['difference_elevation_meters'] = difference_elevation_meters

    site_climate_zones = get_lat_long_climate_zones(site_latitude, site_longitude)
    site_iecc_climate_zone = site_climate_zones['iecc_climate_zone']
    site_iecc_moisture_regime = site_climate_zones['iecc_moisture_regime']
    site_ca_climate_zone = site_climate_zones['ca_climate_zone']
    site_ba_climate_zone = site_climate_zones['ba_climate_zone']

    # create filters
    filters = []

    if match_iecc_climate_zone:
        if site_iecc_climate_zone is None:
            filters.append(candidates.iecc_climate_zone.isnull())
        else:
            filters.append(candidates.iecc_climate_zone == site_iecc_climate_zone)
    if match_iecc_moisture_regime:
        if site_iecc_moisture_regime is None:
            filters.append(candidates.iecc_moisture_regime.isnull())
        else:
            filters.append(candidates.iecc_moisture_regime == site_iecc_moisture_regime)
    if match_ba_climate_zone:
        if site_ba_climate_zone is None:
            filters.append(candidates.ba_climate_zone.isnull())
        else:
            filters.append(candidates.ba_climate_zone == site_ba_climate_zone)
    if match_ca_climate_zone:
        if site_ca_climate_zone is None:
            filters.append(candidates.ca_climate_zone.isnull())
        else:
            filters.append(candidates.ca_climate_zone == site_ca_climate_zone)

    if match_state:
        if site_state is None:
            filters.append(candidates.state.isnull())
        else:
            filters.append(candidates.state == site_state)

    if is_tmy3 is not None:
        filters.append(candidates.is_tmy3.isin([is_tmy3]))
    if is_cz2010 is not None:
        filters.append(candidates.is_cz2010.isin([is_cz2010]))

    if minimum_quality == 'low':
        filters.append(candidates.rough_quality.isin(['high', 'medium', 'low']))
    elif minimum_quality == 'medium':
        filters.append(candidates.rough_quality.isin(['high', 'medium']))
    elif minimum_quality == 'high':
        filters.append(candidates.rough_quality.isin(['high']))

    if minimum_tmy3_class == 'III':
        filters.append(candidates.tmy3_class.isin(['I', 'II', 'III']))
    elif minimum_tmy3_class == 'II':
        filters.append(candidates.tmy3_class.isin(['I', 'II']))
    elif minimum_tmy3_class == 'I':
        filters.append(candidates.tmy3_class.isin(['I']))

    if max_distance_meters is not None:
        filters.append(candidates.distance_meters <= max_distance_meters)

    if max_difference_elevation_meters is not None and site_elevation is not None:
        filters.append(
            candidates.difference_elevation_meters <= max_difference_elevation_meters)

    combined_filters = _combine_filters(filters, candidates.index)
    filtered_candidates = candidates[combined_filters]
    ranked_filtered_candidates = filtered_candidates.sort_values(by=['distance_meters'])
    return ranked_filtered_candidates
