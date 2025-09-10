"""A module for conveniently defining signatures with one or more symbols."""

from __future__ import annotations

__all__ = [
    "Signature",
    "arity",
    "constant",
    "variable",
]

from abc import ABC, abstractmethod
from typing import Self, overload

from .pools import VariablePool, fresh_variable
from .terms import Constant, Function, Variable


class SignatureDescriptor[T](ABC):
    def __init__(self):
        self._name: str | None = None

    @abstractmethod
    def _create_value(self, instance: Signature) -> T: ...

    @property
    def name(self) -> str:
        if self._name is None:
            raise AttributeError("Attribute name is not set")
        return self._name

    def __set_name__(self, owner: type[Signature], name: str) -> None:
        if self._name is None:
            self._name = name

    @overload
    def __get__(self, instance: None, owner: type[Signature]) -> Self: ...
    @overload
    def __get__(self, instance: Signature, owner: type[Signature]) -> T: ...

    def __get__(self, instance: Signature | None, owner: type[Signature]) -> Self | T:
        if instance is None:
            return self

        if self.name not in instance.__dict__:
            instance.__dict__[self.name] = self._create_value(instance)

        return instance.__dict__[self.name]

    def __set__(self, instance: Signature, owner: type[Signature]) -> None:
        raise AttributeError("Symbols are read-only")


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
    def _create_value(self, instance: Signature) -> Variable:
        pool = instance._signature_variable_pool
        return pool[self.name]


class VariablePoolDescriptor(SignatureDescriptor[VariablePool]):
    def _create_value(self, _: object) -> VariablePool:
        return VariablePool()


class Signature:
    """Base class for signatures.

    fresh_variable(Signature): Returns a fresh variable with an empty ('') name.
    """

    _signature_variable_pool = VariablePoolDescriptor()


@fresh_variable.register
def _fresh_variable_signature(signature: Signature) -> Variable:
    return fresh_variable(signature._signature_variable_pool)


def arity(arity) -> FunctionDescriptor:
    """Create a function symbol descriptor.

    For example::

        class Foo(Signature):
            f = arity(2)
            x = variable()
            y = variable()

        foo = Foo()
        t = foo.f(foo.x, foo.y)  # OK
    """
    if arity <= 0:
        raise ValueError("Arity must be non-negative.")
    return FunctionDescriptor(arity=arity)


def constant() -> ConstantDescriptor:
    """Create a constant descriptor.

    For example::

        class Foo(Signature):
            g = arity(1)
            a = constant()
            b = constant()

        foo = Foo()
        t = foo.g(foo.a)  # OK
    """
    return ConstantDescriptor()


def variable() -> VariableDescriptor:
    """Create a variable descriptor.

    For example::

        class Foo(Signature):
            f = arity(2)
            x = variable()
            y = variable()

        foo = Foo()
        t = foo.f(foo.x, foo.y)  # OK

    The signature also creates a backing variable pool, so that::

        fresh_variable(foo.x)

    Works as expected, with the resulting index unique among indices produced
    from that signature instance.
    """
    return VariableDescriptor()
