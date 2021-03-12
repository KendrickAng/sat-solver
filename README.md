# sat-solver
Python 3.9.1

# Getting started

Run a single input file:\
`python main.py --file sample.cnf --branch-heuristic DLIS --stats --progress-bar`\
`python main.py --file uf20-91\uf20-01.cnf --branch-heuristic DLIS --stats --progress-bar`

- Argument to --file should be under the "test" folder.

Run all input files under a single directory:\
`python main.py --dir uf20-91 --log-level INFO`

- Argument to --dir should be under the "test" folder.

# Flags
To see help for all available flags, run `python main.py -h`
- Input file in DIMACS format
  - `--file` or `-f`
- Input directory, all files in DIMACS format
  - `--dir` or `-d`
- Branching variable heuristic
  - Heuristic to select the next symbol to assign
  - `--branch-heuristic` or `-b`
  - `DLIS`: Dynamic Largest Individual Sum (of literals)
  - `RDLIS`: Random DLIS
  - `MOMS` : Maximum Occurrences on clauses of Minimum Size
  - `JWOS`: Jeroslow-Wang one-sided
  - `JWTS`: Jeroslow-Wang two-sided
  - `RANDOM`: Random selection from unassigned symbols
  - `3CH`: Three-clause heuristic, select the symbol with maximum occurrences in 3-clauses
  - `DEFAULT`: Selects in FIFO the next unassigned positive symbol, assigns it true 
- Log level
  - `--log-level` or `l`
  - `NONE`: Turn off all logging (except print statements)
  - `INFO`: High-level overview of cdcl algorithm
  - `DEBUG`: `INFO` + high-level methods called in main cdcl algorithm
  - `TRACE`: `DEBUG` + low-level methods called by everything in "internal.sat" package
- Profiling
  - Profiles the program, printing time spent in each function. Slows program execution.
  - `--profile` or `-p`
- Statistics
  - Time spent to execute CDCL algorithm + number of branches
  - `--stats` or `-s`
- Progress tracker
  - Displays the percentage of resolved clauses (of 100%)
  - `--progress-bar` or `-pb`

# Input
All Non-trivial CNF input has been taken from `https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html`.

`uf20-91`: 20 variables, 91 clauses - 1000 instances, all satisfiable\
`uf50-218` / `uuf50-218`: 50 variables, 218 clauses - 1000 instances, all sat/unsat

# Manual Verification with CryptoMiniSat
1. Navigate to the `cryptominisat` folder
1. Run `.\cryptominisat5.exe --verb 0 <filename>.cnf`
  - E.g `.\cryptominisat5.exe --verb 0 ..\input\sample.cnf`
  - E.g `.\cryptominisat5.exe --verb 0 sample_unsat.cnf`
1. Either `SATISFIABLE` or `UNSATISFIABLE` will be output.
1. Note that the sample input from `https://www.cs.ubc.ca` is not compatible due to the presence of disallowed characters `%` and the `0` at the end.

# Backlog
- https://baldur.iti.kit.edu/sat/files/2016/l05.pdf 
- Restarts
- Lazy data structures
- Fix broken tests once branching vars are added (due to adding branching vars)