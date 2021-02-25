from __future__ import annotations

import threading
from typing import TypeVar, Generic, Union

from ._types import Supplier, Function, PredicateFn
from .iterator import Iterator
from .option import Option
from .predicate import Predicate

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

        lv: Lazy[int] = Lazy.of(random_digit)
        assert lv.is_computed() is False

        value: int = lv.get()  # or lv()
        assert lv.is_computed() is True

        # once computed, always the same value is provided
        for i in range(100):
            assert lv.get() == value
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
        This call does not compute the value of this Lazy.

        Args:
            f: mapper function

        Returns:
            Mapped lazy
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
        return self.get()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Lazy):
            return False
        elif self is other:
            return True
        else:
            return self.get() == other.get()

    def __hash__(self) -> int:
        return hash(self.get())

    def __compute_value(self) -> T:
        supplier = self.__supplier
        with self.__lock:
            if supplier is not None:
                self.__value = supplier()
                self.__supplier = None

            return self.__value


__all__ = ['Lazy']
