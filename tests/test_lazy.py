from koftipy import *
import random


def test_get():
    lazyval = Lazy.of(random_digit)

    computed_value = lazyval.get()

    assert lazyval.get() == computed_value
    assert lazyval.get() == computed_value
    assert lazyval.get() == computed_value

    # __call__ == get
    assert lazyval() == computed_value


def test_is_computed():
    lazyval = Lazy.of(random_digit)

    assert lazyval.is_computed() is False
    lazyval.get()
    assert lazyval.is_computed() is True


def test_map():
    lazyval = Lazy.of(lambda: 3)

    lazyval = lazyval.map(lambda x: x + 7)
    assert lazyval.is_computed() is False
    assert lazyval == Lazy.of(lambda: 10)

    lazyval = lazyval.map(lambda x: str(x))
    assert lazyval.is_computed() is False
    assert lazyval == Lazy.of(lambda: '10')


def random_digit():
    return random.randint(0, 10)
