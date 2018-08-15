"""Module for conveniently defining signatures with one or more symbols"""

_all__ = [
    'Signature',
    'arity',
    'constant',
    'variable'
]


from abc import abstractmethod
from typing import Generic, Optional, Type, TypeVar, Union, overload

from .pools import VariablePool, fresh_variable
from .terms import Constant, Function, Variable


S = TypeVar('S', bound='SignatureDescriptor')
T = TypeVar('T')


class SignatureDescriptor(Generic[T]):
    def __init__(self):
        self._name = None  # type: Optional[str]

    @abstractmethod
    def _create_value(self, instance: 'Signature') -> T:
        pass

    @property
    def name(self) -> str:
        if self._name is None:
            raise AttributeError('Attribute name is not set')
        return self._name

    def __set_name__(self, owner: Type['Signature'], name: str) -> None:
        if self._name is None:
            self._name = name

    @overload
    def __get__(self: S, instance: None, owner: Type['Signature']) -> S:
        pass

    @overload  # noqa: F811  # Ignore redefinition for overload
    def __get__(self, instance: 'Signature', owner: Type['Signature']) -> T:
        pass

    def __get__(  # noqa: F811  # Ignore redefinition for overload
        self: S,
        instance: Optional['Signature'],
        owner: Type['Signature']
    ) -> Union[S, T]:
        if instance is None:
            return self

        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self._create_value(instance)

        return instance.__dict__[self.name]

    def __set__(self, instance: 'Signature', owner: Type['Signature']) -> None:
        raise AttributeError('Symbols are read-only')


class ConstantDescriptor(SignatureDescriptor[Constant]):
    def _create_value(self, _: object) -> Constant:
        return Constant(name=self.name)


class FunctionDescriptor(SignatureDescriptor[Function]):
    def __init__(self, arity: int) -> None:
        super().__init__()
        self.arity = arity

    def _create_value(self, _: object) -> Function:
        return Function(name=self.name, arity=self.arity)


class VariableDescriptor(SignatureDescriptor[Variable]):
    def _create_value(self, instance: 'Signature') -> Variable:
        pool = instance._signature_variable_pool
        return pool[self.name]


class VariablePoolDescriptor(SignatureDescriptor[VariablePool]):
    def _create_value(self, _: object) -> VariablePool:
        return VariablePool()


class Signature:
    _signature_variable_pool = VariablePoolDescriptor()


@fresh_variable.register
def _fresh_variable_signature(signature: Signature) -> Variable:
    return fresh_variable(signature._signature_variable_pool)


def arity(arity) -> FunctionDescriptor:
    if arity <= 0:
        raise ValueError('Arity must be non-negative.')
    return FunctionDescriptor(arity=arity)


def constant() -> ConstantDescriptor:
    return ConstantDescriptor()


def variable() -> VariableDescriptor:
    return VariableDescriptor()
