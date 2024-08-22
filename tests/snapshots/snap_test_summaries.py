# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_get_isd_station_usaf_ids n_usaf_ids"] = 4821

snapshots["test_get_isd_station_usaf_ids_by_state n_usaf_ids"] = 77

snapshots["test_get_zcta_ids n_zcta_ids"] = 33144

snapshots["test_get_zcta_ids_by_state n_zcta_ids"] = 1763
