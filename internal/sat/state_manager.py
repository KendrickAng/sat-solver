from collections import deque, defaultdict
from typing import List

from internal.sat.model import Model
from internal.sat.symbol import Symbol
from internal.sat.symbols import Symbols
from internal.sat.clause import Clause
from internal.sat.constants import TRUE
from internal.utils.logger import Logger

logger = Logger.get_logger()

class StateManager:
    """
    During execution of CDCL, assigned variables as well as their antecedents define a directed acyclic graph.
    This is called an Implication Graph.
    Also handles tracking history of the solver.
    All symbols will be only positive.
    """
    @classmethod
    def from_values(cls, s: Symbols, ig: dict, h: 'History'):
        return StateManager(s, ig, h)

    def __init__(self, symbols: Symbols, implication_graph:dict=None, h:'History'=None):
        # for easier picking of branching variable (only positive)
        for s in symbols:
            assert s.is_pos
        self.unassigned_symbols = symbols
        # makes it easier to match with symbols in a clause, and deleting based on symbols inferred at a level.
        # Symbol (only positive) -> ImplicationNode
        self.implication_graph = {} if implication_graph is None else implication_graph
        # makes it easier to know which history to delete when we backtrack later.
        # dl (int) -> deque[Symbol (only positive)]
        self.history = History() if h is None else h

    def graph_add_node(self, s: Symbol, val: bool, antecedent: Clause, dl: int):
        """
        Adds a node X to the implication graph, updating its history.
        Its parents are the antecedent(X), and those nodes in the antecedent have X as their child.
        Symbol s must only be positive Symbol('A', True), not Symbol('A', False), otherwise there may
        be issues when finding the implication graph node when updating parents.
        """
        logger.debug(f"Implication Graph: {self.implication_graph}")
        assert s not in self.implication_graph, f"{s} should not be in implication graph"
        assert s.negate() not in self.implication_graph, f"{s.negate()} should not be in implication graph"
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
            for symbol_pos in [sbl.to_positive() for sbl in antecedent if sbl.literal != s.literal]:
                # all positive symbols of the antecedent should have been assigned
                if symbol_pos in self.implication_graph:
                    impl_node.add_parent(self.implication_graph[symbol_pos])
                    self.implication_graph[symbol_pos].add_child(impl_node)

    def graph_get_parent_symbols_at_lvl(self, s: Symbol, dl: int) -> List[Symbol]:
        """
        During conflict analysis, we need a way to get all implications at a certain level wrt a certain symbol.
        """
        assert s in self.implication_graph
        parents = self.implication_graph[s].get_parents()
        return [x.symbol for x in parents if x.level == dl]

    def graph_get_parent_symbols(self, s: Symbol) -> List[Symbol]:
        assert s in self.implication_graph
        parents = self.implication_graph[s].get_parents()
        return [x.symbol for x in parents]

    # Returns the list of symbols in the clause matching the decision level
    def graph_get_sbls_at_lvl_in_clause(self, dl: int, c: Clause) -> List[Symbol]:
        ret = []
        assert dl in self.history, f"symbols_at_level dl {dl} not in history"
        for symbol in c:
            if symbol.to_positive() in self.history.get_history_at_lvl(dl):
                ret.append(symbol)
        return ret

    def graph_get_level(self, s: Symbol) -> int:
        assert s in self.implication_graph, f"get_level {s} not in graph"
        return self.implication_graph[s].level

    def graph_get_antecedent(self, s: Symbol) -> Clause:
        assert s in self.implication_graph, f"get_antecedent {s} not in graph"
        return self.implication_graph[s].antecedent

    def revert_history(self, model: Model, dl_lower: int, dl_upper: int):
        """
        Removes all implied nodes and branching nodes NOT INCLUDING dl_from, UP TO AND INCLUDING dl_to
        Also reverts all symbols to their unassigned state, if any.
        ALso removes all nodes in children list which have been deleted.
        Also reverts the model.
        """
        assert dl_lower <= dl_upper
        # range(1,5): 1 2 3 4
        logger.trace(f"Reverting History from {dl_lower} to {dl_upper}")
        logger.trace(f"Graph {self.implication_graph}")
        logger.trace(f"Unasgn Sbls {self.unassigned_symbols}")
        logger.trace(f"History {self.history}")
        logger.trace(f"Model {model}")
        for i in range(dl_lower + 1, dl_upper + 1):
            q = self.history.get_history_at_lvl(i)
            while len(q) > 0:
                sbl = q.popleft()
                self.implication_graph.pop(sbl)
                self.sbls_mark_unassigned(sbl)
            self.history.del_history_at_lvl(i)
        # removes all nodes in children list which have been deleted.
        symbols_left = set(self.implication_graph.keys())
        for node in self.implication_graph.values():
            node.revert_children(to_keep=symbols_left)
        # revert model
        model.revert_model(to_keep=symbols_left)
        logger.trace(f"Reverted History from {dl_lower} to {dl_upper}")
        logger.trace(f"New Graph {self.implication_graph}")
        logger.trace(f"New Unasgn Sbls {self.unassigned_symbols}")
        logger.trace(f"New History {self.history}")
        logger.trace(f"New Model {model}")

    def get_history(self, dl: int):
        return self.history.get_history_at_lvl(dl)

    def sbls_mark_unassigned(self, s: Symbol):
        self.unassigned_symbols.add(s)

    def sbls_mark_assigned(self, s: Symbol):
        neg = s.negate()
        if s in self.unassigned_symbols:
            self.unassigned_symbols.remove(s)
        if neg in self.unassigned_symbols:
            self.unassigned_symbols.remove(neg)

    def sbls_get_unassigned_sbl_fifo(self) -> (Symbol, bool):
        return self.unassigned_symbols.pop_fifo(), TRUE

    def __eq__(self, other):
        return self.unassigned_symbols == other.unassigned_symbols and\
                self.history == other.history and\
                self.implication_graph == other.implication_graph

