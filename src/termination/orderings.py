"""Module creating ordering functions.

An ordering function is applied as:

    my_ord(t1, foo=42) < t2

Which will be evaluated as:

    my_ord(t1, foo=42) < my_ord(t2, foo=42)

At the simplest, this saves the user from having to specify the ordering twice,
and ensures that the arguments passed to the orderings will be the same on both
sides of the comparison. But there is a further benefit. In the case of:

    ord1(t1, foo=42) < ord2(t2) < t3

This will be evaluated as:

    (ord1(t1, foo=42) < ord1(t2, foo=42)) and (ord2(t2) < ord2(t3))

In other words, if the right-hand-side of an ordering comparison is another
ordering function, the value is pulled out and the left-hand function is
applied, allowing chains of different ordering comparisons, which is a very
common style in term rewriting.
"""

from abc import abstractmethod, abstractproperty
from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Dict, Generic, TypeVar, Union

from mypy_extensions import KwArg

from typing_extensions import Protocol

__all__ = ['ordering']


class Comparable(Protocol):
    def __lt__(self, other: Any) -> Any:
        pass

    def __le__(self, other: Any) -> Any:
        pass

    def __gt__(self, other: Any) -> Any:
        pass

    def __ge__(self, other: Any) -> Any:
        pass


T = TypeVar('T')
C = TypeVar('C', bound=Comparable)

ConstructorFn = Callable[[T, KwArg()], C]
OrderingFn = Callable[[T, KwArg()], 'AbstractOrderedValue[T, C]']

ComparisonRHS = Union[T, 'AbstractOrderedValue[T, Any]']


class AbstractOrderedValue(Generic[T, C]):
    @abstractproperty
    def value(self) -> T:
        pass

    @abstractmethod
    def _construct_comparable(self, value: T) -> C:
        pass

    def __lt__(self, right: ComparisonRHS[T]) -> Any:
        return self._evaluate_left() < self._evaluate_right(right)

    def __le__(self, right: ComparisonRHS[T]) -> Any:
        return self._evaluate_left() <= self._evaluate_right(right)

    def __gt__(self, right: ComparisonRHS[T]) -> Any:
        return self._evaluate_left() > self._evaluate_right(right)

    def __ge__(self, right: ComparisonRHS[T]) -> Any:
        return self._evaluate_left() >= self._evaluate_right(right)

    def __eq__(self, right: Any) -> Any:
        return self.value == self._unwrap_right(right)

    def __ne__(self, right: Any) -> Any:
        return self.value != self._unwrap_right(right)

    def _evaluate_left(self) -> C:
        return self._construct_comparable(self.value)

    def _evaluate_right(self, right: ComparisonRHS[T]) -> C:
        if isinstance(right, AbstractOrderedValue):
            return self._construct_comparable(right.value)
        return self._construct_comparable(right)

    def _unwrap_right(self, right: Any) -> Any:
        if isinstance(right, AbstractOrderedValue):
            return right.value
        return right


def ordering(constructor: ConstructorFn[T, C]) -> OrderingFn[T, C]:
    """Decorate a function to create an ordering function.

    The decorated function should take a single positional argument and any
    number of keyword arguments, and return something comparable. After
    decoration, the resulting function will behave as an ordering function, as
    described in the module docstring.
    """
    @dataclass
    class OrderedValue(AbstractOrderedValue[T, C]):
        value: T
        kwargs: Dict[str, Any]

        def _construct_comparable(self, value: T) -> C:
            return constructor(value, **self.kwargs)

    @wraps(constructor)
    def wrapped_constructor(value: T, **kwargs: Any) -> OrderedValue:
        return OrderedValue(
            value=value,
            kwargs=kwargs
        )

    return wrapped_constructor
