import argparse, os
import cProfile, pstats
import time
from internal.utils.constants import *
from internal.utils.logger import Logger
from internal.utils.utils import solve_cnf

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
parser.add_argument("-pb", "--progress-bar", dest="progress", action='store_true',
                    help="Activate progress tracker. Slows program minimally. Off by default.")
parser.add_argument("-b", "--branch-heuristic", dest="heuristic", type=str, default="DEFAULT",
                    help="Branching variable heuristic. Default: DEFAULT")

args = parser.parse_args()

config = {
    F_INPUT_FILE: args.input_file,
    F_INPUT_DIR: args.input_dir,
    F_LOG_LEVEL: args.log_level,
    F_PROFILE: args.profile,
    F_STATS: args.stats,
    F_PROGRESS: args.progress,
    F_HEURISTIC: args.heuristic
}

if config[F_INPUT_FILE] and config[F_INPUT_DIR]:
    parser.print_help()
    exit(-1)
if not (config[F_INPUT_FILE] or config[F_INPUT_DIR]):
    parser.print_help()
    exit(-1)

Logger.set_level(config[F_LOG_LEVEL])
logger = Logger.get_logger()

# parse
root_dir_path = os.path.dirname(__file__)
input_dir_path = os.path.join(root_dir_path, "input")

# profiling
pr = cProfile.Profile(timer=time.process_time)

if config[F_INPUT_FILE]:
    filepath = os.path.join(input_dir_path, config[F_INPUT_FILE])
    if config[F_PROFILE]:
        print("Profiling activated")
        pr.enable()

    solve_cnf(filepath, config)

    if config[F_PROFILE]:
        pr.disable()
        ps = pstats.Stats(pr).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats(10)
elif config[F_INPUT_DIR]:
    dirpath = os.path.join(input_dir_path, config[F_INPUT_DIR])
    if config[F_PROFILE]:
        print("Profiling activated")
        pr.enable()

    for entry in os.scandir(dirpath):
        print(entry.path)
        solve_cnf(entry.path, config)

    if config[F_PROFILE]:
        pr.disable()
        ps = pstats.Stats(pr).sort_stats(pstats.SortKey.CUMULATIVE)
        ps.print_stats(10)
else:
    parser.print_help()
    exit(-1)
