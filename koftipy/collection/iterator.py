from __future__ import annotations
from typing import TypeVar, Generic, Iterator as PyIter, Iterable, Union

from koftipy.typing import Supplier, Function
from .traversable import Traversable

T = TypeVar('T')


class Iterator(Generic[T], Traversable[T]):
    """
    A lazy iteration object whose purpose is to traverse `once` over a sequence of elements.

    Iterators are single-use and one-way data structures. Once an iterator consumed, it
    cannot be reused. The iteration is only forward.

    This class provides an abstract base for Iterator implementations. Each subclass must implement
    `__next__` method to provide the next element in the sequence. It must raise a `StopIteration`
    exception when there is no more elements to iterate.

    There are many static constructors provided by this class to create Iterator instances.

    Examples:
        Iterator.empty()  # provides no elements
        Iterator.of('test')  # provides 'test' for once
        Iterator.of(1, 2, 3)  # provides 1, 2 and 3 in order
        Iterator.from_iterable([1, 2, 3])  # provides 1, 2 and 3 in order
    """

    @staticmethod
    def empty() -> Iterator[T]:
        """Creates an empty iterator which provides no elements."""
        return _EmptyIterator()

    @staticmethod
    def of(first: T, *others: T) -> Iterator[T]:
        """
        Creates an iterator providing the given elements in order and once.

        Args:
            first: the first element to be provided by the iterator
            *others: other elements to be provided

        Returns:
            a non-empty iterator providing the given sequence of elements for once.

        Examples:
            Iterator.of(1)  # provides 1
            Iterator.of(1, 2, 3)  # provides 1, 2 and 3 in order
        """
        if others:
            return Iterator.concat(Iterator.of(first), iter(others))
        else:
            return _SingleIterator(first)

    @staticmethod
    def from_iterable(iterable: Iterable[T]) -> Iterator[T]:
        """
        Creates an iterator that iterates the elements of the given iterable.

        Args:
            iterable: an iterable (list, set, tuple, dict, iterator) of elements

        Returns:
            a non-empty iterator traversing the elements of the given iterable

        Examples:
            Iterator.from_iterable([1, 2, 3])  # from a list
            Iterator.from_iterable({1, 2, 3})  # from a set
            Iterator.from_iterable({'a': 1, 'b': 2, 'c': 3})  # from a dict
        """
        assert iterable is not None, "iterable is None"
        return _PyIterator(iter(iterable))

    @staticmethod
    def concat(*iterators: Union[Iterator[T], Iterable[T]]) -> Iterator[T]:
        """
        Concatenates the given iterators (or iterables) and returns a single iterator
        which returns elements from the first iterator until it is exhausted, then
        elements from the next iterator, until all of the iterators are exhausted.

        Args:
            *iterators: iterators (or iterables) to be concatenated

        Returns:
            a concatenated iterator providing all elements from the given iterators in
            order of their issue.

        Examples:
            Iterator.concat([1, 2], Iterator.of(3), iter([4, 5]))  # provides 1, 2, 3, 4, 5
        """
        if not iterators:
            return Iterator.empty()
        else:
            return _ConcatIterator(iterators)

    @staticmethod
    def continually(value: Union[T, Supplier[T]]) -> Iterator[T]:
        """
        Creates an infinite iterator providing the given element (or outcome of the
        given supplier) forever.

        Args:
            value: an element or a supplier function

        Returns:
            an infinite iterator providing the given element or outcome of the given
            supplier at each iteration forever.

        Examples:
            Iterator.continually(random_digit)  # provides a random digit forever
        """
        return _InfiniteIterator(value)

    @staticmethod
    def repeatedly(value: Union[T, Supplier[T]], n: int) -> Iterator[T]:
        """
        Creates a finite iterator providing the given element (or outcome of the given
        supplier) `n` times.

        Args:
            value: an element or a supplier function
            n: the number of repetitions

        Returns:
            a finite iterator providing the given element or outcome of the given
            supplier `n` times.

        Examples:
            Iterator.repeatedly(random_digit, n=100)  # provides a random digit 100 times
        """
        return _RepetitiveIterator(value, n)

    @staticmethod
    def iterate_until_none(supplier: Supplier[T]) -> Iterator[T]:
        """
        Creates an iterator which iterates over the given supplier until `None` supplied.

        Args:
            supplier: the supplier function

        Returns:
            an iterator providing values from the supplier until it produces `None`

        Examples:
            supplier = iter([1, 2, None, 3])
            Iterator.iterate_until_none(supplier)  # provides 1, 2
        """
        return _UntilNoneIterator(supplier)

    @staticmethod
    def produce(seed: T, f: Function[T, T]) -> Iterator[T]:
        """
        Creates an infinite iterator using a function to compute the next value based on the previous.

        Args:
            seed: the first value to be returned by the iterator
            f: a function calculating the next value based on the previous.

        Returns:
            an iterator producing each value based on the previous
        """
        return _ProducerIterator(seed, f)

    def __next__(self) -> T:
        """
        Implementor must return the next element in the sequence. To stop the iteration of elements,
        a `StopIteration` exception should be raised from this method.

        Returns:
            the next element in the sequence
        """
        raise NotImplementedError

    def __iter__(self) -> Iterator[T]:
        """
        Converts this iterator to an iterable to make it eligible for for-loops.

        Returns:
            this iterator
        """
        return self


