"""Module for syntactic terms and their support.

Constant: A syntactic symbol with a name and zero arity.
Function: A syntactic function symbol, with a name and nonzero arity.
Variable: A "slot" in a term that can be assinged with a substitution.
Term: Application of a function symbol to one or more child terms.
"""

__all__ = [
    'Constant',
    'Position',
    'PositionIterable',
    'Function',
    'Term',
    'Variable',
    'variables'
]


from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from functools import singledispatch
from typing import Any, Iterable, Tuple, TypeVar


Position = Tuple[int]
PositionIterable = Iterable[int]

T = TypeVar('T')


class TermLike(metaclass=ABCMeta):
    """Abtract base class for things that can act as subterms.

    In addition to the listed abstract methods, implementations should respond
    to the free variables() function.
    """

    @abstractmethod
    def __getitem__(self, position: PositionIterable) -> 'TermLike':
        pass

    @abstractmethod
    def subterms(self) -> Iterable[Tuple[Position, 'TermLike']]:
        pass

    def positions(self) -> Iterable[Position]:
        yield from (term for (position, term) in self.subterms())


@dataclass(frozen=True)
class Symbol(metaclass=ABCMeta):
    """Base class for symbols, which have names."""
    name: str


class TerminalSymbol(Symbol, TermLike):
    """Base class for symbols that occur as terms."""
    def __getitem__(self: T, position: PositionIterable) -> T:
        position_copy = tuple(position)
        position_iter = iter(position_copy)

        try:
            next(position_iter)
        except StopIteration:
            return self

        raise IndexError(f'Invalid position: {position_copy}')

    def subterms(self: T) -> Iterable[Tuple[Position, T]]:
        yield ((), self)


@dataclass(frozen=True)
class Function(Symbol):
    arity: int

    def __post_init__(self) -> None:
        if self.arity <= 0:
            raise ValueError('Arity must be 1 or greater. For arity 0, use Constant.')

    def __str__(self) -> str:
        return f'{self.name}.{self.arity}'

    def __call__(self, *args: TermLike) -> 'Term':
        return Term(self, args)


class Constant(TerminalSymbol):
    def __str__(self) -> str:
        return self.name

    def __call__(self) -> 'Constant':
        return self


class Variable(TerminalSymbol):
    def __str__(self) -> str:
        return f'?{self.name}'


@dataclass(frozen=True)
class IndexedVariable(Variable):
    index: int

    def __str__(self) -> str:
        return f'?{self.name}#{self.index}'


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
    root: Function
    children: Tuple[TermLike]

    def __post_init__(self) -> None:
        arity = self.root.arity
        length = len(self.children)
        if arity != length:
            raise ValueError(
                'Incorrect number of child terms: '
                f'Expected {arity}, found {length}'
            )

    def __str__(self) -> str:
        # The default str() for Function includes the arity, which is redundant
        # here. Just use the symbol's name.
        root_str = self.root.name
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
            for (position, term) in child.subterms():
                yield ((index, *position), term)

    def _variables(self) -> Iterable[Variable]:
        for child in self.children:
            yield from variables(child)
