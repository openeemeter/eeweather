# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_isd_file_metadata_table_content data"] = {
    "usaf_id": "690150",
    "wban_id": "93121",
    "year": "2006",
}

snapshots["test_isd_file_metadata_table_count count"] = 44816

snapshots["test_isd_station_metadata_table_content data"] = {
    "ba_climate_zone": "Very Cold",
    "ca_climate_zone": None,
    "elevation": "+0032.5",
    "icao_code": "PATO",
    "iecc_climate_zone": "7",
    "iecc_moisture_regime": None,
    "latitude": "+60.784",
    "longitude": "-148.848",
    "name": "PORTAGE GLACIER",
    "quality": "high",
    "recent_wban_id": "26492",
    "state": "AK",
    "usaf_id": "700001",
    "wban_ids": "26492,99999",
}

snapshots["test_isd_station_metadata_table_count count"] = 4821
