from eeweather.validation import (
    valid_zcta_or_raise,
    valid_usaf_id_or_raise,
)
from eeweather.exceptions import (
    UnrecognizedZCTAError,
    UnrecognizedUSAFIDError,
)
import pytest


def test_valid_zcta_or_raise_valid():
    assert valid_zcta_or_raise('90210') is True


def test_valid_zcta_or_raise_raise_error():
    with pytest.raises(UnrecognizedZCTAError) as excinfo:
        valid_zcta_or_raise('INVALID')
    assert excinfo.value.value == 'INVALID'


def test_valid_usaf_id_or_raise_valid():
    assert valid_usaf_id_or_raise('722880') is True


def test_valid_usaf_id_or_raise_raise_error():
    with pytest.raises(UnrecognizedUSAFIDError) as excinfo:
        valid_usaf_id_or_raise('INVALID')
    assert excinfo.value.value == 'INVALID'
