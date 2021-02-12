class Symbol:
    """
    A symbol is an atomic proposition in a clause, e.g A, -A.
    Symbol(A, true)     ---> A
    Symbol(A, false)    ---> -A
    """
    def __init__(self, literal: str, is_pos: bool):
        self.literal = literal
        self.is_pos = is_pos

    # Allow "if symbol in symbol_list"
    def __eq__(self, other):
        return self.literal == other.literal and self.is_pos == other.is_pos

    # Allow dict usage
    def __hash__(self):
        return hash((self.literal, self.is_pos))

    def __repr__(self):
        if self.is_pos:
            return f"{self.literal}"
        return f"-{self.literal}"
