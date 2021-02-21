import argparse, os
from internal.utils.logger import Logger
from internal.utils.utils import solve_cnf

# setup
parser = argparse.ArgumentParser(description="CDCL SAT Solver.\n"
                                             "To start, specify either a file or directory under '/input'.\n"
                                             "Examples:\n"
                                             "From file: python3 main.py -f sample.cnf -l DEBUG\n"
                                             "From directory: python3 main.py -f uf20-91 -l INFO\n")
parser.add_argument("-f", "--file", dest="input_file", type=str,
                    help="Input file in DIMACS format in directory 'input'.")
parser.add_argument("-d", "--dir", dest="input_dir", type=str,
                    help="Input directory under directory 'input' to get .cnf files from.")
parser.add_argument("-l", "--log-level", dest="log_level", type=str,
                    help="Log level. INFO/DEBUG/ERROR. Default: INFO. Optional.")

args = parser.parse_args()

if args.input_file and args.input_dir:
    parser.print_help()
    exit(-1)
if not (args.input_file or args.input_dir):
    parser.print_help()
    exit(-1)

Logger.set_level(args.log_level)
logger = Logger.get_logger()

# parse
root_dir_path = os.path.dirname(__file__)
input_dir_path = os.path.join(root_dir_path, "input")

if args.input_file:
    filepath = os.path.join(input_dir_path, args.input_file)
    solve_cnf(filepath)
elif args.input_dir:
    dirpath = os.path.join(input_dir_path, args.input_dir)
    for entry in os.scandir(dirpath):
        solve_cnf(entry.path)
else:
    parser.print_help()
    exit(-1)
