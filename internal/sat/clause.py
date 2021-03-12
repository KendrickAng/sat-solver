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

    # Allow dict usage
    def __hash__(self):
        return hash(tuple(self.symbol_list))

    def __eq__(self, other):
        # order shouldnt matter, and duplicates can be removed in a clause
        return set(self.symbol_list) == set(other.symbol_list)
