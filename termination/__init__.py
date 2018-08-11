'''
termination: A library for first-order term-rewriting
'''

__version__ = '0.0.2'

from .orderings import (
    ordering
)
from .terms import (
    Position,
    PositionIterable,
    Symbol,
    Term,
    Variable,
    variables
)

__all__ = [
    # orderings
    'ordering',

    # terms
    'Position',
    'PositionIterable',
    'Symbol',
    'Term',
    'Variable',
    'variables'
]
