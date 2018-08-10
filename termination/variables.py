from dataclasses import dataclass

from .arities import HasArity

__all__ = ['Variable']


@dataclass(frozen=True)
class Variable(HasArity):
    name: str

    def __str__(self) -> str:
        return f'?{self.name}'

    def _arity(self) -> int:
        return 0
