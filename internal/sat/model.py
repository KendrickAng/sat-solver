from typing import List, Dict
from internal.sat.constants import UNASSIGNED
from internal.sat.symbol import Symbol

class Model:
    """
    A Model represents a mapping of symbols in a formula to its truth assignment {True, False}.
    """

    @classmethod
    def from_mapping(cls, mapping: Dict[Symbol, bool]):
        return Model(mapping)

    @classmethod
    def from_symbols(cls, symbols: List[Symbol]) -> 'Model':
        mapping = {}
        for s in symbols:
            mapping[s] = UNASSIGNED
            mapping[s.neg()] = UNASSIGNED
        return Model(mapping)

    def __init__(self, mapping: Dict[Symbol, bool]):
        self.mapping = mapping

    # Implement evaluation of self[key].
    def __getitem__(self, item):
        # A model should start with every possible symbol
        assert item in self.mapping

        return self.mapping[item]
