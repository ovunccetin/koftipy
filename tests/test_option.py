import pytest

from koftipy import *


def test_of():
    assert Option.of(None) is Nothing
    assert Option.of('') == Some('')
    assert Option.of(0) == Some(0)
    assert Option.of(0.0) == Some(0.0)
    assert Option.of(False) == Some(False)
    assert Option.of([]) == Some([])
    assert Option.of({}) == Some({})
    assert Option.of(set()) == Some(set())


def test_of_truthy():
    assert Option.of_truthy(None) is Nothing
    assert Option.of_truthy('') is Nothing
    assert Option.of_truthy(0) is Nothing
    assert Option.of_truthy(0.0) is Nothing
    assert Option.of_truthy(False) is Nothing
    assert Option.of_truthy([]) is Nothing
    assert Option.of_truthy({}) is Nothing
    assert Option.of_truthy(set()) is Nothing

    assert Option.of_truthy(' ') == Some(' ')
    assert Option.of_truthy(1) == Some(1)
    assert Option.of_truthy(0.1) == Some(0.1)
    assert Option.of_truthy(True) == Some(True)
    assert Option.of_truthy([1]) == Some([1])
    assert Option.of_truthy({'a': 1}) == Some({'a': 1})
    assert Option.of_truthy({1}) == Some({1})


def test_when():
    assert Option.when(True, value=None) == Some(None)
    assert Option.when(True, value=1000) == Some(1000)
    assert Option.when(True, value=lambda: 1000) == Some(1000)
    assert Option.when(False, value=1000) == Nothing


def test_sequence():
    assert Option.sequence([]) == Some([])
    assert Option.sequence([Some(1), Some(2), Some(3)]) == Some([1, 2, 3])
    assert Option.sequence([Some(1), Nothing, Some(3)]) is Nothing


def test_get():
    assert Some(1).get() == 1
    with pytest.raises(ValueError):
        Nothing.get()


def test_get_or_else():
    assert Some(1).get_or_else(2) == 1
    assert Some(1).get_or_else(lambda: 2) == 1

    assert Nothing.get_or_else(2) == 2
    assert Nothing.get_or_else(lambda: 2) == 2


def test_get_or_none():
    assert Some(1).or_none() == 1
    assert Nothing.or_none() is None


def test_or_else():
    assert Some(1).or_else(Some(2)) == Some(1)
    assert Some(1).or_else(lambda: Some(2)) == Some(1)

    assert Nothing.or_else(Some(2)) == Some(2)
    assert Nothing.or_else(2) == Some(2)

    assert Nothing.or_else(lambda: Some(2)) == Some(2)
    assert Nothing.or_else(lambda: 2) == Some(2)


def test_is_defined_or_empty():
    assert Some(1).is_defined() is True
    assert Some(1).is_empty() is False
    assert Nothing.is_defined() is False
    assert Nothing.is_empty() is True


def test_iteration():
    assert iter(Some(1)).__next__() == 1
    with pytest.raises(StopIteration):
        assert iter(Nothing).__next__()


def test_map():
    assert Some(3).map(lambda x: x ** 2) == Some(9)
    assert Nothing.map(lambda x: x ** 2) == Nothing

    with pytest.raises(ZeroDivisionError):
        Some(3).map(lambda x: x / 0)


def test_flat_map():
    assert Some(3).flat_map(lambda x: Some(x ** 2)) == Some(9)
    assert Nothing.flat_map(lambda x: Some(x ** 2)) == Nothing

    with pytest.raises(ZeroDivisionError):
        Some(3).flat_map(lambda x: Some(x / 0))


def test_flatten():
    assert Some(1).flatten() == Some(1)
    assert Nothing.flatten() == Nothing
    assert Some(Some(1)).flatten() == Some(1)
    assert Some(Some(Some(1))).flatten() == Some(1)
    assert Some(Some(Some(Nothing))).flatten() == Nothing


def test_filter():
    assert Some(3).filter(lambda x: x > 0) == Some(3)
    assert Some(3).filter(lambda x: x < 0) == Nothing
    assert Some(3).filter(instance_of(int)) == Some(3)
    assert Nothing.filter(lambda x: True) == Nothing


def test_filter_not():
    assert Some(3).filter_not(lambda x: x <= 0) == Some(3)
    assert Some(3).filter_not(lambda x: x > 0) == Nothing
    assert Nothing.filter_not(lambda x: False) == Nothing


def test_contains():
    assert Some(3).contains(3) is True
    assert Some(3).contains(1) is False
    assert Nothing.contains(1) is False


def test_exists():
    assert Some(3).exists(lambda x: x > 0) is True
    assert Some(3).exists(lambda x: x < 0) is False
    assert Nothing.exists(lambda x: True) is False


def test_if_defined():
    result = []

    Some(3).if_defined(result.append)
    Some(5).if_defined(result.append)
    Nothing.if_defined(result.append)

    assert result == [3, 5]


def test_if_empty():
    result = []

    Some(3).if_empty(lambda: result.append(3))
    Nothing.if_empty(lambda: result.append('e'))

    assert result == ['e']


def test_fold():
    assert Option.some(1).fold(
        if_empty=lambda: 0,
        if_defined=lambda x: x + 1
    ) == 2

    assert Option.nothing().fold(
        if_empty=lambda: 0,
        if_defined=lambda x: x + 1
    ) == 0


def test_string_representation():
    assert str(Nothing) == 'Nothing'
    assert str(Some(1)) == 'Some(1)'
    assert str(Some('test')) == "Some('test')"
    assert str(Some({'a': 1})) == "Some({'a': 1})"
    assert str(Some([1, 'a', 0.1])) == "Some([1, 'a', 0.1])"
