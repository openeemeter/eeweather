# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_rank_stations_no_filter df.shape"] = (3874, 15)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_climate_zone"] = (
    497,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_moisture_regime"] = (
    933,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_ba_climate_zone"] = (
    502,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_ca_climate_zone"] = (
    3641,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=False"] = (
    3874,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=True"] = (306, 15)

snapshots["test_rank_stations_match_state site_state=None, match_state=True"] = (71, 15)

snapshots["test_rank_stations_is_tmy3 is_tmy3=True"] = (1019, 15)

snapshots["test_rank_stations_is_tmy3 is_tmy3=False"] = (2855, 15)

snapshots["test_rank_stations_is_cz2010 is_cz2010=True"] = (86, 15)

snapshots["test_rank_stations_is_cz2010 is_cz2010=False"] = (3788, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=low"] = (3874, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=medium"] = (1752, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=high"] = (1595, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=III"] = (1019, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=II"] = (857, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=I"] = (222, 15)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=200000"] = (
    52,
    15,
)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=50000"] = (5, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters max_difference_elevation_meters=200"
] = (3874, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=200"
] = (2185, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=50"
] = (1366, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=1000, max_difference_elevation_meters=50"
] = (46, 15)

snapshots["test_rank_stations_match_climate_zones_not_null match_iecc_climate_zone"] = (
    743,
    15,
)

snapshots[
    "test_rank_stations_match_climate_zones_not_null match_iecc_moisture_regime"
] = (710, 15)

snapshots["test_rank_stations_match_climate_zones_not_null match_ba_climate_zone"] = (
    280,
    15,
)

snapshots["test_rank_stations_match_climate_zones_not_null match_ca_climate_zone"] = (
    10,
    15,
)

snapshots["test_select_station_with_second_level_dates station_id"] = "723895"

snapshots["test_select_station_with_empty_tempC station_id"] = "723896"

snapshots["test_select_station_with_empty_tempC_no_web_fetch station_id"] = "723896"
