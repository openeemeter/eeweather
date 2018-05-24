from . import mappings
from .connections import metadata_db_connection_proxy

from six import string_types


def match_lat_long(latitude, longitude, mapping=None):
    ''' Match a target lat long to an ISD station.

    .. note::

        For CalTRACK compliance (2.4.1), the default mapping
        must be used (mappings.oee_lat_long).

    Uses eeweather.mapping.oee_lat_long by default.
    Accepts callable as mapping.

    For example::

        mapping = lambda lat, long: '123456'
        eeweather.match_lat_long(latitude, longitude, mapping=mapping)

        mapping = eeweather.mappings.lat_long_closest_within_climate_zone
        eeweather.match_lat_long(latitude, longitude, mapping=mapping)

    Parameters
    ----------
    latitude : float
        Target longitude.
    longitude : float
        Target latitude.
    mapping : callable
        Mapping function to use during mapping.

    Returns
    -------
    mapping_result : eeweather.mappings.ISDStationMapping or eeweather.mappings.EmptyMapping
    '''
    if mapping is None:
        mapping = mappings.oee_lat_long

    result = mapping(latitude, longitude)

    # if passed function returns mapping directly, return it, otherwise convert
    if isinstance(result, mappings.MappingResult):
        return result
    else:
        return mappings.ISDStationMapping(result, latitude, longitude)
