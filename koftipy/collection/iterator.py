from __future__ import annotations
from typing import TypeVar, Generic

T = TypeVar('T')


class Iterator(Generic[T]):
    @staticmethod
    def of(element: T) -> Iterator[T]:
        return _SingleIterator(element)

    @staticmethod
    def empty() -> Iterator[T]:
        return _EmptyIterator()

    def __next__(self) -> T:
        raise NotImplementedError


class _SingleIterator(Iterator[T]):
    def __init__(self, element: T):
        self.__element = element

    def __next__(self) -> T:
        return self.__element


class _EmptyIterator(Iterator[T]):
    def __next__(self) -> T:
        raise StopIteration()


__all__ = ['Iterator']
