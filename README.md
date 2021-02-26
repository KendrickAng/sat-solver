# sat-solver
Python 3.9.1

# Getting started

Run a single input file:\
`python main.py --file sample.cnf --log-level INFO --stats True`\
`python main.py --file uf20-91\uf20-01.cnf --log-level NONE --stats True`

- Argument to --file should be under the "test" folder.

Run all input files under a single directory:\
`python main.py --dir uf20-91 --log-level INFO`

- Argument to --dir should be under the "test" folder.

# Log levels
`NONE`: Turn off all logging (except print statements)
`INFO`: High-level overview of cdcl algorithm\
`DEBUG`: `INFO` + high-level methods called in main cdcl algorithm\
`TRACE`: `DEBUG` + low-level methods called by everything in "internal.sat" package

# Input
ALl Non-trivial CNF input has been taken from `https://www.cs.ubc.ca/~hoos/SATLIB/benchm.html`.

`uf20-91`: 20 variables, 91 clauses - 1000 instances, all satisfiable\
`uf50-218` / `uuf50-218`: 50 variables, 218 clauses - 1000 instances, all sat/unsat

# Backlog
- Add algorithm statistics (and a Stats Class)
- Add different branching heuristics
  - DLIS (OK)
- Add CryptoMiniSat
- Fix broken tests once branching vars are added (due to adding branching vars)