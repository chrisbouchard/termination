__all__ = [
    'Signature',
    'arity',
    'constant',
    'variable'
]


from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, Type, TypeVar

from .pools import VariablePool, fresh
from .terms import Constant, Function, Variable


T = TypeVar('T')
U = TypeVar('U')


@dataclass
class ReadOnlyDescriptor(Generic[T], metaclass=ABCMeta):
    name: Optional[str] = field(init=False, default=None)

    @abstractmethod
    def _create_value(self, instance: U, owner: Type[U]) -> T:
        pass

    def __set_name__(self, owner: Type[U], name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, instance: U, owner: Type[U]) -> T:
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self._create_value()
        return instance.__dict__[self.name]

    def __set__(self, instance: U, owner: Type[U]) -> None:
        raise AttributeError('Symbols are read-only')

    def __delete__(self, instance: U, owner: Type[U]) -> None:
        raise AttributeError('Symbols are read-only')


class ConstantDescriptor(ReadOnlyDescriptor[Constant]):
    def _create_value(self, instance: T, owner: Type[T]) -> Constant:
        return Constant(name=self.name)


@dataclass
class FunctionDescriptor(ReadOnlyDescriptor[Function]):
    arity: int

    def _create_value(self, instance: T, owner: Type[T]) -> Function:
        return Function(name=self.name, arity=self.arity)


@dataclass
class VariableDescriptor(ReadOnlyDescriptor[Variable]):
    pool_name: Optional[str] = field(default=None)

    def _create_value(self, instance: T, owner: Type[T]) -> Variable:
        if self.pool_name is None:
            raise AttributeError('Owner is not associated with a variable pool')

        pool = getattr(instance, self.pool_name)
        return pool[self.name]


@dataclass
class VariablePoolDescriptor(ReadOnlyDescriptor[VariablePool]):
    def _create_value(self, instance: T, owner: Type[T]) -> VariablePool:
        return VariablePool()


class Signature:
    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._signature_variable_pool = VariablePoolDescriptor()

        for value in cls.__dict__.values():
            if isinstance(value, VariableDescriptor):
                value.pool_name = '_signature_variable_pool'


@fresh.register
def _fresh_signature(signature: Signature) -> Variable:
    return fresh(signature._signature_variable_pool)


def arity(arity) -> Any:
    if arity < 0:
        raise ValueError('Arity must be non-negative.')

    if arity == 0:
        return constant()

    return FunctionDescriptor(arity=arity)


def constant() -> Any:
    return ConstantDescriptor()


def variable() -> Any:
    return VariableDescriptor()
