__all__ = [
    'VariablePool',
    'fresh_variable'
]


from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any, Dict, Optional

from .terms import IndexedVariable, Variable


@dataclass
class VariableState:
    variable: Variable
    next_index: int = field(default=1)

    def update_index(self, index: int) -> None:
        if index >= self.next_index:
            self.next_index = index + 1


@dataclass
class VariablePool:
    state: Dict[str, VariableState] = field(default_factory=dict)

    def __getitem__(self, name: str) -> Variable:
        return self.get(name)

    def get(self, name: str, index: Optional[int] = None) -> Variable:
        if index is None:
            return self._get_state(name).variable

        self._get_state(name).update_index(index)
        return IndexedPoolVariable(name=name, index=index, pool=self)

    def get_fresh(self, name: str) -> Variable:
        index = self._get_state(name).next_index
        return self.get(name, index)

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
def fresh_variable(variable: Any) -> Variable:
    raise ValueError('Value is not associated with a variable pool')


@fresh_variable.register
def _fresh_variable_vabiable(variable: PoolVariable) -> Variable:
    return variable.pool.get_fresh(variable.name)


@fresh_variable.register
def _fresh_variable_indexed_variable(variable: IndexedPoolVariable) -> Variable:
    return variable.pool.get_fresh(variable.name)


@fresh_variable.register
def _fresh_variable_pool(pool: VariablePool) -> Variable:
    return pool.get_fresh('')
