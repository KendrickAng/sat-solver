from collections import deque
from heapq import nlargest
from internal.sat.model import Model
from internal.sat.symbol import Symbol
from internal.sat.symbols import Symbols
from internal.sat.formula import Formula
from internal.sat.clause import Clause
from internal.sat.implication_graph import ImplicationGraph
from internal.sat.constants import TRUE, FALSE, UNASSIGNED, CONFLICT
from internal.utils.logger import Logger

logger = Logger.get_logger()

class Solver:
    """
    Solver for CDCL algorithm.
    Symbols = the remaining unassigned symbols. Only symbols in original formula.
    Clauses = the set of clauses.
    Model = the truth assignments of ALL variables (positive & negative), all initialised to None.
    """
    def __init__(self, symbols: Symbols, formula: Formula, model: Model):
        self.symbols = symbols
        self.formula = formula
        self.model = model

    # TODO complete algorithm
    def cdcl(self) -> bool:
        graph = ImplicationGraph()
        dl = 0 # decision level
        conf_clause = Solver.unit_propagate(self.formula, self.symbols, self.model, graph, dl)
        if conf_clause:
            return FALSE

        while not Solver.all_variables_assigned(self.formula, self.model):
            # decide stage
            var, val = Solver.pick_branching_variable(self.symbols)
            dl += 1
            self.model.extend(var, val)

            # deduce stage
            conf_clause = Solver.unit_propagate(self.formula, self.symbols, self.model, graph, dl)

            # diagnose stage
            if conf_clause:
                learnt, lvl = Solver.conflict_analysis(conf_clause, graph)
                if lvl < 0:
                    return FALSE
                else:
                    Solver.backtrack(self.formula, self.model, lvl)
                    # decrement decision level due to backtracking
                    dl = lvl
        return TRUE

    @classmethod
    def all_variables_assigned(cls, f: Formula, m: Model) -> bool:
        """
        Returns True when every symbol in the formula has an assignment in model.
        """
        for symbol in f.get_symbols():
            if m[symbol] == UNASSIGNED:
                return False
        return True

    @classmethod
    def unit_propagate(cls, f: Formula, s: Symbols, m: Model, g: ImplicationGraph, dl: int) -> Clause:
        """
        Returns None if no conflict is detected, or the conflicting clause otherwise.
        """
        # First filter out all SAT clauses
        while True:
            # propagation queue
            q = deque()
            for clause in f.get_clauses_with_learnt():
                clause_status = m.get_clause_status(clause)
                if clause_status == TRUE:
                    # ignore already satisfied clauses
                    continue
                elif clause_status == FALSE:
                    # one clause false -> formula false
                    g.add_conflict_node(clause, dl)
                    return clause
                else:
                    # filter unit clauses
                    is_unit, unassigned_sbl = m.is_unit_clause(clause)
                    if is_unit:
                        q.append((unassigned_sbl, clause))
            # propagate (if there's something to propagate)
            if len(q) == 0:
                return None
            else:
                while len(q) > 0:
                    symbol, antecedent = q.popleft()
                    symbol_pos, val = Solver.to_positive(symbol, TRUE)
                    m.extend(symbol_pos, val)
                    g.add_node(symbol_pos, val, antecedent, dl)

    @classmethod
    def pick_branching_variable(cls, symbols: Symbols):
        return symbols.pop_fifo()

    @classmethod
    def conflict_analysis(cls, c: Clause, g: ImplicationGraph, dl: int) -> (Clause, int):
        """
        Conflict analysis involves finding the first Unique Implication Point.
        A UIP is a node in the implication graph other than the conflict node that is on all paths from the current
        decision symbol (symbol@d) to the conflict (K@d).
        A First UIP is the UIP closest to the conflict.
        Receives conflicting clause, returns learnt clause and backtrack level
        """
        # Conflict at first unit propagation, not solvable!
        if dl == 0:
            return None, -1

        done_sbls_pos = set()
        curr_level_symbols = deque(g.get_symbols_at_lvl_in_clause(dl, c))
        learnt_clause = c
        while len(g.get_symbols_at_lvl_in_clause(dl, learnt_clause)) != 1:
            conflict_sbl = curr_level_symbols.popleft()
            conflict_sbl_pos = conflict_sbl.to_positive()
            clause = g.get_antecedent(conflict_sbl_pos)
            learnt_clause = Solver.resolution(learnt_clause, clause, conflict_sbl_pos)
            done_sbls_pos.add(conflict_sbl_pos)
            curr_level_symbols.extend(g.get_parent_list_at_lvl(conflict_sbl_pos, dl))

        lbd = [g.get_level(sbl.to_positive()) for sbl in learnt_clause] # TODO Assume every symbol in learnt clause is recorded in graph

        # TODO NOT SURE WHETHER DL-1 OR 0
        return learnt_clause, dl-1 if len(lbd) == 1 else learnt_clause, nlargest(2, lbd)[-1]

    @classmethod
    def backtrack(cls):
        # TODO migrate history from graph to here, also seems we don't need self.symbols
        pass

    @classmethod
    def resolution(cls, c1: Clause, c2: Clause, s: Symbol) -> Clause:
        assert (s in c1 and s.negate() in c2) or (s.negate() in c1 and s in c2)
        return Clause([sbl for sbl in c1 if sbl.literal != s.literal] +
                      [sbl for sbl in c2 if sbl.literal != s.literal])

    @classmethod
    def to_positive(cls, s: Symbol, val: bool) -> (Symbol, bool):
        """
        Returns respective symbol and truth assignment s.t. symbol is positive
        to_positive(Symbol(A, False), True)) -> Symbol(A, True), False
        to_positive(Symbol(A, True), False)) -> Symbol(A, True), False
        """
        return s, val if s.is_pos else s.negate(), not val
