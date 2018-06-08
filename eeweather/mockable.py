'''
Usage:

    # module.py
    import mockable

    @mockable.mockable
    def expensive_function():
        pass

    def function_a():
        mockable.expensive_function()


    # test_module.py
    import pytest

    @pytest.fixture
    def mock_expensive_function(monkeypatch):
        def cheap_func():
            pass
        monkeypatch.setattr(
            'mockable.expensive_function',
            cheap_func
        )

    def test_function_a(mock_expensive_function):
        function_a()

'''

import sys


def mockable():
    def decorator(func):
        setattr(sys.modules[__name__], func.__name__, func)
        return func
    return decorator
