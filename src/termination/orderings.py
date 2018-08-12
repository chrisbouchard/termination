from dataclasses import dataclass
from functools import wraps
from typing import Any, Callable, Generic, TypeVar

__all__ = ['ordering']


T = TypeVar('T')


@dataclass
class OrderedValue(Generic[T]):
    value: Any
    constructor: Callable[[Any], T]

    def _evaluate_left(self) -> T:
        return self.constructor(self.value)

    def _evaluate_right(self, right: Any) -> T:
        if isinstance(right, OrderedValue):
            return self.constructor(right.value)

        return self.constructor(right)

    def __lt__(self, right: Any) -> Any:
        return self._evaluate_left() < self._evaluate_right(right)

    def __le__(self, right: Any) -> Any:
        return self._evaluate_left() <= self._evaluate_right(right)

    def __gt__(self, right: Any) -> Any:
        return self._evaluate_left() > self._evaluate_right(right)

    def __ge__(self, right: Any) -> Any:
        return self._evaluate_left() >= self._evaluate_right(right)

    def __eq__(self, right: Any) -> Any:
        return self._evaluate_left() == self._evaluate_right(right)

    def __ne__(self, right: Any) -> Any:
        return self._evaluate_left() != self._evaluate_right(right)


def ordering(constructor: Callable[..., T]) -> Callable[..., OrderedValue[T]]:
    @wraps(constructor)
    def wrapped_constructor(value: Any, **kwargs: Any) -> OrderedValue[T]:
        def apply_constructor(value: Any) -> T:
            return constructor(value, **kwargs)

        return OrderedValue(
            value=value,
            constructor=apply_constructor
        )

    return wrapped_constructor
