from typing import List, Dict
from internal.sat.constants import SAT, UNSAT, UNASSIGNED, TRUE, FALSE
from internal.sat.symbol import Symbol
from internal.sat.clause import Clause

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

    def extend(self, s: Symbol, val: bool):
        assert s in self.mapping
        assert s.neg() in self.mapping
        self.mapping[s] = val
        self.mapping[s.neg()] = not val

    def get_clause_status(self, c: Clause) -> bool:
        """
        Returns TRUE if at least one symbol maps to TRUE
                FALSE if all symbols map to FALSE
                UNASSIGNED if no symbols are TRUE and at least one symbol is UNASSIGNED
        """
        s = set(map(lambda symbol: self.mapping[symbol], c))
        if TRUE in s:
            return TRUE
        elif UNASSIGNED not in s:
            return FALSE
        else:
            return UNASSIGNED

    def is_unit_clause(self, c: Clause) -> (bool, Symbol):
        """
        Returns True if all literals but one is assigned to FALSE, with one literal UNASSIGNED.
        Also returns the unassigned symbol, if any.
        """
        l = list(map(lambda symbol: self.mapping[symbol], c))
        if l.count(FALSE) == len(c)-1 and l.count(UNASSIGNED) == 1:
            s = None
            for sbl in c:
                if self.mapping[sbl] == UNASSIGNED:
                    s = sbl
            return True, s
        return False, None

    # Implement evaluation of self[key].
    def __getitem__(self, item):
        # A model should start with every possible symbol
        assert item in self.mapping

        return self.mapping[item]
