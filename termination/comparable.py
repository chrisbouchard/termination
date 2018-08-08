from abc import ABCMeta, abstractmethod
from enum import Enum, auto
import operator
from types import NotImplementedType
from typing import Generic, TypeVar, Union

__all__ = ['Comparable', 'Expression', 'Operation']


T = TypeVar('T', bound='Comparable')


class Expression(Generic[T], metaclass=ABCMeta):
    @abstractmethod
    def _evaluate(self, measure: Callable[[T], Any]) -> Any:
        pass

    def __bool__(self) -> Any:
        return self._evaluate(lambda value: value._default_measure())

    def __and__(self, other: 'Expression[T]') -> 'Expression[T]':
        return ConnectiveExpression(
            connect=operator.and_,
            left=self,
            right=other
        )

    def __or__(self, other: 'Expression[T]') -> 'Expression[T]':
        return ConnectiveExpression(
            connect=operator.or_,
            left=self,
            right=other
        )

    def __not__(self) -> 'Expression[T]':
        return NotExpression(value=self)


@dataclass
class ComparisonExpression(Expression[T]):
    compare: Callable[[Any, Any], Any]
    left: T
    right: T

    def _evaluate(self, measure: Callable[[T], Any]) -> Any:
        left_measure = measure(self.left)
        right_measure = measure(self.right)
        return self.compare(left_measure, right_measure)


@dataclass
class ConnectiveExpression(Expression[T]):
    connect: Callable[[Any, Any], Any]
    left: Expression[T]
    right: Expression[T]

    def _visit(self, visitor: Callable[[T], Any]) -> Any:
        evaluated_left = self.left._evaluate(visitor)
        evaluated_right = self.right._evaluate(visitor)
        return self.connect(evaluated_left, evaluated_right)


@dataclass
class NotExpression(Expression[T]):
    value: T

    def _visit(self, visitor: Callable[[T], Any]) -> Any:
        visited_value = visitor(self.value)
        return not visited_value


def ordering(measure: Callable[[T], Any]) -> Callable[[Expression[T]], Any]:
    def evaluate_ordering(expression: Expression[T], **kwargs: Any) -> Any:
        def _measure(value: T) -> Any:
            return measure(value, **kwargs)
        return expression._evaluate(_measure)

    return evaluate_ordering


TSelf = TypeVar('TSelf')


class Comparable(metaclass=ABCMeta):
    @abstractmethod
    def _default_measure(self) -> Any:
        pass

    def __lt__(self: TSelf, other: TSelf) -> Expression[TSelf]
        return ComparisonExpression(
            compare=operator.lt,
            left=self,
            right=other
        )

    def __le__(self: TSelf, other: TSelf) -> Expression[TSelf]
        return ComparisonExpression(
            compare=operator.le,
            left=self,
            right=other
        )

    def __gt__(self: TSelf, other: TSelf) -> Expression[TSelf]
        return ComparisonExpression(
            compare=operator.gt,
            left=self,
            right=other
        )

    def __ge__(self: TSelf, other: TSelf) -> Expression[TSelf]
        return ComparisonExpression(
            compare=operator.ge,
            left=self,
            right=other
        )

    def __eq__(self: TSelf, other: TSelf) -> Expression[TSelf]
        return ComparisonExpression(
            compare=operator.eq,
            left=self,
            right=other
        )

    def __ne__(self: TSelf, other: TSelf) -> Expression[TSelf]
        return ComparisonExpression(
            compare=operator.ne,
            left=self,
            right=other
        )
