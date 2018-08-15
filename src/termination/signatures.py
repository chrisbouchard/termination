__all__ = [
    'Signature',
    'arity',
    'constant',
    'variable'
]


from abc import abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generic, Optional, Type, TypeVar

from .pools import VariablePool, fresh_variable
from .terms import Constant, Function, Variable


T = TypeVar('T')
U = TypeVar('U')


class ReadOnlyDescriptor(Generic[T]):
    name: Optional[str]

    @abstractmethod
    def _create_value(self, instance: U, owner: Type[U]) -> T:
        pass

    def __set_name__(self, owner: Type[U], name: str) -> None:
        if self.name is None:
            self.name = name

    def __get__(self, instance: U, owner: Type[U]) -> T:
        if self.name is None:
            raise AttributeError('Attribute name is not set')
        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self._create_value(instance, owner)
        return instance.__dict__[self.name]

    def __set__(self, instance: U, owner: Type[U]) -> None:
        raise AttributeError('Symbols are read-only')


@dataclass
class ConstantDescriptor(ReadOnlyDescriptor[Constant]):
    name: Optional[str] = field(init=False)

    def _create_value(self, instance: T, owner: Type[T]) -> Constant:
        if self.name is None:
            raise AttributeError('Attribute name is not set')
        return Constant(name=self.name)


@dataclass
class FunctionDescriptor(ReadOnlyDescriptor[Function]):
    arity: int
    name: Optional[str] = field(init=False)

    def _create_value(self, instance: T, owner: Type[T]) -> Function:
        if self.name is None:
            raise AttributeError('Attribute name is not set')
        return Function(name=self.name, arity=self.arity)


@dataclass
class VariableDescriptor(ReadOnlyDescriptor[Variable]):
    pool_name: Optional[str] = None
    name: Optional[str] = field(init=False)

    def _create_value(self, instance: T, owner: Type[T]) -> Variable:
        if self.name is None:
            raise AttributeError('Attribute name is not set')
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
        cls._signature_variable_pool = VariablePoolDescriptor()
        super().__init_subclass__(**kwargs)

        for value in cls.__dict__.values():
            if isinstance(value, VariableDescriptor):
                value.pool_name = '_signature_variable_pool'


@fresh_variable.register
def _fresh_variable_signature(signature: Signature) -> Variable:
    return fresh_variable(signature._signature_variable_pool)


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
