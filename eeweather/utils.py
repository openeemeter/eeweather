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
