from collections import deque
from internal.sat.model import Model
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
    Symbols = the remaining unassigned symbols.
    Clauses = the set of clauses.
    Model = the truth assignments of all variables. Starts with all initialised to None.
    """
    def __init__(self, symbols: Symbols, formula: Formula, model: Model):
        self.symbols = symbols
        self.formula = formula
        self.model = model
        self.graph = ImplicationGraph()
        self.dl = 0
        self.conflict = None

    # TODO complete algorithm
    def cdcl(self) -> bool:
        up_result = Solver.unit_propagate(self.formula, self.symbols, self.model, self.graph, self.dl)
        if up_result == CONFLICT:
            return FALSE
        dl = 0 # decision level
        while not Solver.all_variables_assigned(self.formula, self.model):

            # decide stage
            var, val = self.pick_branching_variable(self.formula, self.model)
            dl += 1
            self.model.extend(var, val)

            # deduce stage
            up_result = Solver.unit_propagate(self.formula, self.model)

            # diagnose stage
            if up_result == CONFLICT:
                lvl, learnt = self.conflict_analysis(self.formula, self.model)
                if lvl < 0:
                    return FALSE
                else:
                    self.backtrack(self.formula, self.model, lvl)
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
        Returns None if no conflict is detected, or the literal causing the conflict, otherwise.
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
                    symbol, antecedent = q.pop()
                    m.extend(symbol, TRUE)
                    g.add_vertex(symbol, TRUE, antecedent, dl)
