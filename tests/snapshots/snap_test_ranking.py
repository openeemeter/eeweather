# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_rank_stations_is_cz2010 is_cz2010=False"] = (4832, 15)

snapshots["test_rank_stations_is_cz2010 is_cz2010=True"] = (86, 15)

snapshots["test_rank_stations_is_tmy3 is_tmy3=False"] = (3899, 15)

snapshots["test_rank_stations_is_tmy3 is_tmy3=True"] = (1019, 15)

snapshots["test_rank_stations_match_climate_zones_not_null match_ba_climate_zone"] = (
    282,
    15,
)

snapshots["test_rank_stations_match_climate_zones_not_null match_ca_climate_zone"] = (
    10,
    15,
)

snapshots["test_rank_stations_match_climate_zones_not_null match_iecc_climate_zone"] = (
    746,
    15,
)

snapshots[
    "test_rank_stations_match_climate_zones_not_null match_iecc_moisture_regime"
] = (714, 15)

snapshots["test_rank_stations_match_climate_zones_null match_ba_climate_zone"] = (
    1525,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_ca_climate_zone"] = (
    4684,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_climate_zone"] = (
    1522,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_moisture_regime"] = (
    1958,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=False"] = (
    4918,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=True"] = (303, 15)

snapshots["test_rank_stations_match_state site_state=None, match_state=True"] = (
    1119,
    15,
)

snapshots[
    "test_rank_stations_max_difference_elevation_meters max_difference_elevation_meters=200"
] = (4918, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=200"
] = (2843, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=50"
] = (1740, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=1000, max_difference_elevation_meters=50"
] = (51, 15)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=200000"] = (
    51,
    15,
)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=50000"] = (5, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=high"] = (1649, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=low"] = (4918, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=medium"] = (1777, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=I"] = (222, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=II"] = (857, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=III"] = (1019, 15)

snapshots["test_rank_stations_no_filter df.shape"] = (4918, 15)

snapshots["test_select_station_with_empty_tempC station_id"] = "747020"

snapshots["test_select_station_with_second_level_dates station_id"] = "747020"
