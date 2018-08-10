'''
termination: A library for first-order term-rewriting
'''

__version__ = '0.0.2'

__all__ = ['arity', 'ordering', 'Symbol', 'Term', 'Variable']

from .arities import arity
from .orderings import ordering
from .symbols import Symbol
from .terms import Term
from .variables import Variable
