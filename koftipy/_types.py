from typing import TypeVar, Callable

T = TypeVar('T')
U = TypeVar('U')

Supplier = Callable[[], T]
Consumer = Callable[[T], None]
Function = Callable[[T], U]
Procedure = Callable[[], None]
PredicateFn = Callable[[T], bool]

__all__ = ['Supplier', 'Consumer', 'Function', 'Procedure', 'PredicateFn']
