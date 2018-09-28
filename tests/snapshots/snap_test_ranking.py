# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_rank_stations_no_filter df.shape"] = (3890, 15)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_climate_zone"] = (
    501,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_iecc_moisture_regime"] = (
    940,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_ba_climate_zone"] = (
    506,
    15,
)

snapshots["test_rank_stations_match_climate_zones_null match_ca_climate_zone"] = (
    3653,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=False"] = (
    3890,
    15,
)

snapshots["test_rank_stations_match_state site_state=CA, match_state=True"] = (311, 15)

snapshots["test_rank_stations_match_state site_state=None, match_state=True"] = (73, 15)

snapshots["test_rank_stations_is_tmy3 is_tmy3=True"] = (1019, 15)

snapshots["test_rank_stations_is_tmy3 is_tmy3=False"] = (2871, 15)

snapshots["test_rank_stations_is_cz2010 is_cz2010=True"] = (86, 15)

snapshots["test_rank_stations_is_cz2010 is_cz2010=False"] = (3804, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=low"] = (3890, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=medium"] = (1743, 15)

snapshots["test_rank_stations_minimum_quality minimum_quality=high"] = (1632, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=III"] = (1019, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=II"] = (857, 15)

snapshots["test_rank_stations_minimum_tmy3_class minimum_tmy3_class=I"] = (222, 15)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=200000"] = (
    54,
    15,
)

snapshots["test_rank_stations_max_distance_meters max_distance_meters=50000"] = (5, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters max_difference_elevation_meters=200"
] = (3890, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=200"
] = (2199, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=0, max_difference_elevation_meters=50"
] = (1375, 15)

snapshots[
    "test_rank_stations_max_difference_elevation_meters site_elevation=1000, max_difference_elevation_meters=50"
] = (47, 15)

snapshots["test_rank_stations_match_climate_zones_not_null match_iecc_climate_zone"] = (
    748,
    15,
)

snapshots[
    "test_rank_stations_match_climate_zones_not_null match_iecc_moisture_regime"
] = (711, 15)

snapshots["test_rank_stations_match_climate_zones_not_null match_ba_climate_zone"] = (
    281,
    15,
)

snapshots["test_rank_stations_match_climate_zones_not_null match_ca_climate_zone"] = (
    10,
    15,
)
