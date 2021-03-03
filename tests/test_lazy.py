from typing import List

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


def test_filter():
    lazyval = Lazy.of(lambda: 3)

    assert lazyval.filter(lambda x: x >= 0) == Option.some(3)
    assert lazyval.filter(lambda x: x < 0) == Option.nothing()

    assert Lazy.of(lambda: None).filter(lambda x: x is None) == Option.some(None)


def test_filter_not():
    lazyval = Lazy.of(lambda: -3)

    assert lazyval.filter_not(lambda x: x >= 0) == Option.some(-3)
    assert lazyval.filter_not(lambda x: x < 0) == Option.nothing()

    assert Lazy.of(lambda: None).filter_not(lambda x: x is not None) == Option.some(None)


def test_sequence():
    lazies: List[Lazy[int]] = [Lazy.of(lambda: 1), Lazy.of(lambda: 2), Lazy.of(lambda: 3)]
    lazy_seq: Lazy[List[int]] = Lazy.sequence(lazies)

    assert lazies[0].is_computed() is False
    assert lazies[1].is_computed() is False
    assert lazies[2].is_computed() is False
    assert lazy_seq.is_computed() is False

    assert lazy_seq.get() == [1, 2, 3]


def random_digit():
    return random.randint(0, 10)
