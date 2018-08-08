from dataclasses import dataclass, field
from typing import Iterable, Tuple

from .arity import HasArity, arity

__all__ = ['Path', 'PathIterable', 'Term']


Path = Tuple[int]
PathIterable = Iterable[int]


@dataclass(frozen=True)
class Term:
    root: HasArity
    subterms: Tuple['Term'] = field(default_factory=tuple)

    def __post_init__(self) -> None:
        root_arity = arity(self.root)
        length = len(self.subterms)
        if root_arity != length:
            raise ValueError(
                'Incorrect number of subterms: ' +
                f'Expected {root_arity}, found {length}'
            )

    def __str__(self) -> str:
        # TODO: Make name available in the typings
        root_name = self.root.name

        if arity(self.root) == 0:
            return str(self.root.name)

        subterms_str = ', '.join(str(subterm) for subterm in self.subterms)
        return f'{root_name}({subterms_str})'

    def __getitem__(self, path: PathIterable) -> 'Term':
        original_path = tuple(path)
        term = self

        for position in path:
            try:
                term = term.subterms[position]
            except IndexError as ex:
                raise IndexError(f'Invalid path: {original_path}')

        return term
