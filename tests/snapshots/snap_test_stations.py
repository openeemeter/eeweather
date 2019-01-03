# -*- coding: utf-8 -*-
# snapshottest: v1 - https://goo.gl/zC4yUc
from __future__ import unicode_literals

from snapshottest import Snapshot


snapshots = Snapshot()

snapshots["test_get_isd_filenames_single_year filenames"] = [
    "/pub/data/noaa/2007/722860-23119-2007.gz"
]

snapshots["test_get_isd_filenames_multiple_year filenames"] = [
    "/pub/data/noaa/2006/722860-23119-2006.gz",
    "/pub/data/noaa/2007/722860-23119-2007.gz",
    "/pub/data/noaa/2008/722860-23119-2008.gz",
    "/pub/data/noaa/2009/722860-23119-2009.gz",
    "/pub/data/noaa/2010/722860-23119-2010.gz",
    "/pub/data/noaa/2011/722860-23119-2011.gz",
    "/pub/data/noaa/2012/722860-23119-2012.gz",
    "/pub/data/noaa/2013/722860-23119-2013.gz",
    "/pub/data/noaa/2014/722860-23119-2014.gz",
    "/pub/data/noaa/2015/722860-23119-2015.gz",
    "/pub/data/noaa/2016/722860-23119-2016.gz",
    "/pub/data/noaa/2017/722860-23119-2017.gz",
    "/pub/data/noaa/2018/722860-23119-2018.gz",
]

snapshots["test_isd_station_get_isd_filenames filenames"] = [
    "/pub/data/noaa/2006/722860-23119-2006.gz",
    "/pub/data/noaa/2007/722860-23119-2007.gz",
    "/pub/data/noaa/2008/722860-23119-2008.gz",
    "/pub/data/noaa/2009/722860-23119-2009.gz",
    "/pub/data/noaa/2010/722860-23119-2010.gz",
    "/pub/data/noaa/2011/722860-23119-2011.gz",
    "/pub/data/noaa/2012/722860-23119-2012.gz",
    "/pub/data/noaa/2013/722860-23119-2013.gz",
    "/pub/data/noaa/2014/722860-23119-2014.gz",
    "/pub/data/noaa/2015/722860-23119-2015.gz",
    "/pub/data/noaa/2016/722860-23119-2016.gz",
    "/pub/data/noaa/2017/722860-23119-2017.gz",
    "/pub/data/noaa/2018/722860-23119-2018.gz",
]

snapshots["test_isd_station_get_isd_filenames_with_year filenames"] = [
    "/pub/data/noaa/2007/722860-23119-2007.gz"
]

snapshots["test_get_gsod_filenames_single_year filenames"] = [
    "/pub/data/gsod/2007/722860-23119-2007.op.gz"
]

snapshots["test_get_gsod_filenames_multiple_year filenames"] = [
    "/pub/data/gsod/2006/722860-23119-2006.op.gz",
    "/pub/data/gsod/2007/722860-23119-2007.op.gz",
    "/pub/data/gsod/2008/722860-23119-2008.op.gz",
    "/pub/data/gsod/2009/722860-23119-2009.op.gz",
    "/pub/data/gsod/2010/722860-23119-2010.op.gz",
    "/pub/data/gsod/2011/722860-23119-2011.op.gz",
    "/pub/data/gsod/2012/722860-23119-2012.op.gz",
    "/pub/data/gsod/2013/722860-23119-2013.op.gz",
    "/pub/data/gsod/2014/722860-23119-2014.op.gz",
    "/pub/data/gsod/2015/722860-23119-2015.op.gz",
    "/pub/data/gsod/2016/722860-23119-2016.op.gz",
    "/pub/data/gsod/2017/722860-23119-2017.op.gz",
    "/pub/data/gsod/2018/722860-23119-2018.op.gz",
]

snapshots["test_isd_station_get_gsod_filenames filenames"] = [
    "/pub/data/gsod/2006/722860-23119-2006.op.gz",
    "/pub/data/gsod/2007/722860-23119-2007.op.gz",
    "/pub/data/gsod/2008/722860-23119-2008.op.gz",
    "/pub/data/gsod/2009/722860-23119-2009.op.gz",
    "/pub/data/gsod/2010/722860-23119-2010.op.gz",
    "/pub/data/gsod/2011/722860-23119-2011.op.gz",
    "/pub/data/gsod/2012/722860-23119-2012.op.gz",
    "/pub/data/gsod/2013/722860-23119-2013.op.gz",
    "/pub/data/gsod/2014/722860-23119-2014.op.gz",
    "/pub/data/gsod/2015/722860-23119-2015.op.gz",
    "/pub/data/gsod/2016/722860-23119-2016.op.gz",
    "/pub/data/gsod/2017/722860-23119-2017.op.gz",
    "/pub/data/gsod/2018/722860-23119-2018.op.gz",
]

snapshots["test_isd_station_get_gsod_filenames_with_year filenames"] = [
    "/pub/data/gsod/2007/722860-23119-2007.op.gz"
]
