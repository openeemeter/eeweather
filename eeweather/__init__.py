# -*- coding: utf-8 -*-
"""
eeweather library usage
~~~~~~~~~~~~~~~~~~~~~
The eeweather libary pulls weather from public sources to support eemeter
calculations
Basic usage:
   >>> import eeweather
Full documentation is at <https://openee.io>.
:copyright: (c) 2017 by Open Energy Efficiency.
:license: Apache 2.0, see LICENSE for more details.
"""

import logging

from .__version__ import __title__, __description__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__
from .api import (
    get_lat_long_climate_zones,
    get_zcta_metadata,
)
from .database import build_metadata_db
from .exceptions import (
    EEWeatherError,
    UnrecognizedUSAFIDError,
    UnrecognizedZCTAError,
    ISDDataNotAvailableError,
    GSODDataNotAvailableError,
)
from .matching import (
    match_zcta,
    match_lat_long,
)
from .summaries import (
    get_zcta_ids,
)
from .stations import (
    ISDStation,
    get_isd_filenames,
    get_gsod_filenames,
    get_isd_station_metadata,
    get_isd_file_metadata,
    fetch_isd_raw_temp_data,
    fetch_isd_hourly_temp_data,
    fetch_isd_daily_temp_data,
    fetch_gsod_raw_temp_data,
    fetch_gsod_daily_temp_data,
    get_isd_hourly_temp_data_cache_key,
    get_isd_daily_temp_data_cache_key,
    get_gsod_daily_temp_data_cache_key,
    cached_isd_hourly_temp_data_is_expired,
    cached_isd_daily_temp_data_is_expired,
    cached_gsod_daily_temp_data_is_expired,
    validate_isd_hourly_temp_data_cache,
    validate_isd_daily_temp_data_cache,
    validate_gsod_daily_temp_data_cache,
    serialize_isd_hourly_temp_data,
    serialize_isd_daily_temp_data,
    serialize_gsod_daily_temp_data,
    deserialize_isd_hourly_temp_data,
    deserialize_isd_daily_temp_data,
    deserialize_gsod_daily_temp_data,
    read_isd_hourly_temp_data_from_cache,
    read_isd_daily_temp_data_from_cache,
    read_gsod_daily_temp_data_from_cache,
    write_isd_hourly_temp_data_to_cache,
    write_isd_daily_temp_data_to_cache,
    write_gsod_daily_temp_data_to_cache,
    destroy_cached_isd_hourly_temp_data,
    destroy_cached_isd_daily_temp_data,
    destroy_cached_gsod_daily_temp_data,
    load_isd_hourly_temp_data_cached_proxy,
    load_isd_daily_temp_data_cached_proxy,
    load_gsod_daily_temp_data_cached_proxy,
    load_isd_hourly_temp_data,
    load_isd_daily_temp_data,
    load_gsod_daily_temp_data,
    load_cached_isd_hourly_temp_data,
    load_cached_isd_daily_temp_data,
    load_cached_gsod_daily_temp_data,
)
from .mappings import (
    MappingResult,
    EmptyMapping,
    ISDStationMapping,
    zcta_closest_within_climate_zone,
    zcta_naive_closest_high_quality,
    lat_long_naive_closest,
    lat_long_closest_within_climate_zone,
    oee_zcta,
    oee_lat_long,
    plot_mapping_results,
)


def get_version():
    return __version__


# Set default logging handler to avoid "No handler found" warnings.
# will not work below py2.7
# workaround: https://docs.python.org/release/2.6/library/logging.html#configuring-logging-for-a-library
from logging import NullHandler

logging.getLogger(__name__).addHandler(NullHandler())
