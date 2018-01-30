class EEWeatherError(Exception):
    '''Base class for exceptions in the eeweather package.'''
    pass


class UnrecognizedUSAFIDError(EEWeatherError):
    ''' Raised when an unrecognized USAF station id is encountered.

    Attributes
    ----------
    value : str
        the value which is not a valid USAF ID
    message : str
        a message describing the error
    '''

    def __init__(self, value):
        self.value = value
        self.message = (
            'The value "{}" was not recognized as a valid USAF weather station'
            ' identifier.'
            .format(value)
        )


class UnrecognizedZCTAError(EEWeatherError):
    ''' Raised when an unrecognized ZCTA is encountered.

    Attributes
    ----------
    value : str
        the value which is not a valid ZCTA
    message : str
        a message describing the error
    '''

    def __init__(self, value):
        self.value = value
        self.message = (
            'The value "{}" was not recognized as a valid ZCTA identifier.'
            .format(value)
        )


class ISDDataNotAvailableError(EEWeatherError):
    ''' Raised when ISD data is not available for a particular station and year.

    Attributes
    ----------
    usaf_id : str
        the USAF ID for which ISD data does not exist.
    year : int
        the year for which ISD data does not exist.
    message : str
        a message describing the error
    '''

    def __init__(self, usaf_id, year):
        self.usaf_id = usaf_id
        self.year = year
        self.message = (
            'ISD data does not exist for station "{}" in year {}.'
            .format(usaf_id, year)
        )


class GSODDataNotAvailableError(EEWeatherError):
    ''' Raised when GSOD data is not available for a particular station and year.

    Attributes
    ----------
        usaf_id -- The USAF ID for which GSOD data does not exist.
        year -- The year for which GSOD data does not exist.
    '''

    def __init__(self, usaf_id, year):
        self.usaf_id = usaf_id
        self.year = year
        self.message = (
            'GSOD data does not exist for station "{}" in year {}.'
            .format(usaf_id, year)
        )
