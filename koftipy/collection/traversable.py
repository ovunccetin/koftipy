from __future__ import annotations
from typing import TypeVar, Generic

import koftipy.collection.iterator as it

T = TypeVar('T')


class Traversable(Generic[T]):
    def __iter__(self) -> it.Iterator[T]:
        raise NotImplementedError


__all__ = ['Traversable']
