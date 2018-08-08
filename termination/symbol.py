from dataclasses import dataclass, field

from .arity import HasArity
from .term import Term

__all__ = ['Symbol']


@dataclass(frozen=True)
class Symbol(HasArity):
    name: str
    arity: int = field(default=0)

    def __str__(self) -> str:
        return f'{self.name}.{self.arity}'

    def _arity(self) -> int:
        return self.arity

    def __call__(self, *args: Term) -> Term:
        return Term(self, args)
