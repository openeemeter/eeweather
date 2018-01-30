from eeweather.utils import lazy_property


def test_lazy_property():

    class NotLazy(object):

        n_times = 1

        @property
        def tryme(self):
            times = self.n_times
            self.n_times += 1
            return times

    class Lazy(object):

        n_times = 1

        @lazy_property
        def tryme(self):
            times = self.n_times
            self.n_times += 1
            return times

    not_lazy = NotLazy()
    assert not_lazy.tryme == 1
    assert not_lazy.tryme == 2  # called twice

    lazy = Lazy()
    assert lazy.tryme == 1
    assert lazy.tryme == 1  # only called once
