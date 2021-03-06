from koftipy import *


def test_empty():
    iterator = Iterator.empty()
    assert no_more_iterations(iterator)


def test_of():
    # single element
    iterator = Iterator.of(1)
    assert next(iterator) == 1
    assert no_more_iterations(iterator)

    # multiple elements
    iterator = Iterator.of(1, 2, 3)
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert next(iterator) == 3
    assert no_more_iterations(iterator)


def test_from_iterable():
    # from list
    iterator = Iterator.from_iterable([1, 2])
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert no_more_iterations(iterator)

    # from tuple
    iterator = Iterator.from_iterable((1, 2))
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert no_more_iterations(iterator)

    # from set
    iterator = Iterator.from_iterable({1, 2})
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert no_more_iterations(iterator)

    # from dict
    iterator = Iterator.from_iterable({'a': 1, 'b': 2})
    assert next(iterator) == 'a', 1
    assert next(iterator) == 'b', 2
    assert no_more_iterations(iterator)

    # from py-iterator
    iterator = Iterator.from_iterable(iter([1, 2]))
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert no_more_iterations(iterator)

    # from iterator
    iterator = Iterator.from_iterable(Iterator.of(1, 2))
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert no_more_iterations(iterator)


def test_concat():
    # concat no iterators
    iterator = Iterator.concat()
    assert no_more_iterations(iterator)

    # concat single iterator
    iterator = Iterator.concat(Iterator.of(1))
    assert next(iterator) == 1
    assert no_more_iterations(iterator)

    # concat multiple iterators
    iterator = Iterator.concat([1, 2], Iterator.of(3, 4), Iterator.empty(), Iterator.of(5))
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert next(iterator) == 3
    assert next(iterator) == 4
    assert next(iterator) == 5
    assert no_more_iterations(iterator)


def test_continually():
    iterator_1 = Iterator.continually('a')
    iterator_2 = Iterator.continually(lambda: 'a')

    for _ in range(100):
        assert next(iterator_1) == 'a'
        assert next(iterator_2) == 'a'

    for _ in range(100):
        assert has_more_iterations(iterator_1)
        assert has_more_iterations(iterator_2)


def test_repeatedly():
    empty = Iterator.repeatedly('a', n=0)
    assert no_more_iterations(empty)

    iterator_1 = Iterator.repeatedly('a', n=3)
    iterator_2 = Iterator.repeatedly(lambda: 'a', n=3)

    for _ in range(3):
        assert next(iterator_1) == 'a'
        assert next(iterator_2) == 'a'

    assert no_more_iterations(iterator_1)
    assert no_more_iterations(iterator_2)


def test_iterate_until_none():
    iterator = Iterator.iterate_until_none(lambda: None)
    assert no_more_iterations(iterator)

    supplier = iter([1, 2, None, 3]).__next__
    iterator = Iterator.iterate_until_none(supplier)
    assert next(iterator) == 1
    assert next(iterator) == 2
    assert no_more_iterations(iterator)


def test_produce():
    iterator = Iterator.produce(0, lambda x: x + 1)

    for i in range(100):
        assert next(iterator) == i


def no_more_iterations(it: Iterator) -> bool:
    try:
        next(it)
        return False
    except StopIteration:
        return True


def has_more_iterations(it: Iterator) -> bool:
    return not no_more_iterations(it)
