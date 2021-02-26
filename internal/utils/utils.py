from typing import Callable, List
from collections import defaultdict
from internal.sat.model import Model
from internal.sat.solver import Solver
from internal.utils.exceptions import ArgumentFormatError
from internal.utils.logger import Logger
from internal.utils.parser import Parser
from internal.sat.state_manager import StateManager
from internal.sat.symbol import Symbol
from internal.sat.formula import Formula

logger = Logger.get_logger()

def solve_cnf(filepath: str, branch_heuristic: str):
    # parse
    prs = Parser()
    # Symbols (all pos), List[Symbol], Formula
    symbols, symbols_lst, formula = prs.parse(filepath)
    # generate solver
    heuristic_fn = get_branch_heuristic(branch_heuristic, symbols_lst)
    model = Model.from_symbols(symbols)
    solver = Solver(symbols, formula, model, heuristic_fn)
    # evaluate
    is_sat, sat_model = solver.cdcl()
    print(f"SATISIFABLE: {is_sat}")
    if sat_model:
        print(f"MODEL: {sat_model}")

# Returns a function that takes in a state and formula, and returns a symbol and its assignment.
def get_branch_heuristic(heuristic: str, sbl_lst: List[Symbol]) -> Callable:
    def dlis(state: StateManager, formula: Formula) -> (Symbol, bool):
        """
        Dynamic Largest Individual Sum (DLIS)
        """
        sbls_pos = state.unassigned_symbols # unassigned symbols only
        unsat_clauses = Solver.get_unresolved_clauses(formula, state.model)
        scores = defaultdict(int)
        for unsat_clause in unsat_clauses:
            for sbl in unsat_clause:
                scores[sbl] += 1
        sbl = max(sbls_pos, key=lambda s: scores[s])
        return (sbl, True) if scores[sbl] >= scores[sbl.negate()] else (sbl, False)

    def default(state: StateManager, formula: Formula) -> (Symbol, bool):
        sbl, val = state.sbls_get_unassigned_sbl_fifo()
        return sbl, val

    if heuristic == "DLIS":
        print("BRANCHING HEURISTIC: DLIS")
        return dlis
    elif heuristic == "DEFAULT":
        print("BRANCHING HEURISTIC: DEFAULT")
        return default

    raise ArgumentFormatError(f"{heuristic} is not a valid branching heuristic")
