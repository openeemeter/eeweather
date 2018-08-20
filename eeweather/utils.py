class lazy_property(object):
    '''
    Meant to be used for lazy evaluation of an object attribute.
    Property should represent non-mutable data, as it replaces itself.

    e.g.,

    class Test(object):

        @lazy_property
        def results(self):
            calcs = 1  # Do a lot of calculation here
            return calcs

    from https://stackoverflow.com/a/6849299/1965736
    '''

    def __init__(self, fget):
        self.fget = fget
        self.func_name = fget.__name__

    def __get__(self, obj, cls):
        value = self.fget(obj)
        setattr(obj, self.func_name, value)
        return value


class EEWeatherWarning(object):
    ''' An object representing a warning and data associated with it.

    Attributes
    ----------
    qualified_name : :any:`str`
        Qualified name, e.g., `'eeweather.method_abc.missing_data'`.
    description : :any:`str`
        Prose describing the nature of the warning.
    data : :any:`dict`
        Data that reproducibly shows why the warning was issued.
    '''

    def __init__(self, qualified_name, description, data):
        self.qualified_name = qualified_name
        self.description = description
        self.data = data

    def __repr__(self):
        return 'EEWeatherWarning(qualified_name={})'.format(self.qualified_name)

    def json(self):
        ''' Return a JSON-serializable representation of this result.

        The output of this function can be converted to a serialized string
        with :any:`json.dumps`.
        '''
        return {
            'qualified_name': self.qualified_name,
            'description': self.description,
            'data': self.data,
        }
