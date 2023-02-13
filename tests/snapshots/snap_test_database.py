# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_isd_station_metadata_table_count count"] = 4921

snapshots["test_isd_file_metadata_table_count count"] = 43141

snapshots["test_isd_station_metadata_table_content data"] = {
    "ba_climate_zone": "Hot-Dry",
    "ca_climate_zone": "CA_14",
    "elevation": "+0625.1",
    "icao_code": "KNXP",
    "iecc_climate_zone": "3",
    "iecc_moisture_regime": "B",
    "latitude": "+34.300",
    "longitude": "-116.167",
    "name": "TWENTY NINE PALMS",
    "quality": "high",
    "recent_wban_id": "93121",
    "state": "CA",
    "usaf_id": "690150",
    "wban_ids": "93121,99999",
}

snapshots["test_isd_file_metadata_table_content data"] = {
    "usaf_id": "690090",
    "wban_id": "99999",
    "year": "2008",
}
