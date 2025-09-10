"""A module for creating variable pools.

Variable pools are sources of new variables. They have the ability to create
"fresh" indexed variables, meaning variables whose indexes have never been
returned from that pool previously. This can be necessary as variables with the
same name and index are considered equal.
"""

__all__ = ["VariablePool", "fresh_variable"]


from dataclasses import dataclass, field
from functools import singledispatch
from typing import Any

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
    """A class for creating variables.

    A variable pool has methods to get variables with specific indexes, and
    methods for creating "fresh" variables, meaning variables whose indexes
    have never been returned from this pool previously.
    """

    state: dict[str, VariableState] = field(default_factory=dict)

    def __getitem__(self, name: str) -> Variable:
        """Return the the variable with the given name.

        Subsequent calls to the same pool for the same name are guaranteed to return
        the same variable instance.
        """
        return self.get(name)

    def get(self, name: str, index: int | None = None) -> Variable:
        """Return a variable with the given name and index.

        If called with index != None, this method always returns a new variable
        instance. If called with index == None, subsequent calls to the same
        pool for the same name are guaranteed to return the same variable
        instance.
        """
        if index is None:
            return self._get_state(name).variable

        self._get_state(name).update_index(index)
        return IndexedPoolVariable(name=name, index=index, pool=self)

    def get_fresh(self, name: str) -> Variable:
        """Return a variable with the given name and a unique index.

        This method always returns a new variable instance, and its index is
        always guaranteed to be greater than the index of any variable returned
        by this pool previously.
        """
        index = self._get_state(name).next_index
        return self.get(name, index)

    def _get_state(self, name: str) -> VariableState:
        if name not in self.state:
            variable = PoolVariable(name=name, pool=self)
            self.state[name] = VariableState(variable=variable)
        return self.state[name]


@dataclass(frozen=True)
class PoolVariable(Variable):
    pool: VariablePool = field(compare=False)


@dataclass(frozen=True)
class IndexedPoolVariable(IndexedVariable):
    pool: VariablePool = field(compare=False)


@singledispatch
def fresh_variable(source: Any) -> Variable:
    """Return a fresh variable from a given source.

    Different sources will respond differently to this function. The returned
    variable is guaranteed to have a unique index for its name. The name of the
    variable depends on the source.

    * For variables: The name is the name of the variable passed.
    * For variable pools: The name is an empty string ('').
    """
    raise ValueError("Value is not associated with a variable pool")


@fresh_variable.register
def _fresh_variable_vabiable(variable: PoolVariable) -> Variable:
    return variable.pool.get_fresh(variable.name)


@fresh_variable.register
def _fresh_variable_indexed_variable(variable: IndexedPoolVariable) -> Variable:
    return variable.pool.get_fresh(variable.name)


@fresh_variable.register
def _fresh_variable_pool(pool: VariablePool) -> Variable:
    return pool.get_fresh("")
