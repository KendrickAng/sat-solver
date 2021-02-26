import argparse, os
import cProfile, pstats
import time
from internal.utils.logger import Logger
from internal.utils.utils import solve_cnf, get_branch_heuristic

# setup
parser = argparse.ArgumentParser(description="CDCL SAT Solver.\n"
                                             "To start, specify either a file or directory under '/input'.\n"
                                             "Examples:\n"
                                             "From file: python3 main.py -f sample.cnf -l DEBUG -p False\n"
                                             "From directory: python3 main.py -f uf20-91 -l INFO -p False\n")
parser.add_argument("-f", "--file", dest="input_file", type=str,
                    help="Input file in DIMACS format in directory 'input'.")
parser.add_argument("-d", "--dir", dest="input_dir", type=str,
                    help="Input directory under directory 'input' to get .cnf files from.")
parser.add_argument("-l", "--log-level", dest="log_level", type=str, default="NONE",
                    help="Log level. INFO/DEBUG/ERROR. Default: NONE.")
parser.add_argument("-p", "--profile", dest="profile", action='store_true',
                    help="Activate profiling. Slows program significantly. Off by default.")
parser.add_argument("-s", "--stats", dest="stats", action='store_true',
                    help="Activate statistics. Slows program minimally. Off by default.")
parser.add_argument("-b", "--branch-heuristic", dest="heuristic", type=str, default="DEFAULT",
                    help="Branching variable heuristic. Default: DEFAULT")

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

# profiling
pr = cProfile.Profile(timer=time.process_time)

if args.input_file:
    filepath = os.path.join(input_dir_path, args.input_file)
    if args.stats:
        tic = time.perf_counter()
    if args.profile:
        pr.enable()

    solve_cnf(filepath, args.heuristic)

    if args.stats:
        toc = time.perf_counter()
        print(f"Program ran in {toc-tic:0.4f} seconds")
    if args.profile:
        pr.disable()
        ps = pstats.Stats(pr).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats(10)
elif args.input_dir:
    dirpath = os.path.join(input_dir_path, args.input_dir)
    if args.profile:
        pr.enable()

    for entry in os.scandir(dirpath):
        solve_cnf(entry.path, args.heuristic)

    if args.profile:
        pr.disable()
        ps = pstats.Stats(pr).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats(10)
else:
    parser.print_help()
    exit(-1)
