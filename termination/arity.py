from abc import ABCMeta, abstractmethod

__all__ = ['arity', 'HasArity']


class HasArity(metaclass=ABCMeta):
    @abstractmethod
    def _arity(self) -> int:
        pass


def arity(value: HasArity) -> int:
    try:
        return value._arity()
    except AttributeError as ex:
        raise ValueError('Value does not have an arity')
