from typing import List, Dict, Set
from internal.sat.constants import UNASSIGNED, TRUE, FALSE
from internal.sat.formula import Formula
from internal.sat.symbol import Symbol
from internal.sat.clause import Clause
from internal.utils.logger import Logger

logger = Logger.get_logger()

class Model:
    """
    A Model represents a mapping of symbols in a formula to its truth assignment {True, False}.
    Models should always have a key for every symbol in a formula, postive and negative.
    """

    @classmethod
    def from_mapping(cls, mapping: Dict[Symbol, bool]):
        return Model(mapping)

    @classmethod
    def from_symbols(cls, symbols: List[Symbol]) -> 'Model':
        mapping = {}
        for s in symbols:
            mapping[s] = UNASSIGNED
            mapping[s.negate()] = UNASSIGNED
        return Model(mapping)

    def __init__(self, mapping: Dict[Symbol, bool]):
        self.mapping = mapping

    def extend(self, s: Symbol, val: bool):
        assert s in self.mapping
        assert s.negate() in self.mapping
        self.mapping[s] = val
        self.mapping[s.negate()] = not val

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

    def revert_model(self, to_keep: Set[Symbol]):
        logger.trace(f"Before model revert {self.shorten()}")
        logger.trace(f"Keeping {to_keep}")
        for key in self.mapping.keys():
            if key.to_positive() in to_keep:
                continue
            self.mapping[key] = UNASSIGNED
            self.mapping[key.negate()] = UNASSIGNED
        logger.trace(f"After model revert {self.shorten()}")

    # Returns a shortened version of the model (only true symbols)
    def shorten(self) -> str:
        return str([s for s in self.mapping.keys() if self.mapping[s] is True])

    def get_formula_status(self, f: Formula) -> bool:
        for clause in f.get_clauses_with_learnt():
            status = self.get_clause_status(clause)
            assert status is not UNASSIGNED
            if status == FALSE:
                return FALSE
        return TRUE


    # Implement evaluation of self[key].
    def __getitem__(self, item):
        # A model should start with every possible symbol
        assert item in self.mapping

        return self.mapping[item]

    def __eq__(self, other):
        return self.mapping == other.mapping

    def __repr__(self):
        return self.mapping.__repr__()