from internal.sat.symbol import Symbol

class Symbols:
    """
    Represents a collection of symbols, allows us to define branching strategy.
    """
    def __init__(self):
        self.symbols = [] # may change to set

    def add(self, s: Symbol):
        if s not in self.symbols:
            self.symbols.append(s)

    # allow "for s in symbols"
    def __iter__(self):
        return self.symbols.__iter__()

    def __repr__(self):
        return self.symbols.__repr__()