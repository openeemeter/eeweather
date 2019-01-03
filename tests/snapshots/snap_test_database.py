# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_isd_station_metadata_table_count count"] = 3874

snapshots["test_isd_file_metadata_table_count count"] = 29668

snapshots["test_isd_station_metadata_table_content data"] = {
    "ba_climate_zone": "Very Cold",
    "ca_climate_zone": None,
    "elevation": "+0031.4",
    "icao_code": "PATO",
    "iecc_climate_zone": "7",
    "iecc_moisture_regime": None,
    "latitude": "+60.785",
    "longitude": "-148.839",
    "name": "PORTAGE GLACIER",
    "quality": "high",
    "recent_wban_id": "26492",
    "state": "AK",
    "usaf_id": "700001",
    "wban_ids": "26492,99999",
}

snapshots["test_isd_file_metadata_table_content data"] = {
    "usaf_id": "690090",
    "wban_id": "99999",
    "year": "2008",
}
