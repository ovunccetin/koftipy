from __future__ import annotations

import threading
from typing import TypeVar, Generic

from ._types import Supplier, Function
from .iterator import Iterator

T = TypeVar('T')
U = TypeVar('U')
_ctor_key = object()


class Lazy(Generic[T]):
    def __init__(self, supplier: Supplier[T], ctor_key: object):
        assert _ctor_key is ctor_key, "Cannot directly instantiate Lazy! Use constructor methods."
        self.__supplier = supplier
        self.__value = None
        self.__lock = threading.Lock()

    @staticmethod
    def of(supplier: Supplier[T]) -> Lazy[T]:
        assert supplier is not None, "supplier is None"
        if isinstance(supplier, Lazy):
            return supplier
        else:
            return Lazy(supplier, _ctor_key)

    def get(self) -> T:
        if self.__supplier is None:
            return self.__value
        else:
            return self.__compute_value()

    def __iter__(self):
        return Iterator.of(self.get())

    def is_computed(self) -> bool:
        return self.__supplier is None

    def map(self, f: Function[T, U]) -> Lazy[U]:
        return Lazy.of(lambda: f(self.get()))

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
