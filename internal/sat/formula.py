from typing import List
from internal.sat.clause import Clause
from internal.sat.symbols import Symbols

class Formula:
    """
    Represents a formula in CNF form.
    """
    def __init__(self, clause_list: List[Clause]):
        self.clause_list = clause_list
        self.symbols = Symbols()
        for clause in clause_list:
            for symbol in clause:
                self.symbols.add(symbol)

    # Returns a list of all symbols in the formula
    def get_all_symbols(self) -> Symbols:
        return self.symbols
