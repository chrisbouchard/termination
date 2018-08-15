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
