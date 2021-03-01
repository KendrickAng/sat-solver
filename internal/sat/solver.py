from collections import deque
from typing import List, Callable
from heapq import nlargest
from internal.sat.model import Model
from internal.sat.stats import Stats
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
    def __init__(self, symbols: Symbols, formula: Formula, model: Model, heuristic_fn: Callable, stats: Stats):
        self.state = StateManager(symbols, model)
        self.formula = formula
        self.heuristic_fn = heuristic_fn
        self.stats = stats

    def cdcl(self) -> (bool, Model):
        logger.info(f"Formula {self.formula}")
        logger.info(f"Initial model {self.state.get_model()}")
        dl = 0 # no guesses have been made

        while not Solver.all_variables_assigned(self.formula, self.state.get_model()):
            logger.info(f"Now at decision level: {dl}")
            logger.info(f"Current model: {self.state.get_model_summary()}")

            # deduce stage
            # this strange position of unit_propagate is to ensure we propagate immediately after backtracking
            logger.info(f"Begin unit propagation")
            conf_clause = Solver.unit_propagate(self.formula, self.state, dl)
            logger.info(f"End unit propagation")

            if conf_clause:
                # diagnose stage
                logger.info(f"Begin conflict analysis on clause {conf_clause}")
                learnt, lvl = Solver.conflict_analysis(conf_clause, self.state, dl)
                logger.info(f"End conflict analysis on clause {conf_clause}")
                logger.debug(f"Decision level reset to {lvl}")
                logger.debug(f"Learnt {learnt}")
                if lvl < 0:
                    return FALSE, None
                else:
                    # revert history to before we made the mistake
                    logger.info(f"Begin backtrack from {dl} to {lvl}")
                    Solver.backtrack(self.state, lvl, dl)
                    logger.info(f"End backtrack from {dl} to {lvl}")
                    # avoid repeating the same mistake
                    self.formula.add_learnt_clause(learnt)
                    # decrement decision level due to backtracking
                    dl = lvl
            elif Solver.all_variables_assigned(self.formula, self.state.get_model()):
                logger.info("All variables assigned, break")
                break
            else:
                # decide stage
                dl += 1
                logger.info(f"Begin pick branching variable")
                var, val = Solver.pick_branching_variable_update_state(self.state, dl, self.heuristic_fn, self.formula)
                logger.info(f"End pick branching variable {var} {val}")
                self.state.extend_model(var, val)
                self.stats.inc_bc()

        # if we reach here, formula must be sat
        formula_status = self.state.get_model().get_formula_status(self.formula)
        assert formula_status == TRUE
        logger.info(f"Verified formula SAT status with model")

        return TRUE, self.state.get_model_summary()

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
    def unit_propagate(cls, f: Formula, state: StateManager, dl: int) -> Clause:
        """
        Returns None if no conflict is detected, or the conflicting clause otherwise.
        """
        # First filter out all SAT clauses
        while True:
            # propagation queue
            q = deque()
            seen_symbols = set()
            for clause in f.get_clauses_with_learnt():
                clause_status = state.get_model_clause_status(clause)
                if clause_status == TRUE:
                    # ignore already satisfied clauses
                    continue
                elif clause_status == FALSE:
                    # one clause false -> formula false
                    logger.debug(f"Found UNSAT clause {clause}")
                    return clause
                else:
                    # filter unit clauses
                    is_unit, unassigned_sbl = state.get_model().is_unit_clause(clause)
                    tup = (unassigned_sbl, clause)
                    if is_unit and not (unassigned_sbl in seen_symbols or unassigned_sbl.negate() in seen_symbols):
                        q.append(tup)
                        # don't add the same symbol to the implication graph in one UP
                        seen_symbols.add(unassigned_sbl)
            logger.debug(f"Propagate queue: {q}")
            # propagate (if there's something to propagate)
            if len(q) == 0:
                return None
            else:
                while len(q) > 0:
                    symbol, antecedent = q.popleft()
                    symbol_pos, val = Solver.to_positive(symbol, TRUE)
                    state.get_model().extend(symbol_pos, val)
                    state.add_graph_node(symbol_pos, val, antecedent, dl)
                    state.sbls_mark_assigned(symbol_pos)

    @classmethod
    def pick_branching_variable_update_state(cls,
                                             state: StateManager,
                                             dl: int,
                                             heuristic_fn: Callable,
                                             formula: Formula
                                             ) -> (Symbol, bool):
        """
        Picks new branching variable and updates history. dl for recording purposes.
        """
        sbl, val = heuristic_fn(state, formula)
        # sbl, val = state.sbls_get_unassigned_sbl_fifo()
        logger.debug(f"Pick unassigned symbol {sbl} {val}")
        state.add_graph_node(sbl, val, None, dl)
        logger.debug(f"Update implication graph {sbl} {val} {None} {dl}")
        state.sbls_mark_assigned(sbl)
        logger.debug(f"Mark {sbl} as assigned")
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
        def next_recently_assigned(pool: List[Symbol]) -> (Symbol, List[Symbol]):
            """
            Separate the latest assigned symbol according to assignment history from the rest in the clause
            """
            assign_history = list(g.get_history(dl))
            for s in reversed(assign_history):
                if s in pool or s.negate() in pool:
                    return s, [x for x in pool if x.literal != s.literal]

        # Conflict at first unit propagation, not solvable!
        if dl == 0:
            return None, -1

        done_sbls_pos = set()
        learnt_clause = c
        symbol_pool = c.symbol_list
        # Continue until first UIP
        while len(g.get_graph_sbls_at_lvl_in_clause(dl, learnt_clause)) != 1:
            if len(symbol_pool) == 0:
                break
            last_assigned, symbol_pool = next_recently_assigned(symbol_pool)
            last_assgn_pos = last_assigned.to_positive()
            if last_assgn_pos not in done_sbls_pos:
                done_sbls_pos.add(last_assgn_pos)
                clause = g.get_graph_antecedent(last_assgn_pos)
                symbol_pool.extend(g.get_graph_parent_symbols(last_assgn_pos))
                if clause: # branching variables have no antecedent
                    logger.debug(f"Resolution {learnt_clause} {clause}")
                    learnt_clause = Solver.resolution(learnt_clause, clause, last_assgn_pos)

        # We assume every symbol in learnt clause is recorded in implication graph
        lbd = [g.get_graph_level(sbl.to_positive()) for sbl in learnt_clause]

        return (learnt_clause, 0) if len(lbd) == 1 else (learnt_clause, nlargest(2, lbd)[-1])

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

    @classmethod
    def get_unresolved_clauses(cls, f: Formula, m: Model) -> List[Clause]:
        return [x for x in f.get_clauses_with_learnt() if m.get_clause_status(x) == UNASSIGNED]
