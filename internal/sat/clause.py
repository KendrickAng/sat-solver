from typing import List
from internal.sat.symbol import Symbol

class Clause:
    def __init__(self, symbol_list: List[Symbol]):
        self.symbol_list = symbol_list

    # Override this change string representation
    def __repr__(self):
        return str(self.symbol_list)
