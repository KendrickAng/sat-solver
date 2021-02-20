from collections import deque
from heapq import nlargest
from internal.sat.model import Model
from internal.sat.symbol import Symbol
from internal.sat.symbols import Symbols
from internal.sat.formula import Formula
from internal.sat.clause import Clause
from internal.sat.state_manager import StateManager
from internal.sat.constants import TRUE, FALSE, UNASSIGNED
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
        self.state = StateManager(symbols)
        self.formula = formula
        self.model = model

    def cdcl(self) -> bool:
        dl = 0 # no guesses have been made

        while not Solver.all_variables_assigned(self.formula, self.model):
            # deduce stage
            # this strange position of unit_propagate is to ensure we propagate immediately after backtracking
            conf_clause = Solver.unit_propagate(self.formula, self.model, self.state, dl)

            if conf_clause:
                # diagnose stage
                learnt, lvl = Solver.conflict_analysis(conf_clause, self.state, dl)
                if lvl < 0:
                    return FALSE
                else:
                    # revert history to before we made the mistake
                    Solver.backtrack(self.state, lvl, dl)
                    # avoid repeating the same mistake
                    self.formula.add_learnt_clause(learnt)
                    # decrement decision level due to backtracking
                    dl = lvl
            elif Solver.all_variables_assigned(self.formula, self.model):
                break
            else:
                # decide stage
                dl += 1
                var, val = Solver.pick_branching_variable_update_state(self.state, dl)
                self.model.extend(var, val)

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
    def unit_propagate(cls, f: Formula, m: Model, state: StateManager, dl: int) -> Clause:
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
                    state.graph_add_conf_node(clause, dl)
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
                    state.graph_add_node(symbol_pos, val, antecedent, dl)
                    state.sbls_mark_assigned(symbol_pos)

    @classmethod
    def pick_branching_variable_update_state(cls, state: StateManager, dl: int) -> (Symbol, bool):
        """
        Picks new branching variable and updates history. dl for recording purposes.
        """
        sbl, val = state.sbls_get_unassigned_sbl_fifo()
        state.graph_add_node(sbl, val, None, dl)
        state.sbls_mark_assigned(sbl)
        return sbl, val


    @classmethod
    def conflict_analysis(cls, c: Clause, g: StateManager, dl: int) -> (Clause, int):
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
        curr_level_symbols = deque(g.graph_get_sbls_at_lvl_in_clause(dl, c))
        learnt_clause = c
        while len(g.graph_get_sbls_at_lvl_in_clause(dl, learnt_clause)) != 1:
            conflict_sbl = curr_level_symbols.popleft()
            conflict_sbl_pos = conflict_sbl.to_positive()
            if conflict_sbl_pos not in done_sbls_pos:
                clause = g.graph_get_antecedent(conflict_sbl_pos)
                learnt_clause = Solver.resolution(learnt_clause, clause, conflict_sbl_pos)
                done_sbls_pos.add(conflict_sbl_pos)
                curr_level_symbols.extend(g.graph_get_parent_list_at_lvl(conflict_sbl_pos, dl))

        # We assume every symbol in learnt clause is recorded in graph
        lbd = [g.graph_get_level(sbl.to_positive()) for sbl in learnt_clause]

        # NOT SURE WHETHER DL-1 OR 0
        return learnt_clause, 0 if len(lbd) == 1 else learnt_clause, nlargest(2, lbd)[-1]

    @classmethod
    def backtrack(cls, state: StateManager, dl_lower: int, dl_upper: int):
        assert dl_lower <= dl_upper
        # remove the branching history and implication graph history
        state.revert_history(dl_lower, dl_upper)

    @classmethod
    def resolution(cls, c1: Clause, c2: Clause, s: Symbol) -> Clause:
        assert c1 is not None
        assert c2 is not None
        assert (s in c1 and s.negate() in c2) or (s.negate() in c1 and s in c2)
        sbl_list_no_dups = list(set([sbl for sbl in c1 if sbl.literal != s.literal] +
                                    [sbl for sbl in c2 if sbl.literal != s.literal]))
        return Clause(sbl_list_no_dups)

    @classmethod
    def to_positive(cls, s: Symbol, val: bool) -> (Symbol, bool):
        """
        Returns respective symbol and truth assignment s.t. symbol is positive
        to_positive(Symbol(A, False), True)) -> Symbol(A, True), False
        to_positive(Symbol(A, True), False)) -> Symbol(A, True), False
        """
        if s.is_pos:
            return s, val
        else:
            return s.negate(), not val
