from random import getrandbits
from typing import Callable, List
from collections import defaultdict
from internal.utils.constants import F_HEURISTIC, F_STATS
from internal.sat.model import Model
from internal.sat.solver import Solver
from internal.sat.stats import Stats
from internal.utils.exceptions import ArgumentFormatError
from internal.utils.logger import Logger
from internal.utils.parser import Parser
from internal.sat.state_manager import StateManager
from internal.sat.symbol import Symbol
from internal.sat.formula import Formula

logger = Logger.get_logger()

def solve_cnf(filepath: str, config: dict):
    # parse
    prs = Parser()
    # Symbols (all pos), List[Symbol], Formula
    symbols, symbols_lst, formula = prs.parse(filepath)

    # generate solver
    heuristic_fn = get_branch_heuristic(config[F_HEURISTIC], symbols_lst)
    model = Model.from_symbols(symbols)
    stats = Stats()
    if config[F_STATS]:
        solver = Solver(symbols, formula, model, heuristic_fn, stats, config)
    else:
        solver = Solver(symbols, formula, model, heuristic_fn, None, config)

    # evaluate
    is_sat, sat_model = solver.cdcl()

    # display results
    print(f"SATISIFABLE: {is_sat}")
    if sat_model:
        print(f"MODEL: {sat_model}")
    if config[F_STATS]:
        print(stats.string())

# Returns a function that takes in a state and formula, and returns a symbol and its assignment.
def get_branch_heuristic(heuristic: str, sbl_lst: List[Symbol]) -> Callable:
    def dlis(state: StateManager, formula: Formula) -> (Symbol, bool):
        """
        Dynamic Largest Individual Sum (DLIS).
        Counts the number of unresolved clauses in which a given symbol x appears as a positive literal, Cp
        and as a negative literal Cn.
        Consider these values separately.
        Select the variable with the largest individual value, assign it true if Cp >= Cn, false otherwise.
        """
        sbls_pos = state.unassigned_symbols # unassigned symbols only
        unass_cls = Solver.get_unresolved_clauses(formula, state.model)
        scores = defaultdict(int)
        for unsat_clause in unass_cls:
            for sbl in unsat_clause:
                scores[sbl] += 1
        sbl = max(sbls_pos, key=lambda s: scores[s])
        return (sbl, True) if scores[sbl] >= scores[sbl.negate()] else (sbl, False)

    def rdlis(state: StateManager, formula: Formula) -> (Symbol, bool):
        """
        Random DLIS, a variation of DLIS, randomly selects the value to be assigned to a given selected variable,
        instead of comparing Cp with Cn, avoiding making too many bad decisions for a few specific instances.
        """
        sbls_pos = state.unassigned_symbols  # unassigned symbols only
        unass_cls = Solver.get_unresolved_clauses(formula, state.model)
        scores = defaultdict(int)
        for unsat_clause in unass_cls:
            for sbl in unsat_clause:
                scores[sbl] += 1
        sbl = max(sbls_pos, key=lambda s: scores[s])
        return sbl, not getrandbits(1)

    def jwos(state: StateManager, formula: Formula) -> (Symbol, bool):
        """
        Jeroslow-Wang-one-sided (JW-OS) branching heuristic.
        For each literal in unassigned clauses, let
        J(l) = sum(for all lit in clause for all clause in formula s2^{-|w|})
        where |w| is the number of unassigned clauses the literal appears in.
        Select the assignment that satisfies the literal with largest value J(l).
        """
        sbls_pos = state.unassigned_symbols # unassigned symbols only
        unass_cls = Solver.get_unresolved_clauses(formula, state.model)
        scores = defaultdict(float)
        for unsat_clause in unass_cls:
            for s in unsat_clause:
                scores[s.literal] += pow(2, -len(unsat_clause))
        sbl = max(sbls_pos, key=lambda sb: scores[sb.literal])
        return sbl, True

    def jwts(state: StateManager, formula: Formula) -> (Symbol, bool):
        """
        Jeroslow-Wang-two-sided (JS-TS) branching heuristic.
        Identifies the variable x with the largest sum J(x) + J(-x)
        Assign x value true if J(x) >= J(-x), false otherwise.
        """
        sbls_pos = state.unassigned_symbols # unassigned symbols only
        scores = defaultdict(float)
        unass_cls = Solver.get_unresolved_clauses(formula, state.model)
        for c in unass_cls:
            for s in c:
                scores[s] += pow(2, -len(c))
        unass_sbls = [s for s in sbls_pos] + [s.negate() for s in sbls_pos]
        sbl = max(unass_sbls, key=lambda sb: scores[sb] + scores[sb.negate()])
        return (sbl, True) if scores[sbl] >= scores[sbl.negate()] else (sbl, False)

    def moms(state: StateManager, formula: Formula) -> (Symbol, bool):
        """
        Maximum Occurrences on clauses of Minimum Size (MOM's) heuristic.
        Returns the literal with the largest number of occurrences in the smallest unresolved clauses.
        """
        sbls = state.unassigned_symbols # unassigned postiive symbols only
        scores = defaultdict(int)
        clauses = Solver.get_min_unresolved_clauses(formula, state.model)
        for c in clauses:
            for s in c:
                scores[s.literal] += 1
        sbl = max(sbls, key=lambda x: scores[x.literal])
        return sbl, True

    def default(state: StateManager, formula: Formula) -> (Symbol, bool):
        sbl, val = state.sbls_get_unassigned_sbl_fifo()
        return sbl, val

    if heuristic == "DLIS":
        print("BRANCHING HEURISTIC: DLIS")
        return dlis
    elif heuristic == "RDLIS":
        print("BRANCHING HEURISTIC: RDLIS")
        return rdlis
    elif heuristic == "JWOS":
        print("BRANCHING HEURISTIC: JWOS")
        return jwos
    elif heuristic == "JWTS":
        print("BRANCHING HEURISTIC: JWTS")
        return jwts
    elif heuristic == "MOMS":
        print("BRANCHING HEURISTIC: MOMS")
        return moms
    elif heuristic == "DEFAULT":
        print("BRANCHING HEURISTIC: DEFAULT")
        return default

    raise ArgumentFormatError(f"{heuristic} is not a valid branching heuristic")
