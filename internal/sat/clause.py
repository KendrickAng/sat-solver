from typing import List
from internal.sat.symbol import Symbol

class Clause:
    """
    Implements the Watched Literal Data Structure as used in Chaff.
    """
    def __init__(self, symbol_list: List[Symbol]):
        self.symbol_list = symbol_list

    # Allows len(clause)
    def __len__(self):
        return self.symbol_list.__len__()

    # Override this change string representation
    def __repr__(self):
        return str(self.symbol_list)

    # Allow "for symbol in clause"
    def __iter__(self):
        return self.symbol_list.__iter__()

    def __eq__(self, other):
        return self.symbol_list == other.symbol_list
