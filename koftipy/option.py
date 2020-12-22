from __future__ import annotations
from typing import *
from .iterator import Iterator
from .predicate import Predicate
from ._types import *

T = TypeVar('T')
U = TypeVar('U')
_ctor_key = object()


class Option(Generic[T]):

    def __init__(self, ctor_key: object):
        assert _ctor_key is ctor_key, "Cannot directly instantiate Option! Use constructor methods."

    @staticmethod
    def of(value: T) -> Option[T]:
        """
        Creates an Option of a given value.

        Args:
            value: A value

        Returns:
            Some(value) if value is not None, Nothing otherwise

        Examples:
            assert Option.of(0) == Some(0)
            assert Option.of(1) == Some(1)
            assert Option.of(None) == Nothing
        """
        return Option.some(value) if (value is not None) else Option.nothing()

    @staticmethod
    def of_truthy(value: T) -> Option[T]:
        """
        Creates an Option of a given truthy value.

        Args:
            value: A value which evaluates to True or False

        Returns:
            Some(value) if value evaluates to True, Nothing otherwise.

        Examples:
            assert Option.of(0) == Nothing
            assert Option.of('') == Nothing
            assert Option.of(1) == Some(1)
        """
        return Option.when(bool(value), value)

    @staticmethod
    def some(value: T) -> Option[T]:
        """
        Creates a Some of a given value which can even be None. It is equivalent to `Some(value)`.

        Args:
            value: A value, may be None

        Returns:
            Some(value)

        Examples:
            assert Option.some(1) == Some(1)
            assert Option.some(None) == Some(None)
        """
        return Some(value)

    @staticmethod
    def nothing() -> Option[T]:
        """
        Returns the single instance of Nothing. Just a convenience.

        Returns:
            Nothing
        """
        return Nothing

    @staticmethod
    def when(condition: bool, value: Union[T, Supplier[T]]) -> Option[T]:
        """
        Creates Some(value) (or Some(value()) if value is a supplier function)
        if condition satisfies, Nothing otherwise.

        Args:
            condition: Condition to be satisfied
            value: A given value or a supplier function which may supply None

        Returns:
            Some(value) or Some(value()) if the condition is True, Nothing otherwise.

        Examples:
            assert Option.when(True, 1) == Some(1)
            assert Option.when(True, None) == Some(None)
            assert Option.when(False, 2) == Nothing
        """
        if condition:
            if callable(value):
                value = value()
            return Option.some(value)
        else:
            return Option.nothing()

    def __iter__(self):
        """
        Returns an iterator of this Option.

        Returns:
            An empty iterator if this is empty, a singleton iterator of the value otherwise.

        Examples:
            iter(Some(1))  # A singleton iterator of 1.
            iter(Nothing)  # An empty iterator.
        """
        return Iterator.empty() if self.is_empty() else Iterator.of(self.get())

    def is_defined(self) -> bool:
        """
        Returns if this Option has a value or not.

        Returns:
            True if this is a Some, False otherwise.

        Examples:
            assert Option.some(1).is_defined() is True
            assert Option.some(None).is_defined() is True
            assert Option.nothing().is_defined() is False
        """
        raise NotImplementedError

    def is_empty(self) -> bool:
        """
        Returns if this Option is empty or not.

        Returns:
            True if this is Nothing, False otherwise.

        Examples:
            assert Option.nothing().is_empty() is True
            assert Option.some(1).is_empty() is False
            assert Option.some(None).is_empty() is False
        """
        return not self.is_defined()

    def get(self) -> T:
        """
        Gets the value if this is a Some or raises a `ValueError` if this is Nothing.

        Returns:
            The value of Some(value)

        Raises:
            ValueError: If this is Nothing

        Examples:
            assert Option.some(1).get() == 1
            assert Option.nothing().get()...  # raises a ValueError
        """
        raise NotImplementedError

    def get_or_else(self, default: Union[T, Supplier[T]]) -> T:
        if self.is_defined():
            return self.get()
        elif callable(default):
            return default()
        else:
            return default

    def or_else(self, default: Union[Option[T], Supplier[Union[T, Option[T]]]]) -> Option[T]:
        if self.is_defined():
            return self
        else:
            result = default
            if callable(default):
                result = default()

            if not isinstance(result, Option):
                result = Some(result)

            return result

    def map(self, f: Function[T, U]) -> Option[U]:
        return Nothing if self.is_empty() else Some(f(self.get()))

    def flat_map(self, f: Function[T, Option[U]]) -> Option[U]:
        return Nothing if self.is_empty() else f(self.get())

    def flatten(self) -> Option[T]:
        if self.is_empty():
            return self
        else:
            value = self.get()
            return value.flatten() if isinstance(value, Option) else self

    def filter(self, p: Union[Predicate, PredicateFn]) -> Option[T]:
        p = Predicate.of(p)
        return self if self.is_empty() or p.test(self.get()) else Nothing

    def filter_not(self, p: Union[Predicate, PredicateFn]) -> Option[T]:
        return self.filter(Predicate.of(p).negate())

    def contains(self, value: T) -> bool:
        return self.get() == value if self.is_defined() else False

    def exists(self, p: Union[Predicate, PredicateFn]) -> bool:
        p = Predicate.of(p)
        return p.test(self.get()) if self.is_defined() else False

    def if_defined(self, f: Consumer[T]) -> None:
        if self.is_defined():
            f(self.get())

    def if_empty(self, f: Procedure) -> None:
        if self.is_empty():
            f()

    def fold(self, if_empty: Procedure, if_defined: Function[T, U]) -> U:
        if self.is_empty():
            if_empty()
        else:
            return if_defined(self.get())


class Some(Option[T], Generic[T]):
    def __init__(self, value: T):
        super().__init__(_ctor_key)
        self.__value = value

    def __repr__(self) -> str:
        val = self.__value
        return "Some({})".format(repr(val) if isinstance(val, str) else str(val))

    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, Some):
            return False
        elif self is other:
            return True
        else:
            return self.__value == other.__value

    def __hash__(self) -> int:
        return hash(self.__value)

    def is_defined(self) -> bool:
        return True

    def get(self) -> T:
        return self.__value


class _Nothing(Option[T]):

    def __repr__(self) -> str:
        return 'Nothing'

    def __eq__(self, other: Any) -> bool:
        return other is self

    def __hash__(self) -> int:
        return 1

    def is_defined(self) -> bool:
        return False

    def get(self) -> T:
        raise ValueError("No value defined")


Nothing = _Nothing(_ctor_key)

__all__ = ['Option', 'Some', 'Nothing']
