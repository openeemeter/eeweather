from . import mappings
from .connections import metadata_db_connection_proxy
from .validation import valid_zcta_or_raise

from six import string_types


def match_zcta(zcta, mapping=None):
    ''' Match a target ZCTA to ISD Station using the given mapping.

    Uses eeweather.mapping.oee_zcta by default.
    Accepts dict or callable as mapping.

    For example::

        mapping = {'12345': '123456'}
        eeweather.match_zcta(zcta, mapping=mapping)

        mapping = lambda x: '123456' if x == '12345' else None
        eeweather.match_zcta(zcta, mapping=mapping)

        mapping = eeweather.mappings.zcta_closest_within_climate_zone
        eeweather.match_zcta(zcta, mapping=mapping)

    Parameters
    ----------
    zcta : str
        ID of the target ZCTA.
    mapping : dict or callable
        Mapping dict or function to use during mapping.

    Returns
    -------
    mapping_result : eeweather.mappings.ISDStationMapping or eeweather.mappings.EmptyMapping
    '''
    if mapping is None:
        mapping_func = mappings.oee_zcta
    else:
        mapping_func = _zcta_mapping_factory(mapping)
    return mapping_func(zcta)


def match_lat_long(latitude, longitude, mapping=None):
    ''' Match a target lat long to an ISD station.

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


def _get_zcta_lat_long(zcta):
    conn = metadata_db_connection_proxy.get_connection()
    cur = conn.cursor()
    cur.execute('''
      select
        latitude
        , longitude
      from
        zcta_metadata
      where
        zcta_id = ?
    ''', (zcta,))

    return cur.fetchone()


def _zcta_mapping_factory(mapping):
    '''
    # take a dictionary or function and return a function that returns
    # a mapping result.
    '''
    if isinstance(mapping, dict):
        _get_usaf_id = mapping.get
    elif callable(mapping):
        _get_usaf_id = mapping
    else:
        raise ValueError("Mapping must be a dict or callable.")

    def func(zcta):
        valid_zcta_or_raise(zcta)
        result = _get_usaf_id(zcta)
        if isinstance(result, mappings.MappingResult):
            return result

        warnings = []
        if result is None:
            warnings.append(
                'ZCTA ID "{}" was not found in mapping dictionary.'
                .format(zcta)
            )
            return mappings.EmptyMapping(warnings=warnings)

        target_latitude, target_longitude = _get_zcta_lat_long(zcta)

        return mappings.ISDStationMapping(
            result, target_latitude, target_longitude, warnings=warnings)

    return func
