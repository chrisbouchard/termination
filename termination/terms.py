from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Iterable, Tuple

__all__ = ['Path', 'PathIterable', 'Symbol', 'Term', 'Variable', 'variables']


Path = Tuple[int]
PathIterable = Iterable[int]


class TermLike(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, path: PathIterable) -> 'Term':
        pass


@dataclass(frozen=True)
class Symbol:
    name: str
    arity: int = field(default=0)

    def __str__(self) -> str:
        return self.name

    def __call__(self, *args: 'Term') -> 'Term':
        return Term(self, args)


@dataclass(frozen=True)
class Variable(TermLike):
    name: str

    def __str__(self) -> str:
        return f'?{self.name}'

    def __getitem__(self, path: PathIterable) -> TermLike:
        # TODO: This syntax is ugly
        for position in path:
            raise IndexError(f'Invalid path: {original_path}')
        return self


@singledispatch
def variables(value: Any) -> Iterable[Variable]:
    if hasattr(value, _variables) and iscallable(value._variables):
        return value._variables()
    raise ValueError('Value does not have variables')


@variables.register
def _(variable: Variable) -> Iterable[Variable]:
    yield variable


@dataclass(frozen=True)
class Term(TermLike):
    root: Symbol
    subterms: Tuple[TermLike] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        arity = self.root.arity
        length = len(self.subterms)
        if root_arity != length:
            raise ValueError(
                'Incorrect number of subterms: ' +
                f'Expected {arity}, found {length}'
            )

    def __str__(self) -> str:
        root_name = self.root.name

        if self.root.arity == 0:
            return str(root.name)

        subterms_str = ', '.join(str(subterm) for subterm in self.subterms)
        return f'{root_name}({subterms_str})'

    def __getitem__(self, path: PathIterable) -> TermLike:
        path_copy = tuple(path)
        term = self

        for position in path_copy:
            try:
                term = term.subterms[position]
            except IndexError as ex:
                raise IndexError(f'Invalid path: {path_copy}')

        return term

    def _variables(self) -> Iterable[Variable]:
        for subterm in self.subterms:
            yield from variables(subterm)
