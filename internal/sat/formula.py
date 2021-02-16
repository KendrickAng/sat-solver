from typing import List
from internal.sat.clause import Clause

class Formula:
    """
    Represents a formula in CNF form.
    """
    def __init__(self, clause_list: List[Clause]):
        self.formula = clause_list
