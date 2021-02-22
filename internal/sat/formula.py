from typing import List
from internal.sat.clause import Clause
from internal.sat.symbols import Symbols

class Formula:
    """
    Represents a formula in CNF form.
    """
    def __init__(self, clause_list: List[Clause]):
        self.clist = clause_list
        self.learnt_clist = []
        self.symbols = Symbols()
        for clause in clause_list:
            for symbol in clause:
                self.symbols.add(symbol)

    # Returns a list of all symbols in the formula.
    def get_symbols(self) -> Symbols:
        return self.symbols

    # Returns all clauses, original and learnt included.
    def get_clauses_with_learnt(self) -> List[Clause]:
        return self.learnt_clist + self.clist

    def add_learnt_clause(self, c: Clause):
        self.learnt_clist.append(c)

    def __repr__(self):
        return f"Clauses: {self.clist}\nLearnt Clauses: {self.learnt_clist}"