class ImplicationGraphNode:
    @classmethod
    def from_values(cls, s: Symbol, val: bool, dl: int, antecedent: Clause, p: list, c: list):
        return ImplicationGraphNode(s, val, dl, antecedent, p, c)

    def __init__(self, s: Symbol, val: bool, dl: int, antecedent: Clause, p: List['ImplicationGraphNode']=None, c: List['ImplicationGraphNode']=None):
        self.parents = [] if p is None else p
        self.children = [] if c is None else c
        self.antecedent = antecedent # Clause
        self.symbol = s
        self.value = val
        self.level = dl

    def add_parent(self, node: 'ImplicationGraphNode'):
        self.parents.append(node)

    def add_child(self, node: 'ImplicationGraphNode'):
        self.children.append(node)

    def revert_children(self, to_keep: set):
        self.children = [x for x in self.children if x.symbol in to_keep]

    def get_parents(self):
        return self.parents

    def __eq__(self, other):
        return self.parents == other.parents and self.children == other.children and\
                self.antecedent == other.antecedent and self.symbol == other.symbol and\
                self.value == other.value and self.level == other.level

    def __repr__(self):
        parents = list(map(lambda x: f"{x.symbol}",self.parents))
        children = list(map(lambda x: f"{x.symbol}",self.children))
        return f"[{self.symbol} {self.value} Lvl:{self.level} "\
               f"A:{self.antecedent} P:{parents} C:{children}]"

class History:
    """
    Records the symbols selected (branching, or implied)
    """
    @classmethod
    def from_values(cls, d: defaultdict):
        return History(d)

    def __init__(self, history:defaultdict=None):
        # dl (int) -> deque[Symbol (only positive)]
        # makes it easier to know which history to delete when we backtrack later.
        self.history = defaultdict(deque) if history is None else history

    def add_history(self, dl: int, s: Symbol):
        assert s.is_pos, f"add_history: {s} is not positive"  # simplify implementation
        self.history[dl].append(s)

    def get_history_at_lvl(self, dl: int) -> deque:
        assert dl in self.history, f"get_history_queue: level {dl} not in history"
        return self.history[dl]

    def del_history_at_lvl(self, dl: int):
        self.history.pop(dl)

    def __iter__(self):
        return self.history.__iter__()

    def __repr__(self):
        return self.history.__repr__()

    def __len__(self):
        return self.history.__len__()

    def __eq__(self, other):
        return self.history == other.history