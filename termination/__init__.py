'''
termination: A library for first-order term-rewriting
'''

__version__ = '0.0.2'

__all__ = [
    # orderings
    'ordering',

    # terms
    'Path',
    'PathIterable',
    'Symbol',
    'Term',
    'Variable',
    'variables'
]

from .orderings import ordering
from .terms import Path, PathIterable, Symbol, Term, Variable, variables
