__all__ = [
    'VariablePool',
    'fresh'
]


from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any, Dict, Optional

from .term import (
    IndexedVariable,
    Variable
)


@dataclass
class VariableState:
    variable: Variable
    next_index: int = field(default=1)

    def fresh_index(self):
        index = self.next_index
        self.next_index += 1
        return index


@dataclass
class VariablePool:
    state: Dict[str, VariableState] = field(default_factory=dict)

    def __getitem__(self, name: str) -> Variable:
        return self.get(name)

    def fresh(self, name: str) -> Variable:
        index = self._get_state(name).fresh_index()
        return self.get(name, index)

    def get(self, name: str, index: Optional[int] = None) -> Variable:
        if index is None:
            return self._get_state(name).variable
        return IndexedPoolVariable(name=name, index=index, pool=self)

    def _get_state(self, name: str) -> VariableState:
        if name not in self.state:
            variable = PoolVariable(name=name, pool=self)
            self.state[name] = VariableState(variable=variable)

        return self.state[name]


@dataclass(frozen=True)
class PoolVariable(Variable):
    pool: VariablePool


@dataclass(frozen=True)
class IndexedPoolVariable(IndexedVariable):
    pool: VariablePool


@singledispatch
def fresh(variable: Any) -> Variable:
    raise ValueError('Value is not associated with a variable pool')


@fresh.register
def _fresh_vabiable(variable: PoolVariable) -> Variable:
    return variable.pool.fresh(variable.name)


@fresh.register
def _fresh_indexed_variable(variable: IndexedPoolVariable) -> Variable:
    return variable.pool.fresh(variable.name)
