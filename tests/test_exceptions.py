import pytest

from eeweather import (
    EEWeatherError,
    UnrecognizedUSAFIDError,
    UnrecognizedZCTAError,
    ISDDataNotAvailableError,
    GSODDataNotAvailableError,
)


def test_eeweather_error():
    with pytest.raises(EEWeatherError) as excinfo:
        raise EEWeatherError('message')
    assert excinfo.value.args[0] == 'message'


def test_unrecognized_usaf_id_error():
    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        raise UnrecognizedUSAFIDError('INVALID')
    assert excinfo.value.value == 'INVALID'
    assert excinfo.value.message == (
        'The value "INVALID" was not recognized as a'
        ' valid USAF weather station identifier.'
    )


def test_unrecognized_zcta_error():
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        raise UnrecognizedZCTAError('INVALID')
    assert excinfo.value.value == 'INVALID'
    assert excinfo.value.message == (
        'The value "INVALID" was not recognized as a valid ZCTA identifier.'
    )


def test_isd_data_does_not_exist_error():
    with pytest.raises(ISDDataNotAvailableError) as excinfo:
        raise ISDDataNotAvailableError('123456', 1800)
    assert excinfo.value.usaf_id == '123456'
    assert excinfo.value.year == 1800
    assert excinfo.value.message == (
        'ISD data does not exist for station "123456" in year 1800.'
    )


def test_gsod_data_does_not_exist_error():
    with pytest.raises(GSODDataNotAvailableError) as excinfo:
        raise GSODDataNotAvailableError('123456', 1800)
    assert excinfo.value.usaf_id == '123456'
    assert excinfo.value.year == 1800
    assert excinfo.value.message == (
        'GSOD data does not exist for station "123456" in year 1800.'
    )
