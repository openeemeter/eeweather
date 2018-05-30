import pytest

from eeweather.api import zcta_to_lat_long
from eeweather.exceptions import (
    UnrecognizedUSAFIDError,
    UnrecognizedZCTAError,
)
from eeweather.mappings import (
    ISDStationMapping,
    EmptyMapping,
    lat_long_closest_within_climate_zone,
    lat_long_closest_within_climate_zone_tmy3,
    lat_long_closest_within_climate_zone_cz2010,
    lat_long_naive_closest,
    lat_long_naive_closest_tmy3,
    lat_long_naive_closest_cz2010,
    oee_lat_long,
    oee_lat_long_tmy3,
    oee_lat_long_cz2010,
)


def test_empty_mapping():
    mapping = EmptyMapping()
    assert mapping.warnings == ['No mapping result was found.']
    assert mapping.is_empty() is True
    assert repr(mapping) == "EmptyMapping(warnings=['No mapping result was found.'])"


def test_mapping_result_blank_default_kwargs_200km_away():
    mapping = ISDStationMapping('720446', 40, -110)
    assert mapping.target_latitude == 40
    assert mapping.target_longitude == -110
    assert mapping.target_coords == (40, -110)
    assert mapping.distance_meters == 2132142
    assert mapping.isd_station.usaf_id == '720446'
    assert mapping.warnings == [
        'Distance from target to weather station is greater than 200km.'
    ]
    assert str(mapping) == '720446'
    assert repr(mapping) == "ISDStationMapping('720446', distance_meters=2132142)"
    assert mapping.is_empty() is False


def test_mapping_result_blank_default_kwargs_50km_away():
    mapping = ISDStationMapping('720446', 38, -87)
    assert mapping.target_latitude == 38
    assert mapping.target_longitude == -87
    assert mapping.target_coords == (38, -87)
    assert mapping.distance_meters == 133519
    assert mapping.isd_station.usaf_id == '720446'
    assert mapping.warnings == [
        'Distance from target to weather station is greater than 50km.'
    ]
    assert str(mapping) == '720446'
    assert repr(mapping) == "ISDStationMapping('720446', distance_meters=133519)"
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

def test_lat_long_closest_within_climate_zone_tmy3():
    # Bakersfield
    result = lat_long_closest_within_climate_zone_tmy3(35.68, -119.14)
    assert result.isd_station.usaf_id == '723840'

    # Miami
    result = lat_long_closest_within_climate_zone_tmy3(25.73, -80.3)
    assert result.isd_station.usaf_id == '722020'

    # africa, ignores
    result = lat_long_closest_within_climate_zone_tmy3(0, 0)
    assert result.is_empty() is True


def test_lat_long_closest_within_climate_zone_cz2010():
    # Bakersfield
    result = lat_long_closest_within_climate_zone_cz2010(35.68, -119.14)
    assert result.isd_station.usaf_id == '723840'

    # Miami
    result = lat_long_closest_within_climate_zone_cz2010(25.73, -80.3)
    assert result.is_empty() is True

    # africa, ignores
    result = lat_long_closest_within_climate_zone_cz2010(0, 0)
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
    assert result.isd_station.usaf_id == '997172'

def test_lat_long_naive_closest_tmy3():
    # Bakersfield
    result = lat_long_naive_closest_tmy3(35.68, -119.14)
    assert result.isd_station.usaf_id == '723840'

    # Miami
    result = lat_long_naive_closest_tmy3(25.73, -80.3)
    assert result.isd_station.usaf_id == '722020'

    # africa - obviously outside climate zone.
    result = lat_long_naive_closest_tmy3(0, 0)
    assert result.isd_station.usaf_id == '785430'


def test_lat_long_naive_closest_cz2010():
    # Bakersfield
    result = lat_long_naive_closest_cz2010(35.68, -119.14)
    assert result.isd_station.usaf_id == '723840'

    # Miami
    result = lat_long_naive_closest_cz2010(25.73, -80.3)
    assert result.isd_station.usaf_id == '747188'

    # africa - obviously outside climate zone.
    result = lat_long_naive_closest_cz2010(0, 0)
    assert result.isd_station.usaf_id == '723805'


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
    assert result.isd_station.usaf_id == '997172'

def test_oee_lat_long_tmy3_cz2010():
    # California close to border

    #ISD
    result = oee_lat_long(35.85, -115.72)
    assert result.isd_station.usaf_id == '723860'
    assert result.warnings == [
        'Distance from target to weather station is greater than 50km.',
        'Mapped weather station is not in the same climate zone as the provided lat/long point.'
    ]

    #TMY3
    result = oee_lat_long_tmy3(35.85, -115.72)
    assert result.isd_station.usaf_id == '723860'
    assert result.warnings == [
        'Distance from target to weather station is greater than 50km.',
        'Mapped weather station is not in the same climate zone as the provided lat/long point.'
    ]

    #CZ2010
    result = oee_lat_long_cz2010(35.85, -115.72)
    assert result.isd_station.usaf_id == '723815'
    assert result.warnings == [
        'Distance from target to weather station is greater than 50km.',
        'Mapped weather station is not in the same climate zone as the provided lat/long point.'
    ]

def test_zcta_to_lat_long():

    lat, long = zcta_to_lat_long(92389)
    result = oee_lat_long(lat, long)
    assert result.isd_station.usaf_id == '723870'
    assert result.warnings == [
        'Distance from target to weather station is greater than 50km.',
        'Mapped weather station is not in the same climate zone as the provided lat/long point.'
    ]
