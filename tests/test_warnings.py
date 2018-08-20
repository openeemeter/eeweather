import pytest

from eeweather.utils import EEWeatherWarning

@pytest.fixture
def generic_eeweather_warning():
    return EEWeatherWarning(
        qualified_name='qualified_name',
        description='description',
        data={}
    )

def test_str_repr(generic_eeweather_warning):
    assert str(generic_eeweather_warning) == (
        'EEWeatherWarning(qualified_name=qualified_name)'
    )
    assert generic_eeweather_warning.json() == {
        'qualified_name': 'qualified_name',
        'description': 'description',
        'data': {},
    }