class _EmptyIterator(Iterator[T]):
    """
    An empty iterator providing no elements.
    """

    def __next__(self) -> T:
        raise StopIteration()


class _SingleIterator(Iterator[T]):
    """
    An iterator which provides the given element for once.
    """

    def __init__(self, element: T):
        self.__element = element
        self.__consumed = False

    def __next__(self) -> T:
        if self.__consumed:
            raise StopIteration()
        else:
            self.__consumed = True
            return self.__element


class _ConcatIterator(Iterator[T]):
    """
    An iterator to concat given iterators. `__next__` method returns elements
    from the first iterator until it is exhausted, then elements from the next
    iterator, until all of the iterators are exhausted.
    """

    def __init__(self, iterators: Iterable[Iterator[T]]):
        self.__iterators = iter(iterators)
        self.__set_current_iterator()

    def __next__(self) -> T:
        if self.__current is None:
            raise StopIteration()
        else:
            try:
                return next(self.__current)
            except StopIteration:
                self.__set_current_iterator()
                return next(self)

    def __set_current_iterator(self) -> None:
        try:
            self.__current = iter(next(self.__iterators))
        except StopIteration:
            self.__current = None


class _PyIterator(Iterator[T]):
    """
    Wraps the given python iterator.
    """

    def __init__(self, pyiter: PyIter[T]):
        self.__underlying = pyiter

    def __next__(self) -> T:
        return next(self.__underlying)


class _InfiniteIterator(Iterator[T]):
    """
    An infinite iterator providing the given value (or outcome of the given supplier) forever.
    """

    def __init__(self, value: Union[T, Supplier[T]]):
        self.__supplier = _make_supplier(value)

    def __next__(self) -> T:
        return self.__supplier()


class _RepetitiveIterator(Iterator[T]):
    """
    An iterator providing the given value (or outcome of the given supplier) n times.
    """

    def __init__(self, value: Union[T, Supplier[T]], n: int):
        self.__supplier = _make_supplier(value)
        self.__countdown = n

    def __next__(self) -> T:
        if self.__countdown <= 0:
            raise StopIteration()
        else:
            self.__countdown -= 1
            return self.__supplier()


class _UntilNoneIterator(Iterator[T]):
    """
    An iterator which iterates until the given supplier supplies None.
    """

    def __init__(self, supplier: Supplier[T]):
        self.__supplier = supplier

    def __next__(self) -> T:
        element = self.__supplier()
        if element is None:
            raise StopIteration()
        else:
            return element


class _ProducerIterator(Iterator[T]):
    def __init__(self, seed: T, f: Function[T, T]):
        self.__next = seed
        self.__func = f

    def __next__(self) -> T:
        current = self.__next
        self.__next = self.__func(current)
        return current


def _make_supplier(value: Union[T, Supplier[T]]) -> Supplier[T]:
    return value if callable(value) else lambda: value


__all__ = ['Iterator']
