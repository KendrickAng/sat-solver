import argparse, os
from internal.utils.logger import Logger
from internal.utils.parser import Parser
from internal.sat.model import Model
from internal.sat.solver import Solver

# setup
parser = argparse.ArgumentParser(description="CDCL SAT Solver.\nExample: python3 main.py -f sample.cnf -l DEBUG")
parser.add_argument("-f", "--file", dest="input_file", type=str,
                    help="Input file in DIMACS format in directory 'input'. Required.")
parser.add_argument("-l", "--log-level", dest="log_level", type=str,
                    help="Log level. INFO/DEBUG/ERROR. Default: INFO. Optional.")

args = parser.parse_args()
if not args.input_file:
    parser.print_help()
    exit(-1)

Logger.set_level(args.log_level)

# parse
file_dir = os.path.dirname(__file__)
file_path = os.path.join(file_dir, "input", args.input_file)
prs = Parser()
symbols, clauses = prs.parse(file_path)

# evaluate
model = Model.from_symbols(symbols)
solver = Solver(symbols, clauses, model)
solver.cdcl()
