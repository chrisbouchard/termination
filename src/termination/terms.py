"""Module for syntactic terms and their support.

* ``Constant``: A syntactic symbol with a name and zero arity.
* ``Function``: A syntactic function symbol, with a name and nonzero arity.
* ``Variable``: A "slot" in a term that can be assinged with a substitution.
* ``Term``: Application of a function symbol to one or more child terms.
"""

__all__ = [
    'Constant',
    'IndexedVariable',
    'Function',
    'Term',
    'Variable',
    'variables'
]


from abc import ABCMeta, abstractmethod
from dataclasses import dataclass
from functools import singledispatch
from typing import Any, Iterable, Iterator, Tuple, TypeVar

from typing_extensions import Protocol, runtime


Position = Tuple[int, ...]
PositionIterable = Iterable[int]

T = TypeVar('T')


class TermLike(metaclass=ABCMeta):
    """Abstract base class for things that can act as subterms.

    In addition to the listed abstract methods, implementations should respond
    to the free variables() function.
    """

    @abstractmethod
    def __getitem__(self, position: PositionIterable) -> 'TermLike':
        pass

    @abstractmethod
    def subterms(self) -> Iterator[Tuple[Position, 'TermLike']]:
        pass

    def positions(self) -> Iterator[Position]:
        yield from (position for (position, term) in self.subterms())


@dataclass(frozen=True)
class Symbol:
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

    def subterms(self: T) -> Iterator[Tuple[Position, T]]:
        yield ((), self)


@dataclass(frozen=True)
class Function(Symbol):
    """A function symbol.

    Function symbols are not themselves term-like; they are applied to
    term-like objects to create new terms. Function symbols have a name and
    an arity, which together form their identity.
    """

    arity: int

    def __post_init__(self) -> None:
        """Verify that the fields are valid."""
        if self.arity <= 0:
            raise ValueError(
                'Arity must be 1 or greater. For arity 0, use Constant.'
            )

    def __str__(self) -> str:
        """Format the function symbol with its name and arity.

        Example::

            f = Function(name='f', arity=2)
            str(f)  # 'f.2'
        """
        return f'{self.name}.{self.arity}'

    def __call__(self, *args: TermLike) -> 'Term':
        """Create a new term with this symbol as the root."""
        return Term(self, args)


class Constant(TerminalSymbol):
    """A constant symbol.

    Constant symbols are term-like symbols with no children. Constants have a
    name, which is their identity.
    """

    def __str__(self) -> str:
        """Format this constant as its name.

        Example::

            c = Constant(name='c')
            str(c)  # 'c'
        """
        return self.name


class Variable(TerminalSymbol):
    """A variable symbol.

    Variables represent slots in the term that are "unspecified" in some
    sense, and can be replaced by a substitution. Variables have a name,
    which is their identity.
    """

    def __str__(self) -> str:
        """Format this variable with its name.

        Example::

            x = Variable(name='x')
            str(x)  # '?x'
        """
        return f'?{self.name}'


@dataclass(frozen=True)
class IndexedVariable(Variable):
    """A variable with an index.

    Indexed variables are variables, and behave just like Variable, except that
    they have an index, which together with their name forms their identity.

    Having the name separate from the index makes it easier to create fresh
    variables that can be tied back to the original variable.
    """

    index: int

    def __str__(self) -> str:
        """Format this indexed variable with its name.

        Example::

            x = IndexedVariable(name='x', index=2)
            str(x)  # '?x#2'
        """
        return f'?{self.name}#{self.index}'


@runtime
class SupportsVariables(Protocol):
    @abstractmethod
    def _variables(self) -> Iterator[Variable]:
        pass


@singledispatch
def variables(value: Any) -> Iterator[Variable]:
    """Return an iterator of the variables in this object.

    The same variable may be yielded in any order and may appear multiple
    times. If uniqueness is desired, store the results in a set::

        vars = set(variables(obj))

    Different types will define what "in" means in their context.

    * ``Variable``: The variable itself
    * ``Term``: All variables that occur as subterms.
    """
    raise ValueError('Value does not have variables')


@variables.register
def variables_variable(variable: Variable) -> Iterator[Variable]:
    yield variable


@variables.register
def variables_supports_variables(value: SupportsVariables) -> Iterator[Variable]:
    return value._variables()


@dataclass(frozen=True)
class Term(TermLike):
    """Application of a function symbol to children.

    The root of a term is a function symbol. The symbols arity must match the
    length of the tuple of children. The children are a tuple of term-like
    objects. Together, the root and children are the terms identity.
    """

    root: Function
    children: Tuple[TermLike, ...]

    def __post_init__(self) -> None:
        """Verify that the root arity and number of children match."""
        arity = self.root.arity
        length = len(self.children)
        if arity != length:
            raise ValueError(
                'Incorrect number of child terms: '
                f'Expected {arity}, found {length}'
            )

    def __str__(self) -> str:
        """Format this term as a function call.

        Example::

            f = Function(name='f', arity=2)
            g = Function(name='g', arity=1)
            c = Constant(name='c')
            x = Variable(name='x')
            t = Term(root=f, children=(Term(root=g, children=(c,)), x))

            str(t)  # 'f(g(c), ?x)'
        """
        # The default str() for Function includes the arity, which is redundant
        # here. Just use the symbol's name.
        root_str = self.root.name
        children_str = ', '.join(str(child) for child in self.children)
        return f'{root_str}({children_str})'

    def __getitem__(self, position: PositionIterable) -> TermLike:
        """Get the subterm at the specified position in this term.

        The position is specified as an iterable of ints, where each int
        corresponds to an index in the next subterm's children tuple. For
        example::

            f = Function(name='f', arity=2)
            g = Function(name='g', arity=1)
            c = Constant(name='c')
            x = Variable(name='x')
            t = Term(root=f, children=(Term(root=g, children=(c,)), x))

            t[()] == t
            t[(0,)] == Term(root=g, children=(c,))
            t[(0,0)] == c
            t[(1,)] == x

        Accessing an invalid position raises an ``IndexError``::

            t[(-1,)]  # IndexError
            t[(0,1)]  # IndexError
            t[(0,0,0)]  # IndexError
        """
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

    def subterms(self) -> Iterator[Tuple[Position, TermLike]]:
        """Return an iterator over valid positions in this term and the subterm.

        The order in which subterms are yielded is not specified. Each position
        will be yielded exactly once. Subterms will be repeated if the same
        subterm occurs at multiple positions.

        For example::
            f = Function(name='f', arity=2)
            g = Function(name='g', arity=1)
            c = Constant(name='c')
            x = Variable(name='x')
            t = Term(root=f, children=(Term(root=g, children=(c,)), x))

            i = t.subterms()

            # Note the exact order of these pairs is not specified.
            next(i)  # ((), t)
            next(i)  # ((0,), Term(root=g, children=(c,)))
            next(i)  # ((0,0), c)
            next(i)  # ((1,), x)
            next(i)  # StopIteration
        """
        yield ((), self)
        for index, child in enumerate(self.children):
            for (position, term) in child.subterms():
                yield ((index, *position), term)

    def _variables(self) -> Iterator[Variable]:
        for child in self.children:
            yield from variables(child)
