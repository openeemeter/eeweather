from eeweather import (
    match_lat_long,
)
from eeweather.mappings import (
    lat_long_naive_closest,
)
from eeweather.exceptions import (
    UnrecognizedZCTAError,
    UnrecognizedUSAFIDError,
)
import pytest


def test_match_lat_long():
    assert match_lat_long(35.68, -119.14).isd_station.usaf_id == '723840'  # Bakersfield
    assert match_lat_long(25.73, -80.3).isd_station.usaf_id == '722020'  # Miami


def test_match_lat_long_custom_func_mapping():
    def mapping(lat, lng):
        if lat < 30:
            return '722880'
        else:
            return '000000'

    result = match_lat_long(25.68, -119.14, mapping=mapping)
    assert result.isd_station.usaf_id == '722880'

    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        match_lat_long(35.68, -119.14, mapping=mapping)
    assert excinfo.value.value == '000000'


def test_match_lat_long_with_library_mapping():
    result = match_lat_long(35.68, -119.14, mapping=lat_long_naive_closest)
    assert result.isd_station.usaf_id == '723840'
