from internal.sat.model import Model
from internal.sat.solver import Solver
from internal.utils.logger import Logger
from internal.utils.parser import Parser

logger = Logger.get_logger()

def solve_cnf(filepath):
    # parse
    prs = Parser()
    symbols, formula = prs.parse(filepath)
    # generate solver
    model = Model.from_symbols(symbols)
    solver = Solver(symbols, formula, model)
    # evaluate
    is_sat, sat_model = solver.cdcl()
    print(f"SATISIFABLE: {is_sat}")
    if sat_model:
        print(f"MODEL: {sat_model}")