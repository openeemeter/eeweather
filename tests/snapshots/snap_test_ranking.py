# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_rank_stations_is_cz2010 is_cz2010=False"] = (4735, 15)

snapshots["test_rank_stations_is_cz2010 is_cz2010=True"] = (86, 15)

snapshots["test_rank_stations_is_tmy3 is_tmy3=False"] = (3802, 15)

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
    742,
    15,
)

snapshots[
    "test_rank_stations_match_climate_zones_not_null match_iecc_moisture_regime"
] = (714, 15)

snapshots["test_rank_stations_match_climate_zones_null match_ba_climate_zone"] = (
    1478,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_ca_climate_zone"] = (
    4589,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_climate_zone"] = (
    1475,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_moisture_regime"] = (
    1906,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=False"] = (
    4821,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=True"] = (297, 15)

snapshots["test_rank_stations_match_state site_state=None, match_state=True"] = (
    1117,
    15,
)

snapshots[
    "test_rank_stations_max_difference_elevation_meters max_difference_elevation_meters=200"
] = (4821, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=200"
] = (2745, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=50"
] = (1651, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=1000, max_difference_elevation_meters=50"
] = (51, 15)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=200000"] = (
    49,
    15,
)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=50000"] = (5, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=high"] = (1627, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=low"] = (4821, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=medium"] = (1740, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=I"] = (222, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=II"] = (857, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=III"] = (1019, 15)

snapshots["test_rank_stations_no_filter df.shape"] = (4821, 15)

snapshots["test_select_station_with_empty_tempC station_id"] = "747020"

snapshots["test_select_station_with_second_level_dates station_id"] = "747020"
