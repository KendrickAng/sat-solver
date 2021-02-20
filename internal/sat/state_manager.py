from collections import deque, defaultdict
from typing import List
from internal.sat.symbol import Symbol
from internal.sat.symbols import Symbols
from internal.sat.clause import Clause
from internal.sat.constants import TRUE

CONFLICT_SYMBOL = Symbol('K', True)

class StateManager:
    """
    During execution of CDCL, assigned variables as well as their antecedents define a directed acyclic graph.
    This is called an Implication Graph.
    Also handles tracking history of the solver.
    """
    def __init__(self, symbols: Symbols):
        # for easier picking of branching variable
        self.unassigned_symbols = symbols
        # Symbol (only positive) -> ImplicationNode
        # makes it easier to match with symbols in a clause, and deleting based on symbols inferred at a level.
        self.implication_graph = {}
        # dl (int) -> deque[Symbol (only positive)]
        # makes it easier to know which history to delete when we backtrack later.
        self.history = History()

    def add_node(self, s: Symbol, val: bool, antecedent: Clause, dl: int):
        """
        Adds a node X to the implication graph, updating its history.
        Its parents are the antecedent(X), and those nodes in the antecedent have X as their child.
        Symbol s must only be positive Symbol('A', True), not Symbol('A', False), otherwise there may
        be issues when finding the implication graph node when updating parents.
        """
        assert s not in self.implication_graph
        assert s.negate() not in self.implication_graph
        # We only want to deal with positive symbols
        s_pos, v_pos = s, val
        if not s.is_pos:
            s_pos = s.negate()
            v_pos = not val
        impl_node = ImplicationGraphNode(s_pos, v_pos, dl, antecedent)
        self.implication_graph[s_pos] = impl_node
        self.history.add_history(dl, s_pos)

        # antecedent is None only when we are selecting a branching symbol, hence no parent
        if antecedent:
            for symbol in antecedent:
                # all positive symbols of the antecedent should have been assigned
                symbol_pos = symbol.to_positive()
                if symbol_pos in self.implication_graph:
                    impl_node.add_parent(self.implication_graph[symbol_pos])
                    self.implication_graph[symbol_pos].add_child(impl_node)

    def add_conflict_node(self, antecedent: Clause, dl: int):
        self.add_node(CONFLICT_SYMBOL, None, antecedent, dl)

    def get_parent_list_at_lvl(self, s: Symbol, dl: int) -> List[Symbol]:
        """
        During conflict analysis, we need a way to get all implications at a certain level wrt a certain symbol.
        """
        assert s in self.implication_graph
        return [x.symbol for x in self.implication_graph[s].parent if x.level == dl]

    # Returns the list of symbols in the clause matching the decision level
    def get_symbols_at_lvl_in_clause(self, dl: int, c: Clause) -> List[Symbol]:
        ret = []
        for symbol in c:
            assert dl in self.history, f"symbols_at_level dl {dl} not in history"
            if symbol.to_positive() in self.history[dl]:
                ret.append(symbol)
        return ret

    def get_level(self, s: Symbol) -> int:
        assert s in self.implication_graph, f"get_level {s} not in graph"
        return self.implication_graph[s].level

    def get_antecedent(self, s: Symbol) -> Clause:
        assert s in self.implication_graph, f"get_antecedent {s} not in graph"
        return self.implication_graph[s].antecedent

    def revert_history(self, dl_lower: int, dl_upper: int):
        """
        Removes all implied nodes and branching nodes NOT INCLUDING dl_from, UP TO AND INCLUDING dl_to
        Also reverts all symbols to their unassigned state, if any.
        """
        assert dl_lower <= dl_upper
        # range(1,5): 1 2 3 4
        for i in range(dl_lower + 1, dl_upper + 1):
            q = self.history.get_history_queue(i)
            while len(q) > 0:
                sbl = q.popleft()
                self.unassigned_symbols.add(sbl)
                self.implication_graph.pop(sbl)

    def get_unassigned_sbl_fifo(self) -> (Symbol, bool):
        return self.unassigned_symbols.pop_fifo(), TRUE

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

class History:
    """
    Records the symbols selected (branching, or implied)
    """

    def __init__(self):
        # dl (int) -> deque[Symbol (only positive)]
        # makes it easier to know which history to delete when we backtrack later.
        self.history = defaultdict(deque)

    def add_history(self, dl: int, s: Symbol):
        assert s.is_pos, f"add_history: {s} is not positive"  # simplify implementation
        self.history[dl].append(s)

    def get_history_queue(self, dl: int) -> deque:
        assert dl in self.history, f"get_history_queue: level {dl} not in history"
        return self.history[dl]