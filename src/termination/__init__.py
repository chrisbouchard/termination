"""termination: A library for first-order term-rewriting"""

__version__ = '0.0.2'
__author__ = 'Chris Bouchard <chris@upliftinglemma.net>'

__all__ = [
    # orderings
    'ordering',

    # terms
    'Constant',
    'Function',
    'Position',
    'PositionIterable',
    'Term',
    'Variable',
    'variables'
]


from .orderings import (
    ordering
)
from .terms import (
    Constant,
    Function,
    Position,
    PositionIterable,
    Term,
    Variable,
    variables
)
