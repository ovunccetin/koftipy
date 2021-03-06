from __future__ import annotations

import threading
from typing import TypeVar, Generic, Union, Iterable, List

from koftipy.typing import Supplier, Function, PredicateFn
from koftipy.collection.iterator import Iterator
from .option import Option
from koftipy.predicate import Predicate

T = TypeVar('T')
U = TypeVar('U')
_ctor_key = object()


class Lazy(Generic[T]):
    """
    Represents a value which is lazily computed and cached at the first access.
    All subsequent accesses provide the memoized value. Therefore, it is referential transparent.

    Once computed it is immutable. Also, the value computation is thread safe.

    Examples:
        def random_digit():
            return random.randint(0, 10)

        lazynum: Lazy[int] = Lazy.of(random_digit)
        assert lazynum.is_computed() is False

        value: int = lazynum.get()  # or lazynum()
        assert lazynum.is_computed() is True

        # once computed, always the same value is provided
        for i in range(100):
            assert lazynum.get() == value
    """

    def __init__(self, supplier: Supplier[T], ctor_key: object):
        """
        It is internally called by constructor methods. Not for external use.
        """
        assert _ctor_key is ctor_key, "Cannot directly instantiate Lazy! Use constructor methods."
        self.__supplier = supplier
        self.__value = None
        self.__lock = threading.Lock()

    @staticmethod
    def of(supplier: Supplier[T]) -> Lazy[T]:
        """
        Creates a Lazy whose value will be provided by the given supplier.

        Args:
            supplier: supplier function to compute the value of this Lazy

        Returns:
            a new Lazy which is not computed yet
        """
        assert supplier is not None, "supplier is None"
        if isinstance(supplier, Lazy):
            return supplier
        else:
            return Lazy(supplier, _ctor_key)

    @staticmethod
    def sequence(lazies: Iterable[Lazy[T]]) -> Lazy[List[T]]:
        """
        Reduces a list of Lazy values into a single Lazy. This call doesn't cause the lazy objects
        in the given list to be computed.

        Args:
            lazies: a list of Lazy objects

        Returns:
            a single Lazy object containing the list of values computed by given Lazy objects

        Examples:
            assert Lazy.sequence([Lazy.of(lambda: 1), Lazy.of(lambda: 2)]) == [1, 2]
        """
        return Lazy.of(lambda: list(map(lambda lazy: lazy.get(), lazies)))

    def get(self) -> T:
        """
        At the first call, computes, caches the value and returns. At subsequent calls,
        the computed value is immediately returned without re-computation.

        Returns:
            the computed value
        """
        if self.__supplier is None:
            return self.__value
        else:
            return self.__compute_value()

    def __iter__(self):
        """
        Converts this lazy to a singleton iterator providing the computed value.

        Returns:
            a singleton iterator
        """
        return Iterator.of(self.get())

    def is_computed(self) -> bool:
        """
        If value of this Lazy is computed or not. A Lazy is computed at the first access to its value.

        Returns:
            True if this is computed, False otherwise
        """
        return self.__supplier is None

    def map(self, f: Function[T, U]) -> Lazy[U]:
        """
        Maps the value of this Lazy to another one by applying the given mapper function `f`.
        This call does not cause this Lazy to be computed.

        Args:
            f: mapper function

        Returns:
            Mapped lazy

        Examples:
            def random_digit():
                return random.randint(0, 10)

            lazynum: Lazy[int] = Lazy.of(random_digit)
            lazystr: Lazy[str] = lazynum.map(lambda x: str(x))  # not computed yet

            lazystr.get()  # computes here
        """
        return Lazy.of(lambda: f(self.get()))

    def filter(self, p: Union[Predicate, PredicateFn]) -> Option[T]:
        """
        Returns Some(value) if the value of this Lazy satisfies the given predicate.
        Otherwise, Nothing is returned.

        Args:
            p: A predicate to test the value. This can be function f: (T) => bool or a koftipy.Predicate.

        Returns:
            A Some if the value satisfies the predicate, otherwise Nothing.

        Examples:
            assert Lazy.of(lambda: 3).filter(lambda x: x >= 0) == Some(3)
            assert Lazy.of(lambda: 3).filter(lambda x: x <= 0) == Nothing
        """
        p: Predicate = Predicate.of(p)
        value: T = self.get()
        return Option.some(value) if p.test(value) else Option.nothing()

    def filter_not(self, p: Union[Predicate, PredicateFn]) -> Option[T]:
        """
        Returns Some(value) if the value of this Lazy does not satisfy the given predicate.
        Otherwise, Nothing is returned.

        Args:
            p: A predicate to test the value. This can be function f: (T) => bool or a koftipy.Predicate.

        Returns:
            A Some if the value does not satisfy the predicate, otherwise Nothing.

        Examples:
            assert Lazy.of(lambda: 3).filter_not(lambda x: x <= 0) == Some(3)
            assert Lazy.of(lambda: 3).filter(lambda x: x >= 0) == Nothing
        """
        return self.filter(Predicate.of(p).negate())

    def __call__(self):
        """
        A convenience to retrieve the value by directly calling this Lazy instead of get() method.
        So, `lazyval()` is identical to `lazyval.get()`

        Returns:
            the computed value
        """
        return self.get()

    def __eq__(self, other: object) -> bool:
        """
        This and other are equal, if both are Lazy and their computed values are equal.
        Note that, this call causes both Lazy objects (this and the other) to be computed.

        Args:
            other: the other object to check

        Returns:
            True if this and other are both Lazy and their computed values are equal.
        """
        if not isinstance(other, Lazy):
            return False
        elif self is other:
            return True
        else:
            return self.get() == other.get()

    def __hash__(self) -> int:
        """
        Computes the value and returns hash of it.

        Returns:
            Hash of the computed value.
        """
        return hash(self.get())

    def __compute_value(self) -> T:
        supplier = self.__supplier
        with self.__lock:
            if supplier is not None:
                self.__value = supplier()
                self.__supplier = None

            return self.__value


__all__ = ['Lazy']
