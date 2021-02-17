from collections import deque, defaultdict
from typing import List
from internal.sat.symbol import Symbol
from internal.sat.clause import Clause

CONFLICT_SYMBOL = Symbol('K', True)

class ImplicationGraph:
    """
    During execution of CDCL, assigned variables as well as their antecedents define a directed acyclic graph.
    This is called an Implication Graph.
    """
    def __init__(self):
        self.graph = {}         # Symbol (only positive) -> ImplicationNode
        self.history = defaultdict(deque)  # dl (int) -> deque[Symbol (only positive)]

    def add_node(self, s: Symbol, val: bool, antecedent: Clause, dl: int):
        """
        Adds a node X to the implication graph, updating its history.
        Its parents are the antecedent(X), and those nodes in the antecedent have X as their child.
        Symbol s must only be positive Symbol('A', True), not Symbol('A', False), otherwise there may
        be issues when finding the implication graph node when updating parents.
        """
        assert s not in self.graph
        assert s.negate() not in self.graph
        # We only want to deal with positive symbols
        s_pos, v_pos = s, val
        if not s.is_pos:
            s_pos = s.negate()
            v_pos = not val
        impl_node = ImplicationGraphNode(s_pos, v_pos, dl, antecedent)
        self.graph[s_pos] = impl_node
        self.add_history(dl, s_pos)

        # antecedent is None only when we are selecting a branching symbol, hence no parent
        if antecedent:
            for symbol in antecedent:
                # all positive symbols of the antecedent should have been assigned
                symbol_pos = symbol.to_positive()
                if symbol_pos in self.graph:
                    impl_node.add_parent(self.graph[symbol_pos])
                    self.graph[symbol_pos].add_child(impl_node)

    def add_conflict_node(self, antecedent: Clause, dl: int):
        self.add_node(CONFLICT_SYMBOL, None, antecedent, dl)

    def add_history(self, dl: int, s: Symbol):
        self.history[dl].append(s.to_positive())

    def get_parent_list_at_lvl(self, s: Symbol, dl: int) -> List[Symbol]:
        assert s in self.graph
        return [x.symbol for x in self.graph[s].parent if x.level == dl]

    # Returns the number of symbols in the clause matching the decision level
    def get_symbols_at_lvl_in_clause(self, dl: int, c: Clause) -> List[Symbol]:
        ret = []
        for symbol in c:
            assert dl in self.history, f"symbols_at_level dl {dl} not in history"
            if symbol.to_positive() in self.history[dl]:
                ret.append(symbol)
        return ret

    def get_level(self, s: Symbol) -> int:
        assert s in self.graph, f"get_level {s} not in graph"
        return self.graph[s].level

    def get_antecedent(self, s: Symbol) -> Clause:
        assert s in self.graph, f"get_antecedent {s} not in graph"
        return self.graph[s].antecedent

class ImplicationGraphNode:
    def __init__(self, s: Symbol, val: bool, dl: int, antecedent: Clause):
        self.parents = []
        self.children = []
        self.antecedent = antecedent # Clause
        self.symbol = s
        self.value = val
        self.level = dl

    def add_parent(self, node: 'ImplicationGraphNode'):
        self.parents.append(node)

    def add_child(self, node: 'ImplicationGraphNode'):
        self.children.append(node)
