from __future__ import annotations
from typing import *
from .iterator import Iterator
from .predicate import Predicate
from ._types import *

T = TypeVar('T')
U = TypeVar('U')
_ctor_key = object()


class Option(Generic[T]):
    """
    Represents an optional value which can be defined or empty/undefined. If it is defined, then it is an
    instance of Some class. Otherwise, if it is undefined, then it is Nothing object.
    """

    def __init__(self, ctor_key: object):
        """
        It is internally called by constructor methods. Not for external use.
        """
        assert _ctor_key is ctor_key, "Cannot directly instantiate Option! Use constructor methods."

    @staticmethod
    def of(value: T) -> Option[T]:
        """
        Creates an Option of a given value.

        Args:
            value: A value

        Returns:
            Some(value) if value is not None, Nothing otherwise.

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
        if the condition satisfies, Nothing otherwise.

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
        """
        Returns the value if this is a Some or the default value otherwise, if this is Nothing.

        Args:
            default: An alternative value which can be eagerly or lazily (if supplier) computed

        Returns:
            The value if this is a Some, otherwise the default value.

        Examples:
            assert Option.some(1).get_or_else(2) == 1
            assert Option.nothing().get_or_else(2) == 2
            assert Option.nothing().get_or_else(lambda: 2) == 2
        """
        if self.is_defined():
            return self.get()
        elif callable(default):
            return default()
        else:
            return default

    def or_none(self) -> T:
        """
        Returns the value if this is defined, None if this is empty.
        It is equivalent to `opt.get_or_else(None)`.

        Returns:
            The value of Some(value), or None if this is empty

        Examples:
            assert Option.some(1).or_none() == 1
            assert Option.nothing().or_none() is None
        """
        return self.get() if self.is_defined() else None

    def or_else(self, default: Union[Option[T], Supplier[Union[T, Option[T]]]]) -> Option[T]:
        """
        Returns this Option if this is a Some, otherwise the supplied Option is returned.

        Args:
            default: An alternative Option which can be eagerly or lazily (if supplier) computed

        Returns:
            This Option if this is defined, otherwise return the given alternative.

        Examples:
            assert Option.some(1).or_else(Some(2)) == Some(1)
            assert Option.nothing().or_else(Some(2)) == Some(2)
            assert Option.nothing().or_else(lambda: Some(2)) == Some(2)
        """
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
        """
        Maps the value and returns the mapped value in a new Some if this is defined, otherwise returns Nothing.

        Args:
            f: A mapper function to convert existing value to a another one.

        Returns:
            a new Some with the mapped value if this is defined, otherwise Nothing if this is empty.

        Examples:
            assert Option.of(1).map(lambda x: x + 3) == Some(4)
            assert Nothing.map(lambda x: x + 3) == Nothing
        """
        return Nothing if self.is_empty() else Some(f(self.get()))

    def flat_map(self, f: Function[T, Option[U]]) -> Option[U]:
        """
        Maps the value to a new Option returned by f if this is defined, otherwise returns Nothing.

        Args:
            f: A mapper function to convert existing value to a new Option

        Returns:
            a new Option supplied by f if this is a Some, otherwise Nothing.

        Examples:
            assert Option.of(1).flat_map(lambda x: Some(x + 3)) == Some(4)
            assert Nothing.flat_map(lambda x: Some(x + 3)) == Nothing
        """
        return Nothing if self.is_empty() else f(self.get())

    def flatten(self) -> Option[T]:
        """
        Flatten this Option if it is nested.

        Returns:
            a flat Option

        Examples:
            assert Some(Some(Some(1))).flatten() == Some(1)
        """
        if self.is_empty():
            return self
        else:
            value = self.get()
            return value.flatten() if isinstance(value, Option) else self

    def filter(self, p: Union[Predicate, PredicateFn[T]]) -> Option[T]:
        """
        Returns this Option if it is defined and the value satisfies the given predicate.
        Otherwise, Nothing is returned.

        Args:
            p: A predicate to test the value. This can be function f: (T) => bool or a koftipy.Predicate.

        Returns:
            This Option if it is defined and its value satisfies p, otherwise Nothing.

        Examples:
            assert Option.of(1).filter(lambda x: x > 0) == Some(1)
            assert Option.of(-1).filter(lambda x: x > 0) == Nothing
            assert Nothing.filter(lambda x: x > 0) == Nothing
        """
        p = Predicate.of(p)
        return self if self.is_defined() and p.test(self.get()) else Nothing

    def filter_not(self, p: Union[Predicate, PredicateFn[T]]) -> Option[T]:
        """
        Returns this Option if it is defined and the value does not satisfy the given predicate.
        Otherwise, Nothing is returned.

        Args:
            p: A predicate to test the value. This can be function f: (T) => bool or a koftipy.Predicate.

        Returns:
            This Option if it is defined and its value doesn't satisfy p, otherwise Nothing.

        Examples:
            assert Option.of(1).filter_not(lambda x: x <= 0) == Some(1)
            assert Option.of(-1).filter_not(lambda x: x <= 0) == Nothing
            assert Nothing.filter_not(lambda x: x <= 0) == Nothing
        """
        return self.filter(Predicate.of(p).negate())

    def contains(self, value: T) -> bool:
        """
        Returns if this Option is a Some and its value equals to the given.

        Args:
            value: A value to test

        Returns:
            True if this is a Some and its value equals to the given, otherwise False.

        Examples:
            assert Option.of(1).contains(1) is True
            assert Option.of(1).contains(2) is False
            assert Nothing.contains(1) is False
        """
        return self.get() == value if self.is_defined() else False

    def exists(self, p: Union[Predicate, PredicateFn]) -> bool:
        """
        Returns if this Option is a Some and its value satisfies the given predicate.

        Args:
            p: A predicate to test the value. This can be function f: (T) => bool or a koftipy.Predicate.

        Returns:
            True if this is a Some and its value satisfies p, otherwise False.

        Examples:
            assert Option.of(1).exists(lambda x: x > 0) is True
            assert Option.of(-1).exists(lambda x: x > 0) is False
            assert Nothing.exists(lambda x: x > 0) is False
        """
        p = Predicate.of(p)
        return p.test(self.get()) if self.is_defined() else False

    def if_defined(self, f: Consumer[T]) -> None:
        """
        Runs the given function f: (T) => None if this is a Some. Otherwise, it does nothing if this is empty.

        Args:
            f: A function f: (T) => None to run if this a Some

        Examples:
            Option.of(1).if_defined(print)  # prints '1'
            Nothing.if_defined(print)  # does nothing
        """
        if self.is_defined():
            f(self.get())

    def if_empty(self, f: Procedure) -> None:
        """
        Runs the given function f: () => None if this is empty. Otherwise, it does nothing if this is a Some.

        Args:
            f: A function f: () => None to run if this is empty

        Examples:
            Option.of(1).if_empty(lambda: print('Some'))  # does nothing
            Nothing.if_empty(lambda: print('Nothing'))  # prints 'Nothing'
        """
        if self.is_empty():
            f()

    def fold(self, if_empty: Supplier[U], if_defined: Function[T, U]) -> U:
        """
        Folds either Nothing or Some side of this Option. If this is defined, then returns the result of
        `if_defined` function. Otherwise, if this is empty, then returns the result of `if_empty` function.

        Args:
            if_empty: supplies the result if this is empty
            if_defined: maps the value if this is defined

        Returns:
            The result of `if_defined` if this is a Some, otherwise the result of `if_empty`
        """
        if self.is_empty():
            return if_empty()
        else:
            return if_defined(self.get())


class Some(Option[T], Generic[T]):
    """
    Represents a defined Option. It contains a value which can be None.

    A Some instance can be created in the following ways:
    1. Some(value)  # If value is None, then Some(None) is created.
    2. Option.some(value)  # Same as Some(value)
    3. Option.of(value)  # If value is None, then Nothing is returned
    """

    def __init__(self, value: T):
        """
        Creates a Some of the given value.

        Args:
            value: A value which can be None
        """
        super().__init__(_ctor_key)
        self.__value = value

    def __repr__(self) -> str:
        """
        Returns the string representation of this Some.

        Returns:
            string representation

        Examples:
            str(Some(1)) == repr(Some(1)) == 'Some(1)'
        """
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
    """
    Represents an empty Option. This class is not externally instantiated.
    Instead, its singleton instance Nothing is used.
    """

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


# Singleton instance of _Nothing
Nothing = _Nothing(_ctor_key)

__all__ = ['Option', 'Some', 'Nothing']
