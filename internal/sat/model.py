from typing import List, Dict

class Model:
    """
    A Model represents a mapping of symbols in a formula to its truth assignment {True, False}.
    """

    @classmethod
    def from_symbols(cls, symbols: List[str]) -> 'Model':
        mapping = {s: None for s in symbols}
        return Model(mapping)

    def __init__(self, mapping: Dict[str, bool]):
        self.mapping = mapping
