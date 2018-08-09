'''
termination: A library for first-order term-rewriting
'''

__version__ = '0.0.2'

__all__ = ['arity', 'ordering', 'Symbol', 'Term', 'Variable']

from .arity import arity
from .comparable import ordering
from .symbol import Symbol
from .term import Term
from .variable import Variable
