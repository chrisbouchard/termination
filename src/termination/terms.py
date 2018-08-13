from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any, Iterable, Tuple

__all__ = [
    'Position',
    'PositionIterable',
    'Symbol',
    'Term',
    'Variable',
    'variables'
]


Position = Tuple[int]
PositionIterable = Iterable[int]


class TermLike(metaclass=ABCMeta):
    @abstractmethod
    def __getitem__(self, position: PositionIterable) -> 'TermLike':
        pass

    @abstractmethod
    def subterms(self) -> Iterable[Tuple[Position, 'TermLike']]:
        pass

    def positions(self) -> Iterable[Position]:
        yield from (term for (position, term) in self.subterms())


@dataclass(frozen=True)
class Symbol:
    name: str
    arity: int = field(default=0)

    def __str__(self) -> str:
        return self.name

    def __call__(self, *args: TermLike) -> 'Term':
        return Term(self, args)


@dataclass(frozen=True)
class Variable(TermLike):
    name: str

    def __str__(self) -> str:
        return f'?{self.name}'

    def __getitem__(self, position: PositionIterable) -> TermLike:
        position_copy = tuple(position)
        # TODO: This syntax is ugly
        for _ in position_copy:
            raise IndexError(f'Invalid position: {position_copy}')
        return self

    def subterms(self) -> Iterable[Tuple[Position, TermLike]]:
        yield ((), self)


@singledispatch
def variables(value: Any) -> Iterable[Variable]:
    if hasattr(value, '_variables') and callable(value._variables):
        return value._variables()
    raise ValueError('Value does not have variables')


@variables.register
def _(variable: Variable) -> Iterable[Variable]:
    yield variable


@dataclass(frozen=True)
class Term(TermLike):
    root: Symbol
    children: Tuple[TermLike] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        arity = self.root.arity
        length = len(self.children)
        if arity != length:
            raise ValueError(
                'Incorrect number of child terms: '
                f'Expected {arity}, found {length}'
            )

    def __str__(self) -> str:
        root_str = str(self.root)

        if self.root.arity == 0:
            return root_str

        children_str = ', '.join(str(child) for child in self.children)
        return f'{root_str}({children_str})'

    def __getitem__(self, position: PositionIterable) -> TermLike:
        position_copy: Position = tuple(position)

        # We'll iterate over the indices in the position. We get an explicit
        # iterator because we may need to call __getitem__ on one of our
        # subterms, and it gives us a way to say "the rest of the position".
        position_iter = iter(position_copy)

        # Keep track of the current subterm.
        current_term: Term = self

        for index in position_iter:
            try:
                child: TermLike = current_term.children[index]

                if isinstance(child, Term):
                    # If this subterm is still a Term, we can keep iterating
                    # rather than recursing.
                    current_term = child
                else:
                    # Otherwise we need to recurse and let the subterm handle
                    # it. The iterator contains the suffix of the position we
                    # haven't inspected yet.
                    return child[position_iter]

            # If either there's no child at the index, or if the recursive call
            # throws, we will report the error for the entire position. We
            # saved a copy for just this occasion.
            except IndexError as ex:
                raise IndexError(f'Invalid position: {position_copy}')

        return current_term

    def subterms(self) -> Iterable[Tuple[Position, TermLike]]:
        yield ((), self)
        for index, child in enumerate(self.children):
            yield from (
                ((index, *position), term)
                for (position, term) in child.subterms()
            )

    def _variables(self) -> Iterable[Variable]:
        for child in self.children:
            yield from variables(child)
