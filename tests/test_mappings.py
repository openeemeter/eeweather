import pytest

from eeweather.exceptions import (
    UnrecognizedUSAFIDError,
    UnrecognizedZCTAError,
)
from eeweather.mappings import (
    ISDStationMapping,
    EmptyMapping,
    zcta_closest_within_climate_zone,
    zcta_naive_closest_high_quality,
    zcta_naive_closest_medium_quality,
    lat_long_closest_within_climate_zone,
    lat_long_naive_closest,
    oee_zcta,
    oee_lat_long,
)


def test_empty_mapping():
    mapping = EmptyMapping()
    assert mapping.warnings == ['No mapping result was found.']
    assert mapping.is_empty() is True
    assert repr(mapping) == "EmptyMapping(warnings=['No mapping result was found.'])"


def test_mapping_result_blank_default_kwargs():
    mapping = ISDStationMapping('720446', 40, -110)
    assert mapping.target_latitude == 40
    assert mapping.target_longitude == -110
    assert mapping.target_coords == (40, -110)
    assert mapping.distance_meters == 2132142
    assert mapping.isd_station.usaf_id == '720446'
    assert mapping.warnings == [
        'Distance from target to weather station is greater than 50km.'
    ]
    assert str(mapping) == '720446'
    assert repr(mapping) == "ISDStationMapping('720446')"
    assert mapping.is_empty() is False


def test_mapping_with_kwargs():
    mapping = ISDStationMapping(
        '720446', 40, -110, distance_meters=100, warnings=['a', 'b'])
    assert mapping.target_latitude == 40
    assert mapping.target_longitude == -110
    assert mapping.target_coords == (40, -110)
    assert mapping.distance_meters == 100
    assert mapping.isd_station.usaf_id == '720446'
    assert mapping.warnings == ['a', 'b']


def test_mapping_result_with_unrecognized_usaf_id():
    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        ISDStationMapping('FAKE', 40, -100)
    assert excinfo.value.message == (
        'The value "FAKE" was not recognized as a valid'
        ' USAF weather station identifier.'
    )


def test_zcta_closest_within_climate_zone():
    # different from naive
    result = zcta_closest_within_climate_zone('38348')
    assert result.isd_station.usaf_id == '720447'

    # valid zcta but no cz match
    result = zcta_closest_within_climate_zone('00682')
    assert result.is_empty() is True

    # valid zcta but no matches at all
    result = zcta_closest_within_climate_zone('33034')
    assert result.is_empty() is True

    # invalid zcta
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        zcta_closest_within_climate_zone('00000')
    excinfo.value.value == '00000'


def test_zcta_naive_closest_high_quality():
    # OK
    result = zcta_naive_closest_high_quality('38348')
    assert result.isd_station.usaf_id == '723346'
    assert result.distance_meters == 38745

    # different climate zone
    result = zcta_naive_closest_high_quality('00601')
    assert result.isd_station.usaf_id == '785430'
    assert result.distance_meters == 188200

    # valid zcta but no matches at all
    result = zcta_naive_closest_high_quality('33034')
    assert result.is_empty() is True

    # invalid zcta
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        zcta_naive_closest_high_quality('00000')
    excinfo.value.value == '00000'


def test_zcta_naive_closest_medium_quality():
    # OK
    result = zcta_naive_closest_medium_quality('95543')
    assert result.isd_station.usaf_id == '994012'
    assert result.distance_meters == 30119

    # different climate zone
    result = zcta_naive_closest_medium_quality('00601')
    assert result.isd_station.usaf_id == '785140'
    assert result.distance_meters == 53150

    # valid zcta but no matches at all
    result = zcta_naive_closest_medium_quality('33034')
    assert result.is_empty() is True

    # invalid zcta
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        zcta_naive_closest_medium_quality('00000')
    excinfo.value.value == '00000'


def test_oee_zcta():
    # close match within climate zone
    result = oee_zcta('55390')
    assert result.isd_station.usaf_id == '722114'
    assert result.distance_meters == 14966
    assert result.warnings == []

    # prefer climate zone match
    result = oee_zcta('38348')
    assert result.isd_station.usaf_id == '720447'
    assert result.distance_meters == 91915
    assert result.warnings == [
        'Distance from target to weather station is greater than 50km.'
    ]

    # valid no climate zone match
    result = oee_zcta('00601')
    assert result.isd_station.usaf_id == '785430'
    assert result.distance_meters == 188200
    assert result.warnings == [
        'Distance from target to weather station is greater than 50km.',
        'Mapped weather station is not in the same climate zone as the centroid of '
        'the provided ZCTA.'
    ]

    # valid zcta has no matches at all
    result = oee_zcta('33034')
    assert result.is_empty() is True
    assert result.warnings == [
        'No mapping result was found.',
    ]
    with pytest.raises(AttributeError):
        result.distance_meters

    # invalid zcta
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        oee_zcta('00000')
    excinfo.value.value == '00000'


def test_lat_long_closest_within_climate_zone():
    # Bakersfield
    result = lat_long_closest_within_climate_zone(35.68, -119.14)
    assert result.isd_station.usaf_id == '723840'

    # Miami
    result = lat_long_closest_within_climate_zone(25.73, -80.3)
    assert result.isd_station.usaf_id == '722020'

    # africa, ignores
    result = lat_long_closest_within_climate_zone(0, 0)
    assert result.is_empty() is True


def test_lat_long_naive_closest():
    # Bakersfield
    result = lat_long_naive_closest(35.68, -119.14)
    assert result.isd_station.usaf_id == '723840'

    # Miami
    result = lat_long_naive_closest(25.73, -80.3)
    assert result.isd_station.usaf_id == '722020'

    # africa - obviously outside climate zone.
    result = lat_long_naive_closest(0, 0)
    assert result.isd_station.usaf_id == '785430'


def test_oee_lat_long():
    # Bakersfield
    result = oee_lat_long(35.68, -119.14)
    assert result.isd_station.usaf_id == '723840'
    assert result.warnings == []

    # Miami
    result = oee_lat_long(25.73, -80.3)
    assert result.isd_station.usaf_id == '722020'

    # africa - obviously outside climate zone.
    result = oee_lat_long(0, 0)
    assert result.isd_station.usaf_id == '785430'
