from koftipy.predicate import *


def test_always():
    assert always().test(None) is True
    assert always().test(0) is True
    assert always().test(1) is True
    assert always().test("test") is True
    assert always().test(Exception()) is True


def test_never():
    assert never().test(None) is False
    assert never().test(0) is False
    assert never().test(1) is False
    assert never().test("test") is False
    assert never().test(Exception()) is False


def test_custom_predicate():
    assert Predicate.of(lambda x: x > 0).test(10) is True
    assert Predicate.of(lambda x: x > 0).test(-10) is False


# noinspection PyTypeChecker
def test_equal_to():
    assert equal_to(5).test(5) is True
    assert equal_to(None).test(None) is True
    assert equal_to(True).test(True) is True

    assert equal_to(3).test(5) is False
    assert equal_to(None).test(5) is False
    assert equal_to(5).test(None) is False


def test_instance_of():
    assert instance_of(str).test("") is True
    assert instance_of(str, int, float).test(3.14) is True

    assert instance_of().test("") is False
    assert instance_of(str).test(5) is False
    assert instance_of(str, int, float).test(None) is False


def test_in():
    assert in_([1, 3, 5]).test(5) is True
    assert in_({1, 3, 5}).test(5) is True
    assert in_((1, 3, 5)).test(5) is True
    assert in_(iter([1, 3, 5])).test(5) is True
    assert in_({'a': 1, 'b': 2, 'c': 3}).test('b') is True

    assert in_([1, 3, 5]).test(7) is False
    assert in_({1, 3, 5}).test(7) is False
    assert in_((1, 3, 5)).test(7) is False
    assert in_(iter([1, 3, 5])).test(7) is False
    assert in_({'a': 1, 'b': 2, 'c': 3}).test('d') is False


def test_for_all():
    positive = Predicate.of(lambda x: x > 0)
    assert for_all(positive).test([1, 2, 3]) is True
    assert for_all(positive).test([1, 2, -3]) is False


def test_for_any():
    positive = Predicate.of(lambda x: x > 0)
    assert for_any(positive).test([-1, 2, -3]) is True
    assert for_any(positive).test([-1, -2, -3]) is False


def test_not():
    assert not_(is_(5)).test(3) is True
    assert not_(is_(5)).test(5) is False


def test_all_of():
    assert all_of(is_(5), instance_of(int)).test(5) is True
    assert all_of(is_(5), instance_of(str)).test(5) is False
    assert all_of(is_(3), instance_of(str)).test(5) is False


def test_any_of():
    assert any_of(is_(5), instance_of(int)).test(5) is True
    assert any_of(is_(5), instance_of(str)).test(5) is True
    assert any_of(is_(3), instance_of(str)).test(5) is False


def test_none_of():
    assert none_of(is_(3), instance_of(str)).test(5) is True
    assert none_of(is_(3), instance_of(int)).test(5) is False


def test_and_conjunction():
    assert is_(5).and_(instance_of(int)).test(5) is True
    assert is_(5).and_(instance_of(str)).test(5) is False


def test_or_conjunction():
    assert is_(5).or_(instance_of(str)).test(5) is True
    assert is_(3).or_(instance_of(str)).test(5) is False


def test_negate():
    assert is_(5).negate().test(3) is True
    assert is_(5).negate().test(5) is False
