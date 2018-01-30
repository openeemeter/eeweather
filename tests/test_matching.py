from eeweather import (
    match_zcta,
    match_lat_long,
)
from eeweather.mappings import (
    zcta_naive_closest_high_quality,
    lat_long_naive_closest,
)
from eeweather.exceptions import (
    UnrecognizedZCTAError,
    UnrecognizedUSAFIDError,
)
import pytest


def test_match_zcta_default_mapping():
    assert match_zcta('96701').isd_station.usaf_id == '911820'  # HI


def test_match_zcta_default_mapping_bad_zcta():
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        match_zcta('00000')
    assert excinfo.value.value == '00000'


def test_match_zcta_custom_dict_mapping():
    mapping = {
        '96701': '722880',  # ok, ok
        '99999': '722880',  # not ok, ok
        '04005': '999999',  # ok, not ok
    }

    # valid zcta in mapping
    result = match_zcta('96701', mapping=mapping)
    assert result.isd_station.usaf_id == '722880'

    # invalid zcta in mapping
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        match_zcta('99999', mapping=mapping)
    assert excinfo.value.value == '99999'

    # valid zcta not in mapping
    result = match_zcta('02138', mapping=mapping)
    assert result.is_empty() is True
    assert result.warnings == [
        'ZCTA ID "02138" was not found in mapping dictionary.'
    ]

    # invalid zcta not in mapping
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        match_zcta('88888', mapping=mapping)
    assert excinfo.value.value == '88888'

    # valid zcta matched to invalid station
    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        match_zcta('04005', mapping=mapping)
    assert excinfo.value.value == '999999'


def test_match_zcta_custom_func_mapping():
    def mapping(zcta):
        if zcta == '96701':
            return '722880'
        elif zcta == '99999':
            # execution will stop before this b/c ZCTA is verified
            raise ValueError()  # pragma: no cover
        elif zcta == '04005':
            return '999999'
        else:
            return None

    # valid zcta in mapping
    result = match_zcta('96701', mapping=mapping)
    assert result.isd_station.usaf_id == '722880'

    # invalid zcta in mapping
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        match_zcta('99999', mapping=mapping)
    assert excinfo.value.value == '99999'

    # valid zcta not in mapping
    result = match_zcta('02138', mapping=mapping)
    assert result.is_empty() is True
    assert result.warnings == [
        'ZCTA ID "02138" was not found in mapping dictionary.'
    ]

    # invalid zcta not in mapping
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        match_zcta('88888', mapping=mapping)
    assert excinfo.value.value == '88888'

    # valid zcta matched to invalid station
    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        match_zcta('04005', mapping=mapping)
    assert excinfo.value.value == '999999'


def test_match_zcta_with_library_mapping():
    result = match_zcta('96701', mapping=zcta_naive_closest_high_quality)
    assert result.isd_station.usaf_id == '911820'


def test_match_zcta_with_bad_mapping():
    with pytest.raises(ValueError):
        match_zcta('96701', mapping='INVALID')


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
