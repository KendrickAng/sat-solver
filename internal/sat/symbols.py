from collections import deque
from internal.sat.symbol import Symbol

class Symbols:
    """
    Represents a collection of symbols, allows us to define branching strategy.
    Only contains positive symbols.
    """
    @classmethod
    def from_values(cls, d: deque):
        return Symbols(d)

    def __init__(self, d: deque=None):
        self.symbols = deque() if d is None else d # may change to set


    def add(self, s: Symbol):
        pos = s.to_positive()
        if pos not in self.symbols:
            self.symbols.append(pos)

    def pop_fifo(self):
        return self.symbols.popleft()

    def remove(self, s: Symbol):
        pos = s.to_positive()
        self.symbols.remove(pos)
        assert pos not in self.symbols # no duplicates should be present

    # allow "for s in symbols"
    def __iter__(self):
        return self.symbols.__iter__()

    def __repr__(self):
        return self.symbols.__repr__()

    def __eq__(self, other):
        return self.symbols == other.symbols