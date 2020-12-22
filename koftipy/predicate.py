from __future__ import annotations

from typing import Any, TypeVar, Generic, Type, Union, Tuple, Callable, Iterable

__all__ = [
    'Predicate', 'ResultPredicate', 'ErrorPredicate', 'Predicates',
    'always', 'never', 'all_of', 'any_of', 'equal_to', 'instance_of',
    'not_', 'none_of', 'is_', 'in_', 'for_all', 'for_any'
]

V = TypeVar('V', bound=Any)


class Predicate(Generic[V]):
    @staticmethod
    def of(pred: Union[Predicate[V], Callable[[V], bool]]) -> Predicate[V]:
        if isinstance(pred, Predicate):
            return pred
        else:
            return _Custom(pred)

    def test(self, value: V) -> bool:
        raise NotImplementedError

    def and_(self, other: Predicate[V]) -> Predicate[V]:
        return _And(self, other)

    def or_(self, other: Predicate[V]) -> Predicate[V]:
        return _Or(self, other)

    def negate(self) -> Predicate[V]:
        return _Negate(self)


class _And(Predicate[V]):

    def __init__(self, *predicates: Predicate[V]):
        self.__predicates = predicates

    def test(self, value: V) -> bool:
        for p in self.__predicates:
            if p.test(value) is False:
                return False

        return True


class _Or(Predicate):

    def __init__(self, *predicates: Predicate[V]):
        self.__predicates = predicates

    def test(self, value: V) -> bool:
        for p in self.__predicates:
            if p.test(value) is True:
                return True

        return False


class _Negate(Predicate):
    def __init__(self, other: Predicate[V]):
        self.__other = other

    def test(self, value: V) -> bool:
        return not self.__other.test(value)


class _Always(Predicate[V]):
    def test(self, value: V) -> bool:
        return True


class _Never(Predicate[V]):
    def test(self, value: V) -> bool:
        return False


class _Equals(Predicate[V]):
    def __init__(self, other: V):
        self.__other = other

    def test(self, value: V) -> bool:
        return value == self.__other


class _InstanceOf(Predicate[V]):
    def __init__(self, types: Union[Type, Tuple[Type, ...]]):
        self.__types = types

    def test(self, value: V) -> bool:
        return isinstance(value, self.__types)


class _In(Predicate[V]):
    def __init__(self, coll: Iterable[V]):
        self.__coll = coll

    def test(self, value: V) -> bool:
        return value in self.__coll


class _ForAll(Predicate[Iterable[V]]):
    def __init__(self, pred: Predicate[V]):
        self.__pred = pred

    def test(self, coll: Iterable[V]) -> bool:
        for value in coll:
            if self.__pred.test(value) is False:
                return False

        return True


class _ForAny(Predicate[Iterable[V]]):
    def __init__(self, pred: Predicate[V]):
        self.__pred = pred

    def test(self, coll: Iterable[V]) -> bool:
        for value in coll:
            if self.__pred.test(value) is True:
                return True

        return False


class _Custom(Predicate[V]):

    def __init__(self, func: Callable[[V], bool]):
        self.__func = func

    def test(self, value: V) -> bool:
        return self.__func(value)


ResultPredicate = Union[Predicate[Any], Callable[[Any], bool]]
ErrorPredicate = Union[Predicate[BaseException], Callable[[BaseException], bool]]


class Predicates:
    @staticmethod
    def always() -> Predicate[V]:
        return _Always()

    @staticmethod
    def never() -> Predicate[V]:
        return _Never()

    @staticmethod
    def all_of(first: Predicate[V], *others: Predicate[V]) -> Predicate[V]:
        return _And(first, *others)

    @staticmethod
    def any_of(first: Predicate[V], *others: Predicate[V]) -> Predicate[V]:
        return _Or(first, *others)

    @staticmethod
    def none_of(first: Predicate[V], *others: Predicate[V]) -> Predicate[V]:
        return Predicates.not_(Predicates.any_of(first, *others))

    @staticmethod
    def not_(other: Predicate[V]) -> Predicate[V]:
        return _Negate(other)

    @staticmethod
    def equal_to(value: V) -> Predicate[V]:
        return _Equals(value)

    @staticmethod
    def is_(value: V) -> Predicate[V]:
        return Predicates.equal_to(value)

    @staticmethod
    def instance_of(*types: Type) -> Predicate[V]:
        return _InstanceOf(types)

    @staticmethod
    def in_(coll: Iterable[V]) -> Predicate[V]:
        return _In(coll)

    @staticmethod
    def for_all(pred: Predicate[V]) -> Predicate[Iterable[V]]:
        return _ForAll(pred)

    @staticmethod
    def for_any(pred: Predicate[V]) -> Predicate[Iterable[V]]:
        return _ForAny(pred)


always = Predicates.always
never = Predicates.never
all_of = Predicates.all_of
any_of = Predicates.any_of
none_of = Predicates.none_of
not_ = Predicates.not_
equal_to = Predicates.equal_to
is_ = Predicates.equal_to
instance_of = Predicates.instance_of
in_ = Predicates.in_
for_all = Predicates.for_all
for_any = Predicates.for_any
